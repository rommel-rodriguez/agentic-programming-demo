import logging
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
    logging.info("test-string endpoint triggered")
    return "Hallo FastAPI world!"


@app.get("/test-dict")
def test_dictionary():
    logging.error("test-dict endpoint triggered")
    return d1


@app.get("/test-debug")
def test_debug():
    logging.debug("Is this printed while in INFO logging level?")
    return d1


@app.get("/test-warning")
def test_warning():
    logging.warning("Is this Warning logged at INFO level logging?")
    return d1


@app.get("/test-exception")
def test_exception():
    def divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            logging.exception("Hey Ho!")
        except TypeError:
            logging.exception("hey TE!")
        else:
            return result

    result = divide(1, 0)
    return result
