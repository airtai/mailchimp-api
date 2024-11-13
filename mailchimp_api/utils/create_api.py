from pathlib import Path
from typing import Optional

from fastagency.api.openapi.client import OpenAPI
from fastagency.api.openapi.security import HTTPBasic


def create_api(
    mailchimp_api_key: Optional[str] = None,
) -> OpenAPI:
    mailchimp_file_path = Path(__file__).parent.parent.parent / "mailchimp_openapi.json"
    with mailchimp_file_path.open(encoding="utf-8") as f:
        openapi_json = f.read()

    api = OpenAPI.create(
        openapi_json=openapi_json,
    )
    if mailchimp_api_key:
        api.set_security_params(
            HTTPBasic.Parameters(username="anystring", password=mailchimp_api_key)
        )

    return api
