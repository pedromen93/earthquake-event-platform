"""Application use case for querying hourly reports."""

from app.application.dtos.common import PaginatedResultDTO
from app.application.dtos.report import HourlyReportQueryFiltersDTO
from app.application.interfaces.hourly_report_repository import HourlyReportRepository
from app.domain.entities.hourly_report import HourlyReport


class GetHourlyReportsUseCase:
    """Retrieve paginated hourly reports with filtering and sorting."""

    def __init__(self, hourly_report_repository: HourlyReportRepository) -> None:
        """Initialize the use case dependencies."""

        self._hourly_report_repository = hourly_report_repository

    async def execute(
        self,
        filters: HourlyReportQueryFiltersDTO,
    ) -> PaginatedResultDTO[HourlyReport]:
        """Return paginated hourly reports matching the provided filters."""

        items = await self._hourly_report_repository.list(filters)
        total = await self._hourly_report_repository.count(filters)
        return PaginatedResultDTO[HourlyReport](
            items=items,
            total=total,
            page=filters.pagination.page,
            page_size=filters.pagination.page_size,
        )
