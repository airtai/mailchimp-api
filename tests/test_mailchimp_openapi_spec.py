from collections.abc import Iterator

from autogen import UserProxyAgent
from fastagency.api.openapi.client import OpenAPI

from mailchimp_api.utils.create_api import create_api

from unittest.mock import MagicMock, patch
import pytest

class TestMailchimpOpenapiSpec:
    @pytest.fixture(autouse=True)
    def setup(
        self,
    ) -> Iterator[None]:
        self.api = create_api(mailchimp_api_key="test Key")
        yield


    def test_create_api(self) -> None:
        assert isinstance(self.api, OpenAPI)
        url = self.api.servers[0]["url"]
        assert url == "https://us14.api.mailchimp.com/3.0", url

    @patch("fastagency.api.openapi.client.requests.get")
    def test_mailchimp_api(
        self,
        mock_post: MagicMock,
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
        self.api._register_for_execution(user_proxy, functions=functions)

        assert tuple(user_proxy._function_map.keys()) == ("get_ping",)

        get_ping = user_proxy._function_map["get_ping"]
        get_ping(body={})

        mock_post.assert_called_once_with(
            f"{self.api.servers[0]['url']}/ping",
            params={},
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic YW55c3RyaW5nOnRlc3QgS2V5',
            },
        )
