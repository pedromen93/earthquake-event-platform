"""MongoDB connection management using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.domain.exceptions.base import InfrastructureError
from app.infrastructure.config.settings import Settings


class MongoDatabase:
    """Manage MongoDB client lifecycle and database access."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the database manager with application settings."""

        self._settings = settings
        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Establish the MongoDB connection if it is not already open."""

        if self._client is not None and self._database is not None:
            return

        try:
            self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
            self._database = self._client[self._settings.mongodb_database]
            await self._client.admin.command("ping")
        except PyMongoError as exc:
            self._client = None
            self._database = None
            raise InfrastructureError("Unable to connect to MongoDB.") from exc

    async def disconnect(self) -> None:
        """Close the MongoDB client when the application stops."""

        if self._client is None:
            return

        self._client.close()
        self._client = None
        self._database = None

    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Return the initialized application database."""

        if self._database is None:
            raise RuntimeError("MongoDB connection has not been initialized.")
        return self._database
