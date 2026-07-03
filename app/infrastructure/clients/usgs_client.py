"""USGS earthquake feed client implementation."""

from datetime import UTC, datetime
from typing import Any

import httpx
from pydantic import ValidationError

from app.application.dtos.earthquake import EarthquakeFeedItemDTO
from app.application.interfaces.earthquake_feed_client import EarthquakeFeedClient
from app.domain.exceptions.base import InfrastructureError
from app.infrastructure.config.settings import Settings
from app.infrastructure.logging.logger import get_logger


class UsgsEarthquakeFeedClient(EarthquakeFeedClient):
    """HTTP client implementation for the USGS earthquake feed."""

    def __init__(self, http_client: httpx.AsyncClient, settings: Settings) -> None:
        """Initialize the client with a shared async HTTP client."""

        self._http_client = http_client
        self._settings = settings

    async def fetch_latest_events(self) -> list[EarthquakeFeedItemDTO]:
        """Return the latest earthquake events from the configured USGS feed."""

        try:
            response = await self._http_client.get(self._settings.usgs_summary_path)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            raise InfrastructureError("Unable to retrieve earthquake feed from USGS.") from exc
        except ValueError as exc:
            raise InfrastructureError("USGS feed returned invalid JSON.") from exc

        features = payload.get("features", [])
        if not isinstance(features, list):
            raise InfrastructureError("USGS feed returned an invalid features payload.")

        events: list[EarthquakeFeedItemDTO] = []
        for feature in features:
            dto = self._parse_feature(feature)
            if dto is not None:
                events.append(dto)

        get_logger(processed_count=len(events)).info("usgs_feed_retrieved")
        return events

    async def fetch_events_since(self, since: datetime) -> list[EarthquakeFeedItemDTO]:
        """Return only the events that occurred after the provided timestamp."""

        latest_events = await self.fetch_latest_events()
        return [event for event in latest_events if event.event_time >= since]

    def _parse_feature(self, feature: Any) -> EarthquakeFeedItemDTO | None:
        """Convert a raw USGS feature into the normalized application DTO."""

        if not isinstance(feature, dict):
            get_logger(feature_type=type(feature).__name__).warning("usgs_feature_skipped_invalid_type")
            return None

        properties = feature.get("properties")
        geometry = feature.get("geometry")
        feature_id = feature.get("id")
        if not isinstance(properties, dict) or not isinstance(geometry, dict) or not isinstance(feature_id, str):
            get_logger(feature_id=feature_id).warning("usgs_feature_skipped_invalid_structure")
            return None

        coordinates = geometry.get("coordinates")
        if not isinstance(coordinates, list) or len(coordinates) < 3:
            get_logger(feature_id=feature_id).warning("usgs_feature_skipped_invalid_coordinates")
            return None

        event_timestamp_ms = properties.get("time")
        if not isinstance(event_timestamp_ms, (int, float)):
            get_logger(feature_id=feature_id).warning("usgs_feature_skipped_invalid_time")
            return None

        try:
            return EarthquakeFeedItemDTO(
                event_id=feature_id,
                magnitude=float(properties.get("mag", 0.0)),
                location=str(properties.get("place", "Unknown location")),
                longitude=float(coordinates[0]),
                latitude=float(coordinates[1]),
                depth_km=float(coordinates[2]),
                event_time=datetime.fromtimestamp(event_timestamp_ms / 1000, tz=UTC),
                source="usgs",
            )
        except (TypeError, ValueError, ValidationError) as exc:
            get_logger(feature_id=feature_id, error=str(exc)).warning("usgs_feature_skipped_parse_error")
            return None
