"""WebSocket routes for near real-time streaming updates."""

import asyncio
from datetime import UTC, datetime
from typing import cast

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.dtos.common import PaginationDTO, SortDTO
from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.application.use_cases.get_earthquakes import GetEarthquakesUseCase
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.infrastructure.containers.application_container import ApplicationContainer
from app.infrastructure.logging.logger import get_logger
from app.presentation.api.schemas.earthquake import EarthquakeResponse
from app.presentation.api.schemas.stream import (
    EarthquakeStreamSnapshotEvent,
    EarthquakeStreamUpdateEvent,
    WebSocketConnectionEvent,
    WebSocketHeartbeatEvent,
)

router = APIRouter(prefix="/stream", tags=["stream"])

_STREAM_NAME = "earthquakes"
_DEFAULT_POLL_INTERVAL_SECONDS = 3.0
_DEFAULT_PAGE_SIZE = 20
_HEARTBEAT_INTERVAL_SECONDS = 15.0


@router.websocket("/earthquakes")
async def stream_earthquakes(
    websocket: WebSocket,
    poll_interval_seconds: float = _DEFAULT_POLL_INTERVAL_SECONDS,
    page_size: int = _DEFAULT_PAGE_SIZE,
) -> None:
    """Stream newly detected earthquakes over WebSocket."""

    await websocket.accept()

    container = cast(ApplicationContainer, websocket.app.state.container)
    use_case = container.get_earthquakes_use_case
    poll_interval_seconds = _normalize_poll_interval_seconds(poll_interval_seconds)
    page_size = _normalize_page_size(page_size)

    get_logger(stream=_STREAM_NAME, page_size=page_size).info("websocket_stream_connected")

    last_seen_time: datetime | None = None
    seen_event_ids_at_cursor: set[str] = set()
    last_heartbeat_at = datetime.now(tz=UTC)

    try:
        await websocket.send_json(
            WebSocketConnectionEvent(
                stream=_STREAM_NAME,
                poll_interval_seconds=poll_interval_seconds,
                sent_at=datetime.now(tz=UTC),
            ).model_dump(mode="json")
        )

        snapshot = await _load_latest_events(use_case=use_case, page_size=page_size)
        if snapshot:
            last_seen_time = snapshot[-1].event_time
            seen_event_ids_at_cursor = {
                event.event_id for event in snapshot if event.event_time == last_seen_time
            }

        await websocket.send_json(
            EarthquakeStreamSnapshotEvent(
                stream=_STREAM_NAME,
                count=len(snapshot),
                items=[EarthquakeResponse.from_domain(event) for event in snapshot],
                sent_at=datetime.now(tz=UTC),
            ).model_dump(mode="json")
        )

        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=poll_interval_seconds)
            except TimeoutError:
                pass

            updates = await _load_updates(
                use_case=use_case,
                page_size=page_size,
                last_seen_time=last_seen_time,
                seen_event_ids_at_cursor=seen_event_ids_at_cursor,
            )
            if updates:
                last_seen_time, seen_event_ids_at_cursor = _advance_cursor(
                    updates=updates,
                    last_seen_time=last_seen_time,
                    seen_event_ids_at_cursor=seen_event_ids_at_cursor,
                )
                await websocket.send_json(
                    EarthquakeStreamUpdateEvent(
                        stream=_STREAM_NAME,
                        count=len(updates),
                        items=[EarthquakeResponse.from_domain(event) for event in updates],
                        sent_at=datetime.now(tz=UTC),
                    ).model_dump(mode="json")
                )
                get_logger(stream=_STREAM_NAME, event_count=len(updates)).info(
                    "websocket_stream_update_sent"
                )
                last_heartbeat_at = datetime.now(tz=UTC)
                continue

            now = datetime.now(tz=UTC)
            heartbeat_age = (now - last_heartbeat_at).total_seconds()
            if heartbeat_age >= _HEARTBEAT_INTERVAL_SECONDS:
                await websocket.send_json(
                    WebSocketHeartbeatEvent(
                        stream=_STREAM_NAME,
                        sent_at=now,
                    ).model_dump(mode="json")
                )
                last_heartbeat_at = now
    except WebSocketDisconnect:
        get_logger(stream=_STREAM_NAME).info("websocket_stream_disconnected")


def _normalize_poll_interval_seconds(value: float) -> float:
    """Clamp the polling interval to a safe range."""

    return min(max(value, 1.0), 30.0)


def _normalize_page_size(value: int) -> int:
    """Clamp the page size used for WebSocket snapshots and updates."""

    return min(max(value, 1), 100)


async def _load_latest_events(
    use_case: GetEarthquakesUseCase,
    page_size: int,
) -> list[EarthquakeEvent]:
    """Load the latest known earthquakes for the initial client snapshot."""

    result = await use_case.execute(
        EarthquakeQueryFiltersDTO(
            pagination=PaginationDTO(page=1, page_size=page_size),
            sort=SortDTO(field="event_time", direction="desc"),
        )
    )
    return list(reversed(result.items))


async def _load_updates(
    use_case: GetEarthquakesUseCase,
    page_size: int,
    last_seen_time: datetime | None,
    seen_event_ids_at_cursor: set[str],
) -> list[EarthquakeEvent]:
    """Load new earthquakes detected after the current WebSocket cursor."""

    filters = EarthquakeQueryFiltersDTO(
        start_time=last_seen_time,
        pagination=PaginationDTO(page=1, page_size=page_size),
        sort=SortDTO(field="event_time", direction="asc"),
    )
    result = await use_case.execute(filters)

    updates: list[EarthquakeEvent] = []
    for event in result.items:
        if last_seen_time is None or event.event_time > last_seen_time:
            updates.append(event)
            continue
        if event.event_time == last_seen_time and event.event_id not in seen_event_ids_at_cursor:
            updates.append(event)
    return updates


def _advance_cursor(
    updates: list[EarthquakeEvent],
    last_seen_time: datetime | None,
    seen_event_ids_at_cursor: set[str],
) -> tuple[datetime | None, set[str]]:
    """Move the in-memory cursor after sending WebSocket updates."""

    next_time = last_seen_time
    next_seen_ids = set(seen_event_ids_at_cursor)

    for event in updates:
        if next_time is None or event.event_time > next_time:
            next_time = event.event_time
            next_seen_ids = {event.event_id}
        elif event.event_time == next_time:
            next_seen_ids.add(event.event_id)

    return next_time, next_seen_ids
