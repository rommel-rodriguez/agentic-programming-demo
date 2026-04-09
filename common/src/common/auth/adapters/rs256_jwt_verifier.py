from typing import Iterable

import jwt
from jwt import InvalidTokenError

from common.auth.domain.errors import InvalidCredentialsError
from common.auth.domain.models import AuthenticatedPrincipal
from common.auth.ports.key_set_provider import KeySetProviderPort
from common.auth.ports.principal_mapper import PrincipalMapperPort
from common.auth.ports.token_verifier import TokenVerifierPort


class RS256JWTVerifier(TokenVerifierPort):
    def __init__(
        self,
        *,
        key_provider: KeySetProviderPort,
        principal_mapper: PrincipalMapperPort,
        issuer: str,
        audience: str | None = None,
        algorithms: Iterable[str] = ("RS256",),
        leeway_seconds: int = 0,
    ):
        self._key_provider = key_provider
        self._principal_mapper = principal_mapper
        self._issuer = issuer
        self._audience = audience
        self._algorithms = tuple(algorithms)
        self._leeway_seconds = leeway_seconds

    async def verify(self, token: str) -> AuthenticatedPrincipal:
        try:
            header = jwt.get_unverified_header(token)
        except InvalidTokenError as exc:
            raise InvalidCredentialsError("Access token header is invalid") from exc

        key = await self._key_provider.get_signing_key(header.get("kid"))
        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self._algorithms),
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway_seconds,
                options={
                    "require": ["exp", "sub"],
                    "verify_aud": self._audience is not None,
                },
            )
        except InvalidTokenError as exc:
            raise InvalidCredentialsError("Access token verification failed") from exc

        return self._principal_mapper.map_claims(claims)
