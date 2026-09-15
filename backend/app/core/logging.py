import logging
from logging.config import dictConfig
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE = LOG_DIR / "app.log"


def configurar_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "file": {
                    "format": "[%(levelname)s] | %(asctime)s | %(message)s | %(pathname)s - Linha: %(lineno)d",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "access": {
                    "format": "[%(levelname)s] | %(asctime)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "application_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(LOG_FILE),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 5,
                    "encoding": "utf-8",
                    "level": "WARNING",
                    "formatter": "file",
                },
                "access_console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "access",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "backend.app": {
                    "handlers": ["application_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "backend.app.access": {
                    "handlers": ["access_console"],
                    "level": "INFO",
                    "propagate": False,
                },
                "py.warnings": {
                    "handlers": ["application_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["application_file"],
                "level": "WARNING",
            },
        }
    )
    logging.captureWarnings(True)


def obter_logger(nome: str) -> logging.Logger:
    return logging.getLogger(nome)
