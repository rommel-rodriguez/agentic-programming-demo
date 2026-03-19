from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path, PurePosixPath
from typing import AsyncIterator, Mapping

from app.ports.errors import MediaStorageError
from app.ports.media_storage import MediaStoragePort, StoredObject

logger = logging.getLogger(__name__)


class LocalDevMediaStorage(MediaStoragePort):
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _resolve(self, key: str) -> Path:
        pure = PurePosixPath(key.strip().lstrip("/"))
        if pure.is_absolute() or ".." in pure.parts or not pure.parts:
            raise MediaStorageError(f"invalid storage key: {key}")
        return self.base_dir.joinpath(*pure.parts)

    def _meta_path(self, obj_path: Path) -> Path:
        return obj_path.with_suffix(obj_path.suffix + ".meta.json")

    async def _to_bytes(self, content: bytes | AsyncIterator[bytes]) -> bytes:
        if isinstance(content, bytes):
            return content
        chunks: list[bytes] = []
        async for chunk in content:
            chunks.append(chunk)
        return b"".join(chunks)

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
        try:
            path = self._resolve(storage_key)
            data = await self._to_bytes(content)

            await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
            if if_absent and await asyncio.to_thread(path.exists):
                raise MediaStorageError(f"object already exists: {storage_key}")

            await asyncio.to_thread(path.write_bytes, data)
            meta = {
                "content_type": content_type,
                "original_filename": original_filename,
                "checksum_sha256": checksum_sha256,
                "metadata": dict(metadata or {}),
            }
            await asyncio.to_thread(
                self._meta_path(path).write_text, json.dumps(meta), "utf-8"
            )
            return storage_key
        except MediaStorageError:
            raise
        except Exception as e:
            logger.exception(
                "local media save failed",
                extra={
                    "storage_key": storage_key,
                    "resolved_path": str(path),
                    "base_dir": str(self.base_dir),
                },
            )
            raise MediaStorageError(f"save failed for key={storage_key}") from e

    async def get_bytes(self, *, key: str) -> bytes:
        path = self._resolve(key)
        try:
            return await asyncio.to_thread(path.read_bytes)
        except Exception as e:
            raise MediaStorageError(f"read failed for key={key}") from e

    async def open_read(
        self, *, key: str, chunk_size: int = 1024 * 1024
    ) -> AsyncIterator[bytes]:
        path = self._resolve(key)
        f = await asyncio.to_thread(open, path, "rb")
        try:
            while True:
                chunk = await asyncio.to_thread(f.read, chunk_size)
                if not chunk:
                    break
                yield chunk
        except Exception as e:
            raise MediaStorageError(f"stream failed for key={key}") from e
        finally:
            await asyncio.to_thread(f.close)

    async def stat(self, *, key: str) -> StoredObject:
        path = self._resolve(key)
        try:
            st = await asyncio.to_thread(path.stat)
            meta_path = self._meta_path(path)
            meta = {}
            if await asyncio.to_thread(meta_path.exists):
                meta = json.loads(await asyncio.to_thread(meta_path.read_text, "utf-8"))
            return StoredObject(
                key=key,
                size_bytes=st.st_size,
                content_type=meta.get("content_type", "application/octet-stream"),
                checksum_sha256=meta.get("checksum_sha256"),
                metadata=meta.get("metadata"),
            )
        except Exception as e:
            raise MediaStorageError(f"stat failed for key={key}") from e

    async def exists(self, *, key: str) -> bool:
        path = self._resolve(key)
        return await asyncio.to_thread(path.exists)

    async def delete(self, *, key: str, missing_ok: bool = True) -> bool:
        path = self._resolve(key)
        meta = self._meta_path(path)
        exists = await asyncio.to_thread(path.exists)
        if not exists:
            if missing_ok:
                return False
            raise MediaStorageError(f"missing object for key={key}")
        try:
            await asyncio.to_thread(path.unlink)
            if await asyncio.to_thread(meta.exists):
                await asyncio.to_thread(meta.unlink)
            return True
        except Exception as e:
            raise MediaStorageError(f"delete failed for key={key}") from e
