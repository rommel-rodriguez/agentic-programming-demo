import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from app.bootstrap.logging import configure_logging
from app.entrypoints.webapp.routers.invoice import router as invoice_router
from app.entrypoints.webapp.routers.workflows import router as wf_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(wf_router, prefix="/wf")
    app.include_router(invoice_router, prefix="/invoice")
    app.add_exception_handler(HTTPException, http_exception_handle_logging)
    return app
