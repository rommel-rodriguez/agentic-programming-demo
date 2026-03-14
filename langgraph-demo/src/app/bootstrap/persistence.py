from psycopg import AsyncConnection, Connection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool, ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import config
from app.adapters.orm import start_mappers


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


def build_engine() -> AsyncEngine:
    db_url = str(config.get_settings().db_url_sqlalchemy)
    return create_async_engine(
        db_url,
        isolation_level="REPEATABLE READ",
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=0,
        pool_timeout=5,
        pool_recycle=3600,
        pool_use_lifo=True,
    )


def build_session_factory(engine: AsyncEngine):
    db_url = str(config.get_settings().db_url_sqlalchemy)
    # engine = build_engine()
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


async def configure_persistence(start_orm: bool = True):
    if start_orm:
        start_mappers()
