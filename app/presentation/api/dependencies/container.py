"""FastAPI dependency helpers for application container access."""

from typing import cast

from fastapi import Request

from app.infrastructure.containers.application_container import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    """Return the root container stored in application state."""

    return cast(ApplicationContainer, request.app.state.container)
