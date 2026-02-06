from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap.logging import configure_logging
from app.entrypoints.webapp.routers.workflows import router as wf_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(wf_router)
    return app
