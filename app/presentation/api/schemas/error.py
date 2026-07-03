"""HTTP error response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized HTTP error payload."""

    detail: str = Field(description="Human-readable error detail.")
    error_code: str = Field(description="Stable application error code.")
    request_id: str = Field(description="Request correlation identifier.")
    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional validation error details.",
    )
