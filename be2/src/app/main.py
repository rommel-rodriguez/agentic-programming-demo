from pathlib import Path

import anyio
from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app import bootstrap

app = FastAPI()

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}


@app.get("/test-string")
def test_endpoint():
    return "Hallo FastAPI world!"


@app.get("/test-dict")
def test_serialization():
    return d1
