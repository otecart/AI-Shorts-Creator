import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(levelname)s] - %(message)s",
            },
            "with_timestamps": {
                "format": "%(asctime)s [%(levelname)s] - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "with_timestamps",
                "level": "DEBUG",
                "filename": "autocropper.log",
            },
        },
        "loggers": {
            "root": {
                "handlers": ["console"],
                "level": "WARN",
            },
            "app": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
