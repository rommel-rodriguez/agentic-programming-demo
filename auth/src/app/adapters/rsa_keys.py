import json

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.domain.models import ActiveSigningKey, PublicSigningKey
from app.ports.jwks import JWKBuilderPort
from app.ports.keys import SigningKeyGeneratorPort


class RSAKeyGenerator(SigningKeyGeneratorPort):
    def __init__(self, *, key_size: int = 2048):
        self._key_size = key_size

    def generate(self, *, kid: str) -> ActiveSigningKey:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self._key_size,
        )
        public_key = private_key.public_key()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        return ActiveSigningKey(
            kid=kid,
            private_key_pem=private_pem,
            public_key_pem=public_pem,
        )


class RSAJWKBuilder(JWKBuilderPort):
    def build(self, key: PublicSigningKey) -> dict[str, str]:
        jwk = json.loads(
            jwt.algorithms.RSAAlgorithm.to_jwk(
                serialization.load_pem_public_key(key.public_key_pem.encode())
            )
        )
        jwk["kid"] = key.kid
        jwk["alg"] = "RS256"
        jwk["use"] = "sig"
        return jwk
