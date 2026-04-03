"""Calendar management tool with Google Calendar integration and local fallback."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from ..memory.structured_db import get_structured_db

logger = logging.getLogger(__name__)


class CalendarTool:
    """Tool for calendar management with Google Calendar API and local fallback.

    Supports:
    - Google Calendar API (when OAuth is configured)
    - Local SQLite fallback (when Google not configured)
    """

    def __init__(self):
        self._db = get_structured_db()
        self._google_configured = self._check_google_config()
        self._calendar_service = None

    def _check_google_config(self) -> bool:
        """Check if Google OAuth credentials are configured."""
        try:
            from ..config import get_settings
            settings = get_settings()
            return bool(settings.google_client_id and settings.google_client_secret)
        except Exception:
            return False

    async def list_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 10,
    ) -> list[dict]:
        """List calendar events within a date range."""
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=7)

        if self._google_configured:
            return await self._list_google_events(start_date, end_date, max_results)
        else:
            return await self._list_local_events(start_date, end_date, max_results)

    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: str = "",
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
    ) -> dict:
        """Create a new calendar event."""
        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        if self._google_configured:
            return await self._create_google_event(
                title, start_time, end_time, description, location, attendees
            )
        else:
            return await self._create_local_event(
                title, start_time, end_time, description, location, attendees
            )

    async def delete_event(self, event_id: str) -> dict:
        """Delete a calendar event."""
        if self._google_configured:
            return await self._delete_google_event(event_id)
        else:
            return await self._delete_local_event(event_id)

    async def get_availability(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Check availability/availability for booking."""
        events = await self.list_events(start_date, end_date)
        busy_slots = [
            {
                "start": e["start"].isoformat() if isinstance(e["start"], datetime) else e["start"],
                "end": e["end"].isoformat() if isinstance(e["end"], datetime) else e["end"],
                "title": e.get("title", "Busy"),
            }
            for e in events
        ]
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "busy_slots": busy_slots,
            "has_availability": len(busy_slots) < 20,  # Arbitrary threshold
        }

    # --- Google Calendar Implementation (stub - requires OAuth) ---

    async def _list_google_events(
        self, start: datetime, end: datetime, max_results: int
    ) -> list[dict]:
        """List events from Google Calendar."""
        # TODO: Implement Google Calendar API
        logger.warning("Google Calendar not yet implemented")
        return []

    async def _create_google_event(
        self, title, start, end, description, location, attendees
    ) -> dict:
        """Create event in Google Calendar."""
        # TODO: Implement Google Calendar API
        return {"id": "google_" + str(hash(title)), "status": "simulated"}

    async def _delete_google_event(self, event_id: str) -> dict:
        """Delete event from Google Calendar."""
        return {"deleted": True, "id": event_id}

    # --- Local SQLite Fallback Implementation ---

    async def _list_local_events(
        self, start: datetime, end: datetime, max_results: int
    ) -> list[dict]:
        """List events from local database."""
        db = self._db
        conn = db._get_connection()
        cursor = conn.execute(
            """SELECT id, title, description, start_time, end_time, 
                      location, attendees, context_mode, created_at
               FROM calendar_events
               WHERE start_time >= ? AND start_time <= ?
               ORDER BY start_time ASC
               LIMIT ?""",
            (start.isoformat(), end.isoformat(), max_results),
        )
        rows = cursor.fetchall()
        events = []
        for row in rows:
            events.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "start": row[3],
                "end": row[4],
                "location": row[5],
                "attendees": row[6].split(",") if row[6] else [],
                "context_mode": row[7],
                "created_at": row[8],
            })
        conn.close()
        return events

    async def _create_local_event(
        self, title, start, end, description, location, attendees
    ) -> dict:
        """Create event in local database."""
        db = self._db
        event_id = f"evt_{int(datetime.now().timestamp() * 1000)}"
        attendees_str = ",".join(attendees) if attendees else ""
        conn = db._get_connection()
        conn.execute(
            """INSERT INTO calendar_events 
               (id, title, description, start_time, end_time, location, attendees)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event_id, title, description, start.isoformat(), end.isoformat(),
             location, attendees_str),
        )
        conn.commit()
        conn.close()
        return {
            "id": event_id,
            "title": title,
            "status": "created",
            "message": "Event created successfully",
        }

    async def _delete_local_event(self, event_id: str) -> dict:
        """Delete event from local database."""
        db = self._db
        conn = db._get_connection()
        conn.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()
        return {"deleted": True, "id": event_id}


_tool: CalendarTool | None = None


def get_calendar_tool() -> CalendarTool:
    """Get calendar tool singleton."""
    global _tool
    if _tool is None:
        _tool = CalendarTool()
    return _tool