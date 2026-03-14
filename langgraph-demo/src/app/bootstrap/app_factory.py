import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.bootstrap.logging import configure_logging
from app.bootstrap.persistence import (
    build_app_pool,
    build_engine,
    build_langgraph_pool,
    build_session_factory,
    configure_persistence,
)
from app.config import get_settings
from app.entrypoints.webapp.routers.invoice import router as invoice_router
from app.entrypoints.webapp.routers.workflows import router as wf_router
from app.services.errors import ApplicationError

logger = logging.getLogger(__name__)


def _build_lifespan(checkpointer_backend: str):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging()
        await configure_persistence()  # Starts ORM mappers

        settings = get_settings()
        if checkpointer_backend == "memory":
            app.state.checkpointer = InMemorySaver()
            app.state.pg_pool = None
            yield
            return

        db_url = str(settings.db_url)
        db_url_sqlalchemy = str(settings.db_url_sqlalchemy)
        logger.info(f"Starting db with db_url: SHOW ONLY NON-PASSWORD")
        lg_pool = build_langgraph_pool(db_url)
        app_pool = build_app_pool(db_url_sqlalchemy)
        await lg_pool.open(wait=True)
        await app_pool.open(wait=True)

        app.state.langgraph_pool = lg_pool
        engine = build_engine()
        app.state.session_factory = build_session_factory(engine)
        app.state.app_pool = app_pool
        app.state.checkpointer = AsyncPostgresSaver(lg_pool)
        await app.state.checkpointer.setup()
        try:
            yield
        finally:
            await lg_pool.close()
            await app_pool.close()
            await engine.dispose()

    return lifespan


async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


async def handle_application_error(request, exc):
    status_map = {
        "unsupported_mime_type": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "attachment_not_pending": status.HTTP_404_NOT_FOUND,  # or 409 depending on business semantcis
        "storage_unavailable": status.HTTP_503_SERVICE_UNAVAILABLE,
        "attachment_metadata_update_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "attachment_size_bytes_too_big": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    }

    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={"error": {"code": exc.code, "message": str(exc)}},
    )


def create_app(*, checkpointer_backend: str = "postgres") -> FastAPI:
    app = FastAPI(lifespan=_build_lifespan(checkpointer_backend))
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(wf_router, prefix="/wf")
    app.include_router(invoice_router, prefix="/invoice")
    app.add_exception_handler(HTTPException, http_exception_handle_logging)
    app.add_exception_handler(ApplicationError, handle_application_error)
    return app
