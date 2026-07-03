"""Application use case for recalculating hourly metrics."""

from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta

from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.application.interfaces.hourly_metric_repository import HourlyMetricRepository
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.services.hourly_metrics_calculator import HourlyMetricsCalculator


class RefreshHourlyMetricsUseCase:
    """Rebuild hourly metric snapshots for affected time windows."""

    def __init__(
        self,
        earthquake_repository: EarthquakeRepository,
        hourly_metric_repository: HourlyMetricRepository,
        hourly_metrics_calculator: HourlyMetricsCalculator,
    ) -> None:
        """Initialize the use case dependencies."""

        self._earthquake_repository = earthquake_repository
        self._hourly_metric_repository = hourly_metric_repository
        self._hourly_metrics_calculator = hourly_metrics_calculator

    async def execute(self, events: Sequence[EarthquakeEvent]) -> list[datetime]:
        """Refresh hourly metrics for the windows touched by the provided events."""

        window_starts = self._extract_window_starts(events)
        return await self.execute_for_window_starts(window_starts)

    async def execute_for_window_starts(
        self,
        window_starts: Iterable[datetime],
    ) -> list[datetime]:
        """Refresh hourly metrics for the provided hourly windows."""

        refreshed_windows: list[datetime] = []
        for window_start in sorted(set(window_starts)):
            window_end = window_start + timedelta(hours=1)
            events_in_window = await self._earthquake_repository.get_by_time_range(
                start_inclusive=window_start,
                end_exclusive=window_end,
            )
            metric = self._hourly_metrics_calculator.calculate(
                window_start=window_start,
                events=events_in_window,
            )
            await self._hourly_metric_repository.upsert(metric)
            refreshed_windows.append(window_start)

        return refreshed_windows

    @staticmethod
    def _extract_window_starts(events: Sequence[EarthquakeEvent]) -> set[datetime]:
        """Extract unique hourly windows from the provided earthquake events."""

        return {
            event.event_time.replace(minute=0, second=0, microsecond=0)
            for event in events
        }
