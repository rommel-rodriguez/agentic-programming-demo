from typing import Protocol

from app.domain.models import AccessTokenClaims, ActiveSigningKey


class AccessTokenSignerPort(Protocol):
    def sign(self, *, claims: AccessTokenClaims, signing_key: ActiveSigningKey) -> str:
        ...
