from pathlib import Path

import anyio
from fastapi import FastAPI, File, HTTPException, UploadFile, status

app = FastAPI()

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}


def _ensure_upload_dir(subdir: str) -> Path:
    directory = UPLOAD_ROOT / subdir
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _validate_pdf(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pdf files are accepted",
        )

    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid PDF content type",
        )


async def _stream_to_disk(file: UploadFile, destination: Path, *, max_bytes: int | None = None) -> int:
    written = 0
    try:
        async with await anyio.open_file(destination, "wb") as buffer:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                written += len(chunk)
                if max_bytes is not None and written > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Uploaded file exceeds allowed size",
                    )
                await buffer.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return written


def _safe_filename(filename: str) -> str:
    return Path(filename).name


@app.post("/upload/pdf-streaming", status_code=status.HTTP_201_CREATED)
async def upload_pdf_streaming(file: UploadFile = File(...)) -> dict[str, str | int]:
    """Upload a PDF using chunked streaming to limit RAM usage."""

    _validate_pdf(file)
    target_dir = _ensure_upload_dir("pdf")
    saved_name = _safe_filename(file.filename)
    destination = target_dir / saved_name
    size = await _stream_to_disk(file, destination)

    return {"filename": saved_name, "bytes_saved": size}


@app.post("/upload/binary-streaming", status_code=status.HTTP_201_CREATED)
async def upload_binary_streaming(
    file: UploadFile = File(..., description="Any binary file"),
    max_bytes: int | None = None,
) -> dict[str, str | int]:
    """Upload an arbitrary binary file with chunked streaming and optional size cap."""

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    target_dir = _ensure_upload_dir("binary")
    saved_name = _safe_filename(file.filename)
    destination = target_dir / saved_name
    size = await _stream_to_disk(file, destination, max_bytes=max_bytes)

    return {"filename": saved_name, "bytes_saved": size, "content_type": file.content_type}


@app.post("/upload/pdf-small", status_code=status.HTTP_201_CREATED)
async def upload_pdf_small(file: UploadFile = File(...)) -> dict[str, str | int]:
    """Upload a small PDF by reading it fully into memory."""

    _validate_pdf(file)
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    content = await file.read()
    target_dir = _ensure_upload_dir("pdf")
    saved_name = _safe_filename(file.filename)
    destination = target_dir / saved_name
    destination.write_bytes(content)

    return {"filename": saved_name, "bytes_saved": len(content)}


@app.get("/test-string")
def test_endpoint():
    return "Hallo FastAPI world!"


@app.get("/test-dict")
def test_serialization():
    return d1
