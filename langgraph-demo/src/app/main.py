import logging
from pathlib import Path

from app.config import configure_logging, settings  # type:ignore

# from app.entrypoints.webapp.app import fapi_app

# NOTE: Is it correct to configure logging here? Or just at the entrypoints where
# it was suggested before?
configure_logging()

# app = fapi_app

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}

logger = logging.getLogger(__name__)

logger.info("Application Started")
