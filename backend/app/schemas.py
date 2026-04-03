"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContextMode(str, Enum):
    """Context modes for the agent."""
    BUSINESS = "business"
    PERSONAL = "personal"
    NEUTRAL = "neutral"


class IntentType(str, Enum):
    """Types of user intents the agent can handle."""
    QUESTION = "question"
    TASK_CREATE = "task_create"
    TASK_LIST = "task_list"
    DIARY_ENTRY = "diary_entry"
    DIARY_READ = "diary_read"
    EMAIL_SEND = "email_send"
    EMAIL_READ = "email_read"
    CALENDAR_QUERY = "calendar_query"
    CALENDAR_CREATE = "calendar_create"
    REMINDER_CREATE = "reminder_create"
    REMINDER_LIST = "reminder_list"
    WEB_SEARCH = "web_search"
    MEMORY_STORE = "memory_store"  # "Remember that..."
    MEMORY_RECALL = "memory_recall"  # "What did I say about..."
    CONTEXT_SWITCH = "context_switch"
    CHIT_CHAT = "chit_chat"
    UNKNOWN = "unknown"


# --- Chat Message Schemas ---

class ChatMessage(BaseModel):
    """A single message in the chat conversation."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request body for sending a message to the agent."""
    message: str = Field(..., description="User's input message")
    context_mode: ContextMode = Field(
        default=ContextMode.NEUTRAL,
        description="Current context mode",
    )
    session_id: str = Field(
        default="default",
        description="Session identifier for conversation continuity",
    )


class ChatResponse(BaseModel):
    """Response from the agent."""
    response: str = Field(..., description="Agent's text response")
    intent: IntentType = Field(default=IntentType.UNKNOWN)
    context_mode: ContextMode = Field(default=ContextMode.NEUTRAL)
    action_taken: str | None = Field(
        default=None,
        description="Description of any action the agent took",
    )
    audio_url: str | None = Field(
        default=None,
        description="URL to generated TTS audio file",
    )
    session_id: str = Field(default="default")


# --- WebSocket Streaming Schemas ---

class StreamChunk(BaseModel):
    """A chunk of streamed response."""
    type: Literal["text", "audio", "status", "complete"]
    content: str | None = None
    audio_base64: str | None = None


# --- Memory Schemas ---

class MemoryStoreRequest(BaseModel):
    """Request to store a memory."""
    content: str
    context_mode: ContextMode = ContextMode.NEUTRAL
    tags: list[str] = Field(default_factory=list)


class MemoryRecallRequest(BaseModel):
    """Request to recall memories."""
    query: str
    limit: int = Field(default=5)
    context_mode: ContextMode | None = None


class MemoryEntry(BaseModel):
    """A stored memory entry."""
    id: str
    content: str
    context_mode: ContextMode
    tags: list[str]
    created_at: datetime
    score: float | None = None


# --- Task Schemas ---

