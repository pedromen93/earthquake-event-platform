"""Health-related HTTP routes."""

from fastapi import APIRouter, Depends

from app.infrastructure.containers.application_container import ApplicationContainer
from app.presentation.api.dependencies.container import get_container
from app.presentation.api.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def get_health(
    container: ApplicationContainer = Depends(get_container),
) -> HealthResponse:
    """Expose a lightweight health check endpoint."""

    return HealthResponse(
        status="ok",
        service=container.settings.app_name,
        environment=container.settings.app_env,
    )
