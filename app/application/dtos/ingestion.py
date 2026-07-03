"""Application DTOs for ingestion workflows."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class IngestionResultDTO(BaseModel):
    """Summary of an earthquake ingestion execution."""

    fetched_count: int = Field(ge=0)
    new_count: int = Field(ge=0)
    persisted_count: int = Field(ge=0)
    affected_windows: list[datetime] = Field(default_factory=list)
    processed_at: datetime

    @field_validator("processed_at")
    @classmethod
    def validate_processed_at(cls, value: datetime) -> datetime:
        """Ensure the processing timestamp is timezone-aware."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("processed_at must be timezone-aware.")
        return value
