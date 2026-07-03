"""Value objects related to earthquake geospatial data."""

from dataclasses import dataclass
from math import isfinite

from app.domain.exceptions.earthquakes import InvalidCoordinatesError


@dataclass(frozen=True, slots=True)
class Coordinates:
    """Represents the immutable geospatial coordinates of an earthquake event."""

    latitude: float
    longitude: float
    depth_km: float

    def __post_init__(self) -> None:
        """Validate coordinate invariants."""

        if not isfinite(self.latitude) or not -90.0 <= self.latitude <= 90.0:
            raise InvalidCoordinatesError("Latitude must be a finite value between -90 and 90.")
        if not isfinite(self.longitude) or not -180.0 <= self.longitude <= 180.0:
            raise InvalidCoordinatesError("Longitude must be a finite value between -180 and 180.")
        if not isfinite(self.depth_km):
            raise InvalidCoordinatesError("Depth must be a finite numeric value.")
