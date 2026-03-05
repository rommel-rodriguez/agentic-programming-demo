from uuid import UUID

import pytest

from app.domain.models import Document, DocumentPurpose, DocumentStatus
from app.ports.attachments import AttachmentMetadataPort
from app.ports.media_storage import MediaStoragePort
from app.services.commands import UploadAttachmentContentCommand
from app.services.invoices import UploadAttachmentContent


class FakeStorage(MediaStoragePort):
    def __init__(self, objects: dict[str, dict] | None = None):
        self.objects: dict[str, dict] = objects or {}
        self.save_calls: list[tuple[UUID | str, bytes, str, str | None, str]] = []

    async def save(
        self,
        *,
        key: UUID | str,
        content: bytes,
        content_type: str,
        original_filename: str | None = None
    ) -> str:
        # TODO: Figure out how to derive the storage_ref properly
        storage_key = str(key)
        doc = {
            key: key,
            content: content,
            content_type: content_type,
            original_filename: original_filename,
            storage_key: storage_key,
        }
        self.objects[storage_key] = doc
        self.save_calls.append(
            (key, content, content_type, original_filename, storage_key)
        )
        return storage_key


class FakeAttachment(AttachmentMetadataPort):
    # documents: dict[str, Document]

    def __init__(self, documents: dict[UUID, Document] | None = None):
        self.documents: dict[UUID, Document] = documents or dict()
        self.mark_uploaded_calls: list[tuple[UUID, str, str, int]] = []

    async def mark_uploaded(
        self,
        attachment_id: UUID,
        storage_key: str,
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
            storage_key=storage_key, checksum_sha256=checksum_sha256
        )
        self.documents[attachment_id] = updated
        self.mark_uploaded_calls.append(
            (attachment_id, storage_key, content_type, size_bytes)
        )

    async def exists_pending(self, attachment_id: UUID) -> bool:
        doc = self.documents.get(attachment_id)
        return bool(doc and doc.status == DocumentStatus.PENDING_UPLOAD)


@pytest.mark.asyncio
async def test_upload_attachment_content_rejects_non_valid_filetypes():
    documents = dict()
    storage_objects: dict[str, dict] = {}
    doc1 = Document(
        user_id=1,
        filename="invoice_1",
        content_type="application/invalid-mimetype",
        purpose=DocumentPurpose.CONTEXT,
        size_bytes=1024,
    )
    # doc2 = Document(
    #     user_id=1,
    #     filename="invoice_1",
    #     content_type="application/nightmare",
    #     purpose=DocumentPurpose.CONTEXT,
    #     size_bytes=1024,
    # )
    documents[doc1.id] = doc1
    command1 = UploadAttachmentContentCommand(
        attachment_id=doc1.id,
        content_type=doc1.content_type,
        content="content1".encode("utf-8"),
    )
    upat_uc = UploadAttachmentContent(
        storage=FakeStorage(objects=storage_objects),
        attachments=FakeAttachment(documents=documents),
    )
    with pytest.raises(ValueError):
        await upat_uc(command1)


@pytest.mark.asyncio
async def test_upload_attachment_content_accepts_valid_mimetypes():
    documents = dict()
    storage_objects: dict[str, dict] = {}
    fake_content: bytes = "content1".encode("utf-8")
    doc = Document(
        user_id=1,
        filename="invoice_1",
        content_type="application/pdf",
        purpose=DocumentPurpose.CONTEXT,
        size_bytes=len(fake_content),
    )
    documents[doc.id] = doc
    storage = FakeStorage(objects=storage_objects)
    attachments = FakeAttachment(documents=documents)
    command1 = UploadAttachmentContentCommand(
        attachment_id=doc.id,
        content_type=doc.content_type,
        content=fake_content,
    )
    upat_uc = UploadAttachmentContent(
        storage=storage,
        attachments=attachments,
    )
    await upat_uc(command1)
    assert len(storage.save_calls) == 1
    assert len(attachments.mark_uploaded_calls) == 1


@pytest.mark.asyncio
async def test_upload_attachment_content_rejects_non_pending_documents():
    documents = dict()
    storage_objects: dict[str, dict] = {}
    doc = Document(
        user_id=1,
        filename="invoice_1",
        content_type="application/pdf",
        purpose=DocumentPurpose.CONTEXT,
        size_bytes=1024,
    )
    updated_doc = doc.mark_uploaded(
        storage_key="fake storage key", checksum_sha256="fake checksum"
    )

    assert updated_doc.status == DocumentStatus.UPLOADED
    documents[updated_doc.id] = updated_doc
    storage = FakeStorage(objects=storage_objects)
    attachments = FakeAttachment(documents=documents)
    command1 = UploadAttachmentContentCommand(
        attachment_id=doc.id,
        content_type=doc.content_type,
        content="content1".encode("utf-8"),
    )
    upat_uc = UploadAttachmentContent(
        storage=storage,
        attachments=attachments,
    )
    with pytest.raises(LookupError):
        await upat_uc(command1)
