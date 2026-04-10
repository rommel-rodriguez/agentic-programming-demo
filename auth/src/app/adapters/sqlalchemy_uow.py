from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.persistence import (
    SQLAlchemyRefreshSessionRepository,
    SQLAlchemyUserRepository,
)
from app.ports.uow import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        await super().__aenter__()
        self.session = self._session_factory()
        self.users = SQLAlchemyUserRepository(self.session)
        self.refresh_sessions = SQLAlchemyRefreshSessionRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await super().__aexit__(exc_type, exc, tb)
        finally:
            if self.session is not None:
                await self.session.close()

    async def _commit(self) -> None:
        if self.session is not None:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()
