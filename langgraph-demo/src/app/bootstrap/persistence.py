from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import config
from app.adapters.orm import start_mappers


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


def build_session_factory():
    db_url = str(config.get_settings().db_url_sqlalchemy)
    engine = build_engine()
    return async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


async def configure_persistence(start_orm: bool = True):
    if start_orm:
        start_mappers()
