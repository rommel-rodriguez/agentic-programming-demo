from typing import Protocol


class AttachmentMetadataPort(Protocol):
    async def mark_uploaded(
        self, attachment_id: str, storage_ref: str, content_type: str, size_bytes: int
    ) -> None: ...
    async def exists_pending(self, attachment_id: str) -> bool: ...
