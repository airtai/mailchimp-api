import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse

from .config import Config
from .processing.update_tags import update_tags

app = FastAPI()


def _get_config() -> Config:
    api_key = os.getenv("MAILCHIMP_API_KEY")
    if not api_key:
        raise ValueError("MAILCHIMP_API_KEY not set")

    config = Config("us14", api_key)
    return config


config = _get_config()


def get_df(file: UploadFile) -> pd.DataFrame:
    try:
        contents = file.file.read()
        filename = file.filename if file.filename else "uploaded_file"
        path = Path(filename)
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
def upload(file: UploadFile) -> dict[str, str]:
    df = get_df(file)

    update_tags(crm_df=df, config=config, list_name="airt")

    return {"message": f"Successfully uploaded {file.filename}"}


# Access the form at 'http://127.0.0.1:8002/' from your browser
@app.get("/")
def main() -> HTMLResponse:
    content = """<body>
    <form action='/upload' enctype='multipart/form-data' method='post'>
        <input name='file' type='file'>
        <input type='submit'>
    </form>
</body>
"""
    return HTMLResponse(content=content)
