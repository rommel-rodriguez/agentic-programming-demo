import abc

from app.ports.refresh_sessions import RefreshSessionRepositoryPort
from app.ports.users import UserRepositoryPort


class UnitOfWork(abc.ABC):
    users: UserRepositoryPort
    refresh_sessions: RefreshSessionRepositoryPort

    def __init__(self):
        self._committed = False

    async def __aenter__(self) -> "UnitOfWork":
        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None or not self._committed:
            await self.rollback()

    async def commit(self) -> None:
        await self._commit()
        self._committed = True

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _commit(self) -> None:
        raise NotImplementedError
