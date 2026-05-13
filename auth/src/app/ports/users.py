from typing import Protocol

from app.domain.models import UserAccount


class UserRepositoryPort(Protocol):
    async def add(self, user: UserAccount) -> None:
        ...

    async def get_by_id(self, user_id: str) -> UserAccount | None:
        ...

    async def get_by_username_normalized(
        self, username_normalized: str
    ) -> UserAccount | None:
        ...
