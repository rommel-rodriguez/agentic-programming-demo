from typing import BinaryIO, Protocol


class MediaStoragePort(Protocol):
    async def save_pdf(self, attachment_id: str, content: bytes) -> str:
        """Returns storage key/path."""
