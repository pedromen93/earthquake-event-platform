"""Unit tests for hourly report consolidation."""

from datetime import UTC, datetime

from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.services.hourly_report_builder import HourlyReportBuilder
from app.domain.value_objects.coordinates import Coordinates


def build_event(*, event_id: str, magnitude: float, location: str) -> EarthquakeEvent:
    """Build a domain earthquake event for report tests."""

    return EarthquakeEvent(
        event_id=event_id,
        magnitude=magnitude,
        location=location,
        coordinates=Coordinates(latitude=10.0, longitude=-70.0, depth_km=5.0),
        event_time=datetime(2026, 6, 17, 10, 15, tzinfo=UTC),
    )


def test_build_returns_consolidated_report_with_top_locations() -> None:
    """Build a report with correct totals, magnitudes and top locations."""

    builder = HourlyReportBuilder()
    report_date = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)
    events = [
        build_event(event_id="eq-1", magnitude=3.0, location="California"),
        build_event(event_id="eq-2", magnitude=4.0, location="California"),
        build_event(event_id="eq-3", magnitude=5.5, location="Alaska"),
        build_event(event_id="eq-4", magnitude=2.5, location="Chile"),
        build_event(event_id="eq-5", magnitude=6.0, location="Chile"),
    ]

    result = builder.build(report_date=report_date, events=events)

    assert result.report_date == report_date
    assert result.total_events == 5
    assert result.average_magnitude == 4.2
    assert result.max_magnitude == 6.0
    assert result.top_locations == ("California", "Chile", "Alaska")


def test_build_returns_empty_report_for_empty_hour() -> None:
    """Build a zeroed report when the target hour contains no events."""

    builder = HourlyReportBuilder()
    report_date = datetime(2026, 6, 17, 11, 0, tzinfo=UTC)

    result = builder.build(report_date=report_date, events=[])

    assert result.total_events == 0
    assert result.average_magnitude == 0.0
    assert result.max_magnitude == 0.0
    assert result.top_locations == ()
