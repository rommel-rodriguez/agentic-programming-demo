from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


fapi_app = FastAPI(lifespan=lifespan)
