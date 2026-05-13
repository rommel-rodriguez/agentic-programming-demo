from datetime import UTC, datetime

import pytest_asyncio

from app.adapters.password_hasher import BcryptPasswordHasher
from app.adapters.refresh_tokens import OpaqueRefreshTokenGenerator
from app.adapters.rsa_keys import RSAKeyGenerator
from app.adapters.jwt_signer import RS256JWTSigner
from app.domain.models import KeySet, RefreshSession, UserAccount
from app.services.authentication import RefreshUserSession, SignInUser, SignOutUser, SignUpUser
from app.services.tokens import IssueAccessToken, IssueSessionTokens


class FakeUsersRepository:
    def __init__(self):
        self._users_by_id: dict[str, UserAccount] = {}
        self._users_by_username: dict[str, UserAccount] = {}

    async def add(self, user: UserAccount) -> None:
        self._users_by_id[user.id_] = user
        self._users_by_username[user.username_normalized] = user

    async def get_by_id(self, user_id: str) -> UserAccount | None:
        return self._users_by_id.get(user_id)

    async def get_by_username_normalized(
        self, username_normalized: str
    ) -> UserAccount | None:
        return self._users_by_username.get(username_normalized)


class FakeRefreshSessionsRepository:
    def __init__(self):
        self._sessions_by_id: dict[str, RefreshSession] = {}
        self._sessions_by_hash: dict[str, RefreshSession] = {}

    async def add(self, session: RefreshSession) -> None:
        self._sessions_by_id[session.id_] = session
        self._sessions_by_hash[session.token_hash] = session

    async def get_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        return self._sessions_by_hash.get(token_hash)

    async def revoke(self, session_id: str) -> None:
        session = self._sessions_by_id.get(session_id)
        if session is None or session.revoked_at is not None:
            return
        revoked = RefreshSession(
            id_=session.id_,
            user_id=session.user_id,
            token_hash=session.token_hash,
            expires_at=session.expires_at,
            created_at=session.created_at,
            revoked_at=datetime.now(UTC),
        )
        self._sessions_by_id[session_id] = revoked
        self._sessions_by_hash[session.token_hash] = revoked


class FakeUnitOfWork:
    def __init__(self, users: FakeUsersRepository, refresh_sessions: FakeRefreshSessionsRepository):
        self.users = users
        self.refresh_sessions = refresh_sessions
        self._committed = False

    async def __aenter__(self):
        self._committed = False
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self) -> None:
        self._committed = True


@pytest_asyncio.fixture
async def key_set():
    active_key = RSAKeyGenerator().generate(kid="main")
    return KeySet(active_key=active_key, public_keys=(active_key,))


@pytest_asyncio.fixture
async def auth_services():
    users = FakeUsersRepository()
    refresh_sessions = FakeRefreshSessionsRepository()

    def uow_factory():
        return FakeUnitOfWork(users, refresh_sessions)

    issue_access_token = IssueAccessToken(
        signer=RS256JWTSigner(),
        issuer="https://auth.example.com",
        default_audience="fapi-services",
        default_ttl_seconds=900,
        max_ttl_seconds=3600,
    )
    issue_session_tokens = IssueSessionTokens(
        access_token_issuer=issue_access_token,
        refresh_token_generator=OpaqueRefreshTokenGenerator(),
        refresh_token_ttl_seconds=86400,
        access_token_ttl_seconds=900,
    )
    return {
        "signup": SignUpUser(
            uow_factory=uow_factory,
            password_hasher=BcryptPasswordHasher(),
            session_token_issuer=issue_session_tokens,
        ),
        "signin": SignInUser(
            uow_factory=uow_factory,
            password_hasher=BcryptPasswordHasher(),
            session_token_issuer=issue_session_tokens,
        ),
        "refresh": RefreshUserSession(
            uow_factory=uow_factory,
            session_token_issuer=issue_session_tokens,
        ),
        "signout": SignOutUser(uow_factory=uow_factory),
    }
