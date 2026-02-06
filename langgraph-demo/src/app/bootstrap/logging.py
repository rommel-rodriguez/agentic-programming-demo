import logging
import logging.config

from app.config import settings

LOG_LEVEL: int = logging.INFO

# NOTE: Consider not making LOG_LEVEL dependend on environment variable
if settings.env == "dev":
    LOG_LEVEL = logging.DEBUG

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s::%(levelname)-08s::%(name)s:%(lineno)d::%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {"uvicorn": {"handlers": ["console"], "level": "INFO"}},
}


def configure_logging():
    logging.config.dictConfig(LOG_CONFIG)
