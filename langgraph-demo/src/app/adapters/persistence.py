from uuid import UUID

import sqlalchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.models import Document, DocumentPurpose
from app.ports.attachments import AttachmentMetadataPort
from app.ports.errors import AttachmentRepositoryError


class SQLAlchemyAttachmentMetadata(AttachmentMetadataPort):
    def __init__(self, session):
        self.session = session

    async def mark_uploaded(
        self,
        attachment_id: UUID,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None:
        # Function Logic Here
        raise NotImplementedError

    async def exists_pending(self, attachment_id: UUID) -> bool:
        # Function Logic Here
        raise NotImplementedError

    async def register_pending(
        self,
        *,
        user_id: int,
        original_filename: str | None,
        content_type: str,
        size_bytes: int,
        purpose: DocumentPurpose
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
