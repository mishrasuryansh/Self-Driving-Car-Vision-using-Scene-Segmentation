"""MongoDB Database Connection Lifecycle Manager.

Provides async Motor client initialization, ping verification, graceful connection cleanup,
automatic index creation, and FastAPI database dependency helpers.
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
        """Initialize Motor client, bind database, test ping connectivity, and create indexes."""
        uris_to_try = []
        if settings.MONGODB_URI:
            uris_to_try.append(settings.MONGODB_URI)
        if settings.MONGODB_URL and settings.MONGODB_URL not in uris_to_try:
            uris_to_try.append(settings.MONGODB_URL)

        # Fallback local URIs
        default_local = "mongodb://127.0.0.1:27017/self_driving_db"
        if default_local not in uris_to_try:
            uris_to_try.append(default_local)

        connected = False
        for uri in uris_to_try:
            logger.info("Attempting MongoDB connection to '%s'...", uri)
            try:
                client = AsyncIOMotorClient(
                    uri,
                    serverSelectionTimeoutMS=2000,
                )
                await client.admin.command("ping")
                db_name = settings.MONGO_INITDB_DATABASE or "self_driving_db"
                self.client = client
                self.db = client[db_name]
                connected = True
                logger.info("MongoDB ping successful! Active database: '%s'", db_name)
                await self._ensure_indexes()
                break
            except Exception as exc:
                logger.warning("MongoDB ping failed for '%s': %s", uri, exc)

        if not connected:
            logger.warning("All MongoDB connection attempts failed. Operating in fallback store mode.")

    async def _ensure_indexes(self) -> None:
        """Create database indexes for optimal collection performance (Phase 8)."""
        if self.db is None:
            return
        try:
            await self.db["users"].create_index("email", unique=True)
            await self.db["media"].create_index("user_id")
            await self.db["tasks"].create_index("user_id")
            await self.db["tasks"].create_index("media_id")
            logger.info("MongoDB collection indexes ('users.email', 'media.user_id', 'tasks.user_id', 'tasks.media_id') verified.")
        except Exception as exc:
            logger.warning("MongoDB index creation warning: %s", exc)

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
