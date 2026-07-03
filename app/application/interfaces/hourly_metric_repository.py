"""Application port for hourly metrics persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.application.dtos.metric import HourlyMetricQueryFiltersDTO
from app.domain.entities.hourly_metric import HourlyMetric


class HourlyMetricRepository(ABC):
    """Abstract repository for hourly metric persistence and queries."""

    @abstractmethod
    async def upsert(self, metric: HourlyMetric) -> None:
        """Create or replace the metric for the provided hourly window."""

    @abstractmethod
    async def get_by_window_start(self, window_start: datetime) -> HourlyMetric | None:
        """Return the metric stored for the provided window, if any."""

    @abstractmethod
    async def list(self, filters: HourlyMetricQueryFiltersDTO) -> list[HourlyMetric]:
        """Return hourly metrics matching the provided filters."""

    @abstractmethod
    async def count(self, filters: HourlyMetricQueryFiltersDTO) -> int:
        """Return the total amount of hourly metrics matching the filters."""
