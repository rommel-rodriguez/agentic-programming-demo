from typing import Protocol
from uuid import UUID

from app.domain.models import DocumentPurpose


class AttachmentMetadataPort(Protocol):
    async def mark_uploaded(
        self,
        attachment_id: UUID,
        storage_key: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None: ...
    async def exists_pending(self, attachment_id: UUID) -> bool: ...

    async def register_pending(
        self,
        *,
        user_id: int,
        filename: str,
        content_type: str,
        size_bytes: int,
        purpose: DocumentPurpose,
    ) -> UUID: ...
