"""CLI entrypoint for hourly report generation."""

import argparse
import asyncio
from datetime import datetime

from app.infrastructure.logging.logger import get_logger
from app.workers.reporting.runner import run_hourly_report_generation


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for hourly report generation."""

    parser = argparse.ArgumentParser(description="Generate hourly consolidated reports.")
    parser.add_argument(
        "--report-date",
        type=str,
        default=None,
        help="Target hour in ISO 8601 format. Example: 2026-06-17T10:00:00+00:00",
    )
    return parser


def parse_report_date(raw_value: str | None) -> datetime | None:
    """Parse an optional ISO 8601 datetime string."""

    if raw_value is None:
        return None
    return datetime.fromisoformat(raw_value)


async def run(report_date: datetime | None) -> None:
    """Run the hourly report generation workflow."""

    await run_hourly_report_generation(report_date=report_date)


def run_sync(report_date: datetime | None) -> None:
    """Run hourly report generation from synchronous callers such as Airflow."""

    asyncio.run(run(report_date=report_date))


def main() -> None:
    """Parse arguments and execute report generation."""

    args = build_argument_parser().parse_args()
    try:
        run_sync(report_date=parse_report_date(args.report_date))
    except KeyboardInterrupt:
        get_logger().info("hourly_report_generation_interrupted")


if __name__ == "__main__":
    main()
