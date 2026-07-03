"""CLI entrypoint for the earthquake ingestion worker."""

import argparse
import asyncio

from app.infrastructure.logging.logger import get_logger
from app.workers.ingestion.worker import EarthquakeIngestionWorker
from app.workers.runtime import managed_container


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the ingestion worker."""

    parser = argparse.ArgumentParser(description="Run the earthquake ingestion worker.")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute a single ingestion cycle and exit.",
    )
    return parser


async def run(once: bool) -> None:
    """Run the ingestion worker in one-shot or periodic mode."""

    async with managed_container() as container:
        worker = EarthquakeIngestionWorker(
            ingest_earthquakes_use_case=container.ingest_earthquakes_use_case,
            interval_seconds=container.settings.ingestion_interval_seconds,
        )
        if once:
            await worker.run_once()
            return
        await worker.run_forever()


def main() -> None:
    """Parse arguments and execute the ingestion worker."""

    args = build_argument_parser().parse_args()
    try:
        asyncio.run(run(once=args.once))
    except KeyboardInterrupt:
        get_logger().info("ingestion_worker_interrupted")


if __name__ == "__main__":
    main()
