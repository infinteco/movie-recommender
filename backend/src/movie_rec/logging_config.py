"""Structured JSON logging shared by the API and CLI scripts."""

from __future__ import annotations

import logging

from pythonjsonlogger import jsonlogger

from movie_rec.config import settings

_CONFIGURED = False


def configure_logging(level: str | None = None) -> None:
    """Install a JSON log formatter on the root logger (idempotent)."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"asctime": "timestamp", "levelname": "level"},
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level or settings.log_level)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger."""
    configure_logging()
    return logging.getLogger(name)
