"""Common HTTP response schemas."""

from pydantic import BaseModel, Field


class PaginationMetadataResponse(BaseModel):
    """HTTP schema describing a paginated result set."""

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
