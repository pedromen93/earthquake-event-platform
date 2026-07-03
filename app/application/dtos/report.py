"""Application DTOs related to hourly report queries."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.application.dtos.common import PaginationDTO, SortDTO


class HourlyReportQueryFiltersDTO(BaseModel):
    """Query filters for retrieving consolidated hourly reports."""

    start_time: datetime | None = None
    end_time: datetime | None = None
    pagination: PaginationDTO = Field(default_factory=PaginationDTO)
    sort: SortDTO = Field(default_factory=lambda: SortDTO(field="report_date", direction="desc"))

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_optional_datetimes(cls, value: datetime | None) -> datetime | None:
        """Ensure provided date filters are timezone-aware."""

        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Date filters must be timezone-aware.")
        return value
