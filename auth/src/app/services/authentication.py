from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.domain.errors import (
    InvalidCredentialsError,
    RefreshTokenInvalidError,
    UserAlreadyExistsError,
)
from app.domain.models import KeySet, SessionTokens, UserAccount
from app.ports.passwords import PasswordHasherPort
from app.ports.uow import UnitOfWork
from app.services.tokens import IssueSessionTokens, hash_refresh_token


def normalize_username(username: str) -> tuple[str, str]:
    cleaned = username.strip()
    return cleaned, cleaned.casefold()


class SignUpUser:
    def __init__(
        self,
        *,
        uow_factory,
        password_hasher: PasswordHasherPort,
        session_token_issuer: IssueSessionTokens,
    ):
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher
        self._session_token_issuer = session_token_issuer

    async def __call__(
        self,
        *,
        key_set: KeySet,
        username: str,
        password: str,
    ) -> SessionTokens:
        display_username, username_normalized = normalize_username(username)
        async with self._uow_factory() as uow:
            existing_user = await uow.users.get_by_username_normalized(
                username_normalized
            )
            if existing_user is not None:
                raise UserAlreadyExistsError("username already exists")

            now = datetime.now(UTC)
            user = UserAccount(
                id_=str(uuid4()),
                username=display_username,
                username_normalized=username_normalized,
                password_hash=self._password_hasher.hash(password),
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            await uow.users.add(user)
            tokens = await self._session_token_issuer(
                key_set=key_set,
                user=user,
                refresh_sessions=uow.refresh_sessions,
            )
            try:
                await uow.commit()
            except IntegrityError as exc:
                raise UserAlreadyExistsError("username already exists") from exc
            return tokens


class SignInUser:
    def __init__(
        self,
        *,
        uow_factory,
        password_hasher: PasswordHasherPort,
        session_token_issuer: IssueSessionTokens,
    ):
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher
        self._session_token_issuer = session_token_issuer

    async def __call__(
        self,
        *,
        key_set: KeySet,
        username: str,
        password: str,
    ) -> SessionTokens:
        _, username_normalized = normalize_username(username)
        async with self._uow_factory() as uow:
            user = await uow.users.get_by_username_normalized(username_normalized)
            if user is None or not user.is_active:
                raise InvalidCredentialsError("invalid username or password")
            if not self._password_hasher.verify(password, user.password_hash):
                raise InvalidCredentialsError("invalid username or password")

            tokens = await self._session_token_issuer(
                key_set=key_set,
                user=user,
                refresh_sessions=uow.refresh_sessions,
            )
            await uow.commit()
            return tokens


class RefreshUserSession:
    def __init__(
        self,
        *,
        uow_factory,
        session_token_issuer: IssueSessionTokens,
    ):
        self._uow_factory = uow_factory
        self._session_token_issuer = session_token_issuer

    async def __call__(self, *, key_set: KeySet, refresh_token: str) -> SessionTokens:
        token_hash = hash_refresh_token(refresh_token)
        now = datetime.now(UTC)
        async with self._uow_factory() as uow:
            session = await uow.refresh_sessions.get_by_token_hash(token_hash)
            if (
                session is None
                or session.revoked_at is not None
                or session.expires_at <= now
            ):
                raise RefreshTokenInvalidError("refresh token is invalid")

            user = await uow.users.get_by_id(session.user_id)
            if user is None or not user.is_active:
                raise RefreshTokenInvalidError("refresh token is invalid")

            await uow.refresh_sessions.revoke(session.id_)
            tokens = await self._session_token_issuer(
                key_set=key_set,
                user=user,
                refresh_sessions=uow.refresh_sessions,
            )
            await uow.commit()
            return tokens


class SignOutUser:
    def __init__(self, *, uow_factory):
        self._uow_factory = uow_factory

    async def __call__(self, *, refresh_token: str) -> None:
        token_hash = hash_refresh_token(refresh_token)
        async with self._uow_factory() as uow:
            session = await uow.refresh_sessions.get_by_token_hash(token_hash)
            if session is not None:
                await uow.refresh_sessions.revoke(session.id_)
            await uow.commit()
