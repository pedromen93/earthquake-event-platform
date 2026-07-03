"""Health check response schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Basic health status payload."""

    status: str = Field(description="Application health status.")
    service: str = Field(description="Service name.")
    environment: str = Field(description="Current runtime environment.")