class TaskCreate(BaseModel):
    """Create a new task."""
    title: str
    description: str = ""
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    due_date: datetime | None = None
    context_mode: ContextMode = ContextMode.NEUTRAL
    tags: list[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """Update an existing task."""
    title: str | None = None
    description: str | None = None
    priority: Literal["low", "medium", "high", "urgent"] | None = None
    due_date: datetime | None = None
    completed: bool | None = None
    tags: list[str] | None = None


class Task(BaseModel):
    """A task item."""
    id: str
    title: str
    description: str
    priority: str
    due_date: datetime | None
    completed: bool
    context_mode: ContextMode
    tags: list[str]
    created_at: datetime
    updated_at: datetime


# --- Diary Schemas ---

class DiaryEntryCreate(BaseModel):
    """Create a diary entry."""
    content: str
    mood: str | None = None
    tags: list[str] = Field(default_factory=list)
    context_mode: ContextMode = ContextMode.NEUTRAL


class DiaryEntry(BaseModel):
    """A diary entry."""
    id: str
    content: str
    mood: str | None
    tags: list[str]
    context_mode: ContextMode
    created_at: datetime
    updated_at: datetime


# --- Reminder Schemas ---

class ReminderCreate(BaseModel):
    """Create a reminder."""
    message: str
    remind_at: datetime
    repeat: Literal["none", "daily", "weekly", "monthly"] = "none"
    context_mode: ContextMode = ContextMode.NEUTRAL


class Reminder(BaseModel):
    """A reminder."""
    id: str
    message: str
    remind_at: datetime
    repeat: str
    active: bool
    context_mode: ContextMode
    created_at: datetime


# --- Calendar Schemas ---

class CalendarEvent(BaseModel):
    """A calendar event."""
    id: str
    title: str
    description: str
    start: datetime
    end: datetime
    location: str | None = None
    attendees: list[str] = Field(default_factory=list)


# --- Console / Dashboard Schemas ---

class DashboardStats(BaseModel):
    """Dashboard overview statistics."""
    total_conversations: int
    total_tasks: int
    completed_tasks: int
    total_memories: int
    total_diary_entries: int
    active_reminders: int
    uptime_hours: float
    avg_response_time_ms: float


class ConversationSummary(BaseModel):
    """Summary of a conversation session."""
    session_id: str
    message_count: int
    first_message_at: datetime
    last_message_at: datetime
    context_mode: ContextMode
    intents_used: list[str]


class SystemHealth(BaseModel):
    """System health status."""
    status: Literal["healthy", "degraded", "unhealthy"]
    groq_api: bool
    database: bool
    lancedb: bool
    tts_service: bool
    uptime_seconds: float
    memory_usage_mb: float
    last_error: str | None = None


# --- Appointment Schemas ---

class AppointmentRequest(BaseModel):
    """Book a new appointment."""
    start_time: datetime
    end_time: datetime | None = None
    client_name: str = ""
    client_contact: str = ""
    appointment_type: str = "general"
    notes: str = ""


class AppointmentUpdate(BaseModel):
    """Update appointment details."""
    new_start_time: datetime | None = None
    new_end_time: datetime | None = None


class Appointment(BaseModel):
    """Appointment information."""
    id: str
    client_name: str
    client_contact: str
    start_time: datetime
    end_time: datetime
    appointment_type: str
    notes: str
    status: str
    created_at: datetime


# --- Calendar API Schemas ---

class CalendarEventCreate(BaseModel):
    """Create a calendar event."""
    title: str
    start_time: datetime
    end_time: datetime | None = None
    description: str = ""
    location: str | None = None
    attendees: list[str] = Field(default_factory=list)


class CalendarEventResponse(BaseModel):
    """Calendar event response."""
    id: str
    title: str
    start: datetime
    end: datetime
    description: str
    location: str | None
    attendees: list[str]


class AvailabilityRequest(BaseModel):
    """Check availability for a date."""
    date: datetime


class AvailabilityResponse(BaseModel):
    """Available time slots."""
    period: dict
    busy_slots: list[dict]
    has_availability: bool


# --- Email Schemas ---

class EmailSendRequest(BaseModel):
    """Send an email."""
    to: str
    subject: str
    body: str
    cc: str | None = None


class EmailListRequest(BaseModel):
    """List emails request."""
    folder: str = "inbox"
    query: str = ""
    max_results: int = 20
    unread_only: bool = False


class EmailResponse(BaseModel):
    """Email information."""
    id: str
    sender: str | None = None
    to: str | None = None
    subject: str
    body: str
    received_at: str | None = None
    sent_at: str | None = None
    read: bool = False


class EmailTemplateRequest(BaseModel):
    """Send an email template."""
    to: str
    template_name: str
    variables: dict[str, str] = Field(default_factory=dict)


# --- Receptionist Schemas ---

class ReceptionistStatus(BaseModel):
    """Receptionist system status."""
    mode: str = "active"
    business_name: str = ""
    working_hours: dict
    total_unread_emails: int
    upcoming_appointments: int
    active_reminders: int


# --- Auth Schemas ---

class LoginRequest(BaseModel):
    """Login request."""
    passphrase: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"