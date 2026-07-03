"""MongoDB repository implementation for hourly metrics."""

from __future__ import annotations

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection

from app.application.dtos.metric import HourlyMetricQueryFiltersDTO
from app.application.interfaces.hourly_metric_repository import HourlyMetricRepository
from app.domain.entities.hourly_metric import HourlyMetric
from app.infrastructure.config.settings import Settings
from app.infrastructure.database.mongodb import MongoDatabase
from app.infrastructure.repositories.mongo_mappers import (
    document_to_hourly_metric,
    hourly_metric_to_document,
)
from app.infrastructure.repositories.query_builders import (
    build_hourly_metric_query,
    build_hourly_metric_sort,
)


class MongoHourlyMetricRepository(HourlyMetricRepository):
    """MongoDB-backed repository for hourly metric snapshots."""

    def __init__(self, database: MongoDatabase, settings: Settings) -> None:
        """Initialize repository dependencies."""

        self._database = database
        self._settings = settings

    @property
    def _collection(self) -> AsyncIOMotorCollection:
        """Return the MongoDB collection for hourly metrics."""

        return self._database.database[self._settings.mongodb_hourly_metrics_collection]

    async def upsert(self, metric: HourlyMetric) -> None:
        """Create or replace the hourly metric for the target window."""

        await self._collection.replace_one(
            {"window_start": metric.window_start},
            hourly_metric_to_document(metric),
            upsert=True,
        )

    async def get_by_window_start(self, window_start: datetime) -> HourlyMetric | None:
        """Return the stored metric for the given window, if present."""

        document = await self._collection.find_one({"window_start": window_start})
        if document is None:
            return None
        return document_to_hourly_metric(document)

    async def list(self, filters: HourlyMetricQueryFiltersDTO) -> list[HourlyMetric]:
        """Return hourly metrics matching the provided filters."""

        cursor = (
            self._collection.find(build_hourly_metric_query(filters))
            .sort(build_hourly_metric_sort(filters))
            .skip(filters.pagination.offset)
            .limit(filters.pagination.page_size)
        )
        documents = await cursor.to_list(length=filters.pagination.page_size)
        return [document_to_hourly_metric(document) for document in documents]

    async def count(self, filters: HourlyMetricQueryFiltersDTO) -> int:
        """Return the total amount of hourly metrics matching the filters."""

        return await self._collection.count_documents(build_hourly_metric_query(filters))
