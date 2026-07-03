"""HTTP and WebSocket schemas for streaming endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.presentation.api.schemas.earthquake import EarthquakeResponse


class WebSocketConnectionEvent(BaseModel):
    """Event emitted when a WebSocket connection is established."""

    type: str = "connection_established"
    stream: str
    poll_interval_seconds: float
    sent_at: datetime


class WebSocketHeartbeatEvent(BaseModel):
    """Heartbeat event emitted to keep WebSocket clients informed."""

    type: str = "heartbeat"
    stream: str
    sent_at: datetime


class EarthquakeStreamSnapshotEvent(BaseModel):
    """Initial snapshot sent to newly connected WebSocket clients."""

    type: str = "initial_snapshot"
    stream: str
    count: int = Field(ge=0)
    items: list[EarthquakeResponse] = Field(default_factory=list)
    sent_at: datetime


class EarthquakeStreamUpdateEvent(BaseModel):
    """Incremental updates emitted when new earthquakes are detected."""

    type: str = "earthquake_events"
    stream: str
    count: int = Field(ge=0)
    items: list[EarthquakeResponse] = Field(default_factory=list)
    sent_at: datetime
