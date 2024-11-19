from typing import Any

import requests

from ..config import Config


class MailchimpService:
    def __init__(self, config: Config) -> None:
        self.config = config

    def _mailchim_request_get(self, url: str) -> Any:
        response = requests.get(url, headers=self.config.headers, timeout=10)

        if response.status_code != 200:
            # This automatically raises an HTTPError with details
            response.raise_for_status()

        return response.json()

    def get_account_lists(self) -> dict[str, list[dict[str, str]]]:
        """Get information about all lists in the account."""
        url = f"{self.config.base_url}/lists?fields=lists.id,lists.name"

        return self._mailchim_request_get(url)  # type: ignore[no-any-return]

    def get_members(self, list_id: str) -> dict[str, list[dict[str, str]]]:
        url = f"{self.config.base_url}lists/{list_id}/members?fields=members.email_address,members.id"

        return self._mailchim_request_get(url)  # type: ignore[no-any-return]
