"""Application port for earthquake persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Sequence

from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.domain.entities.earthquake_event import EarthquakeEvent


class EarthquakeRepository(ABC):
    """Abstract repository for earthquake event persistence and queries."""

    @abstractmethod
    async def save_new_events(self, events: Sequence[EarthquakeEvent]) -> int:
        """Persist only new earthquake events and return the inserted count."""

    @abstractmethod
    async def list(self, filters: EarthquakeQueryFiltersDTO) -> list[EarthquakeEvent]:
        """Return earthquake events matching the provided filters."""

    @abstractmethod
    async def count(self, filters: EarthquakeQueryFiltersDTO) -> int:
        """Return the total amount of earthquake events matching the filters."""

    @abstractmethod
    async def get_by_event_ids(self, event_ids: Sequence[str]) -> list[EarthquakeEvent]:
        """Return the events that match the provided external identifiers."""

    @abstractmethod
    async def get_by_time_range(
        self,
        start_inclusive: datetime,
        end_exclusive: datetime,
    ) -> list[EarthquakeEvent]:
        """Return earthquake events within the provided event time window."""
