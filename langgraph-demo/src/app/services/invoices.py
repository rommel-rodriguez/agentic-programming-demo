import hashlib
import logging
from datetime import UTC, datetime
from uuid import UUID

from app.ports.errors import MediaStorageError
from app.ports.media_storage import MediaStoragePort
from app.ports.uow import UnitOfWork
from app.services.commands import (
    RegisterAttachmentCommand,
    UploadAttachmentContentCommand,
)
from app.services.errors import (
    AttachmentMetadataUpdateError,
    AttachmentNotPendingError,
    AttachmentSizeBytesTooBig,
    StorageUnavailableError,
    UnsupportedMimeTypeError,
)
from app.services.storage_key_builder import StorageKeyBuilder

# NOTE: Should this come from a database table?
VALID_MIMETYPES = {"application/pdf"}
MAX_FILE_SIZE = 20971520  # NOTE: 20MiB

logger = logging.getLogger(__name__)


async def parse_invoice():
    pass


def compute_document_sha256_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def get_month_and_year() -> tuple[int, int]:
    now_utc = datetime.now(UTC)
    return (now_utc.month, now_utc.year)


class RegisterAttachment:
    def __init__(self, *, uow: UnitOfWork):
        self._uow = uow

    async def __call__(self, cmd: RegisterAttachmentCommand) -> UUID:
        if cmd.content_type not in VALID_MIMETYPES:
            raise UnsupportedMimeTypeError(
                f"Must have a valid MIME type, got {cmd.content_type}"
            )

        if cmd.size_bytes > MAX_FILE_SIZE:
            raise AttachmentSizeBytesTooBig(
                f"The file must be under {MAX_FILE_SIZE} bytes"
            )
        async with self._uow:
            attachment_id = await self._uow.attachments.register_pending(
                user_id=cmd.user_id,
                original_filename=cmd.original_filename,
                content_type=cmd.content_type,
                size_bytes=cmd.size_bytes,
                purpose=cmd.purpose,
            )
            await self._uow.commit()
        return attachment_id


class UploadAttachmentContent:
    def __init__(
        self,
        *,
        storage: MediaStoragePort,
        uow: UnitOfWork,
        key_builder: StorageKeyBuilder,
    ) -> None:
        self._storage = storage
        self._uow = uow
        self._key_builder = key_builder

    async def __call__(self, cmd: UploadAttachmentContentCommand) -> None:
        checksum = compute_document_sha256_hash(cmd.content)
        month, year = get_month_and_year()
        if cmd.content_type not in VALID_MIMETYPES:
            raise UnsupportedMimeTypeError(
                f"Must have a valid MIME type, got {cmd.content_type}"
            )
        async with self._uow:
            exists = await self._uow.attachments.exists_pending(cmd.attachment_id)
            if not exists:
                raise AttachmentNotPendingError(
                    "Attachment not found or is not pending upload"
                )

            try:
                storage_key = self._key_builder.attachment(
                    tenant_id=str(cmd.user_id),
                    attachment_id=cmd.attachment_id,
                    yyyy=year,
                    mm=month,
                )
                storage_key = await self._storage.save(
                    storage_key=storage_key,
                    content=cmd.content,
                    content_type=cmd.content_type,
                    original_filename=cmd.original_filename,
                )
            except MediaStorageError as e:
                logger.error(f"Storage to media backend failed with error: {e}")
                raise StorageUnavailableError() from e

            try:
                await self._uow.attachments.mark_uploaded(
                    attachment_id=cmd.attachment_id,
                    storage_key=storage_key,
                    content_type=cmd.content_type,
                    size_bytes=len(cmd.content),
                    checksum_sha256=checksum,
                )
                await self._uow.commit()
            except Exception as db_err:
                # compensation
                try:
                    await self._storage.delete(key=storage_key)
                except MediaStorageError as cleanup_err:
                    logger.exception("orphan cleanup failed for %s", storage_key)
                    # if self._cleanup is not None:
                    #     await self._cleanup.enqueue_delete(
                    #         storage_key=storage_key,
                    #         reason=str(cleanup_err),
                    #     )
                raise AttachmentMetadataUpdateError() from db_err
