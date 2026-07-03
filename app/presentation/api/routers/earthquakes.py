"""HTTP routes for earthquake event queries."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.application.dtos.common import PaginationDTO, SortDTO
from app.application.dtos.earthquake import EarthquakeQueryFiltersDTO
from app.application.use_cases.get_earthquakes import GetEarthquakesUseCase
from app.presentation.api.dependencies.use_cases import get_earthquakes_use_case
from app.presentation.api.schemas.earthquake import EarthquakeListResponse
from app.presentation.api.schemas.error import ErrorResponse

router = APIRouter(prefix="/earthquakes", tags=["earthquakes"])


@router.get(
    "",
    response_model=EarthquakeListResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="List earthquake events",
)
async def list_earthquakes(
    min_magnitude: float | None = Query(default=None),
    max_magnitude: float | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    location_contains: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="event_time"),
    sort_direction: str = Query(default="desc", pattern="^(asc|desc)$"),
    use_case: GetEarthquakesUseCase = Depends(get_earthquakes_use_case),
) -> EarthquakeListResponse:
    """Return earthquake events with filters, pagination and sorting."""

    filters = EarthquakeQueryFiltersDTO(
        min_magnitude=min_magnitude,
        max_magnitude=max_magnitude,
        start_time=start_time,
        end_time=end_time,
        location_contains=location_contains,
        pagination=PaginationDTO(page=page, page_size=page_size),
        sort=SortDTO(field=sort_by, direction=sort_direction),
    )
    result = await use_case.execute(filters)
    return EarthquakeListResponse.from_result(result)
