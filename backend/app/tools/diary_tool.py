"""Diary/journal management tool."""

import logging
from ..memory.structured_db import StructuredDB, get_structured_db

logger = logging.getLogger(__name__)


class DiaryTool:
    """Tool for diary/journal management."""

    def __init__(self, db: StructuredDB | None = None):
        self._db = db or get_structured_db()

    async def create_entry(
        self,
        content: str,
        mood: str | None = None,
        context_mode: str = "neutral",
    ) -> dict:
        """Create a diary entry."""
        entry = self._db.create_diary_entry(
            content=content,
            mood=mood,
            context_mode=context_mode,
        )
        logger.info(f"Diary entry created: {entry['id']}")
        return entry

    async def get_entries(
        self,
        context_mode: str = "all",
        limit: int = 20,
    ) -> list[dict]:
        """Get diary entries."""
        return self._db.list_diary_entries(
            context_mode=context_mode,
            limit=limit,
        )

    async def get_entry(self, entry_id: str) -> dict | None:
        """Get a single diary entry."""
        return self._db.get_diary_entry(entry_id)

    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a diary entry."""
        return self._db.delete_diary_entry(entry_id)


_tool: DiaryTool | None = None


def get_diary_tool() -> DiaryTool:
    """Get diary tool singleton."""
    global _tool
    if _tool is None:
        _tool = DiaryTool()
    return _tool