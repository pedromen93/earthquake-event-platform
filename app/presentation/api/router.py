"""Main API router composition."""

from fastapi import APIRouter

from app.presentation.api.routers.earthquakes import router as earthquakes_router
from app.presentation.api.routers.health import router as health_router
from app.presentation.api.routers.metrics import router as metrics_router
from app.presentation.api.routers.operations import router as operations_router
from app.presentation.api.routers.reports import router as reports_router
from app.presentation.api.routers.stream import router as stream_router


def build_api_router() -> APIRouter:
    """Build the root API router."""

    api_router = APIRouter()
    api_router.include_router(health_router)
    api_router.include_router(earthquakes_router)
    api_router.include_router(metrics_router)
    api_router.include_router(reports_router)
    api_router.include_router(operations_router)
    api_router.include_router(stream_router)
    return api_router
