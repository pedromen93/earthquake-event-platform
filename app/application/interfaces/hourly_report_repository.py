"""Application port for hourly report persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.application.dtos.report import HourlyReportQueryFiltersDTO
from app.domain.entities.hourly_report import HourlyReport


class HourlyReportRepository(ABC):
    """Abstract repository for hourly report persistence and queries."""

    @abstractmethod
    async def upsert(self, report: HourlyReport) -> None:
        """Create or replace the report for the provided reporting window."""

    @abstractmethod
    async def get_by_report_date(self, report_date: datetime) -> HourlyReport | None:
        """Return the report stored for the provided reporting window, if any."""

    @abstractmethod
    async def list(self, filters: HourlyReportQueryFiltersDTO) -> list[HourlyReport]:
        """Return hourly reports matching the provided filters."""

    @abstractmethod
    async def count(self, filters: HourlyReportQueryFiltersDTO) -> int:
        """Return the total amount of hourly reports matching the filters."""
