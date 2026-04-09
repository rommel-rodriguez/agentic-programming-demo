from collections.abc import Mapping
from typing import Any

from common.auth.domain.errors import InvalidCredentialsError
from common.auth.domain.models import AuthenticatedPrincipal
from common.auth.ports.principal_mapper import PrincipalMapperPort


class JWTClaimsPrincipalMapper(PrincipalMapperPort):
    def __init__(
        self,
        *,
        subject_claim: str = "sub",
        tenant_id_claim: str = "tenant_id",
        scope_claim: str = "scope",
    ):
        self._subject_claim = subject_claim
        self._tenant_id_claim = tenant_id_claim
        self._scope_claim = scope_claim

    def map_claims(self, claims: Mapping[str, Any]) -> AuthenticatedPrincipal:
        subject = claims.get(self._subject_claim)
        if not isinstance(subject, str) or not subject:
            raise InvalidCredentialsError("Access token is missing a valid subject")

        tenant_id = claims.get(self._tenant_id_claim)
        if tenant_id is not None and not isinstance(tenant_id, str):
            tenant_id = str(tenant_id)

        raw_scopes = claims.get(self._scope_claim, "")
        scopes = self._parse_scopes(raw_scopes)
        return AuthenticatedPrincipal(
            subject=subject,
            tenant_id=tenant_id,
            scopes=scopes,
        )

    @staticmethod
    def _parse_scopes(raw_scopes: Any) -> frozenset[str]:
        if isinstance(raw_scopes, str):
            return frozenset(scope for scope in raw_scopes.split() if scope)
        if isinstance(raw_scopes, list):
            return frozenset(str(scope) for scope in raw_scopes if str(scope))
        return frozenset()
