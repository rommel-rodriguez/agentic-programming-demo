import logging
import logging.config
import logging.handlers

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

LOG_LEVEL: int = logging.INFO

# NOTE: Consider not making LOG_LEVEL dependend on environment variable
if ENV == "dev":
    LOG_LEVEL = logging.DEBUG

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s::%(levelname)s::%(name)s::%(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}


def configure_logging():
    logging.config.dictConfig(LOG_CONFIG)


def get_custom_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)

    stdout_handler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_PATH, maxBytes=1048576, backupCount=2
    )
    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    formatter = logging.Formatter(
        ("%(asctime)s - %(levelname)s - %(name)s - " "%(message)s")
    )
    stdout_handler.setFormatter(formatter)

    return logger
