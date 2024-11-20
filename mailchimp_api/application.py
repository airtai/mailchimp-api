from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.post("/upload")
def upload(file: UploadFile) -> dict[str, str]:
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
