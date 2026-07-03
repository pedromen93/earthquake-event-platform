"""HTTP schemas for hourly report endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.application.dtos.common import PaginatedResultDTO
from app.domain.entities.hourly_report import HourlyReport
from app.presentation.api.schemas.common import PaginationMetadataResponse


class HourlyReportResponse(BaseModel):
    """HTTP schema for a consolidated hourly report."""

    report_date: datetime
    total_events: int
    average_magnitude: float
    max_magnitude: float
    top_locations: list[str]

    @classmethod
    def from_domain(cls, report: HourlyReport) -> "HourlyReportResponse":
        """Build an HTTP response model from a domain entity."""

        return cls(
            report_date=report.report_date,
            total_events=report.total_events,
            average_magnitude=report.average_magnitude,
            max_magnitude=report.max_magnitude,
            top_locations=list(report.top_locations),
        )


class HourlyReportListResponse(BaseModel):
    """Paginated HTTP response for hourly report listings."""

    items: list[HourlyReportResponse] = Field(default_factory=list)
    pagination: PaginationMetadataResponse

    @classmethod
    def from_result(
        cls,
        result: PaginatedResultDTO[HourlyReport],
    ) -> "HourlyReportListResponse":
        """Build a paginated response from an application result DTO."""

        return cls(
            items=[HourlyReportResponse.from_domain(item) for item in result.items],
            pagination=PaginationMetadataResponse(
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages,
            ),
        )
