import pytest
from fastapi import HTTPException

from common.auth.domain.errors import InvalidCredentialsError
from common.auth.domain.models import AuthenticatedPrincipal
from common.auth.fastapi.dependencies import build_require_principal_dependency


class StubVerifier:
    async def verify(self, token: str) -> AuthenticatedPrincipal:
        if token != "valid-token":
            raise InvalidCredentialsError("Access token verification failed")
        return AuthenticatedPrincipal(subject="user-123", tenant_id="tenant-1")


@pytest.mark.asyncio
async def test_require_principal_dependency_accepts_valid_bearer_token():
    require_principal = build_require_principal_dependency(StubVerifier())

    principal = await require_principal(token="valid-token")

    assert principal.subject == "user-123"
    assert principal.tenant_id == "tenant-1"


@pytest.mark.asyncio
async def test_require_principal_dependency_rejects_invalid_token():
    require_principal = build_require_principal_dependency(StubVerifier())

    with pytest.raises(HTTPException) as exc_info:
        await require_principal(token="invalid-token")

    assert exc_info.value.status_code == 401
