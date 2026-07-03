"""HTTP routes for hourly metric queries."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.application.dtos.common import PaginationDTO, SortDTO
from app.application.dtos.metric import HourlyMetricQueryFiltersDTO
from app.application.use_cases.get_hourly_metrics import GetHourlyMetricsUseCase
from app.presentation.api.dependencies.use_cases import get_hourly_metrics_use_case
from app.presentation.api.schemas.error import ErrorResponse
from app.presentation.api.schemas.metric import HourlyMetricListResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get(
    "",
    response_model=HourlyMetricListResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="List hourly metrics",
)
async def list_hourly_metrics(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="window_start"),
    sort_direction: str = Query(default="desc", pattern="^(asc|desc)$"),
    use_case: GetHourlyMetricsUseCase = Depends(get_hourly_metrics_use_case),
) -> HourlyMetricListResponse:
    """Return hourly metrics with filters, pagination and sorting."""

    filters = HourlyMetricQueryFiltersDTO(
        start_time=start_time,
        end_time=end_time,
        pagination=PaginationDTO(page=page, page_size=page_size),
        sort=SortDTO(field=sort_by, direction=sort_direction),
    )
    result = await use_case.execute(filters)
    return HourlyMetricListResponse.from_result(result)
