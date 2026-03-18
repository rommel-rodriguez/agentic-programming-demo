import logging
from typing import Any

from app.adapters.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.config import get_settings
from app.ports.media_storage import MediaStoragePort
from app.ports.uow import UnitOfWork
from app.services.invoices import UploadAttachmentContent
from app.services.storage_key_builder import StorageKeyBuilder

logger = logging.getLogger(__name__)


def _build_default_uow(session_factory) -> UnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory)


def build_upload_attachment_use_case(
    *,
    session_factory: Any | None,
    storage: MediaStoragePort,
    uow: UnitOfWork,
    key_builder,
) -> UploadAttachmentContent:
    key_builder = key_builder or StorageKeyBuilder(get_settings().env)
    if uow is None and session_factory is None:
        logger.error(
            f"Can not build Register Attachment use case, session_factory: {session_factory}, uow: {uow}"
        )
        raise ValueError("uow error: you must provide either session_factory or UoW")
    uow = uow or _build_default_uow(session_factory)
    return UploadAttachmentContent(storage=storage, uow=uow, key_builder=key_builder)
