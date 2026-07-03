"""Unit tests for hourly metric aggregation."""

from datetime import UTC, datetime

from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.services.hourly_metrics_calculator import HourlyMetricsCalculator
from app.domain.value_objects.coordinates import Coordinates


def build_event(*, event_id: str, magnitude: float, event_time: datetime) -> EarthquakeEvent:
    """Build a domain earthquake event for tests."""

    return EarthquakeEvent(
        event_id=event_id,
        magnitude=magnitude,
        location="Test Location",
        coordinates=Coordinates(latitude=10.0, longitude=-70.0, depth_km=5.0),
        event_time=event_time,
    )


def test_calculate_returns_expected_aggregates_and_distribution() -> None:
    """Aggregate hourly metrics from multiple events and bucket magnitudes correctly."""

    calculator = HourlyMetricsCalculator()
    window_start = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)
    events = [
        build_event(event_id="eq-1", magnitude=1.5, event_time=window_start),
        build_event(event_id="eq-2", magnitude=2.0, event_time=window_start),
        build_event(event_id="eq-3", magnitude=4.5, event_time=window_start),
        build_event(event_id="eq-4", magnitude=6.1, event_time=window_start),
    ]

    result = calculator.calculate(window_start=window_start, events=events)

    assert result.window_start == window_start
    assert result.earthquake_count == 4
    assert result.average_magnitude == 3.525
    assert result.max_magnitude == 6.1
    assert result.magnitude_distribution == {
        "lt_2": 1,
        "2_to_4": 1,
        "4_to_6": 1,
        "gte_6": 1,
    }


def test_calculate_returns_zeroed_snapshot_for_empty_window() -> None:
    """Return a valid zeroed metric snapshot when no events exist for the window."""

    calculator = HourlyMetricsCalculator()
    window_start = datetime(2026, 6, 17, 11, 0, tzinfo=UTC)

    result = calculator.calculate(window_start=window_start, events=[])

    assert result.earthquake_count == 0
    assert result.average_magnitude == 0.0
    assert result.max_magnitude == 0.0
    assert result.magnitude_distribution == {
        "lt_2": 0,
        "2_to_4": 0,
        "4_to_6": 0,
        "gte_6": 0,
    }
