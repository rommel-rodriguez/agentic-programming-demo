import time

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from common.auth.adapters.jwt_claims_mapper import JWTClaimsPrincipalMapper
from common.auth.adapters.rs256_jwt_verifier import RS256JWTVerifier
from common.auth.adapters.static_key_provider import StaticKeyProvider
from common.auth.domain.errors import InvalidCredentialsError


@pytest.fixture
def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


@pytest.mark.asyncio
async def test_rs256_verifier_returns_principal(rsa_keypair):
    private_pem, public_pem = rsa_keypair
    token = jwt.encode(
        {
            "sub": "user-123",
            "tenant_id": "tenant-1",
            "scope": "chat:read chat:write",
            "iss": "https://auth.example.com",
            "aud": "langgraph-demo",
            "exp": int(time.time()) + 300,
        },
        private_pem,
        algorithm="RS256",
        headers={"kid": "main-key"},
    )
    verifier = RS256JWTVerifier(
        key_provider=StaticKeyProvider(public_pem.decode()),
        principal_mapper=JWTClaimsPrincipalMapper(),
        issuer="https://auth.example.com",
        audience="langgraph-demo",
    )

    principal = await verifier.verify(token)

    assert principal.subject == "user-123"
    assert principal.tenant_id == "tenant-1"
    assert principal.has_scope("chat:read")


@pytest.mark.asyncio
async def test_rs256_verifier_rejects_invalid_audience(rsa_keypair):
    private_pem, public_pem = rsa_keypair
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": "https://auth.example.com",
            "aud": "another-service",
            "exp": int(time.time()) + 300,
        },
        private_pem,
        algorithm="RS256",
    )
    verifier = RS256JWTVerifier(
        key_provider=StaticKeyProvider(public_pem.decode()),
        principal_mapper=JWTClaimsPrincipalMapper(),
        issuer="https://auth.example.com",
        audience="langgraph-demo",
    )

    with pytest.raises(InvalidCredentialsError):
        await verifier.verify(token)
