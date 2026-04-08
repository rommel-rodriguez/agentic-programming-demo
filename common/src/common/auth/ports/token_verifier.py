from typing import Protocol

from common.auth.domain.models import AuthenticatedPrincipal


class TokenVerifierPort(Protocol):
    async def verify(self, token: str) -> AuthenticatedPrincipal:
        ...
