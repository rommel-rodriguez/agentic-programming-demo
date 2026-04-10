from typing import Any

from app.domain.models import KeySet
from app.ports.jwks import JWKBuilderPort


class BuildJWKS:
    def __init__(self, *, jwk_builder: JWKBuilderPort):
        self._jwk_builder = jwk_builder

    def __call__(self, key_set: KeySet) -> dict[str, list[dict[str, Any]]]:
        return {
            "keys": [self._jwk_builder.build(key) for key in key_set.public_keys],
        }
