from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class PublicSigningKey:
    kid: str
    public_key_pem: str


@dataclass(frozen=True, slots=True)
class ActiveSigningKey(PublicSigningKey):
    private_key_pem: str


@dataclass(frozen=True, slots=True)
class KeySet:
    active_key: ActiveSigningKey
    public_keys: tuple[PublicSigningKey, ...]


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    subject: str
    issuer: str
    audience: str
    scopes: tuple[str, ...] = ()
    tenant_id: str | None = None
    username: str | None = None
    issued_at: datetime | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UserAccount:
    id_: str
    username: str
    username_normalized: str
    password_hash: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class RefreshSession:
    id_: str
    user_id: str
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SessionTokens:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
