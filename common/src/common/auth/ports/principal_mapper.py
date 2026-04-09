from typing import Any, Mapping, Protocol

from common.auth.domain.models import AuthenticatedPrincipal


class PrincipalMapperPort(Protocol):
    def map_claims(self, claims: Mapping[str, Any]) -> AuthenticatedPrincipal:
        ...
