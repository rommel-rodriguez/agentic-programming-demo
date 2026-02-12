import logging
import logging.config
import logging.handlers
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
    env: str = "prod"
    tavily_api_key: str = ""
    gemini_api_key: SecretStr


settings = Settings()


# NOTE: Replace most, if not all, with environment variables
USERNAME = "appuser"
LOG_PATH = f"/home/{USERNAME}/hello.log"
