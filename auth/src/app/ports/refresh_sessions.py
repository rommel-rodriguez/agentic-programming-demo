from typing import Protocol

from app.domain.models import RefreshSession


class RefreshSessionRepositoryPort(Protocol):
    async def add(self, session: RefreshSession) -> None:
        ...

    async def get_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        ...

    async def revoke(self, session_id: str) -> None:
        ...
