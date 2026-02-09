import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
