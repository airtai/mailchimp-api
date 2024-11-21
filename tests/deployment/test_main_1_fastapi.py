from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from mailchimp_api.deployment.main_1_fastapi import _save_file


class TestUploadFile:
    def test_get_df(self) -> None:
        csv_content = "email\nexample1@example.com\nexample2@example.com"
        csv_file = BytesIO(csv_content.encode("utf-8"))
        uploaded_file = UploadFile(filename="emails.csv", file=csv_file)
        path = _save_file(uploaded_file, "22-09-2021")
        df = pd.read_csv(path)

        expected_df = pd.DataFrame(
            {"email": ["example1@example.com", "example2@example.com"]}
        )
        assert df.equals(expected_df)
