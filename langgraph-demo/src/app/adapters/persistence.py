from uuid import UUID

import sqlalchemy
import sqlalchemy.exc

from app.domain.models import Document, DocumentPurpose
from app.ports.attachments import AttachmentMetadataPort


class SQLAlchemyAttachmentMetadata(AttachmentMetadataPort):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def mark_uploaded(
        self,
        attachment_id: UUID,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None:
        self.session = self.session_factory()
        # Function Logic Here
        self.session.close()
        raise NotImplementedError

    async def exists_pending(self, attachment_id: UUID) -> bool:
        self.session = self.session_factory()
        # Function Logic Here
        self.session.close()
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
        self.session = self.session_factory()
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
            return document.id
        except sqlalchemy.exc.SQLAlchemyError as sqle:
            raise ValueError() from sqle  # TODO: Replace for persistence layer level error
        finally:
            self.session.close()
