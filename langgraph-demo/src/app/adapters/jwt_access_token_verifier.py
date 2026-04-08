import jwt
from jwt import InvalidTokenError

from app.ports.auth import AccessTokenVerifierPort, AuthenticatedPrincipal


class JWTAccessTokenVerifier(AccessTokenVerifierPort):
    def __init__(
        self,
        *,
        secret: str,
        algorithm: str,
        audience: str | None = None,
        issuer: str | None = None,
    ):
        self._secret = secret
        self._algorithm = algorithm
        self._audience = audience
        self._issuer = issuer

    async def verify(self, token: str) -> AuthenticatedPrincipal | None:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={
                    "verify_aud": self._audience is not None,
                    "verify_iss": self._issuer is not None,
                },
            )
        except InvalidTokenError:
            return None

        raw_user_id = payload.get("sub", payload.get("user_id"))
        if raw_user_id is None:
            return None

        try:
            user_id = int(raw_user_id)
        except (TypeError, ValueError):
            return None

        tenant_id = str(payload.get("tenant_id", user_id))
        return AuthenticatedPrincipal(user_id=user_id, tenant_id=tenant_id)
