from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


def build_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.db_url_sqlalchemy,
        future=True,
        pool_pre_ping=True,
    )


def build_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
