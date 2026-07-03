"""Structured logging configuration for the application."""

import logging
import sys
from typing import Any

from loguru import logger

from app.infrastructure.config.settings import Settings
from app.infrastructure.logging.request_context import get_request_id


class InterceptHandler(logging.Handler):
    """Redirect standard logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Send the received log record to Loguru."""

        level_names = logging.getLevelNamesMapping()
        level_name = record.levelname if record.levelname in level_names else "INFO"
        logger.bind(request_id=get_request_id()).opt(exception=record.exc_info).log(
            level_name,
            record.getMessage(),
        )


def configure_logging(settings: Settings) -> None:
    """Configure structured logging for the full application process."""

    logger.remove()
    logger.add(
        sys.stdout,
        serialize=settings.log_json,
        level=settings.log_level.upper(),
        backtrace=False,
        diagnose=settings.app_debug,
        enqueue=False,
    )

    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=settings.log_level.upper(), force=True)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(logger_name).handlers = [intercept_handler]
        logging.getLogger(logger_name).propagate = False


def get_logger(**context: Any):
    """Return a contextualized logger instance."""

    enriched_context = {"request_id": get_request_id(), **context}
    return logger.bind(**enriched_context)
