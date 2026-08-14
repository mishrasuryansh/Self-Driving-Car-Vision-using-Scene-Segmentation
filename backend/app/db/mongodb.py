"""MongoDB Database Connection Lifecycle Manager.

Provides async Motor client initialization, ping verification, graceful connection cleanup,
and FastAPI database dependency helpers matching Section 8.2 & 8.3 requirements.
"""

import logging
from typing import AsyncGenerator, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("app.db.mongodb")


class MongoDBManager:
    """Async MongoDB connection manager encapsulating client lifecycle and database handle."""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        """Initialize Motor client, bind database, and test ping connectivity."""
        logger.info("Initializing MongoDB connection to '%s'...", settings.MONGODB_URI)
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000,
            )
            self.db = self.client[settings.MONGO_INITDB_DATABASE]

            # Verify connection via admin ping command
            await self.client.admin.command("ping")
            logger.info("MongoDB connection ping successful! Active database: '%s'", settings.MONGO_INITDB_DATABASE)
        except Exception as exc:
            logger.warning("MongoDB ping failed or host unreachable (%s). Database manager operating in disconnected/fallback state.", exc)

    async def close(self) -> None:
        """Close Motor client connection on application shutdown."""
        if self.client is not None:
            logger.info("Closing MongoDB client connection...")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed cleanly.")

    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Return active Motor database handle."""
        return self.db


# Global singleton database manager instance
mongodb_manager = MongoDBManager()


async def get_db() -> AsyncGenerator[Optional[AsyncIOMotorDatabase], None]:
    """FastAPI dependency yielding active MongoDB database instance."""
    yield mongodb_manager.get_database()


__all__ = ["MongoDBManager", "mongodb_manager", "get_db"]
