"""HTTP schemas for hourly metric endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.application.dtos.common import PaginatedResultDTO
from app.domain.entities.hourly_metric import HourlyMetric
from app.presentation.api.schemas.common import PaginationMetadataResponse


class HourlyMetricResponse(BaseModel):
    """HTTP schema for an hourly metric snapshot."""

    window_start: datetime
    earthquake_count: int
    average_magnitude: float
    max_magnitude: float
    magnitude_distribution: dict[str, int]

    @classmethod
    def from_domain(cls, metric: HourlyMetric) -> "HourlyMetricResponse":
        """Build an HTTP response model from a domain entity."""

        return cls(
            window_start=metric.window_start,
            earthquake_count=metric.earthquake_count,
            average_magnitude=metric.average_magnitude,
            max_magnitude=metric.max_magnitude,
            magnitude_distribution=dict(metric.magnitude_distribution),
        )


class HourlyMetricListResponse(BaseModel):
    """Paginated HTTP response for hourly metric listings."""

    items: list[HourlyMetricResponse] = Field(default_factory=list)
    pagination: PaginationMetadataResponse

    @classmethod
    def from_result(
        cls,
        result: PaginatedResultDTO[HourlyMetric],
    ) -> "HourlyMetricListResponse":
        """Build a paginated response from an application result DTO."""

        return cls(
            items=[HourlyMetricResponse.from_domain(item) for item in result.items],
            pagination=PaginationMetadataResponse(
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages,
            ),
        )
