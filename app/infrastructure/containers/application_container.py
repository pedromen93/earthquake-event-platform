"""Application dependency container."""

from dataclasses import dataclass

import httpx

from app.application.interfaces.earthquake_feed_client import EarthquakeFeedClient
from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.application.interfaces.hourly_metric_repository import HourlyMetricRepository
from app.application.interfaces.hourly_report_repository import HourlyReportRepository
from app.application.use_cases.generate_hourly_report import GenerateHourlyReportUseCase
from app.application.use_cases.get_earthquakes import GetEarthquakesUseCase
from app.application.use_cases.get_hourly_metrics import GetHourlyMetricsUseCase
from app.application.use_cases.get_hourly_reports import GetHourlyReportsUseCase
from app.application.use_cases.ingest_earthquakes import IngestEarthquakesUseCase
from app.application.use_cases.refresh_hourly_metrics import RefreshHourlyMetricsUseCase
from app.domain.services.hourly_metrics_calculator import HourlyMetricsCalculator
from app.domain.services.hourly_report_builder import HourlyReportBuilder
from app.infrastructure.clients.usgs_client import UsgsEarthquakeFeedClient
from app.infrastructure.config.settings import Settings, get_settings
from app.infrastructure.database.indexes import ensure_indexes
from app.infrastructure.database.mongodb import MongoDatabase
from app.infrastructure.repositories.mongo_earthquake_repository import MongoEarthquakeRepository
from app.infrastructure.repositories.mongo_hourly_metric_repository import (
    MongoHourlyMetricRepository,
)
from app.infrastructure.repositories.mongo_hourly_report_repository import (
    MongoHourlyReportRepository,
)


@dataclass(slots=True)
class ApplicationContainer:
    """Root dependency container for bootstrapping the application."""

    settings: Settings
    http_client: httpx.AsyncClient
    mongo_database: MongoDatabase
    earthquake_repository: EarthquakeRepository
    hourly_metric_repository: HourlyMetricRepository
    hourly_report_repository: HourlyReportRepository
    earthquake_feed_client: EarthquakeFeedClient
    hourly_metrics_calculator: HourlyMetricsCalculator
    hourly_report_builder: HourlyReportBuilder
    refresh_hourly_metrics_use_case: RefreshHourlyMetricsUseCase
    ingest_earthquakes_use_case: IngestEarthquakesUseCase
    generate_hourly_report_use_case: GenerateHourlyReportUseCase
    get_earthquakes_use_case: GetEarthquakesUseCase
    get_hourly_metrics_use_case: GetHourlyMetricsUseCase
    get_hourly_reports_use_case: GetHourlyReportsUseCase

    async def startup(self) -> None:
        """Initialize infrastructure resources required at application startup."""

        await self.mongo_database.connect()
        await ensure_indexes(self.mongo_database, self.settings)

    async def shutdown(self) -> None:
        """Release infrastructure resources when the application stops."""

        await self.http_client.aclose()
        await self.mongo_database.disconnect()


def build_container() -> ApplicationContainer:
    """Build the root dependency container."""

    settings = get_settings()
    http_client = httpx.AsyncClient(
        base_url=settings.usgs_base_url,
        timeout=settings.request_timeout_seconds,
    )
    mongo_database = MongoDatabase(settings=settings)
    earthquake_repository = MongoEarthquakeRepository(database=mongo_database, settings=settings)
    hourly_metric_repository = MongoHourlyMetricRepository(database=mongo_database, settings=settings)
    hourly_report_repository = MongoHourlyReportRepository(database=mongo_database, settings=settings)
    earthquake_feed_client = UsgsEarthquakeFeedClient(http_client=http_client, settings=settings)
    hourly_metrics_calculator = HourlyMetricsCalculator()
    hourly_report_builder = HourlyReportBuilder()
    refresh_hourly_metrics_use_case = RefreshHourlyMetricsUseCase(
        earthquake_repository=earthquake_repository,
        hourly_metric_repository=hourly_metric_repository,
        hourly_metrics_calculator=hourly_metrics_calculator,
    )
    ingest_earthquakes_use_case = IngestEarthquakesUseCase(
        earthquake_feed_client=earthquake_feed_client,
        earthquake_repository=earthquake_repository,
        refresh_hourly_metrics_use_case=refresh_hourly_metrics_use_case,
    )
    generate_hourly_report_use_case = GenerateHourlyReportUseCase(
        earthquake_repository=earthquake_repository,
        hourly_report_repository=hourly_report_repository,
        hourly_report_builder=hourly_report_builder,
    )
    get_earthquakes_use_case = GetEarthquakesUseCase(
        earthquake_repository=earthquake_repository,
    )
    get_hourly_metrics_use_case = GetHourlyMetricsUseCase(
        hourly_metric_repository=hourly_metric_repository,
    )
    get_hourly_reports_use_case = GetHourlyReportsUseCase(
        hourly_report_repository=hourly_report_repository,
    )

    return ApplicationContainer(
        settings=settings,
        http_client=http_client,
        mongo_database=mongo_database,
        earthquake_repository=earthquake_repository,
        hourly_metric_repository=hourly_metric_repository,
        hourly_report_repository=hourly_report_repository,
        earthquake_feed_client=earthquake_feed_client,
        hourly_metrics_calculator=hourly_metrics_calculator,
        hourly_report_builder=hourly_report_builder,
        refresh_hourly_metrics_use_case=refresh_hourly_metrics_use_case,
        ingest_earthquakes_use_case=ingest_earthquakes_use_case,
        generate_hourly_report_use_case=generate_hourly_report_use_case,
        get_earthquakes_use_case=get_earthquakes_use_case,
        get_hourly_metrics_use_case=get_hourly_metrics_use_case,
        get_hourly_reports_use_case=get_hourly_reports_use_case,
    )
