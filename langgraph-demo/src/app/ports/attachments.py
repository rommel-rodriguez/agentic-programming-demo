from typing import Protocol


class AttachmentMetadataPort(Protocol):
    async def mark_uploaded(
        self,
        attachment_id: str,
        storage_ref: str,
        content_type: str,
        size_bytes: int,
        checksum_sha256: str,
    ) -> None: ...
    async def exists_pending(self, attachment_id: str) -> bool: ...
