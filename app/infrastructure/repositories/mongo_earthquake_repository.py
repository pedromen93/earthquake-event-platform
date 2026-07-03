"""MongoDB repository implementation for earthquake events."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.application.interfaces.earthquake_repository import EarthquakeRepository
from app.domain.entities.earthquake_event import EarthquakeEvent
from app.infrastructure.config.settings import Settings
from app.infrastructure.database.mongodb import MongoDatabase
from app.infrastructure.repositories.mongo_mappers import (
    document_to_earthquake,
    earthquake_to_document,
)
from app.infrastructure.repositories.query_builders import (
    build_earthquake_query,
    build_earthquake_sort,
)


class MongoEarthquakeRepository(EarthquakeRepository):
    """MongoDB-backed repository for earthquake events."""

    def __init__(self, database: MongoDatabase, settings: Settings) -> None:
        """Initialize repository dependencies."""

        self._database = database
        self._settings = settings

    @property
    def _collection(self) -> AsyncIOMotorCollection:
        """Return the MongoDB collection for earthquake events."""

        return self._database.database[self._settings.mongodb_earthquakes_collection]

    async def save_new_events(self, events: Sequence[EarthquakeEvent]) -> int:
        """Persist only new events using upserts keyed by external event id."""

        if not events:
            return 0

        operations = [
            UpdateOne(
                {"event_id": event.event_id},
                {"$setOnInsert": earthquake_to_document(event)},
                upsert=True,
            )
            for event in events
        ]
        result = await self._collection.bulk_write(operations, ordered=False)
        return result.upserted_count

    async def list(self, filters: EarthquakeQueryFiltersDTO) -> list[EarthquakeEvent]:
        """Return earthquake events matching the provided filters."""

        cursor = (
            self._collection.find(build_earthquake_query(filters))
            .sort(build_earthquake_sort(filters))
            .skip(filters.pagination.offset)
            .limit(filters.pagination.page_size)
        )
        documents = await cursor.to_list(length=filters.pagination.page_size)
        return [document_to_earthquake(document) for document in documents]

    async def count(self, filters: EarthquakeQueryFiltersDTO) -> int:
        """Return the total amount of matching earthquake events."""

        return await self._collection.count_documents(build_earthquake_query(filters))

    async def get_by_event_ids(self, event_ids: Sequence[str]) -> list[EarthquakeEvent]:
        """Return earthquake events that match the given external identifiers."""

        if not event_ids:
            return []

        documents = await self._collection.find({"event_id": {"$in": list(event_ids)}}).to_list(length=None)
        return [document_to_earthquake(document) for document in documents]

    async def get_by_time_range(
        self,
        start_inclusive: datetime,
        end_exclusive: datetime,
    ) -> list[EarthquakeEvent]:
        """Return earthquake events within the requested event time window."""

        documents = await self._collection.find(
            {
                "event_time": {
                    "$gte": start_inclusive,
                    "$lt": end_exclusive,
                }
            }
        ).to_list(length=None)
        return [document_to_earthquake(document) for document in documents]
