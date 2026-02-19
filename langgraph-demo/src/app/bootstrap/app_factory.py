import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import ConnectionPool

from app.bootstrap.logging import configure_logging
from app.config import settings
from app.entrypoints.webapp.routers.invoice import router as invoice_router
from app.entrypoints.webapp.routers.workflows import router as wf_router

logger = logging.getLogger(__name__)


def _build_lifespan(checkpointer_backend: str):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging()

        if checkpointer_backend == "memory":
            app.state.checkpointer = InMemorySaver()
            app.state.pg_pool = None
            yield
            return

        db_url = str(settings.db_url)
        logger.info(f"Starting db with db_url: SHOW ONLY NON-PASSWORD")
        pool = ConnectionPool(
            db_url,
            max_size=10,
            connection_class=Connection[DictRow],  # Needed ore mypy complains
            kwargs={"autocommit": True, "row_factory": dict_row},
        )
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()  # Creates required tables for checkpointing for the first time

        app.state.checkpointer = checkpointer
        app.state.pg_pool = pool
        try:
            yield
        finally:
            pool.close()

    return lifespan


async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


# TODO: Modify this entrypoint so we can use either an in-memory checkpointer or a
# production checkpointer. Nest the lifespan function inside if needed.
def create_app(*, checkpointer_backend: str = "postgres") -> FastAPI:
    app = FastAPI(lifespan=_build_lifespan(checkpointer_backend))
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(wf_router, prefix="/wf")
    app.include_router(invoice_router, prefix="/invoice")
    app.add_exception_handler(HTTPException, http_exception_handle_logging)
    return app
