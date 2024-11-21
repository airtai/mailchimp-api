from pathlib import Path
from typing import Any

import pandas as pd
from fastagency.adapters.fastapi import FastAPIAdapter
from fastapi import FastAPI, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import HTMLResponse

from ..constants import UPLOADED_FILES_DIR
from ..workflow import wf

adapter = FastAPIAdapter(provider=wf)

app = FastAPI()
app.include_router(adapter.router)


# this is optional, but we would like to see the list of available workflows
@app.get("/")
def list_workflows() -> dict[str, Any]:
    return {"Workflows": {name: wf.get_description(name) for name in wf.names}}


def _save_file(file: UploadFile, timestamp: str) -> Path:
    UPLOADED_FILES_DIR.mkdir(exist_ok=True)
    try:
        contents = file.file.read()
        file_name = f"uploaded-file-{timestamp}.csv"
        path = UPLOADED_FILES_DIR / file_name
        with path.open("wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        ) from e
    finally:
        file.file.close()

    return path


@app.post("/upload")
def upload(
    account_name: str = Form(...),
    file: UploadFile = UploadFile(...),  # type: ignore[arg-type] # noqa: B008
    timestamp: str = Form(...),
) -> dict[str, str]:
    if not account_name or file.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide both account name and .csv file",
        )

    path = _save_file(file, timestamp)
    df = pd.read_csv(path)
    if "email" not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'email' column not found in CSV file",
        )

    return {"message": f"Successfully uploaded {file.filename}"}


@app.get("/upload-file")
def upload_file(timestamp: str = Query(default="default-timestamp")) -> HTMLResponse:
    content = f"""<body>
    <form action='/upload' enctype='multipart/form-data' method='post'>
        <div>
            <input name='account_name' type='text' placeholder='Enter account name'>
        </div>
        <div style="margin-top: 15px;">
            <input name='file' type='file'>
        </div>
        <!-- Hidden field for timestamp -->
        <input name='timestamp' type='hidden' value='{timestamp}'>
        <div style="margin-top: 15px;">
            <input type='submit'>
        </div>
    </form>
</body>
"""
    return HTMLResponse(content=content)


# start the adapter with the following command
# uvicorn mailchimp_api.deployment.main_1_fastapi:app -b 0.0.0.0:8008 --reload
