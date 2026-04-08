from fastapi import HTTPException, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.auth.domain.errors import MissingCredentialsError

bearer_scheme = HTTPBearer(auto_error=False)


def extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise MissingCredentialsError("Missing bearer token")
    if credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise MissingCredentialsError("Missing bearer token")
    return credentials.credentials


def extract_websocket_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise MissingCredentialsError("Missing bearer token")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise MissingCredentialsError("Missing bearer token")
    return token


def unauthorized_http_exception(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def unauthorized_websocket_exception(detail: str = "Unauthorized") -> WebSocketException:
    return WebSocketException(
        code=status.WS_1008_POLICY_VIOLATION,
        reason=detail,
    )
