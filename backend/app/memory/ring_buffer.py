"""Ring buffer for short-term conversation memory."""

import logging
from collections import defaultdict, deque
from datetime import datetime
from threading import Lock

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


class RingBuffer:
    """Thread-safe rolling conversation buffer per session."""

    _instance: "RingBuffer | None" = None
    _lock = Lock()

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._max_size = self._settings.max_ring_buffer_size
        # defaultdict with deque as default factory
        self._buffers: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self._max_size)
        )

    @classmethod
    def get_instance(cls) -> "RingBuffer":
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        context_mode=None,
    ) -> None:
        """Add a message to the session's ring buffer."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if context_mode:
            message["context_mode"] = context_mode.value if hasattr(context_mode, "value") else str(context_mode)

        self._buffers[session_id].append(message)

    def get_session_messages(self, session_id: str, limit: int | None = None) -> list[dict]:
        """Get messages from a session's ring buffer."""
        buffer = self._buffers.get(session_id, deque())
        messages = list(buffer)
        if limit:
            messages = messages[-limit:]
        return messages

    def get_conversation_text(
        self, session_id: str, last_n: int = 10
    ) -> str:
        """Get conversation as formatted text string."""
        messages = self.get_session_messages(session_id, limit=last_n)
        lines = []
        for msg in messages:
            role_label = "User" if msg["role"] == "user" else "Donut"
            lines.append(f"{role_label}: {msg['content']}")
        return "\n".join(lines)

    def clear_session(self, session_id: str) -> None:
        """Clear a session's ring buffer."""
        self._buffers[session_id].clear()

    def get_all_sessions(self) -> list[str]:
        """Get list of active session IDs."""
        return list(self._buffers.keys())

    def get_session_count(self, session_id: str) -> int:
        """Get message count for a session."""
        return len(self._buffers.get(session_id, []))

    def get_stats(self) -> dict:
        """Get ring buffer statistics."""
        total_sessions = len(self._buffers)
        total_messages = sum(len(buf) for buf in self._buffers.values())
        return {
            "active_sessions": total_sessions,
            "total_messages": total_messages,
            "max_buffer_size": self._max_size,
        }