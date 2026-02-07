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
    "filters": {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            # "uuid_length": 8 if isinstance(config, DevConfig) else 32,
            "uuid_length": 8 if settings.env == "dev" else 32,
            "default_value": "-",
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s::%(correlation_id)s::%(levelname)-08s::%(name)s:%(lineno)d::%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
            "filters": ["correlation_id"],
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        # NOTE: Not a good practice to set a handler per logger, this is just a
        # workaround in order not to get so many DEBUG level messages from the
        # listed third-party library loggers. It would be better to find a way to
        # simplify this this.
        "uvicorn": {"handlers": ["console"], "level": "INFO"},
        "uvicorn.error": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "httpcore": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "urllib3": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


def configure_logging():
    logging.config.dictConfig(LOG_CONFIG)
