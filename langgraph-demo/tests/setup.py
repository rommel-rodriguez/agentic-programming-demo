import httpx
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
