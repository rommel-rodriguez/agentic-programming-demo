import time

import jwt

from app.adapters.jwt_signer import RS256JWTSigner
from app.adapters.rsa_keys import RSAKeyGenerator
from app.domain.models import KeySet
from app.services.tokens import IssueAccessToken


def test_issue_access_token_signs_rs256_token():
    active_key = RSAKeyGenerator().generate(kid="main")
    key_set = KeySet(active_key=active_key, public_keys=(active_key,))
    service = IssueAccessToken(
        signer=RS256JWTSigner(),
        issuer="https://auth.example.com",
        default_audience="langgraph-demo",
        default_ttl_seconds=900,
        max_ttl_seconds=3600,
    )

    token = service(
        key_set=key_set,
        subject="user-123",
        tenant_id="tenant-1",
        username="alice",
        scopes=("chat:read", "chat:write"),
    )
    claims = jwt.decode(
        token,
        active_key.public_key_pem,
        algorithms=["RS256"],
        audience="langgraph-demo",
        issuer="https://auth.example.com",
    )

    assert claims["sub"] == "user-123"
    assert claims["tenant_id"] == "tenant-1"
    assert claims["preferred_username"] == "alice"
    assert claims["scope"] == "chat:read chat:write"
    assert claims["exp"] > int(time.time())
