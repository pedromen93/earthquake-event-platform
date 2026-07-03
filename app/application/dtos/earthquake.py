"""Application DTOs related to earthquake ingestion and queries."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.application.dtos.common import PaginationDTO, SortDTO


class EarthquakeFeedItemDTO(BaseModel):
    """Normalized DTO produced by the external earthquake feed client."""

    event_id: str = Field(min_length=1)
    magnitude: float
    location: str = Field(min_length=1)
    latitude: float
    longitude: float
    depth_km: float
    event_time: datetime
    source: str = Field(default="usgs", min_length=1)

    @field_validator("event_time")
    @classmethod
    def validate_event_time(cls, value: datetime) -> datetime:
        """Ensure the event timestamp is timezone-aware."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware.")
        return value


class EarthquakeQueryFiltersDTO(BaseModel):
    """Query filters for listing earthquake events."""

    min_magnitude: float | None = None
    max_magnitude: float | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location_contains: str | None = Field(default=None, min_length=1)
    pagination: PaginationDTO = Field(default_factory=PaginationDTO)
    sort: SortDTO = Field(default_factory=SortDTO)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_optional_datetimes(cls, value: datetime | None) -> datetime | None:
        """Ensure provided date filters are timezone-aware."""

        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Date filters must be timezone-aware.")
        return value
