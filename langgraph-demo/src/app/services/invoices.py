import hashlib
import logging
from uuid import UUID

from app.domain.models import DocumentPurpose
from app.ports.attachments import AttachmentMetadataPort
from app.ports.errors import MediaStorageError
from app.ports.media_storage import MediaStoragePort
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
    def __init__(self, *, attachments: AttachmentMetadataPort):
        self._attachments = attachments

    async def __call__(self, cmd: RegisterAttachmentCommand) -> UUID:
        if cmd.content_type not in VALID_MIMETYPES:
            raise UnsupportedMimeTypeError(
                f"Must have a valid MIME type, got {cmd.content_type}"
            )

        if cmd.size_bytes > MAX_FILE_SIZE:
            raise AttachmentSizeBytesTooBig(
                f"The file must be under {MAX_FILE_SIZE} bytes"
            )

        attachment_id = await self._attachments.register_pending(
            user_id=cmd.user_id,
            filename=cmd.original_filename,
            content_type=cmd.content_type,
            size_bytes=cmd.size_bytes,
            purpose=cmd.purpose,
        )
        return attachment_id


class UploadAttachmentContent:
    def __init__(
        self, *, storage: MediaStoragePort, attachments: AttachmentMetadataPort
    ) -> None:
        self._storage = storage
        self._attachments = attachments

    async def __call__(self, cmd: UploadAttachmentContentCommand) -> None:
        checksum = compute_document_sha256_hash(cmd.content)
        if cmd.content_type not in VALID_MIMETYPES:
            raise UnsupportedMimeTypeError(
                f"Must have a valid MIME type, got {cmd.content_type}"
            )

        exists = await self._attachments.exists_pending(cmd.attachment_id)
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

        await self._attachments.mark_uploaded(
            attachment_id=cmd.attachment_id,
            storage_key=storage_key,
            content_type=cmd.content_type,
            size_bytes=len(cmd.content),
            checksum_sha256=checksum,
        )
