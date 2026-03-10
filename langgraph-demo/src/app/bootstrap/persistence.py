from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import config
from app.adapters.orm import start_mappers


def build_session_factory():
    db_url = str(config.get_settings().db_url_sqlalchemy)
    return async_sessionmaker(
        bind=create_async_engine(
            url=db_url, isolation_level="REPEATABLE READ", pool_pre_ping=True
        )
    )


async def configure_persistence(start_orm: bool = True):
    start_mappers()
