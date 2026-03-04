import pytest

from app.domain.models import Document, DocumentStatus
from app.ports.attachments import AttachmentMetadataPort
from app.ports.media_storage import MediaStoragePort
from app.services.invoices import UploadAttachmentContent


class FakeStorage(MediaStoragePort):
    documents: dict[str, dict]

    def __init__(self, documents=None):
        self.documents = documents or {}

    async def save(
        self,
        *,
        key: str,
        content: bytes,
        content_type: str,
        original_filename: str | None = None
    ) -> str:
        self.documents[key] = {
            content: content,
            content_type: content_type,
            original_filename: original_filename,
        }
        storage_ref = key
        return storage_ref


class FakeAttachment(AttachmentMetadataPort):
    # documents: dict[str, Document]

    def __init__(self, documents: dict[str, Document] | None = None):
        self.documents: dict[str, Document] = documents or {}
        self.mark_uploaded_calls: list[tuple[str, str, str, int]] = []

    async def mark_uploaded(
        self,
        attachment_id: str,
        storage_ref: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None:
        # TODO: Find out the proper way to generate that hash
        doc = self.documents.get(attachment_id)
        if doc is None:
            raise LookupError("Attachment not found")

        if doc.content_type != content_type:
            raise ValueError("content_type mismatch")

        if doc.size_bytes != size_bytes:
            raise ValueError("size mismatch")

        updated = doc.mark_uploaded(
            storage_key=attachment_id, checksum_sha256=checksum_sha256
        )
        self.documents[attachment_id] = updated
        self.mark_uploaded_calls.append(
            (attachment_id, storage_ref, content_type, size_bytes)
        )

    async def exists_pending(self, attachment_id: str) -> bool:
        doc = self.documents.get(attachment_id)
        return bool(doc and doc.status == DocumentStatus.PENDING_UPLOAD)


def test_upload_attachment_content_rejects_non_valid_filetypes():
    upat_uc = UploadAttachmentContent(
        storage=FakeStorage(), attachments=FakeAttachment()
    )
