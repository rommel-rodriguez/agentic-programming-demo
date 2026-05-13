from datetime import UTC

import jwt

from app.domain.models import AccessTokenClaims, ActiveSigningKey
from app.ports.tokens import AccessTokenSignerPort


class RS256JWTSigner(AccessTokenSignerPort):
    def sign(self, *, claims: AccessTokenClaims, signing_key: ActiveSigningKey) -> str:
        payload = {
            "sub": claims.subject,
            "iss": claims.issuer,
            "aud": claims.audience,
            "scope": " ".join(claims.scopes),
            "iat": int(claims.issued_at.astimezone(UTC).timestamp())
            if claims.issued_at is not None
            else None,
            "exp": int(claims.expires_at.astimezone(UTC).timestamp())
            if claims.expires_at is not None
            else None,
        }
        if claims.tenant_id is not None:
            payload["tenant_id"] = claims.tenant_id
        if claims.username is not None:
            payload["preferred_username"] = claims.username
        return jwt.encode(
            payload,
            signing_key.private_key_pem,
            algorithm="RS256",
            headers={"kid": signing_key.kid},
        )
