"""Mapping helpers between MongoDB documents and domain entities."""

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.entities.hourly_metric import HourlyMetric
from app.domain.entities.hourly_report import HourlyReport
from app.domain.value_objects.coordinates import Coordinates


def earthquake_to_document(event: EarthquakeEvent) -> dict[str, Any]:
    """Map an earthquake event domain entity into a MongoDB document."""

    return {
        "event_id": event.event_id,
        "magnitude": event.magnitude,
        "location": event.location,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "depth_km": event.depth_km,
        "event_time": event.event_time,
        "source": event.source,
    }


def document_to_earthquake(document: dict[str, Any]) -> EarthquakeEvent:
    """Map a MongoDB document into an earthquake event domain entity."""

    return EarthquakeEvent(
        event_id=str(document["event_id"]),
        magnitude=float(document["magnitude"]),
        location=str(document["location"]),
        coordinates=Coordinates(
            latitude=float(document["latitude"]),
            longitude=float(document["longitude"]),
            depth_km=float(document["depth_km"]),
        ),
        event_time=_as_datetime(document["event_time"]),
        source=str(document.get("source", "usgs")),
    )


def hourly_metric_to_document(metric: HourlyMetric) -> dict[str, Any]:
    """Map an hourly metric domain entity into a MongoDB document."""

    return {
        "window_start": metric.window_start,
        "earthquake_count": metric.earthquake_count,
        "average_magnitude": metric.average_magnitude,
        "max_magnitude": metric.max_magnitude,
        "magnitude_distribution": dict(metric.magnitude_distribution),
    }


def document_to_hourly_metric(document: dict[str, Any]) -> HourlyMetric:
    """Map a MongoDB document into an hourly metric domain entity."""

    return HourlyMetric(
        window_start=_as_datetime(document["window_start"]),
        earthquake_count=int(document["earthquake_count"]),
        average_magnitude=float(document["average_magnitude"]),
        max_magnitude=float(document["max_magnitude"]),
        magnitude_distribution=dict(document.get("magnitude_distribution", {})),
    )


def hourly_report_to_document(report: HourlyReport) -> dict[str, Any]:
    """Map an hourly report domain entity into a MongoDB document."""

    return {
        "report_date": report.report_date,
        "total_events": report.total_events,
        "average_magnitude": report.average_magnitude,
        "max_magnitude": report.max_magnitude,
        "top_locations": list(report.top_locations),
    }


def document_to_hourly_report(document: dict[str, Any]) -> HourlyReport:
    """Map a MongoDB document into an hourly report domain entity."""

    return HourlyReport(
        report_date=_as_datetime(document["report_date"]),
        total_events=int(document["total_events"]),
        average_magnitude=float(document["average_magnitude"]),
        max_magnitude=float(document["max_magnitude"]),
        top_locations=tuple(str(value) for value in document.get("top_locations", [])),
    )


def _as_datetime(value: Any) -> datetime:
    """Cast a MongoDB value into a datetime instance."""

    if not isinstance(value, datetime):
        raise TypeError("Expected datetime value from MongoDB document.")
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value
