import logging
from pathlib import Path

import anyio
from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app import bootstrap, config

config.configure_logging()

fapi_app = FastAPI()

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}

logger = logging.getLogger(__name__)


@fapi_app.get("/test-string")
def test_endpoint():
    logger.info("test-string endpoint aufwiedersehen")
    return "Hallo FastAPI world!"


@fapi_app.get("/test-dict")
def test_dictionary():
    logger.error("test-dict endpoint triggered")
    return d1


@fapi_app.get("/test-debug")
def test_debug():
    logger.debug("Is this printed while in INFO logger level?")
    return d1


@fapi_app.get("/test-warning")
def test_warning():
    logger.warning("Is this Warning logged at INFO level logger?")
    return d1


@fapi_app.get("/test-exception")
def test_exception():
    def divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            logger.exception("Hey Ho!")
        except TypeError:
            logger.exception("hey TE!")
        else:
            return result

    result = divide(1, 0)
    return result
