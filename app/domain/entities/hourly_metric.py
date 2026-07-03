"""Domain entity for aggregated hourly metrics."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Mapping

from app.domain.exceptions.earthquakes import InvalidHourlyMetricError


@dataclass(frozen=True, slots=True)
class HourlyMetric:
    """Represents an hourly aggregation of earthquake metrics."""

    window_start: datetime
    earthquake_count: int
    average_magnitude: float
    max_magnitude: float
    magnitude_distribution: Mapping[str, int]

    def __post_init__(self) -> None:
        """Validate the invariants of an hourly metric snapshot."""

        if self.window_start.tzinfo is None or self.window_start.utcoffset() is None:
            raise InvalidHourlyMetricError("Metric window start must be timezone-aware.")
        if self.earthquake_count < 0:
            raise InvalidHourlyMetricError("Earthquake count cannot be negative.")
        if not isfinite(self.average_magnitude):
            raise InvalidHourlyMetricError("Average magnitude must be finite.")
        if not isfinite(self.max_magnitude):
            raise InvalidHourlyMetricError("Max magnitude must be finite.")

        normalized_distribution = dict(self.magnitude_distribution)
        if any(value < 0 for value in normalized_distribution.values()):
            raise InvalidHourlyMetricError("Magnitude distribution cannot contain negative counts.")

        object.__setattr__(self, "magnitude_distribution", normalized_distribution)
