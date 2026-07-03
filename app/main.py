"""FastAPI application bootstrap."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.infrastructure.containers.application_container import (
    ApplicationContainer,
    build_container,
)
from app.infrastructure.logging.logger import configure_logging, get_logger
from app.presentation.api.errors.handlers import register_exception_handlers
from app.presentation.api.router import build_api_router
from app.presentation.middlewares.request_context import RequestContextMiddleware


def build_lifespan(container: ApplicationContainer):
    """Manage application startup and shutdown hooks."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Manage application startup and shutdown hooks."""

        app.state.container = container
        configure_logging(container.settings)
        await container.startup()
        get_logger(environment=container.settings.app_env).info("application_starting")
        yield
        get_logger(environment=container.settings.app_env).info("application_stopping")
        await container.shutdown()

    return lifespan


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    container = build_container()
    app = FastAPI(
        title=container.settings.app_name,
        debug=container.settings.app_debug,
        lifespan=build_lifespan(container),
    )
    app.state.container = container
    app.add_middleware(RequestContextMiddleware)
    app.include_router(build_api_router(), prefix=container.settings.api_v1_prefix)
    register_exception_handlers(app)
    return app


app = create_application()
