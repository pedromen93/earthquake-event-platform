"""Application use case for querying earthquake events."""

from app.application.dtos.common import PaginatedResultDTO
from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.domain.entities.earthquake_event import EarthquakeEvent


class GetEarthquakesUseCase:
    """Retrieve paginated earthquake events with filtering and sorting."""

    def __init__(self, earthquake_repository: EarthquakeRepository) -> None:
        """Initialize the use case dependencies."""

        self._earthquake_repository = earthquake_repository

    async def execute(
        self,
        filters: EarthquakeQueryFiltersDTO,
    ) -> PaginatedResultDTO[EarthquakeEvent]:
        """Return paginated earthquake events matching the provided filters."""

        items = await self._earthquake_repository.list(filters)
        total = await self._earthquake_repository.count(filters)
        return PaginatedResultDTO[EarthquakeEvent](
            items=items,
            total=total,
            page=filters.pagination.page,
            page_size=filters.pagination.page_size,
        )
