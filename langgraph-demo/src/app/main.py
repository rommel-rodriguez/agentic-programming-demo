import logging
from pathlib import Path

from app.config import settings  # type:ignore
from app.entrypoints.webapp.app import fapi_app

app = fapi_app

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}

logger = logging.getLogger(__name__)

logger.info("Application Started")
