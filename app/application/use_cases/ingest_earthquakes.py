"""Application use case for ingesting earthquake events from the external feed."""

from datetime import UTC, datetime

from app.application.dtos.ingestion import IngestionResultDTO
from app.application.interfaces.earthquake_feed_client import EarthquakeFeedClient
from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.application.mappers.earthquake_mapper import map_feed_item_to_domain
from app.application.use_cases.refresh_hourly_metrics import RefreshHourlyMetricsUseCase
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.infrastructure.logging.logger import get_logger


class IngestEarthquakesUseCase:
    """Fetch, deduplicate, persist and post-process earthquake events."""

    def __init__(
        self,
        earthquake_feed_client: EarthquakeFeedClient,
        earthquake_repository: EarthquakeRepository,
        refresh_hourly_metrics_use_case: RefreshHourlyMetricsUseCase,
    ) -> None:
        """Initialize the use case dependencies."""

        self._earthquake_feed_client = earthquake_feed_client
        self._earthquake_repository = earthquake_repository
        self._refresh_hourly_metrics_use_case = refresh_hourly_metrics_use_case

    async def execute(self) -> IngestionResultDTO:
        """Run the earthquake ingestion workflow and return an execution summary."""

        feed_items = await self._earthquake_feed_client.fetch_latest_events()
        normalized_events = [map_feed_item_to_domain(feed_item) for feed_item in feed_items]
        new_events = await self._filter_new_events(normalized_events)
        persisted_count = await self._earthquake_repository.save_new_events(new_events)

        affected_windows = []
        if new_events:
            affected_windows = await self._refresh_hourly_metrics_use_case.execute(new_events)

        result = IngestionResultDTO(
            fetched_count=len(feed_items),
            new_count=len(new_events),
            persisted_count=persisted_count,
            affected_windows=affected_windows,
            processed_at=datetime.now(tz=UTC),
        )
        get_logger(
            fetched_count=result.fetched_count,
            new_count=result.new_count,
            persisted_count=result.persisted_count,
            affected_windows=len(result.affected_windows),
        ).info("earthquake_ingestion_completed")
        return result

    async def _filter_new_events(self, events: list[EarthquakeEvent]) -> list[EarthquakeEvent]:
        """Filter events that are not yet persisted in the repository."""

        if not events:
            return []

        existing_events = await self._earthquake_repository.get_by_event_ids(
            [event.event_id for event in events]
        )
        existing_event_ids = {event.event_id for event in existing_events}
        return [event for event in events if event.event_id not in existing_event_ids]
