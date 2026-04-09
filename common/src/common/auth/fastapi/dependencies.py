from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from common.auth.domain.errors import (
    ForbiddenError,
    InvalidCredentialsError,
    MissingCredentialsError,
)
from common.auth.domain.models import AuthenticatedPrincipal
from common.auth.fastapi.security import (
    bearer_scheme,
    extract_bearer_token,
    unauthorized_http_exception,
)
from common.auth.ports.token_verifier import TokenVerifierPort
from common.auth.services.verify_access_token import VerifyAccessToken


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    try:
        return extract_bearer_token(credentials)
    except MissingCredentialsError as exc:
        raise unauthorized_http_exception(str(exc)) from exc


async def get_optional_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str | None:
    if credentials is None:
        return None
    try:
        return extract_bearer_token(credentials)
    except MissingCredentialsError as exc:
        raise unauthorized_http_exception(str(exc)) from exc


def build_require_principal_dependency(
    verifier: TokenVerifierPort,
) -> Callable[..., AuthenticatedPrincipal]:
    verify_access_token = VerifyAccessToken(verifier)

    async def require_principal(
        token: str = Depends(get_bearer_token),
    ) -> AuthenticatedPrincipal:
        try:
            return await verify_access_token(token)
        except MissingCredentialsError as exc:
            raise unauthorized_http_exception(str(exc)) from exc
        except InvalidCredentialsError as exc:
            raise unauthorized_http_exception(str(exc)) from exc
        except ForbiddenError as exc:
            raise unauthorized_http_exception(str(exc)) from exc

    return require_principal


def build_optional_principal_dependency(
    verifier: TokenVerifierPort,
) -> Callable[..., AuthenticatedPrincipal | None]:
    verify_access_token = VerifyAccessToken(verifier)

    async def optional_principal(
        token: str | None = Depends(get_optional_bearer_token),
    ) -> AuthenticatedPrincipal | None:
        if token is None:
            return None
        try:
            return await verify_access_token(token)
        except MissingCredentialsError as exc:
            raise unauthorized_http_exception(str(exc)) from exc
        except InvalidCredentialsError as exc:
            raise unauthorized_http_exception(str(exc)) from exc
        except ForbiddenError as exc:
            raise unauthorized_http_exception(str(exc)) from exc

    return optional_principal
