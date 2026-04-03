"""SQLite structured database for tasks, diary entries, reminders, etc."""

import json
import logging
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)

# Database initialization SQL
INIT_SQL = """
-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT DEFAULT 'medium',
    due_date TIMESTAMP,
    completed BOOLEAN DEFAULT 0,
    context_mode TEXT DEFAULT 'neutral',
    tags TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Diary entries table
CREATE TABLE IF NOT EXISTS diary_entries (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    mood TEXT,
    tags TEXT DEFAULT '[]',
    context_mode TEXT DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id TEXT PRIMARY KEY,
    message TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    repeat TEXT DEFAULT 'none',
    active BOOLEAN DEFAULT 1,
    context_mode TEXT DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversation log table
CREATE TABLE IF NOT EXISTS conversation_log (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    user_message TEXT,
    agent_response TEXT,
    intent TEXT,
    context_mode TEXT DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calendar events table (for AI receptionist)
CREATE TABLE IF NOT EXISTS calendar_events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location TEXT,
    attendees TEXT DEFAULT '',
    context_mode TEXT DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments table (for AI receptionist)
CREATE TABLE IF NOT EXISTS appointments (
    id TEXT PRIMARY KEY,
    client_name TEXT NOT NULL,
    client_contact TEXT DEFAULT '',
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    appointment_type TEXT DEFAULT 'general',
    notes TEXT DEFAULT '',
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_context ON tasks(context_mode);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_diary_context ON diary_entries(context_mode);
CREATE INDEX IF NOT EXISTS idx_diary_created ON diary_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_reminders_active ON reminders(active);
CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(remind_at);
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_log(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_created ON conversation_log(created_at);
CREATE INDEX IF NOT EXISTS idx_calendar_start ON calendar_events(start_time);
CREATE INDEX IF NOT EXISTS idx_appointments_start ON appointments(start_time);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
"""


