import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.domain.errors import InvalidTokenRequestError
from app.domain.models import AccessTokenClaims, KeySet, RefreshSession, SessionTokens, UserAccount
from app.ports.refresh_sessions import RefreshSessionRepositoryPort
from app.ports.refresh_tokens import RefreshTokenGeneratorPort
from app.ports.tokens import AccessTokenSignerPort


class IssueAccessToken:
    def __init__(
        self,
        *,
        signer: AccessTokenSignerPort,
        issuer: str,
        default_audience: str,
        default_ttl_seconds: int,
        max_ttl_seconds: int,
    ):
        self._signer = signer
        self._issuer = issuer
        self._default_audience = default_audience
        self._default_ttl_seconds = default_ttl_seconds
        self._max_ttl_seconds = max_ttl_seconds

    def __call__(
        self,
        *,
        key_set: KeySet,
        subject: str,
        tenant_id: str | None,
        username: str | None,
        scopes: tuple[str, ...],
        audience: str | None = None,
        ttl_seconds: int | None = None,
    ) -> str:
        if not subject.strip():
            raise InvalidTokenRequestError("subject must not be blank")

        effective_ttl = ttl_seconds or self._default_ttl_seconds
        if effective_ttl <= 0 or effective_ttl > self._max_ttl_seconds:
            raise InvalidTokenRequestError(
                "ttl_seconds must be between 1 and AUTH_MAX_ACCESS_TOKEN_TTL_SECONDS"
            )

        now = datetime.now(UTC)
        claims = AccessTokenClaims(
            subject=subject.strip(),
            issuer=self._issuer,
            audience=audience or self._default_audience,
            scopes=scopes,
            tenant_id=tenant_id,
            username=username,
            issued_at=now,
            expires_at=now + timedelta(seconds=effective_ttl),
        )
        return self._signer.sign(claims=claims, signing_key=key_set.active_key)


def hash_refresh_token(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode()).hexdigest()


class IssueSessionTokens:
    def __init__(
        self,
        *,
        access_token_issuer: IssueAccessToken,
        refresh_token_generator: RefreshTokenGeneratorPort,
        refresh_token_ttl_seconds: int,
        access_token_ttl_seconds: int,
    ):
        self._access_token_issuer = access_token_issuer
        self._refresh_token_generator = refresh_token_generator
        self._refresh_token_ttl_seconds = refresh_token_ttl_seconds
        self._access_token_ttl_seconds = access_token_ttl_seconds

    async def __call__(
        self,
        *,
        key_set: KeySet,
        user: UserAccount,
        refresh_sessions: RefreshSessionRepositoryPort,
    ) -> SessionTokens:
        refresh_token = self._refresh_token_generator.generate()
        now = datetime.now(UTC)
        refresh_session = RefreshSession(
            id_=str(uuid4()),
            user_id=user.id_,
            token_hash=hash_refresh_token(refresh_token),
            created_at=now,
            expires_at=now + timedelta(seconds=self._refresh_token_ttl_seconds),
            revoked_at=None,
        )
        await refresh_sessions.add(refresh_session)
        access_token = self._access_token_issuer(
            key_set=key_set,
            subject=user.id_,
            tenant_id=None,
            username=user.username,
            scopes=(),
            audience=None,
            ttl_seconds=None,
        )
        return SessionTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._access_token_ttl_seconds,
        )
