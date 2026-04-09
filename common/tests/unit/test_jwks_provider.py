import json

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from common.auth.adapters.jwks_provider import AsyncJWKSKeyProvider


@pytest.fixture
def jwk_bundle():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk["kid"] = "main-key"
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return {"keys": [jwk]}, public_pem


@pytest.mark.asyncio
async def test_jwks_provider_fetches_and_returns_signing_key(jwk_bundle):
    jwks_payload, public_pem = jwk_bundle

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://auth.example.com/.well-known/jwks.json")
        return httpx.Response(status_code=200, json=jwks_payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    provider = AsyncJWKSKeyProvider(
        jwks_url="https://auth.example.com/.well-known/jwks.json",
        client=client,
    )

    signing_key = await provider.get_signing_key("main-key")

    assert signing_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ) == public_pem
    await client.aclose()
