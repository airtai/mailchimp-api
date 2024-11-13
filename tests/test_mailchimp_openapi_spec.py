from unittest.mock import MagicMock, patch

import pytest
from autogen import UserProxyAgent
from fastagency.api.openapi.client import OpenAPI

from mailchimp_api.utils.create_api import create_api


@pytest.fixture(scope="class")
def setup_api() -> OpenAPI:
    return create_api(mailchimp_api_key="test Key")  # pragma: allowlist secret


class TestMailchimpOpenapiSpec:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
    ) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic YW55c3RyaW5nOnRlc3QgS2V5",
        }
        return

    def test_create_api(self, setup_api: OpenAPI) -> None:
        assert isinstance(setup_api, OpenAPI)
        url = setup_api.servers[0]["url"]
        assert url == "https://us14.api.mailchimp.com/3.0", url

    def _test_mailchimp_api(
        self,
        mock_post: MagicMock,
        setup_api: OpenAPI,
        function: str,
    ) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_post.return_value = mock_response

        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
        )

        setup_api._register_for_execution(user_proxy, functions=[function])

        assert tuple(user_proxy._function_map.keys()) == (function,)

        func = user_proxy._function_map[function]
        func(body={})

    @patch("fastagency.api.openapi.client.requests.get")
    def test_mailchimp_api(
        self,
        mock_post: MagicMock,
        setup_api: OpenAPI,
    ) -> None:
        self._test_mailchimp_api(
            mock_post=mock_post,
            setup_api=setup_api,
            function="get_ping",
        )

        mock_post.assert_called_once_with(
            f"{setup_api.servers[0]['url']}/ping",
            params={},
            headers=self.headers,
        )
