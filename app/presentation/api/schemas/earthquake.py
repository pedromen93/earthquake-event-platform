"""HTTP schemas for earthquake endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.application.dtos.common import PaginatedResultDTO
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.presentation.api.schemas.common import PaginationMetadataResponse


class EarthquakeResponse(BaseModel):
    """HTTP schema for a normalized earthquake event."""

    event_id: str
    magnitude: float
    location: str
    latitude: float
    longitude: float
    depth_km: float
    event_time: datetime
    source: str

    @classmethod
    def from_domain(cls, event: EarthquakeEvent) -> "EarthquakeResponse":
        """Build an HTTP response model from a domain entity."""

        return cls(
            event_id=event.event_id,
            magnitude=event.magnitude,
            location=event.location,
            latitude=event.latitude,
            longitude=event.longitude,
            depth_km=event.depth_km,
            event_time=event.event_time,
            source=event.source,
        )


class EarthquakeListResponse(BaseModel):
    """Paginated HTTP response for earthquake listings."""

    items: list[EarthquakeResponse] = Field(default_factory=list)
    pagination: PaginationMetadataResponse

    @classmethod
    def from_result(
        cls,
        result: PaginatedResultDTO[EarthquakeEvent],
    ) -> "EarthquakeListResponse":
        """Build a paginated response from an application result DTO."""

        return cls(
            items=[EarthquakeResponse.from_domain(item) for item in result.items],
            pagination=PaginationMetadataResponse(
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages,
            ),
        )
