from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from mailchimp_api.config import Config
from mailchimp_api.processing.update_tags import update_tags
from mailchimp_api.services.mailchimp_service import MailchimpService


class TestUpdateTags:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.config = Config(dc="us14", api_key="anystring")
        # self.config = Config(dc="us14", api_key=os.getenv("MAILCHIMP_API_KEY"))
        self.mailchimp_service = MailchimpService(config=self.config)
        return

    def _setup_mailchimp_request_method(
        self,
        mock_get: MagicMock,
        json_responses: list[Any],
        status_code: int = 200,
    ) -> None:
        side_effect = []
        for json_response in json_responses:
            mock_response = MagicMock()
            mock_response.status_code = status_code
            mock_response.json.return_value = json_response
            side_effect.append(mock_response)

        mock_get.side_effect = side_effect

    @patch("mailchimp_api.services.mailchimp_service.requests.get")
    def test_update_tags(self, mock_get: MagicMock) -> None:
        json_responses = [
            {"lists": [{"id": "list_id", "name": "airt"}]},
            {
                "members": [
                    {
                        "id": "first_member_id",
                        "email_address": "email1@airt.ai",
                        "tags": [
                            {"id": 1, "name": "Test API Tag"},
                            {"id": 2, "name": "M3"},
                        ],
                    },
                    {
                        "id": "second_member_id",
                        "email_address": "email2@gmail.com",
                        "tags": [
                            {"id": 1, "name": "Test API Tag"},
                            {"id": 2, "name": "M3"},
                            {"id": 3, "name": "test-tag"},
                        ],
                    },
                    {
                        "id": "third_member_id",
                        "email_address": "email2@airt.ai",
                        "tags": [
                            {"id": 1, "name": "Test API Tag"},
                            {"id": 2, "name": "M2"},
                        ],
                    },
                ]
            },
        ]
        crm_df = pd.DataFrame(
            {
                "email": [
                    "email1@airt.ai",
                    "email2@airt.ai",
                ]
            }
        )
        self._setup_mailchimp_request_method(mock_get, json_responses=json_responses)
        update_tags(crm_df=crm_df, config=self.config, list_name="airt")
