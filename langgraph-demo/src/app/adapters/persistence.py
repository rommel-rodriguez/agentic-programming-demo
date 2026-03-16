import datetime
import logging
from typing import cast
from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Document, DocumentPurpose, DocumentStatus
from app.ports.attachments import AttachmentMetadataPort
from app.ports.errors import AttachmentRepositoryError

logger = logging.getLogger(__name__)


class SQLAlchemyAttachmentMetadata(AttachmentMetadataPort):
    def __init__(self, session):
        self.session: AsyncSession = session

    async def mark_uploaded(
        self,
        attachment_id: UUID,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None:
        # Function Logic Here
        # TODO: Implement the failure-mode (retry logic) in case the document was
        # successfully uploaded to the media storage backend, but just failed to be
        # marked as uploaded.
        try:
            stmt = (
                select(Document)
                .where(cast("ColumnElement[bool]", Document.id == attachment_id))
                .with_for_update()
            )

            doc = (await self.session.execute(stmt)).scalar_one_or_none()
            if doc is None:
                raise AttachmentRepositoryError(f"document not found: {attachment_id}")
            if doc.status != DocumentStatus.PENDING_UPLOAD:
                raise AttachmentRepositoryError("not pending")
            if doc.content_type != content_type:
                raise AttachmentRepositoryError("content_type mismatch")
            if doc.size_bytes != size_bytes:
                raise AttachmentRepositoryError("size mismatch")

            doc.mark_uploaded(
                storage_key=storage_key,
                checksum_sha256=checksum_sha256,
                uploaded_at=datetime.datetime.now(datetime.UTC),
            )

            await self.session.flush()
        except IntegrityError as e:
            raise AttachmentRepositoryError(
                f"failed marking the document: {attachment_id}, as uploaded"
            ) from e  # TODO: Replace for persistence layer level error
        except SQLAlchemyError as e:
            raise AttachmentRepositoryError(
                "failed marking the document as uploaded"
            ) from e  # TODO: Replace for persistence layer level error
        except ValueError as e:
            raise AttachmentRepositoryError(
                f"invalid state transition for: {attachment_id}"
            ) from e

    async def exists_pending(self, attachment_id: UUID) -> bool:
        # Function Logic Here
        try:
            doc = await self.session.get(Document, attachment_id)
        except SQLAlchemyError as e:
            logger.error(
                f"failed checking whether pending document with id: {attachment_id}, exists"
            )
            raise AttachmentRepositoryError(
                f"failed checking whether pending document with id: {attachment_id}, exists"
            ) from e  # TODO: Replace for persistence layer level error

        return bool(doc and doc.status == DocumentStatus.PENDING_UPLOAD)

    async def register_pending(
        self,
        *,
        user_id: int,
        original_filename: str | None,
        content_type: str,
        size_bytes: int,
        purpose: DocumentPurpose,
    ) -> UUID:
        # Function Logic Here
        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            purpose=purpose,
        )
        try:
            self.session.add(document)
            await self.session.flush()
            return document.id
        except IntegrityError as e:
            raise AttachmentRepositoryError(
                "failed to register attachment: integrity error"
            ) from e  # TODO: Replace for persistence layer level error
        except SQLAlchemyError as e:
            raise AttachmentRepositoryError(
                "failed to register attachment"
            ) from e  # TODO: Replace for persistence layer level error
