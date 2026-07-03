"""Domain services for hourly report consolidation."""

from collections import Counter
from collections.abc import Sequence
from datetime import datetime

from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.entities.hourly_report import HourlyReport


class HourlyReportBuilder:
    """Build hourly consolidated reports from earthquake events."""

    def build(
        self,
        *,
        report_date: datetime,
        events: Sequence[EarthquakeEvent],
    ) -> HourlyReport:
        """Build the consolidated report for the provided hour."""

        magnitudes = [event.magnitude for event in events]
        total_events = len(magnitudes)
        average_magnitude = sum(magnitudes) / total_events if total_events > 0 else 0.0
        max_magnitude = max(magnitudes) if total_events > 0 else 0.0
        top_locations = self._resolve_top_locations(events)

        return HourlyReport(
            report_date=report_date,
            total_events=total_events,
            average_magnitude=round(average_magnitude, 4),
            max_magnitude=round(max_magnitude, 4),
            top_locations=top_locations,
        )

    def _resolve_top_locations(self, events: Sequence[EarthquakeEvent]) -> tuple[str, ...]:
        """Resolve the top three locations by event frequency."""

        location_counter = Counter(event.location for event in events)
        top_locations = tuple(location for location, _ in location_counter.most_common(3))
        return top_locations
