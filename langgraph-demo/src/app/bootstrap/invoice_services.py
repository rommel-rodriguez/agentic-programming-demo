import logging
from email.mime import base
from pathlib import Path
from typing import Any

from app.adapters.media_storage.local_dev_media_storage import LocalDevMediaStorage
from app.adapters.media_storage.posix_file_media_storage import PosixFileMediaStorage
from app.adapters.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.config import get_settings
from app.ports.media_storage import MediaStoragePort
from app.ports.uow import UnitOfWork
from app.services.invoices import UploadAttachmentContent
from app.services.storage_key_builder import StorageKeyBuilder

logger = logging.getLogger(__name__)


def _build_default_file_media_storage(root: Path | None = None) -> MediaStoragePort:
    base_dir = root or Path("./.data/media")
    env = get_settings().env
    if env == "prod":
        return PosixFileMediaStorage(base_dir=base_dir)
    return LocalDevMediaStorage(base_dir=base_dir)


def _build_default_uow(session_factory) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory)


def build_upload_attachment_use_case(
    *,
    uow: UnitOfWork | None = None,
    session_factory: Any | None,
    storage: MediaStoragePort | None = None,
    key_builder: StorageKeyBuilder | None = None,
) -> UploadAttachmentContent:
    key_builder = key_builder or StorageKeyBuilder(get_settings().env)
    storage = storage or _build_default_file_media_storage()
    if uow is None and session_factory is None:
        logger.error(
            f"Can not build Register Attachment use case, session_factory: {session_factory}, uow: {uow}"
        )
        raise ValueError("uow error: you must provide either session_factory or UoW")
    uow = uow or _build_default_uow(session_factory)
    return UploadAttachmentContent(storage=storage, uow=uow, key_builder=key_builder)
