import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection, Connection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from app.bootstrap.logging import configure_logging
from app.config import get_settings
from app.entrypoints.webapp.routers.invoice import router as invoice_router
from app.entrypoints.webapp.routers.workflows import router as wf_router
from app.services.errors import ApplicationError

logger = logging.getLogger(__name__)


def build_langgraph_pool(dsn: str) -> AsyncConnectionPool[AsyncConnection[DictRow]]:
    return AsyncConnectionPool(
        conninfo=dsn,
        min_size=1,
        max_size=5,
        timeout=10,
        max_lifetime=1800,
        max_idle=300,
        open=False,
        kwargs={"autocommit": True, "row_factory": dict_row},
        check=AsyncConnectionPool[AsyncConnection[DictRow]].check_connection,
        name="langraph_pool",
    )


def build_app_pool(dsn: str) -> AsyncConnectionPool:
    return AsyncConnectionPool(
        conninfo=dsn,
        min_size=2,
        max_size=20,
        timeout=5,
        max_waiting=50,
        max_lifetime=3600,
        max_idle=600,
        open=False,
        kwargs={
            "autocommit": False,
        },
        check=AsyncConnectionPool.check_connection,
        name="app_pool",
    )


def _build_lifespan(checkpointer_backend: str):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging()

        settings = get_settings()
        #  TODO: This is the flag for the checkpointer backend, a flag for the
        #  application model backend is still required.
        if checkpointer_backend == "memory":
            app.state.checkpointer = InMemorySaver()
            app.state.pg_pool = None
            yield
            return

        db_url = str(settings.db_url)
        logger.info(f"Starting db with db_url: SHOW ONLY NON-PASSWORD")
        # pool = ConnectionPool(
        #     db_url,
        #     max_size=10,
        #     connection_class=Connection[DictRow],  # Needed ore mypy complains
        #     kwargs={"autocommit": True, "row_factory": dict_row},
        # )
        lg_pool = build_langgraph_pool(db_url)
        app_pool = build_langgraph_pool(db_url)
        await lg_pool.open(wait=True)
        await app_pool.open(wait=True)

        app.state.langgraph_pool = lg_pool
        app.state.app_pool = lg_pool
        app.state.checkpointer = AsyncPostgresSaver(lg_pool)
        await app.state.checkpointer.setup()
        try:
            yield
        finally:
            await lg_pool.close()
            await app_pool.close()

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


# TODO: Modify this entrypoint so we can use either an in-memory checkpointer or a
# production checkpointer. Nest the lifespan function inside if needed.
def create_app(*, checkpointer_backend: str = "postgres") -> FastAPI:
    app = FastAPI(lifespan=_build_lifespan(checkpointer_backend))
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(wf_router, prefix="/wf")
    app.include_router(invoice_router, prefix="/invoice")
    app.add_exception_handler(HTTPException, http_exception_handle_logging)
    app.add_exception_handler(ApplicationError, handle_application_error)
    return app
