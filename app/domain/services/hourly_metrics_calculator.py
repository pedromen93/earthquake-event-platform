"""Domain services for hourly metric aggregation."""

from collections import Counter
from collections.abc import Sequence
from datetime import datetime

from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.entities.hourly_metric import HourlyMetric


class HourlyMetricsCalculator:
    """Compute hourly metric snapshots from earthquake events."""

    _DISTRIBUTION_BUCKETS: tuple[tuple[str, float, float | None], ...] = (
        ("lt_2", float("-inf"), 2.0),
        ("2_to_4", 2.0, 4.0),
        ("4_to_6", 4.0, 6.0),
        ("gte_6", 6.0, None),
    )

    def calculate(
        self,
        *,
        window_start: datetime,
        events: Sequence[EarthquakeEvent],
    ) -> HourlyMetric:
        """Calculate the hourly metric snapshot for the provided events."""

        magnitudes = [event.magnitude for event in events]
        count = len(magnitudes)
        average_magnitude = sum(magnitudes) / count if count > 0 else 0.0
        max_magnitude = max(magnitudes) if count > 0 else 0.0
        distribution = self._build_distribution(magnitudes)

        return HourlyMetric(
            window_start=window_start,
            earthquake_count=count,
            average_magnitude=round(average_magnitude, 4),
            max_magnitude=round(max_magnitude, 4),
            magnitude_distribution=distribution,
        )

    def _build_distribution(self, magnitudes: Sequence[float]) -> dict[str, int]:
        """Build magnitude buckets for the provided event magnitudes."""

        counter = Counter({bucket_name: 0 for bucket_name, _, _ in self._DISTRIBUTION_BUCKETS})

        for magnitude in magnitudes:
            bucket_name = self._resolve_bucket(magnitude)
            counter[bucket_name] += 1

        return dict(counter)

    def _resolve_bucket(self, magnitude: float) -> str:
        """Resolve the configured magnitude bucket for the provided value."""

        for bucket_name, lower_bound, upper_bound in self._DISTRIBUTION_BUCKETS:
            if upper_bound is None and magnitude >= lower_bound:
                return bucket_name
            if lower_bound <= magnitude < upper_bound:
                return bucket_name

        return "lt_2"
