from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.persistence import SQLAlchemyAttachmentMetadata
from app.ports.uow import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> UnitOfWork:
        await super().__aenter__()  # sets _committed=False
        self.session = self._session_factory()
        # await self.session.__aenter__()
        self.attachments = SQLAlchemyAttachmentMetadata(self.session)
        # self.applications = SQLAlchemyApplicationRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            await super().__aexit__(exc_type, exc, tb)
        finally:
            if self.session is not None:
                await self.session.close()

    async def rollback(self) -> None:
        if self.session is not None:
            await self.session.rollback()

    async def _commit(self):
        if self.session is None:
            raise RuntimeError("UoW session not initialized; call inside 'async with'")
        await self.session.commit()