class StructuredDB:
    """SQLite database for structured data."""

    _instance: "StructuredDB | None" = None

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._db_path = self._settings.sqlite_db_path
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_conn() as conn:
            conn.executescript(INIT_SQL)
            logger.info(f"Database initialized at {self._db_path}")

    @contextmanager
    def _get_conn(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # --- Task Operations ---

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: datetime | None = None,
        context_mode: str = "neutral",
        tags: list[str] | None = None,
    ) -> dict:
        """Create a new task."""
        task_id = str(uuid.uuid4())[:8]
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO tasks (id, title, description, priority, due_date,
                   completed, context_mode, tags) VALUES (?, ?, ?, ?, ?, 0, ?, ?)""",
                (task_id, title, description, priority,
                 due_date.isoformat() if due_date else None,
                 context_mode, json.dumps(tags or [])),
            )
        return self.get_task(task_id)

    def get_task(self, task_id: str) -> dict | None:
        """Get a single task by ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if row:
                return dict(row)
        return None

    def list_tasks(
        self,
        context_mode: str | None = None,
        completed: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List tasks with optional filtering."""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if context_mode and context_mode != "all":
            query += " AND context_mode = ?"
            params.append(context_mode)

        if completed is not None:
            query += " AND completed = ?"
            params.append(1 if completed else 0)

        query += " ORDER BY CASE WHEN priority = 'urgent' THEN 1 WHEN priority = 'high' THEN 2 WHEN priority = 'medium' THEN 3 ELSE 4 END, due_date ASC"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task."""
        allowed = {"title", "description", "priority", "due_date", "completed", "tags"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False

        fields["updated_at"] = datetime.utcnow().isoformat()
        if "tags" in fields and isinstance(fields["tags"], list):
            fields["tags"] = json.dumps(fields["tags"])

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [task_id]

        with self._get_conn() as conn:
            conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        return True

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return True

    # --- Diary Operations ---

    def create_diary_entry(
        self,
        content: str,
        mood: str | None = None,
        tags: list[str] | None = None,
        context_mode: str = "neutral",
    ) -> dict:
        """Create a diary entry."""
        entry_id = str(uuid.uuid4())[:8]
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO diary_entries (id, content, mood, tags, context_mode)
                   VALUES (?, ?, ?, ?, ?)""",
                (entry_id, content, mood, json.dumps(tags or []), context_mode),
            )
        return self.get_diary_entry(entry_id)

    def get_diary_entry(self, entry_id: str) -> dict | None:
        """Get a diary entry by ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM diary_entries WHERE id = ?", (entry_id,)
            ).fetchone()
            if row:
                return dict(row)
        return None

    def list_diary_entries(
        self,
        context_mode: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """List diary entries."""
        query = "SELECT * FROM diary_entries WHERE 1=1"
        params = []

        if context_mode and context_mode != "all":
            query += " AND context_mode = ?"
            params.append(context_mode)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def update_diary_entry(self, entry_id: str, **kwargs) -> bool:
        """Update a diary entry."""
        allowed = {"content", "mood", "tags"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False

        fields["updated_at"] = datetime.utcnow().isoformat()
        if "tags" in fields and isinstance(fields["tags"], list):
            fields["tags"] = json.dumps(fields["tags"])

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [entry_id]

        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE diary_entries SET {set_clause} WHERE id = ?", values
            )
        return True

    def delete_diary_entry(self, entry_id: str) -> bool:
        """Delete a diary entry."""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM diary_entries WHERE id = ?", (entry_id,))
        return True

    # --- Reminder Operations ---

    def create_reminder(
        self,
        message: str,
        remind_at: datetime,
        repeat: str = "none",
        context_mode: str = "neutral",
    ) -> dict:
        """Create a reminder."""
        reminder_id = str(uuid.uuid4())[:8]
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO reminders (id, message, remind_at, repeat, context_mode)
                   VALUES (?, ?, ?, ?, ?)""",
                (reminder_id, message, remind_at.isoformat(), repeat, context_mode),
            )
        return self.get_reminder(reminder_id)

    def get_reminder(self, reminder_id: str) -> dict | None:
        """Get a reminder by ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM reminders WHERE id = ?", (reminder_id,)
            ).fetchone()
            if row:
                return dict(row)
        return None

    def list_reminders(
        self,
        active: bool = True,
        context_mode: str | None = None,
    ) -> list[dict]:
        """List reminders."""
        query = "SELECT * FROM reminders WHERE active = ?"
        params = [1 if active else 0]

        if context_mode and context_mode != "all":
            query += " AND context_mode = ?"
            params.append(context_mode)

        query += " ORDER BY remind_at ASC"

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_due_reminders(self, max_ahead_minutes: int = 5) -> list[dict]:
        """Get reminders that are due within the specified window."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM reminders 
                   WHERE active = 1 
                   AND remind_at <= datetime('now', '+' || ? || ' minutes')
                   AND remind_at >= datetime('now')
                   ORDER BY remind_at ASC""",
                (max_ahead_minutes,),
            ).fetchall()
            return [dict(r) for r in rows]

    def deactivate_reminder(self, reminder_id: str) -> bool:
        """Mark a reminder as inactive."""
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE reminders SET active = 0 WHERE id = ?", (reminder_id,)
            )
        return True

    # --- Conversation Log ---

    def log_conversation(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        intent: str,
        context_mode: str = "neutral",
    ) -> str:
        """Log a conversation exchange."""
        log_id = str(uuid.uuid4())[:8]
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO conversation_log (id, session_id, user_message,
                   agent_response, intent, context_mode) VALUES (?, ?, ?, ?, ?, ?)""",
                (log_id, session_id, user_message, agent_response, intent, context_mode),
            )
        return log_id

    def get_conversation_history(
        self,
        session_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """Get conversation history."""
        query = "SELECT * FROM conversation_log WHERE 1=1"
        params = []

        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    # --- Stats ---

    def get_stats(self) -> dict:
        """Get database statistics."""
        with self._get_conn() as conn:
            stats = {}
            for table in ["tasks", "diary_entries", "reminders", "conversation_log"]:
                row = conn.execute(f"SELECT COUNT(*) as count FROM {table}").fetchone()
                stats[table] = row["count"]

            # Completed tasks
            row = conn.execute(
                "SELECT COUNT(*) as count FROM tasks WHERE completed = 1"
            ).fetchone()
            stats["completed_tasks"] = row["count"]

            # Active reminders
            row = conn.execute(
                "SELECT COUNT(*) as count FROM reminders WHERE active = 1"
            ).fetchone()
            stats["active_reminders"] = row["count"]

            return stats


# Singleton
_db: StructuredDB | None = None


def get_structured_db() -> StructuredDB:
    """Get or create structured DB singleton."""
    global _db
    if _db is None:
        _db = StructuredDB()
    return _db