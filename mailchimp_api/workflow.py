import os
import time
from typing import Any

from fastagency import UI
from fastagency.runtimes.autogen import AutoGenWorkflows

from .constants import UPLOADED_FILES_DIR

wf = AutoGenWorkflows()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8008")


@wf.register(name="simple_learning", description="Student and teacher learning chat")  # type: ignore[misc]
def simple_workflow(ui: UI, params: dict[str, Any]) -> str:
    body = f"""Please upload **.csv** file with the email addresses for which you want to update the tags.

<a href="{FASTAPI_URL}/upload-file" target="_blank">Upload File</a>
"""
    ui.text_message(
        sender="Workflow",
        recipient="User",
        body=body,
    )

    file_name = "import_audience.csv"
    file_path = UPLOADED_FILES_DIR / file_name
    while not file_path.exists():
        time.sleep(2)

    file_path.unlink()

    return "Done"
