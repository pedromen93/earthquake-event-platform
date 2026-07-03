"""HTTP schemas for ingestion operations."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.application.dtos.ingestion import IngestionResultDTO


class IngestionExecutionResponse(BaseModel):
    """HTTP schema describing the outcome of an ingestion execution."""

    fetched_count: int = Field(ge=0)
    new_count: int = Field(ge=0)
    persisted_count: int = Field(ge=0)
    affected_windows: list[datetime] = Field(default_factory=list)
    processed_at: datetime

    @classmethod
    def from_result(cls, result: IngestionResultDTO) -> "IngestionExecutionResponse":
        """Build the HTTP response from the application DTO."""

        return cls(
            fetched_count=result.fetched_count,
            new_count=result.new_count,
            persisted_count=result.persisted_count,
            affected_windows=result.affected_windows,
            processed_at=result.processed_at,
        )
