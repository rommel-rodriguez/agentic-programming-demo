from typing import Protocol
from uuid import UUID


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
