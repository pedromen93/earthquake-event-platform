"""Smoke tests for earthquake API endpoints."""

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from app.application.dtos.common import PaginatedResultDTO
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.value_objects.coordinates import Coordinates
from app.main import create_application


class FakeGetEarthquakesUseCase:
    """Test double for earthquake query use case."""

    async def execute(self, filters: Any) -> PaginatedResultDTO[EarthquakeEvent]:
        """Return a deterministic paginated earthquake result."""

        assert filters.pagination.page == 1
        assert filters.pagination.page_size == 10
        assert filters.sort.field == "magnitude"
        assert filters.sort.direction == "asc"
        assert filters.location_contains == "california"

        event = EarthquakeEvent(
            event_id="eq-100",
            magnitude=4.2,
            location="20 km NW of California",
            coordinates=Coordinates(latitude=35.44, longitude=-120.12, depth_km=10.5),
            event_time=datetime(2026, 6, 17, 10, 30, tzinfo=UTC),
        )
        return PaginatedResultDTO[EarthquakeEvent](
            items=[event],
            total=1,
            page=1,
            page_size=10,
        )


@dataclass(slots=True)
class FakeContainer:
    """Minimal container required by the API application factory."""

    settings: Any
    get_earthquakes_use_case: FakeGetEarthquakesUseCase
    get_hourly_metrics_use_case: Any
    get_hourly_reports_use_case: Any

    async def startup(self) -> None:
        """No-op startup for API smoke tests."""

    async def shutdown(self) -> None:
        """No-op shutdown for API smoke tests."""


def test_list_earthquakes_returns_paginated_http_response(monkeypatch: Any) -> None:
    """Expose earthquake results through the HTTP contract without real infrastructure."""

    fake_container = FakeContainer(
        settings=SimpleNamespace(
            app_name="Earthquake Event Platform",
            app_env="test",
            app_debug=False,
            api_v1_prefix="/api/v1",
            log_json=False,
            log_level="INFO",
        ),
        get_earthquakes_use_case=FakeGetEarthquakesUseCase(),
        get_hourly_metrics_use_case=SimpleNamespace(),
        get_hourly_reports_use_case=SimpleNamespace(),
    )
    monkeypatch.setattr("app.main.build_container", lambda: fake_container)

    app = create_application()
    client = TestClient(app)

    response = client.get(
        "/api/v1/earthquakes",
        params={
            "page": 1,
            "page_size": 10,
            "sort_by": "magnitude",
            "sort_direction": "asc",
            "location_contains": "california",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pagination"] == {
        "total": 1,
        "page": 1,
        "page_size": 10,
        "total_pages": 1,
    }
    assert payload["items"][0]["event_id"] == "eq-100"
    assert payload["items"][0]["magnitude"] == 4.2
