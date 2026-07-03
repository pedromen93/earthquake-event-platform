"""Application port for the external earthquake feed provider."""

from abc import ABC, abstractmethod
from datetime import datetime

from app.application.dtos.earthquake import EarthquakeFeedItemDTO


class EarthquakeFeedClient(ABC):
    """Abstract contract for fetching earthquake events from an external provider."""

    @abstractmethod
    async def fetch_latest_events(self) -> list[EarthquakeFeedItemDTO]:
        """Return the latest available earthquake events from the provider."""

    @abstractmethod
    async def fetch_events_since(self, since: datetime) -> list[EarthquakeFeedItemDTO]:
        """Return events updated after the provided timestamp when supported."""
