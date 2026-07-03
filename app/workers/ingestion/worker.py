"""Periodic worker for earthquake ingestion."""

import asyncio

from app.application.dtos.ingestion import IngestionResultDTO
from app.application.use_cases.ingest_earthquakes import IngestEarthquakesUseCase
from app.domain.exceptions.base import ApplicationError
from app.infrastructure.logging.logger import get_logger


class EarthquakeIngestionWorker:
    """Run earthquake ingestion either once or on a fixed interval."""

    def __init__(
        self,
        ingest_earthquakes_use_case: IngestEarthquakesUseCase,
        interval_seconds: int,
    ) -> None:
        """Initialize the worker dependencies."""

        self._ingest_earthquakes_use_case = ingest_earthquakes_use_case
        self._interval_seconds = interval_seconds

    async def run_once(self) -> IngestionResultDTO:
        """Execute a single ingestion cycle."""

        get_logger(interval_seconds=self._interval_seconds).info("ingestion_worker_cycle_started")
        result = await self._ingest_earthquakes_use_case.execute()
        get_logger(
            fetched_count=result.fetched_count,
            new_count=result.new_count,
            persisted_count=result.persisted_count,
            affected_windows=len(result.affected_windows),
        ).info("ingestion_worker_cycle_finished")
        return result

    async def run_forever(self) -> None:
        """Execute ingestion on a fixed interval until the process stops."""

        get_logger(interval_seconds=self._interval_seconds).info("ingestion_worker_started")
        while True:
            try:
                await self.run_once()
            except ApplicationError as exc:
                get_logger(error=str(exc)).warning("ingestion_worker_cycle_failed")
            await asyncio.sleep(self._interval_seconds)
