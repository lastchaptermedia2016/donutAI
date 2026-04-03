"""Task management tool for creating, listing, and updating tasks."""

import json
import logging
from typing import Optional

from ..memory.structured_db import StructuredDB, get_structured_db

logger = logging.getLogger(__name__)


class TaskTool:
    """Tool for task/to-do management."""

    def __init__(self, db: StructuredDB | None = None):
        self._db = db or get_structured_db()

    async def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        context_mode: str = "neutral",
    ) -> dict:
        """Create a new task.

        The LLM should extract priority and description from user message.
        """
        task = self._db.create_task(
            title=title,
            description=description,
            priority=priority,
            context_mode=context_mode,
        )
        logger.info(f"Task created: {task['id']} - {title}")
        return task

    async def list_tasks(
        self,
        context_mode: str = "all",
        show_completed: bool = False,
    ) -> list[dict]:
        """List tasks."""
        tasks = self._db.list_tasks(
            context_mode=context_mode,
            completed=False if not show_completed else None,
            limit=50,
        )
        return tasks

    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        return self._db.update_task(task_id, completed=True)

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return self._db.delete_task(task_id)

    async def get_task(self, task_id: str) -> dict | None:
        """Get a single task."""
        return self._db.get_task(task_id)


_tool: TaskTool | None = None


def get_task_tool() -> TaskTool:
    """Get task tool singleton."""
    global _tool
    if _tool is None:
        _tool = TaskTool()
    return _tool