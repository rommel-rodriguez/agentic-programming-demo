from typing import BinaryIO, Protocol


class MediaStoragePort(Protocol):
    async def save(
        self,
        *,
        key: str,
        content: bytes,
        content_type: str,
        original_filename: str | None = None
    ) -> str:
        """Returns storage key/path."""
