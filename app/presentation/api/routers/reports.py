"""HTTP routes for hourly report queries."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.application.dtos.common import PaginationDTO, SortDTO
from app.application.dtos.report import HourlyReportQueryFiltersDTO
from app.application.use_cases.get_hourly_reports import GetHourlyReportsUseCase
from app.presentation.api.dependencies.use_cases import get_hourly_reports_use_case
from app.presentation.api.schemas.error import ErrorResponse
from app.presentation.api.schemas.report import HourlyReportListResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "",
    response_model=HourlyReportListResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="List hourly reports",
)
async def list_hourly_reports(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="report_date"),
    sort_direction: str = Query(default="desc", pattern="^(asc|desc)$"),
    use_case: GetHourlyReportsUseCase = Depends(get_hourly_reports_use_case),
) -> HourlyReportListResponse:
    """Return hourly reports with filters, pagination and sorting."""

    filters = HourlyReportQueryFiltersDTO(
        start_time=start_time,
        end_time=end_time,
        pagination=PaginationDTO(page=page, page_size=page_size),
        sort=SortDTO(field=sort_by, direction=sort_direction),
    )
    result = await use_case.execute(filters)
    return HourlyReportListResponse.from_result(result)
