"""In-memory Storage Fallbacks.

Provides thread-safe in-memory dictionary stores for offline execution
when MongoDB host is unreachable during local testing.
"""

from typing import Dict

_in_memory_users: Dict[str, dict] = {}
_in_memory_media: Dict[str, dict] = {}
_in_memory_tasks: Dict[str, dict] = {}
_in_memory_jobs: Dict[str, dict] = {}

__all__ = [
    "_in_memory_users",
    "_in_memory_media",
    "_in_memory_tasks",
    "_in_memory_jobs",
]
