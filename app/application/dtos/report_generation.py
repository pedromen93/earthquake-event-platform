"""Application DTOs for report generation workflows."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ReportGenerationResultDTO(BaseModel):
    """Summary of an hourly report generation execution."""

    report_date: datetime
    total_events: int = Field(ge=0)
    average_magnitude: float
    max_magnitude: float
    top_locations: list[str] = Field(default_factory=list)

    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, value: datetime) -> datetime:
        """Ensure the report date is timezone-aware."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("report_date must be timezone-aware.")
        return value
