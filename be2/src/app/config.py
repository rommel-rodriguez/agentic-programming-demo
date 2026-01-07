import logging

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    debug: bool = False
    database_url: PostgresDsn


# NOTE: Replace most, if not all, with environment variables
ENV = "dev"
USERNAME = "appuser"
LOG_PATH = f"/home/{USERNAME}/hello.log"

log_level: int = logging.INFO

if ENV == "dev":
    log_level = logging.DEBUG

logging.basicConfig(filename=LOG_PATH, level=log_level)
