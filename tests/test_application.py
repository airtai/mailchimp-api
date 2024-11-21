from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile
from pandas import DataFrame

from mailchimp_api.application import get_df


class TestUploadFile:
    def test_get_df(self) -> None:
        csv_content = "email\nexample1@example.com\nexample2@example.com"
        csv_file = BytesIO(csv_content.encode("utf-8"))
        uploaded_file = UploadFile(filename="emails.csv", file=csv_file)
        df = get_df(uploaded_file)

        expected_df = DataFrame(
            {"email": ["example1@example.com", "example2@example.com"]}
        )
        assert df.equals(expected_df)

    @pytest.mark.parametrize(
        ("filename", "content", "expected_error"),
        [
            ("emails.txt", "email\n", "Only CSV files are supported"),
            (
                "emails.csv",
                "first_column\n",
                "'email' column not found in CSV file",
            ),
        ],
    )
    def test_get_df_raises_error(
        self, filename: str, content: str, expected_error: str
    ) -> None:
        csv_file = BytesIO(content.encode("utf-8"))
        uploaded_file = UploadFile(filename=filename, file=csv_file)

        with pytest.raises(HTTPException) as e:
            get_df(uploaded_file)

        assert e.value.detail == expected_error
