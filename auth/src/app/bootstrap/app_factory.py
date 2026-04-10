import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.bootstrap.persistence import build_engine, build_session_factory
from app.bootstrap.services import (
    build_jwks_document,
    build_key_set,
    build_refresh_user_session,
    build_signin_user,
    build_signout_user,
    build_signup_user,
)
from app.config import get_settings
from app.domain.errors import (
    AuthServiceError,
    InvalidCredentialsError,
    RefreshTokenInvalidError,
    SigningKeyNotFoundError,
    UserAlreadyExistsError,
)
from app.entrypoints.webapp.routers.openid import router as openid_router
from app.entrypoints.webapp.routers.users import router as users_router

logger = logging.getLogger(__name__)


def _build_lifespan():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = get_settings()
        engine = build_engine()
        session_factory = build_session_factory(engine)
        key_set = build_key_set()
        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = session_factory
        app.state.key_set = key_set
        app.state.jwks_document = build_jwks_document(key_set)
        app.state.signup_user = build_signup_user(session_factory)
        app.state.signin_user = build_signin_user(session_factory)
        app.state.refresh_user_session = build_refresh_user_session(session_factory)
        app.state.signout_user = build_signout_user(session_factory)
        try:
            yield
        finally:
            await engine.dispose()

    return lifespan


async def handle_auth_service_error(request: Request, exc: AuthServiceError):
    logger.warning(
        "Auth service error",
        extra={"path": str(request.url.path), "error": str(exc)},
    )
    status_code = 400
    if isinstance(exc, UserAlreadyExistsError):
        status_code = 409
    elif isinstance(exc, (InvalidCredentialsError, RefreshTokenInvalidError)):
        status_code = 401
    elif isinstance(exc, SigningKeyNotFoundError):
        status_code = 503
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": exc.__class__.__name__, "message": str(exc)}},
    )


def create_app() -> FastAPI:
    app = FastAPI(lifespan=_build_lifespan())
    app.include_router(openid_router)
    app.include_router(users_router)
    app.add_exception_handler(AuthServiceError, handle_auth_service_error)
    return app
