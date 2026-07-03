"""MongoDB repository implementation for hourly reports."""

from __future__ import annotations

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection

from app.application.dtos.report import HourlyReportQueryFiltersDTO
from app.application.interfaces.hourly_report_repository import HourlyReportRepository
from app.domain.entities.hourly_report import HourlyReport
from app.infrastructure.config.settings import Settings
from app.infrastructure.database.mongodb import MongoDatabase
from app.infrastructure.repositories.mongo_mappers import (
    document_to_hourly_report,
    hourly_report_to_document,
)
from app.infrastructure.repositories.query_builders import (
    build_hourly_report_query,
    build_hourly_report_sort,
)


class MongoHourlyReportRepository(HourlyReportRepository):
    """MongoDB-backed repository for consolidated hourly reports."""

    def __init__(self, database: MongoDatabase, settings: Settings) -> None:
        """Initialize repository dependencies."""

        self._database = database
        self._settings = settings

    @property
    def _collection(self) -> AsyncIOMotorCollection:
        """Return the MongoDB collection for hourly reports."""

        return self._database.database[self._settings.mongodb_hourly_reports_collection]

    async def upsert(self, report: HourlyReport) -> None:
        """Create or replace the hourly report for the target date."""

        await self._collection.replace_one(
            {"report_date": report.report_date},
            hourly_report_to_document(report),
            upsert=True,
        )

    async def get_by_report_date(self, report_date: datetime) -> HourlyReport | None:
        """Return the stored report for the given date, if present."""

        document = await self._collection.find_one({"report_date": report_date})
        if document is None:
            return None
        return document_to_hourly_report(document)

    async def list(self, filters: HourlyReportQueryFiltersDTO) -> list[HourlyReport]:
        """Return hourly reports matching the provided filters."""

        cursor = (
            self._collection.find(build_hourly_report_query(filters))
            .sort(build_hourly_report_sort(filters))
            .skip(filters.pagination.offset)
            .limit(filters.pagination.page_size)
        )
        documents = await cursor.to_list(length=filters.pagination.page_size)
        return [document_to_hourly_report(document) for document in documents]

    async def count(self, filters: HourlyReportQueryFiltersDTO) -> int:
        """Return the total amount of hourly reports matching the filters."""

        return await self._collection.count_documents(build_hourly_report_query(filters))
