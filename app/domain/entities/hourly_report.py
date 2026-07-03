"""Domain entity for consolidated hourly reports."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable

from app.domain.exceptions.earthquakes import InvalidHourlyReportError


@dataclass(frozen=True, slots=True)
class HourlyReport:
    """Represents a persisted reporting snapshot for a completed hourly window."""

    report_date: datetime
    total_events: int
    average_magnitude: float
    max_magnitude: float
    top_locations: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate the invariants of a reporting snapshot."""

        if self.report_date.tzinfo is None or self.report_date.utcoffset() is None:
            raise InvalidHourlyReportError("Report date must be timezone-aware.")
        if self.total_events < 0:
            raise InvalidHourlyReportError("Total events cannot be negative.")
        if not isfinite(self.average_magnitude):
            raise InvalidHourlyReportError("Average magnitude must be finite.")
        if not isfinite(self.max_magnitude):
            raise InvalidHourlyReportError("Max magnitude must be finite.")

        normalized_locations = self._normalize_locations(self.top_locations)
        object.__setattr__(self, "top_locations", normalized_locations)

    @staticmethod
    def _normalize_locations(locations: Iterable[str]) -> tuple[str, ...]:
        """Normalize reported top locations into an immutable tuple."""

        normalized_locations = tuple(location.strip() for location in locations if location.strip())
        return normalized_locations
