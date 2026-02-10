from venv import create

import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport

from app.bootstrap.app_factory import create_app

TEST_BASE_URL = 'http://testserver' 

# NOTE: Or should I import this from entrypoints.webapp.asgi?
# Or the current approach is better, as I can build the app differently
# for tests?
app = create_app()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture()
def base_url()
    return TEST_BASE_URL

@pytest.fixture()
def client(base_url):
    with TestClient(app, base_url=base_url) as c:
        yield c


# @pytest.fixture()
# async def db():
#     await database.connect()
#     yield
#     await database.disconnect()

@pytest.fixture()
async def async_client(base_url):
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac