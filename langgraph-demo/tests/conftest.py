import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import clear_mappers

from app import config
from app.adapters.orm import mapper_registry, start_mappers
from app.bootstrap.app_factory import create_app

TEST_BASE_URL = "http://testserver"

# NOTE: Or should I import this from entrypoints.webapp.asgi?
# Or the current approach is better, as I can build the app differently
# for tests?


@pytest.fixture(scope="session")
def mappers():
    start_mappers()
    yield
    clear_mappers()


@pytest_asyncio.fixture()
async def in_memory_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # mapper_registry.metadata.create_all(engine)
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
    return engine


@pytest.fixture
def in_memory_session_factory(in_memory_db):
    return async_sessionmaker(in_memory_db)


@pytest.fixture
def postgres_db():
    db_url_sqlalchemy: str = str(config.get_settings().db_url_sqlalchemy)
    engine = create_async_engine(db_url_sqlalchemy, isolation_level="SERIALIZABLE")
    # NOTE: If we add code to wait for postgres here, this fixture would need to become
    # an async fixture.
    return engine


@pytest.fixture
def postgres_session_factory(postgres_db):
    return async_sessionmaker(bind=postgres_db)


@pytest.fixture
def app_memory():
    return create_app(checkpointer_backend="memory")


@pytest.fixture
def app_postgres():
    return create_app(checkpointer_backend="postgres")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def base_url():
    return TEST_BASE_URL


@pytest.fixture
def client_memory(app_memory, base_url):
    with TestClient(app_memory, base_url=base_url) as c:
        yield c


@pytest.fixture
def client_postgres(app_postgres, base_url):
    with TestClient(app_postgres, base_url=base_url) as c:
        yield c


@pytest_asyncio.fixture
async def async_client_memory(app_memory, base_url):
    transport = ASGITransport(app=app_memory)
    async with httpx.AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac


@pytest_asyncio.fixture
async def async_client_postgres(app_postgres, base_url):
    transport = ASGITransport(app=app_postgres)
    async with httpx.AsyncClient(transport=transport, base_url=base_url) as ac:
        yield ac
