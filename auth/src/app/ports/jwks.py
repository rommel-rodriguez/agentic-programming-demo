from typing import Any, Protocol

from app.domain.models import PublicSigningKey


class JWKBuilderPort(Protocol):
    def build(self, key: PublicSigningKey) -> dict[str, Any]:
        ...
