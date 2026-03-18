from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator, Mapping, Protocol
from uuid import UUID

StorageKey = str


@dataclass(frozen=True, slots=True)
class StoredObject:
    key: StorageKey
    size_bytes: int
    content_type: str
    checksum_sha256: str | None = None
    etag: str | None = None
    version_id: str | None = None
    last_modified: datetime | None = None
    metadata: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class WriteResult:
    key: StorageKey
    size_bytes: int
    checksum_sha256: str | None = None
    etag: str | None = None
    version_id: str | None = None


class MediaStoragePort(Protocol):
    async def save(
        self,
        *,
        storage_key: str,
        content: bytes | AsyncIterator[bytes],
        content_type: str,
        original_filename: str | None = None,
        metadata: Mapping[str, str] | None = None,
        checksum_sha256: str | None = None,
        if_absent: bool = False,
    ) -> str:
        """Returns storage key/path."""
        ...

    # async def delete(self, *, key: str) -> None:
    #     """Best-effort delete for compensation path."""
    #     ...
    async def get_bytes(self, *, key: str) -> bytes:
        """Read full object content."""
        ...

    async def open_read(
        self,
        *,
        key: str,
        chunk_size: int = 1024 * 1024,
    ) -> AsyncIterator[bytes]:
        """Stream object content."""
        ...

    async def stat(self, *, key: str) -> StoredObject:
        """Return metadata; raise if object does not exist."""
        ...

    async def exists(self, *, key: str) -> bool:
        """Fast existence check."""
        ...

    async def delete(self, *, key: str, missing_ok: bool = True) -> bool:
        """Delete object. Return True if deleted, False if already missing."""
        ...
