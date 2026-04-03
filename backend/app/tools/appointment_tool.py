"""Appointment booking tool for AI receptionist.</

Provides client-facing appointment scheduling with:
- Available slot management
- Booking with conflict detection
- Cancellation and rescheduling
- Integration with calendar tool for double-booking prevention
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from ..memory.structured_db import get_structured_db

logger = logging.getLogger(__name__)


# Default working hours for appointment booking
DEFAULT_WORKING_HOURS = {
    "start_hour": 9,
    "end_hour": 17,
    "slot_duration_minutes": 30,
    "timezone": "UTC",
}


class AppointmentTool:
    """Tool for appointment booking management.

    Handles:
    - Getting available appointment slots
    - Booking appointments with conflict checking
    - Cancelling and rescheduling
    - Listing upcoming appointments
    """

    def __init__(self):
        self._db = get_structured_db()
        self._working_hours = DEFAULT_WORKING_HOURS

    def set_working_hours(
        self,
        start_hour: int = 9,
        end_hour: int = 17,
        slot_duration: int = 30,
    ) -> None:
        """Configure working hours for appointment booking."""
        self._working_hours = {
            "start_hour": start_hour,
            "end_hour": end_hour,
            "slot_duration_minutes": slot_duration,
        }

    async def get_available_slots(
        self,
        date: datetime,
        exclude_booked: bool = True,
    ) -> list[dict]:
        """Get available appointment slots for a given date.

        Args:
            date: The date to check for availability
            exclude_booked: Whether to exclude already-booked slots

        Returns:
            List of available time slots
        """
        start_hour = self._working_hours["start_hour"]
        end_hour = self._working_hours["end_hour"]
        slot_duration = self._working_hours["slot_duration_minutes"]

        slots = []
        current = datetime(
            date.year, date.month, date.day, start_hour, 0
        )
        end = datetime(date.year, date.month, date.day, end_hour, 0)

        while current < end:
            slot_end = current + timedelta(minutes=slot_duration)
            slots.append({
                "start": current.isoformat(),
                "end": slot_end.isoformat(),
                "available": True,
            })
            current = slot_end

        if exclude_booked:
            booked = await self._get_booked_slots(date)
            slot_keys = {s["start"] for s in slots}
            booked_keys = {b["start"] for b in booked}
            slots = [s for s in slots if s["start"] not in booked_keys]

        return slots

    async def book_appointment(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        client_name: str = "",
        client_contact: str = "",
        appointment_type: str = "general",
        notes: str = "",
    ) -> dict:
        """Book a new appointment.

        Args:
            start_time: Appointment start time
            end_time: Appointment end time (auto-calculated if not provided)
            client_name: Client's name
            client_contact: Client's contact info (email/phone)
            appointment_type: Type/purpose of appointment
            notes: Additional notes

        Returns:
            Booking confirmation with details
        """
        if end_time is None:
            end_time = start_time + timedelta(minutes=self._working_hours["slot_duration_minutes"])

        # Check for conflicts
        if not await self._is_slot_available(start_time, end_time):
            return {
                "status": "conflict",
                "message": "The requested time slot is not available",
            }

        # Validate working hours
        if not self._is_within_working_hours(start_time, end_time):
            return {
                "status": "outside_hours",
                "message": "The requested time is outside working hours",
            }

        appointment_id = f"appt_{int(datetime.now().timestamp() * 1000)}"
        db = self._db

        conn = db._get_connection()
        conn.execute(
            """INSERT INTO appointments 
               (id, client_name, client_contact, start_time, end_time, 
                appointment_type, notes, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (appointment_id, client_name, client_contact, start_time.isoformat(),
             end_time.isoformat(), appointment_type, notes, "confirmed"),
        )
        conn.commit()
        conn.close()

        logger.info(
            f"Appointment booked: {appointment_id} for {client_name} at {start_time}"
        )

        return {
            "id": appointment_id,
            "status": "confirmed",
            "client_name": client_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "appointment_type": appointment_type,
            "message": f"Appointment confirmed for {client_name}",
        }

    async def list_appointments(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: str = "all",
    ) -> list[dict]:
        """List upcoming appointments.

        Args:
            start_date: Filter from date (default: now)
            end_date: Filter to date
            status: Filter by status ('all', 'confirmed', 'cancelled', 'completed')
        """
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)

        db = self._db
        conn = db._get_connection()

        query = """SELECT id, client_name, client_contact, start_time, end_time,
                          appointment_type, notes, status, created_at
                   FROM appointments 
                   WHERE start_time >= ? AND start_time <= ?"""
        params = [start_date.isoformat(), end_date.isoformat()]

        if status != "all":
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY start_time ASC"

        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        appointments = []
        for row in rows:
            appointments.append({
                "id": row[0],
                "client_name": row[1],
                "client_contact": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "appointment_type": row[5],
                "notes": row[6],
                "status": row[7],
                "created_at": row[8],
            })

        return appointments

    async def cancel_appointment(
        self,
        appointment_id: str,
        reason: str = "",
    ) -> dict:
        """Cancel an appointment.

        Args:
            appointment_id: The appointment to cancel
            reason: Optional cancellation reason
        """
        db = self._db
        conn = db._get_connection()
        cursor = conn.execute(
            "UPDATE appointments SET status = 'cancelled', notes = ? WHERE id = ? AND status != 'cancelled'",
            (reason, appointment_id),
        )
        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            logger.info(f"Appointment cancelled: {appointment_id}")
            return {"cancelled": True, "id": appointment_id}
        return {"cancelled": False, "reason": "Appointment not found or already cancelled"}

    async def reschedule_appointment(
        self,
        appointment_id: str,
        new_start_time: datetime,
        new_end_time: Optional[datetime] = None,
    ) -> dict:
        """Reschedule an appointment to a new time.

        Args:
            appointment_id: The appointment to reschedule
            new_start_time: New start time
            new_end_time: New end time (auto-calculated if not provided)
        """
        if new_end_time is None:
            new_end_time = new_start_time + timedelta(
                minutes=self._working_hours["slot_duration_minutes"]
            )

        # Check for conflicts (exclude current appointment)
        if not await self._is_slot_available(new_start_time, new_end_time, exclude_id=appointment_id):
            return {
                "status": "conflict",
                "message": "The requested time slot is not available",
            }

        db = self._db
        conn = db._get_connection()
        cursor = conn.execute(
            "UPDATE appointments SET start_time = ?, end_time = ? WHERE id = ? AND status != 'cancelled'",
            (new_start_time.isoformat(), new_end_time.isoformat(), appointment_id),
        )
        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            return {
                "status": "rescheduled",
                "id": appointment_id,
                "new_start": new_start_time.isoformat(),
                "new_end": new_end_time.isoformat(),
            }
        return {"status": "not_found", "message": "Appointment not found or cancelled"}

    # --- Internal Helper Methods ---

    async def _get_booked_slots(self, date: datetime) -> list[dict]:
        """Get already-booked time slots for a date."""
        start_of_day = datetime(date.year, date.month, date.day, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

        db = self._db
        conn = db._get_connection()
        cursor = conn.execute(
            """SELECT start_time, end_time FROM appointments 
               WHERE status = 'confirmed' 
               AND start_time >= ? AND start_time <= ?""",
            (start_of_day.isoformat(), end_of_day.isoformat()),
        )
        rows = cursor.fetchall()
        conn.close()

        return [{"start": row[0], "end": row[1]} for row in rows]

    async def _is_slot_available(
        self,
        start: datetime,
        end: datetime,
        exclude_id: Optional[str] = None,
    ) -> bool:
        """Check if a time slot is available (no conflicts)."""
        db = self._db
        conn = db._get_connection()

        if exclude_id:
            cursor = conn.execute(
                """SELECT COUNT(*) FROM appointments 
                   WHERE status = 'confirmed' 
                   AND id != ?
                   AND start_time < ? AND end_time > ?""",
                (exclude_id, end.isoformat(), start.isoformat()),
            )
        else:
            cursor = conn.execute(
                """SELECT COUNT(*) FROM appointments 
                   WHERE status = 'confirmed' 
                   AND start_time < ? AND end_time > ?""",
                (end.isoformat(), start.isoformat()),
            )

        count = cursor.fetchone()[0]
        conn.close()
        return count == 0

    def _is_within_working_hours(self, start: datetime, end: datetime) -> bool:
        """Check if the time slot falls within working hours."""
        wh = self._working_hours
        return (
            start.hour >= wh["start_hour"]
            and end.hour <= wh["end_hour"]
        )


_tool: AppointmentTool | None = None


def get_appointment_tool() -> AppointmentTool:
    """Get appointment tool singleton."""
    global _tool
    if _tool is None:
        _tool = AppointmentTool()
    return _tool