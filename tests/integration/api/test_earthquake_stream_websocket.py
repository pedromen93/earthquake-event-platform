"""Integration tests for the earthquake WebSocket stream."""

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from app.application.dtos.common import PaginatedResultDTO
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.value_objects.coordinates import Coordinates
from app.main import create_application


class FakeStreamingGetEarthquakesUseCase:
    """Test double for the earthquake query use case used by WebSocket streams."""

    async def execute(self, filters: Any) -> PaginatedResultDTO[EarthquakeEvent]:
        """Return a deterministic snapshot for new WebSocket clients."""

        event = EarthquakeEvent(
            event_id="eq-stream-100",
            magnitude=3.9,
            location="12 km SE of Test City",
            coordinates=Coordinates(latitude=10.5, longitude=-70.2, depth_km=8.4),
            event_time=datetime(2026, 7, 3, 12, 0, tzinfo=UTC),
        )
        return PaginatedResultDTO[EarthquakeEvent](
            items=[event],
            total=1,
            page=1,
            page_size=filters.pagination.page_size,
        )


@dataclass(slots=True)
class FakeContainer:
    """Minimal container required by the application factory for WebSocket tests."""

    settings: Any
    get_earthquakes_use_case: FakeStreamingGetEarthquakesUseCase
    get_hourly_metrics_use_case: Any
    get_hourly_reports_use_case: Any
    ingest_earthquakes_use_case: Any

    async def startup(self) -> None:
        """No-op startup for integration tests."""

    async def shutdown(self) -> None:
        """No-op shutdown for integration tests."""


def test_earthquake_stream_websocket_sends_connection_and_snapshot(monkeypatch: Any) -> None:
    """Expose a WebSocket stream with an initial earthquake snapshot."""

    fake_container = FakeContainer(
        settings=SimpleNamespace(
            app_name="Earthquake Event Platform",
            app_env="test",
            app_debug=False,
            api_v1_prefix="/api/v1",
            log_json=False,
            log_level="INFO",
        ),
        get_earthquakes_use_case=FakeStreamingGetEarthquakesUseCase(),
        get_hourly_metrics_use_case=SimpleNamespace(),
        get_hourly_reports_use_case=SimpleNamespace(),
        ingest_earthquakes_use_case=SimpleNamespace(),
    )
    monkeypatch.setattr("app.main.build_container", lambda: fake_container)

    app = create_application()
    client = TestClient(app)

    with client.websocket_connect("/api/v1/stream/earthquakes") as websocket:
        connection_event = websocket.receive_json()
        snapshot_event = websocket.receive_json()

    assert connection_event["type"] == "connection_established"
    assert connection_event["stream"] == "earthquakes"
    assert snapshot_event["type"] == "initial_snapshot"
    assert snapshot_event["count"] == 1
    assert snapshot_event["items"][0]["event_id"] == "eq-stream-100"
