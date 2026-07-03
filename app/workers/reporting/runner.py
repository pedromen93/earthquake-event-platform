"""Reusable runner for hourly reporting workflows."""

from datetime import datetime

from app.application.dtos.report_generation import ReportGenerationResultDTO
from app.infrastructure.logging.logger import get_logger
from app.workers.runtime import managed_container


async def run_hourly_report_generation(
    report_date: datetime | None = None,
) -> ReportGenerationResultDTO:
    """Run hourly report generation for the provided hour."""

    async with managed_container() as container:
        result = await container.generate_hourly_report_use_case.execute(report_date=report_date)
        get_logger(
            report_date=result.report_date.isoformat(),
            total_events=result.total_events,
        ).info("hourly_reporting_runner_completed")
        return result
