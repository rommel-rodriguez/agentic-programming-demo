from common.auth.domain.models import AuthenticatedPrincipal
from common.auth.ports.token_verifier import TokenVerifierPort


class VerifyAccessToken:
    def __init__(self, verifier: TokenVerifierPort):
        self._verifier = verifier

    async def __call__(self, token: str) -> AuthenticatedPrincipal:
        return await self._verifier.verify(token)
