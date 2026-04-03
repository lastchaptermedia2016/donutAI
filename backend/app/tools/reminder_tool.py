"""Reminder management tool with APScheduler integration."""

import logging
from datetime import datetime
from typing import Optional

from ..memory.structured_db import get_structured_db

logger = logging.getLogger(__name__)


class ReminderTool:
    """Tool for reminder management with APScheduler integration.

    Supports:
    - Create reminders with date/time triggers
    - List, activate/deactivate reminders
    - Recurring reminders (daily, weekly, monthly)
    """

    def __init__(self):
        self._db = get_structured_db()

    async def create_reminder(
        self,
        message: str,
        remind_at: datetime,
        repeat: str = "none",
        context_mode: str = "neutral",
    ) -> dict:
        """Create a new reminder.

        Args:
            message: Reminder text
            remind_at: When to trigger the reminder
            repeat: 'none', 'daily', 'weekly', or 'monthly'
            context_mode: Context for the reminder
        """
        reminder_id = f"rem_{int(datetime.now().timestamp() * 1000)}"
        db = self._db

        conn = db._get_connection()
        conn.execute(
            """INSERT INTO reminders 
               (id, message, remind_at, repeat_interval, active, context_mode)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (reminder_id, message, remind_at.isoformat(), repeat, True, context_mode),
        )
        conn.commit()
        conn.close()

        logger.info(f"Reminder created: {reminder_id} at {remind_at}")

        return {
            "id": reminder_id,
            "message": message,
            "remind_at": remind_at.isoformat(),
            "repeat": repeat,
            "active": True,
            "status": "created",
            "message_status": "Reminder scheduled",
        }

    async def list_reminders(
        self,
        context_mode: str = "all",
        show_inactive: bool = False,
    ) -> list[dict]:
        """List reminders with optional filtering."""
        db = self._db
        conn = db._get_connection()

        query = "SELECT id, message, remind_at, repeat_interval, active, context_mode, created_at FROM reminders WHERE 1=1"
        params = []

        if not show_inactive:
            query += " AND active = 1"
        if context_mode != "all":
            query += " AND context_mode = ?"
            params.append(context_mode)

        query += " ORDER BY remind_at ASC"

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        reminders = []
        for row in rows:
            reminders.append({
                "id": row[0],
                "message": row[1],
                "remind_at": row[2],
                "repeat": row[3],
                "active": bool(row[4]),
                "context_mode": row[5],
                "created_at": row[6],
            })

        return reminders

    async def update_reminder(
        self,
        reminder_id: str,
        message: Optional[str] = None,
        remind_at: Optional[datetime] = None,
        active: Optional[bool] = None,
        repeat: Optional[str] = None,
    ) -> dict:
        """Update an existing reminder."""
        db = self._db
        updates = []
        params = []

        if message is not None:
            updates.append("message = ?")
            params.append(message)
        if remind_at is not None:
            updates.append("remind_at = ?")
            params.append(remind_at.isoformat())
        if active is not None:
            updates.append("active = ?")
            params.append(1 if active else 0)
        if repeat is not None:
            updates.append("repeat_interval = ?")
            params.append(repeat)

        if not updates:
            return {"updated": False, "reason": "No fields to update"}

        params.append(reminder_id)
        query = f"UPDATE reminders SET {', '.join(updates)} WHERE id = ?"

        conn = db._get_connection()
        cursor = conn.execute(query, params)
        conn.commit()
        conn.close()

        return {
            "updated": cursor.rowcount > 0,
            "id": reminder_id,
        }

    async def delete_reminder(self, reminder_id: str) -> dict:
        """Delete a reminder."""
        db = self._db
        conn = db._get_connection()
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()
        return {"deleted": True, "id": reminder_id}

    async def toggle_reminder(self, reminder_id: str, active: bool) -> dict:
        """Activate or deactivate a reminder."""
        return await self.update_reminder(reminder_id, active=active)

    async def get_overdue_reminders(self) -> list[dict]:
        """Get reminders that have passed their trigger time."""
        now = datetime.now().isoformat()
        db = self._db
        conn = db._get_connection()
        cursor = conn.execute(
            "SELECT id, message, remind_at, repeat_interval, active, context_mode FROM reminders WHERE remind_at < ? AND active = 1",
            (now,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "message": row[1],
                "remind_at": row[2],
                "repeat": row[3],
                "active": bool(row[4]),
                "context_mode": row[5],
            }
            for row in rows
        ]


_tool: ReminderTool | None = None


def get_reminder_tool() -> ReminderTool:
    """Get reminder tool singleton."""
    global _tool
    if _tool is None:
        _tool = ReminderTool()
    return _tool