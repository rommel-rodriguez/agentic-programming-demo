from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import configure_logging

from .routers.workflows import router as wf_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


fapi_app = FastAPI(lifespan=lifespan)

fapi_app.include_router(wf_router)
