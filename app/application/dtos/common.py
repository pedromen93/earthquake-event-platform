"""Reusable application-layer DTOs."""

from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class PaginationDTO(BaseModel):
    """Pagination configuration shared across query use cases."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def offset(self) -> int:
        """Compute the zero-based offset from pagination parameters."""

        return (self.page - 1) * self.page_size


class SortDTO(BaseModel):
    """Sorting configuration shared across query use cases."""

    field: str = Field(default="event_time", min_length=1)
    direction: str = Field(default="desc", pattern="^(asc|desc)$")


class PaginatedResultDTO(BaseModel, Generic[T]):
    """Reusable paginated result envelope for application use cases."""

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_pages(self) -> int:
        """Compute the total amount of pages for the current result set."""

        if self.total == 0:
            return 0
        return ceil(self.total / self.page_size)
