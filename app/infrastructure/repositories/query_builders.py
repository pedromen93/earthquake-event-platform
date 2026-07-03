"""MongoDB query helpers for repository adapters."""

from typing import Any

from pymongo import ASCENDING, DESCENDING

from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.application.dtos.metric import HourlyMetricQueryFiltersDTO
from app.application.dtos.report import HourlyReportQueryFiltersDTO


def build_earthquake_query(filters: EarthquakeQueryFiltersDTO) -> dict[str, Any]:
    """Build a MongoDB query for earthquake listings."""

    query: dict[str, Any] = {}

    if filters.min_magnitude is not None or filters.max_magnitude is not None:
        magnitude_filter: dict[str, Any] = {}
        if filters.min_magnitude is not None:
            magnitude_filter["$gte"] = filters.min_magnitude
        if filters.max_magnitude is not None:
            magnitude_filter["$lte"] = filters.max_magnitude
        query["magnitude"] = magnitude_filter

    if filters.start_time is not None or filters.end_time is not None:
        time_filter: dict[str, Any] = {}
        if filters.start_time is not None:
            time_filter["$gte"] = filters.start_time
        if filters.end_time is not None:
            time_filter["$lte"] = filters.end_time
        query["event_time"] = time_filter

    if filters.location_contains is not None:
        query["location"] = {"$regex": filters.location_contains, "$options": "i"}

    return query


def build_earthquake_sort(filters: EarthquakeQueryFiltersDTO) -> list[tuple[str, int]]:
    """Build a validated MongoDB sort definition for earthquake listings."""

    allowed_fields = {"event_time", "magnitude", "location"}
    field = filters.sort.field if filters.sort.field in allowed_fields else "event_time"
    direction = ASCENDING if filters.sort.direction == "asc" else DESCENDING
    return [(field, direction)]


def build_hourly_metric_query(filters: HourlyMetricQueryFiltersDTO) -> dict[str, Any]:
    """Build a MongoDB query for hourly metric listings."""

    return _build_datetime_range_query(
        field_name="window_start",
        start_time=filters.start_time,
        end_time=filters.end_time,
    )


def build_hourly_metric_sort(filters: HourlyMetricQueryFiltersDTO) -> list[tuple[str, int]]:
    """Build a validated MongoDB sort definition for hourly metric listings."""

    allowed_fields = {"window_start", "earthquake_count", "average_magnitude", "max_magnitude"}
    field = filters.sort.field if filters.sort.field in allowed_fields else "window_start"
    direction = ASCENDING if filters.sort.direction == "asc" else DESCENDING
    return [(field, direction)]


def build_hourly_report_query(filters: HourlyReportQueryFiltersDTO) -> dict[str, Any]:
    """Build a MongoDB query for hourly report listings."""

    return _build_datetime_range_query(
        field_name="report_date",
        start_time=filters.start_time,
        end_time=filters.end_time,
    )


def build_hourly_report_sort(filters: HourlyReportQueryFiltersDTO) -> list[tuple[str, int]]:
    """Build a validated MongoDB sort definition for hourly report listings."""

    allowed_fields = {"report_date", "total_events", "average_magnitude", "max_magnitude"}
    field = filters.sort.field if filters.sort.field in allowed_fields else "report_date"
    direction = ASCENDING if filters.sort.direction == "asc" else DESCENDING
    return [(field, direction)]


def _build_datetime_range_query(
    field_name: str,
    start_time: Any,
    end_time: Any,
) -> dict[str, Any]:
    """Build a generic datetime range query for MongoDB."""

    if start_time is None and end_time is None:
        return {}

    time_filter: dict[str, Any] = {}
    if start_time is not None:
        time_filter["$gte"] = start_time
    if end_time is not None:
        time_filter["$lte"] = end_time
    return {field_name: time_filter}
