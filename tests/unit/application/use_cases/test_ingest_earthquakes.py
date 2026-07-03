"""Unit tests for the earthquake ingestion use case."""

from datetime import UTC, datetime

import pytest

from app.application.dtos.earthquake import EarthquakeFeedItemDTO
from app.application.use_cases.ingest_earthquakes import IngestEarthquakesUseCase
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.value_objects.coordinates import Coordinates


class FakeEarthquakeFeedClient:
    """Test double for the external earthquake feed client."""

    def __init__(self, items: list[EarthquakeFeedItemDTO]) -> None:
        """Initialize the client with predefined feed items."""

        self._items = items

    async def fetch_latest_events(self) -> list[EarthquakeFeedItemDTO]:
        """Return predefined feed items."""

        return self._items


class FakeEarthquakeRepository:
    """Test double for earthquake persistence."""

    def __init__(self, existing_events: list[EarthquakeEvent]) -> None:
        """Initialize repository state."""

        self._existing_events = existing_events
        self.saved_events: list[EarthquakeEvent] = []

    async def get_by_event_ids(self, event_ids: list[str]) -> list[EarthquakeEvent]:
        """Return only events already known by the repository."""

        return [event for event in self._existing_events if event.event_id in event_ids]

    async def save_new_events(self, events: list[EarthquakeEvent]) -> int:
        """Record newly saved events."""

        self.saved_events.extend(events)
        return len(events)


class FakeRefreshHourlyMetricsUseCase:
    """Test double for post-ingestion hourly metric refresh."""

    def __init__(self) -> None:
        """Initialize tracking state."""

        self.received_events: list[EarthquakeEvent] = []

    async def execute(self, events: list[EarthquakeEvent]) -> list[datetime]:
        """Track the refreshed events and return their affected windows."""

        self.received_events = list(events)
        return [
            event.event_time.replace(minute=0, second=0, microsecond=0)
            for event in events
        ]


def build_feed_item(*, event_id: str, magnitude: float, event_time: datetime) -> EarthquakeFeedItemDTO:
    """Build a normalized feed item DTO for ingestion tests."""

    return EarthquakeFeedItemDTO(
        event_id=event_id,
        magnitude=magnitude,
        location="Test Location",
        latitude=10.0,
        longitude=-70.0,
        depth_km=5.0,
        event_time=event_time,
    )


def build_existing_event(event_id: str) -> EarthquakeEvent:
    """Build an existing persisted earthquake event."""

    return EarthquakeEvent(
        event_id=event_id,
        magnitude=3.5,
        location="Persisted Location",
        coordinates=Coordinates(latitude=10.0, longitude=-70.0, depth_km=5.0),
        event_time=datetime(2026, 6, 17, 9, 30, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_execute_persists_only_new_events_and_refreshes_metrics() -> None:
    """Persist only unseen events and refresh metrics for their affected windows."""

    now = datetime(2026, 6, 17, 10, 15, tzinfo=UTC)
    feed_items = [
        build_feed_item(event_id="eq-1", magnitude=2.5, event_time=now),
        build_feed_item(event_id="eq-2", magnitude=5.0, event_time=now),
    ]
    repository = FakeEarthquakeRepository(existing_events=[build_existing_event("eq-1")])
    refresh_use_case = FakeRefreshHourlyMetricsUseCase()
    use_case = IngestEarthquakesUseCase(
        earthquake_feed_client=FakeEarthquakeFeedClient(feed_items),
        earthquake_repository=repository,
        refresh_hourly_metrics_use_case=refresh_use_case,
    )

    result = await use_case.execute()

    assert result.fetched_count == 2
    assert result.new_count == 1
    assert result.persisted_count == 1
    assert [event.event_id for event in repository.saved_events] == ["eq-2"]
    assert [event.event_id for event in refresh_use_case.received_events] == ["eq-2"]
    assert result.affected_windows == [datetime(2026, 6, 17, 10, 0, tzinfo=UTC)]


@pytest.mark.asyncio
async def test_execute_skips_metric_refresh_when_no_new_events_exist() -> None:
    """Avoid refreshing metrics when the ingestion cycle contains only duplicates."""

    now = datetime(2026, 6, 17, 10, 15, tzinfo=UTC)
    feed_items = [build_feed_item(event_id="eq-1", magnitude=2.5, event_time=now)]
    repository = FakeEarthquakeRepository(existing_events=[build_existing_event("eq-1")])
    refresh_use_case = FakeRefreshHourlyMetricsUseCase()
    use_case = IngestEarthquakesUseCase(
        earthquake_feed_client=FakeEarthquakeFeedClient(feed_items),
        earthquake_repository=repository,
        refresh_hourly_metrics_use_case=refresh_use_case,
    )

    result = await use_case.execute()

    assert result.new_count == 0
    assert result.persisted_count == 0
    assert repository.saved_events == []
    assert refresh_use_case.received_events == []
    assert result.affected_windows == []
