"""Mappers between application DTOs and domain entities."""

from app.application.dtos.earthquake import EarthquakeFeedItemDTO
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.domain.value_objects.coordinates import Coordinates


def map_feed_item_to_domain(dto: EarthquakeFeedItemDTO) -> EarthquakeEvent:
    """Map a normalized feed DTO into a domain entity."""

    return EarthquakeEvent(
        event_id=dto.event_id,
        magnitude=dto.magnitude,
        location=dto.location,
        coordinates=Coordinates(
            latitude=dto.latitude,
            longitude=dto.longitude,
            depth_km=dto.depth_km,
        ),
        event_time=dto.event_time,
        source=dto.source,
    )
