import os
from typing import Any

import pandas as pd
from fastagency.adapters.fastapi import FastAPIAdapter
from fastapi import FastAPI, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import HTMLResponse

from ..config import Config
from ..constants import UPLOADED_FILES_DIR
from ..processing.update_tags import update_tags
from ..workflow import wf

adapter = FastAPIAdapter(provider=wf)

app = FastAPI()
app.include_router(adapter.router)


# this is optional, but we would like to see the list of available workflows
@app.get("/")
def list_workflows() -> dict[str, Any]:
    return {"Workflows": {name: wf.get_description(name) for name in wf.names}}


def _get_config() -> Config:
    api_key = os.getenv("MAILCHIMP_API_KEY")
    if not api_key:
        raise ValueError("MAILCHIMP_API_KEY not set")

    config = Config("us14", api_key)
    return config


config = _get_config()


def get_df(file: UploadFile) -> pd.DataFrame:
    UPLOADED_FILES_DIR.mkdir(exist_ok=True)
    try:
        contents = file.file.read()
        filename = file.filename if file.filename else "uploaded_file"
        path = UPLOADED_FILES_DIR / filename
        with path.open("wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        ) from e
    finally:
        file.file.close()

    if path.suffix != ".csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    df = pd.read_csv(path)
    if "email" not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'email' column not found in CSV file",
        )

    return df


@app.post("/upload")
def upload(
    account_name: str = Form(...),
    file: UploadFile = UploadFile(...),  # type: ignore[arg-type] # noqa: B008
    timestamp: str = Form(...),
) -> dict[str, str]:
    if not account_name or file.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide both account name and file",
        )

    df = get_df(file)

    try:
        update_tags(crm_df=df, config=config, list_name=account_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e

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
