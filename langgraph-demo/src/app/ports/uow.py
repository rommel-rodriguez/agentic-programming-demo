import abc

from app.ports.application import ApplicationPort
from app.ports.attachments import AttachmentMetadataPort


class UnitOfWork(abc.ABC):
    attachments: AttachmentMetadataPort
    applications: ApplicationPort

    def __init__(self):
        self._committed = False

    async def __aenter__(self) -> "UnitOfWork":
        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        # Rollback unless commit() was explicitly called and no exception occurred.
        if exc_type is not None or not self._committed:
            await self.rollback()

    async def commit(self) -> None:
        await self._commit()
        self._committed = True

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError
