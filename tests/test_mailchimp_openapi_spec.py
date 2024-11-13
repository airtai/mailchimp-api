from collections.abc import Iterator

from autogen import UserProxyAgent
from fastagency.api.openapi.client import OpenAPI

from mailchimp_api.utils.create_api import create_api

from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture(scope="class")
def setup_api() -> OpenAPI:
    return create_api(mailchimp_api_key="test Key") # pragma: allowlist secret

class TestMailchimpOpenapiSpec:

    def test_create_api(self, setup_api: OpenAPI) -> None:
        assert isinstance(setup_api, OpenAPI)
        url = setup_api.servers[0]["url"]
        assert url == "https://us14.api.mailchimp.com/3.0", url

    @patch("fastagency.api.openapi.client.requests.get")
    def test_mailchimp_api(
        self,
        mock_post: MagicMock,
        setup_api: OpenAPI,
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

        functions = ["get_ping"]
        setup_api._register_for_execution(user_proxy, functions=functions)

        assert tuple(user_proxy._function_map.keys()) == ("get_ping",)

        get_ping = user_proxy._function_map["get_ping"]
        get_ping(body={})

        mock_post.assert_called_once_with(
            f"{setup_api.servers[0]['url']}/ping",
            params={},
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic YW55c3RyaW5nOnRlc3QgS2V5',
            },
        )
