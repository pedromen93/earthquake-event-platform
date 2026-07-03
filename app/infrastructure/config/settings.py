"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    app_name: str = Field(default="Earthquake Event Platform", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")
    mongodb_uri: str = Field(default="mongodb://mongodb:27017", alias="MONGODB_URI")
    mongodb_database: str = Field(default="earthquake_platform", alias="MONGODB_DATABASE")
    mongodb_earthquakes_collection: str = Field(
        default="earthquakes",
        alias="MONGODB_EARTHQUAKES_COLLECTION",
    )
    mongodb_hourly_metrics_collection: str = Field(
        default="hourly_metrics",
        alias="MONGODB_HOURLY_METRICS_COLLECTION",
    )
    mongodb_hourly_reports_collection: str = Field(
        default="hourly_reports",
        alias="MONGODB_HOURLY_REPORTS_COLLECTION",
    )
    usgs_base_url: str = Field(default="https://earthquake.usgs.gov", alias="USGS_BASE_URL")
    usgs_summary_path: str = Field(
        default="/earthquakes/feed/v1.0/summary/all_hour.geojson",
        alias="USGS_SUMMARY_PATH",
    )
    request_timeout_seconds: int = Field(default=10, alias="REQUEST_TIMEOUT_SECONDS")
    ingestion_interval_seconds: int = Field(default=180, alias="INGESTION_INTERVAL_SECONDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
