from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.orm import RefreshSessionModel, UserAccountModel
from app.domain.models import RefreshSession, UserAccount
from app.ports.refresh_sessions import RefreshSessionRepositoryPort
from app.ports.users import UserRepositoryPort


def _to_user(model: UserAccountModel) -> UserAccount:
    return UserAccount(
        id_=model.id,
        username=model.username,
        username_normalized=model.username_normalized,
        password_hash=model.password_hash,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _to_refresh_session(model: RefreshSessionModel) -> RefreshSession:
    return RefreshSession(
        id_=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        created_at=model.created_at,
        revoked_at=model.revoked_at,
    )


class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, user: UserAccount) -> None:
        self._session.add(
            UserAccountModel(
                id=user.id_,
                username=user.username,
                username_normalized=user.username_normalized,
                password_hash=user.password_hash,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )
        await self._session.flush()

    async def get_by_id(self, user_id: str) -> UserAccount | None:
        model = await self._session.get(UserAccountModel, user_id)
        if model is None:
            return None
        return _to_user(model)

    async def get_by_username_normalized(
        self, username_normalized: str
    ) -> UserAccount | None:
        stmt = select(UserAccountModel).where(
            UserAccountModel.username_normalized == username_normalized
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            return None
        return _to_user(model)


class SQLAlchemyRefreshSessionRepository(RefreshSessionRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, session: RefreshSession) -> None:
        self._session.add(
            RefreshSessionModel(
                id=session.id_,
                user_id=session.user_id,
                token_hash=session.token_hash,
                expires_at=session.expires_at,
                created_at=session.created_at,
                revoked_at=session.revoked_at,
            )
        )
        await self._session.flush()

    async def get_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        stmt = select(RefreshSessionModel).where(
            RefreshSessionModel.token_hash == token_hash
        )
        model = (await self._session.execute(stmt)).scalar_one_or_none()
        if model is None:
            return None
        return _to_refresh_session(model)

    async def revoke(self, session_id: str) -> None:
        model = await self._session.get(RefreshSessionModel, session_id)
        if model is None:
            return
        if model.revoked_at is not None:
            return
        from datetime import UTC, datetime

        model.revoked_at = datetime.now(UTC)
        await self._session.flush()
