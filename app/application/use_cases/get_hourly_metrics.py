"""Application use case for querying hourly metrics."""

from app.application.dtos.common import PaginatedResultDTO
from app.application.dtos.metric import HourlyMetricQueryFiltersDTO
from app.application.interfaces.hourly_metric_repository import HourlyMetricRepository
from app.domain.entities.hourly_metric import HourlyMetric


class GetHourlyMetricsUseCase:
    """Retrieve paginated hourly metrics with filtering and sorting."""

    def __init__(self, hourly_metric_repository: HourlyMetricRepository) -> None:
        """Initialize the use case dependencies."""

        self._hourly_metric_repository = hourly_metric_repository

    async def execute(
        self,
        filters: HourlyMetricQueryFiltersDTO,
    ) -> PaginatedResultDTO[HourlyMetric]:
        """Return paginated hourly metrics matching the provided filters."""

        items = await self._hourly_metric_repository.list(filters)
        total = await self._hourly_metric_repository.count(filters)
        return PaginatedResultDTO[HourlyMetric](
            items=items,
            total=total,
            page=filters.pagination.page,
            page_size=filters.pagination.page_size,
        )
