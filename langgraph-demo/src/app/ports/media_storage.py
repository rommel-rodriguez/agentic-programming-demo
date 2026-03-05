from typing import BinaryIO, Protocol
from uuid import UUID


class MediaStoragePort(Protocol):
    async def save(
        self,
        *,
        key: UUID | str,
        content: bytes,
        content_type: str,
        original_filename: str | None = None
    ) -> str:
        """Returns storage key/path."""
        ...
