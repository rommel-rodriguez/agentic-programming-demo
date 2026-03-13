import hashlib
import logging
from uuid import UUID

from app.domain.models import DocumentPurpose
from app.ports.attachments import AttachmentMetadataPort
from app.ports.errors import MediaStorageError
from app.ports.media_storage import MediaStoragePort
from app.ports.uow import UnitOfWork
from app.services.commands import (
    RegisterAttachmentCommand,
    UploadAttachmentContentCommand,
)
from app.services.errors import (
    AttachmentNotPendingError,
    AttachmentSizeBytesTooBig,
    StorageUnavailableError,
    UnsupportedMimeTypeError,
)

# NOTE: Should this come from a database table?
VALID_MIMETYPES = {"application/pdf"}
MAX_FILE_SIZE = 20971520  # NOTE: 20MiB

logger = logging.getLogger(__name__)


async def parse_invoice():
    pass


def compute_document_sha256_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


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
    def __init__(self, *, storage: MediaStoragePort, uow: UnitOfWork) -> None:
        self._storage = storage
        self._uow = uow

    async def __call__(self, cmd: UploadAttachmentContentCommand) -> None:
        checksum = compute_document_sha256_hash(cmd.content)
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
                storage_key = await self._storage.save(
                    key=cmd.attachment_id,
                    content=cmd.content,
                    content_type=cmd.content_type,
                    original_filename=cmd.original_filename,
                )
            except MediaStorageError as e:
                logger.error(f"Storage to media backend failed with error: {e}")
                raise StorageUnavailableError() from e

            await self._uow.attachments.mark_uploaded(
                attachment_id=cmd.attachment_id,
                storage_key=storage_key,
                content_type=cmd.content_type,
                size_bytes=len(cmd.content),
                checksum_sha256=checksum,
            )
            await self._uow.commit()
