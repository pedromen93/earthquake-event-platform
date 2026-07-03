"""Domain-specific exceptions for earthquake processing."""

from app.domain.exceptions.base import DomainError


class InvalidCoordinatesError(DomainError):
    """Raised when earthquake coordinates are invalid."""


class InvalidEarthquakeEventError(DomainError):
    """Raised when an earthquake event violates domain invariants."""


class InvalidHourlyMetricError(DomainError):
    """Raised when an hourly metric violates domain invariants."""


class InvalidHourlyReportError(DomainError):
    """Raised when an hourly report violates domain invariants."""
