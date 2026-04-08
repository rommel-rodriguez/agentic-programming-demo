from functools import lru_cache
from pathlib import Path
from typing import Union

from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     env_file=Path(__file__).resolve().parent / ".env", env_file_encoding="utf-8"
    # )

    # debug: bool = False
    db_url: Union[PostgresDsn, None] = None
    db_url_sqlalchemy: Union[PostgresDsn, None] = None
    env: str = "prod"
    tavily_api_key: str = ""
    gemini_api_key: SecretStr
    redis_url: str = "redis://redis:6379/0"
    ws_ticket_ttl_seconds: int = Field(default=30, ge=1)
    auth_access_token_secret: SecretStr = SecretStr("dev-only-change-me")
    auth_access_token_algorithm: str = "HS256"
    auth_access_token_audience: str | None = None
    auth_access_token_issuer: str | None = None


# settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


# NOTE: Replace most, if not all, with environment variables
USERNAME = "appuser"
LOG_PATH = f"/home/{USERNAME}/hello.log"
