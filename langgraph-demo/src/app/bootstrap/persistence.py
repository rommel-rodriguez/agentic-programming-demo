from app.adapters.orm import start_mappers


async def configure_persistence(start_orm: bool = True):
    start_mappers()
