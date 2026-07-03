"""HTTP routes for operational actions such as manual ingestion."""

from fastapi import APIRouter, Depends, status

from app.application.use_cases.ingest_earthquakes import IngestEarthquakesUseCase
from app.presentation.api.dependencies.use_cases import get_ingest_earthquakes_use_case
from app.presentation.api.schemas.error import ErrorResponse
from app.presentation.api.schemas.ingestion import IngestionExecutionResponse

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post(
    "/ingestions/run",
    response_model=IngestionExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Run ingestion manually",
)
async def run_ingestion(
    use_case: IngestEarthquakesUseCase = Depends(get_ingest_earthquakes_use_case),
) -> IngestionExecutionResponse:
    """Trigger an on-demand ingestion cycle through the API."""

    result = await use_case.execute()
    return IngestionExecutionResponse.from_result(result)
