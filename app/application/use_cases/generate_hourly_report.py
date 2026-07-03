"""Application use case for generating consolidated hourly reports."""

from datetime import UTC, datetime, timedelta

from app.application.dtos.report_generation import ReportGenerationResultDTO
from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.application.interfaces.hourly_report_repository import HourlyReportRepository
from app.domain.services.hourly_report_builder import HourlyReportBuilder
from app.infrastructure.logging.logger import get_logger


class GenerateHourlyReportUseCase:
    """Generate and persist the hourly consolidated report for a target window."""

    def __init__(
        self,
        earthquake_repository: EarthquakeRepository,
        hourly_report_repository: HourlyReportRepository,
        hourly_report_builder: HourlyReportBuilder,
    ) -> None:
        """Initialize the use case dependencies."""

        self._earthquake_repository = earthquake_repository
        self._hourly_report_repository = hourly_report_repository
        self._hourly_report_builder = hourly_report_builder

    async def execute(self, report_date: datetime | None = None) -> ReportGenerationResultDTO:
        """Generate the consolidated report for the provided or latest completed hour."""

        window_start = self._resolve_window_start(report_date)
        window_end = window_start + timedelta(hours=1)
        events = await self._earthquake_repository.get_by_time_range(
            start_inclusive=window_start,
            end_exclusive=window_end,
        )
        report = self._hourly_report_builder.build(
            report_date=window_start,
            events=events,
        )
        await self._hourly_report_repository.upsert(report)

        result = ReportGenerationResultDTO(
            report_date=report.report_date,
            total_events=report.total_events,
            average_magnitude=report.average_magnitude,
            max_magnitude=report.max_magnitude,
            top_locations=list(report.top_locations),
        )
        get_logger(
            report_date=result.report_date.isoformat(),
            total_events=result.total_events,
        ).info("hourly_report_generated")
        return result

    @staticmethod
    def _resolve_window_start(report_date: datetime | None) -> datetime:
        """Normalize the target report date to the start of its hour in UTC."""

        if report_date is None:
            current_utc = datetime.now(tz=UTC)
            completed_hour = current_utc.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            return completed_hour

        return report_date.replace(minute=0, second=0, microsecond=0)
