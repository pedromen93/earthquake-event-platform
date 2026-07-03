"""Domain entity for earthquake events."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from app.domain.exceptions.earthquakes import InvalidEarthquakeEventError
from app.domain.value_objects.coordinates import Coordinates


@dataclass(frozen=True, slots=True)
class EarthquakeEvent:
    """Represents a normalized earthquake event from the external provider."""

    event_id: str
    magnitude: float
    location: str
    coordinates: Coordinates
    event_time: datetime
    source: str = "usgs"

    def __post_init__(self) -> None:
        """Validate the core invariants of the earthquake event."""

        if not self.event_id.strip():
            raise InvalidEarthquakeEventError("Event identifier cannot be empty.")
        if not self.location.strip():
            raise InvalidEarthquakeEventError("Event location cannot be empty.")
        if not self.source.strip():
            raise InvalidEarthquakeEventError("Event source cannot be empty.")
        if not isfinite(self.magnitude):
            raise InvalidEarthquakeEventError("Magnitude must be a finite numeric value.")
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise InvalidEarthquakeEventError("Event time must be timezone-aware.")

    @property
    def latitude(self) -> float:
        """Expose latitude as a convenience property for adapters."""

        return self.coordinates.latitude

    @property
    def longitude(self) -> float:
        """Expose longitude as a convenience property for adapters."""

        return self.coordinates.longitude

    @property
    def depth_km(self) -> float:
        """Expose depth as a convenience property for adapters."""

        return self.coordinates.depth_km
