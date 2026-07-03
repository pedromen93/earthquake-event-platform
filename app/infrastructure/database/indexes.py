"""MongoDB index bootstrap for application collections."""

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from app.domain.exceptions.base import InfrastructureError
from app.infrastructure.config.settings import Settings
from app.infrastructure.database.mongodb import MongoDatabase


async def ensure_indexes(database: MongoDatabase, settings: Settings) -> None:
    """Create the base indexes required by the application."""

    try:
        db = database.database

        earthquakes = db[settings.mongodb_earthquakes_collection]
        await earthquakes.create_index([("event_id", ASCENDING)], unique=True, name="uq_event_id")
        await earthquakes.create_index([("event_time", DESCENDING)], name="idx_event_time_desc")
        await earthquakes.create_index(
            [("event_time", DESCENDING), ("magnitude", DESCENDING)],
            name="idx_event_time_magnitude_desc",
        )
        await earthquakes.create_index([("location", ASCENDING)], name="idx_location")

        hourly_metrics = db[settings.mongodb_hourly_metrics_collection]
        await hourly_metrics.create_index(
            [("window_start", ASCENDING)],
            unique=True,
            name="uq_hourly_metric_window_start",
        )

        hourly_reports = db[settings.mongodb_hourly_reports_collection]
        await hourly_reports.create_index(
            [("report_date", ASCENDING)],
            unique=True,
            name="uq_hourly_report_date",
        )
    except PyMongoError as exc:
        raise InfrastructureError("Unable to create MongoDB indexes.") from exc
