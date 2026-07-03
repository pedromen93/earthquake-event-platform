"""Shared runtime helpers for non-HTTP application processes."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from app.infrastructure.containers.application_container import (
    ApplicationContainer,
    build_container,
)
from app.infrastructure.logging.logger import configure_logging, get_logger


@asynccontextmanager
async def managed_container() -> AsyncIterator[ApplicationContainer]:
    """Build, initialize and dispose the root application container."""

    container = build_container()
    configure_logging(container.settings)
    get_logger(environment=container.settings.app_env).info("process_starting")
    await container.startup()
    try:
        yield container
    finally:
        get_logger(environment=container.settings.app_env).info("process_stopping")
        await container.shutdown()
