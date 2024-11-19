from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from mailchimp_api.config import Config
from mailchimp_api.services.mailchimp_service import MailchimpService


class TestMailchimpService:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.config = Config(dc="us14", api_key="anystring")
        self.mailchimp_service = MailchimpService(config=self.config)
        return

    def _setup_mailchimp_request_get(
        self,
        mock_get: MagicMock,
        status_code: int = 200,
        json_response: Optional[dict[str, str]] = None,
    ) -> None:
        if json_response is None:
            json_response = {"status": "success"}
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_response
        mock_get.return_value = mock_response

    @patch("mailchimp_api.services.mailchimp_service.requests.get")
    def test_mailchimp_request_get(self, mock_get: MagicMock) -> None:
        self._setup_mailchimp_request_get(mock_get)
        self.mailchimp_service._mailchim_request_get(url="http://test123.com")

        mock_get.assert_called_once_with(
            "http://test123.com",
            headers=self.config.headers,
            timeout=10,
        )

    @patch("mailchimp_api.services.mailchimp_service.requests.get")
    def test_get_account_lists(self, mock_get: MagicMock) -> None:
        self._setup_mailchimp_request_get(mock_get)
        self.mailchimp_service.get_account_lists()

        mock_get.assert_called_once_with(
            f"{self.config.base_url}/lists?fields=lists.id,lists.name",
            headers=self.config.headers,
            timeout=10,
        )

    @patch("mailchimp_api.services.mailchimp_service.requests.get")
    def test_get_members(self, mock_get: MagicMock) -> None:
        self._setup_mailchimp_request_get(mock_get)
        self.mailchimp_service.get_members(list_id="123")

        mock_get.assert_called_once_with(
            f"{self.config.base_url}lists/123/members?fields=members.email_address,members.id",
            headers=self.config.headers,
            timeout=10,
        )

    @patch("mailchimp_api.services.mailchimp_service.requests.get")
    def test_get_tags(self, mock_get: MagicMock) -> None:
        self._setup_mailchimp_request_get(mock_get)
        self.mailchimp_service.get_tags(list_id="123", member_id="456")

        mock_get.assert_called_once_with(
            f"{self.config.base_url}lists/123/members/456/tags?fields=tags.name",
            headers=self.config.headers,
            timeout=10,
        )
