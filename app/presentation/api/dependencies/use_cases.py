"""FastAPI dependency helpers for application use cases."""

from fastapi import Depends

from app.application.use_cases.ingest_earthquakes import IngestEarthquakesUseCase
from app.application.use_cases.get_earthquakes import GetEarthquakesUseCase
from app.application.use_cases.get_hourly_metrics import GetHourlyMetricsUseCase
from app.application.use_cases.get_hourly_reports import GetHourlyReportsUseCase
from app.infrastructure.containers.application_container import ApplicationContainer
from app.presentation.api.dependencies.container import get_container


def get_earthquakes_use_case(
    container: ApplicationContainer = Depends(get_container),
) -> GetEarthquakesUseCase:
    """Return the earthquake query use case from the application container."""

    return container.get_earthquakes_use_case


def get_ingest_earthquakes_use_case(
    container: ApplicationContainer = Depends(get_container),
) -> IngestEarthquakesUseCase:
    """Return the earthquake ingestion use case from the application container."""

    return container.ingest_earthquakes_use_case


def get_hourly_metrics_use_case(
    container: ApplicationContainer = Depends(get_container),
) -> GetHourlyMetricsUseCase:
    """Return the hourly metrics query use case from the application container."""

    return container.get_hourly_metrics_use_case


def get_hourly_reports_use_case(
    container: ApplicationContainer = Depends(get_container),
) -> GetHourlyReportsUseCase:
    """Return the hourly reports query use case from the application container."""

    return container.get_hourly_reports_use_case
