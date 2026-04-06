"""Donut AI - FastAPI backend entry point."""

import logging
import time
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware

from .config import Settings, get_settings
from .llm import get_groq_client
from .memory.ring_buffer import RingBuffer
from .memory.structured_db import get_structured_db
from .schemas import (
    Appointment,
    AppointmentRequest,
    AppointmentUpdate,
    AvailabilityRequest,
    AvailabilityResponse,
    CalendarEvent,
    CalendarEventCreate,
    CalendarEventResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ContextMode,
    ConversationSummary,
    DashboardStats,
    DiaryEntry,
    DiaryEntryCreate,
    EmailListRequest,
    EmailResponse,
    EmailSendRequest,
    EmailTemplateRequest,
    LoginRequest,
    MemoryEntry,
    MemoryRecallRequest,
    MemoryStoreRequest,
    ReceptionistStatus,
    Reminder,
    ReminderCreate,
    SystemHealth,
    Task,
    TaskCreate,
    TaskUpdate,
    TokenResponse,
)
from .tools.diary_tool import get_diary_tool
from .tools.memory_tool import get_memory_tool
from .tools.search_tool import get_search_tool
from .tools.task_tool import get_task_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Track startup time for uptime
START_TIME = time.time()

# Rate limiting
rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 200  # requests per window (increased for slider interactions)
RATE_LIMIT_WINDOW = 60  # seconds

# Endpoints exempt from rate limiting (low-risk operations)
RATE_LIMIT_EXEMPT = {
    "/api/ai-settings",
    "/api/branding",
    "/api/ai-settings/options",
}


def check_rate_limit(client_ip: str, path: str) -> bool:
    """Check if client has exceeded rate limit."""
    # Skip rate limiting for exempt endpoints
    if path in RATE_LIMIT_EXEMPT:
        return True
    
    now = time.time()
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if now - t < RATE_LIMIT_WINDOW
    ]
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True


async def process_message(
    message: str,
    context_mode: ContextMode = ContextMode.NEUTRAL,
    session_id: str = "default",
) -> ChatResponse:
    """Process a chat message through the agent and log it."""
    from .agents.orchestrator import run_agent

    db = get_structured_db()

    # Run through agent orchestrator
    result = await run_agent(
        user_message=message,
        context_mode=context_mode,
        session_id=session_id,
    )

    # Log conversation
    db.log_conversation(
        session_id=session_id,
        user_message=message,
        agent_response=result.get("response", ""),
        intent=str(result.get("intent", "unknown")),
        context_mode=context_mode.value,
    )

    return ChatResponse(
        response=result.get("response", ""),
        intent=result.get("intent", "unknown"),
        context_mode=result.get("context_mode", context_mode),
        action_taken=result.get("action_taken"),
        session_id=session_id,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for startup/shutdown events."""
    logger.info("=" * 50)
    logger.info("🍩 Donut AI - Executive Function Co-Pilot")
    logger.info("=" * 50)

    settings = get_settings()
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"TTS Provider: {settings.tts_provider}")
    logger.info(f"Data directory: {settings.sqlite_db_path.parent}")

    # Test Groq connection
    try:
        groq = get_groq_client()
        logger.info("✅ Groq client initialized")
    except Exception as e:
        logger.warning(f"⚠️ Groq client warning: {e}")

    logger.info("Donut is ready! Listening for commands...")

    yield

    logger.info("Shutting down Donut AI...")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Donut AI",
        description="Executive Function Co-Pilot - Backend API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    settings = settings or get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001", "https://vercel.com/lastchaptermedia2016-5232s-projects/donut-ai/EaY5wFYgs4rxib4Y4NPqa3ENoTVe"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "donutai-production.up.railway.app", "*.railway.app", "donut-ai-eosin.vercel.app", "*.vercel.app", settings.frontend_url.replace("http://", "").replace("https://", "")]
    )

    # Rate limiting middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Apply rate limiting to API endpoints."""
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Skip rate limiting for health checks and exempt endpoints
        if path in ["/", "/health"] or path in RATE_LIMIT_EXEMPT:
            return await call_next(request)
        
        # Check rate limit
        if not check_rate_limit(client_ip, path):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        return await call_next(request)

    # Request validation middleware
    @app.middleware("http")
    async def validate_request_middleware(request: Request, call_next):
        """Validate and sanitize incoming requests."""
        # Check content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type and request.url.path not in ["/api/stt"]:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Content-Type header is required"}
                )
        
        # Check request size (max 10MB)
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large"}
            )
        
        response = await call_next(request)
        return response

    # --- Public Routes ---

    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint."""
        settings = get_settings()
        return {
            "name": settings.app_name,
            "description": settings.app_description,
            "version": "0.1.0",
            "status": "healthy",
            "uptime_seconds": time.time() - START_TIME,
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Detailed health check."""
        uptime = time.time() - START_TIME
        db = get_structured_db()
        ring = RingBuffer.get_instance()
        settings = get_settings()

        # Check various services
        services = {}
        all_ok = True

        # Check Groq API
        try:
            groq = get_groq_client()
            services["groq"] = {"status": "ok", "model": settings.llm_model}
        except Exception as e:
            services["groq"] = {"status": "error", "error": str(e)}
            all_ok = False

        # Check database
        try:
            stats = db.get_stats()
            services["database"] = {"status": "ok", "type": "sqlite"}
        except Exception as e:
            services["database"] = {"status": "error", "error": str(e)}
            all_ok = False

        # Check ring buffer
        try:
            ring_stats = ring.get_stats()
            services["ring_buffer"] = {"status": "ok", "sessions": ring_stats.get("total_sessions", 0)}
        except Exception as e:
            services["ring_buffer"] = {"status": "error", "error": str(e)}
            all_ok = False

        # Check vector store
        try:
            from .memory.vector_store import get_vector_store
            store = await get_vector_store()
            services["vector_store"] = {"status": "ok", "type": "lancedb"}
        except Exception as e:
            services["vector_store"] = {"status": "error", "error": str(e)}
            all_ok = False

        overall = "healthy" if all_ok else "degraded"

        return {
            "status": overall,
            "version": "0.1.0",
            "uptime_seconds": round(uptime, 2),
            "uptime_hours": round(uptime / 3600, 2),
            "services": services,
            "configuration": {
                "llm_model": settings.llm_model,
                "tts_provider": settings.tts_provider,
                "frontend_url": settings.frontend_url,
            },
        }

    # --- Chat Routes ---

    @app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
    async def chat(request: ChatRequest, settings: Settings = Depends(get_settings)):
        """Send a message to Donut and get a response."""
        try:
            response = await process_message(
                message=request.message,
                context_mode=request.context_mode,
                session_id=request.session_id,
            )
            return response
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Memory Routes ---

    @app.post("/api/memory/store", tags=["Memory"])
    async def store_memory(request: MemoryStoreRequest):
        """Store a memory."""
        try:
            memory_tool = get_memory_tool()
            result = await memory_tool.store_memory(
                content=request.content,
                context_mode=request.context_mode.value,
                tags=request.tags,
            )
            return result
        except Exception as e:
            logger.error(f"Error storing memory: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/memory/recall", tags=["Memory"])
    async def recall_memories(request: MemoryRecallRequest):
        """Recall memories by query."""
        try:
            memory_tool = get_memory_tool()
            results = await memory_tool.recall_memories(
                query=request.query,
                limit=request.limit,
                context_mode=request.context_mode.value if request.context_mode else None,
            )
            return results
        except Exception as e:
            logger.error(f"Error recalling memories: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/memory/all", tags=["Memory"])
    async def get_all_memories(limit: int = 50):
        """Get all memories (for console)."""
        try:
            memory_tool = get_memory_tool()
            memories = await memory_tool.get_all_memories(limit=limit)
            return memories
        except Exception as e:
            logger.error(f"Error fetching memories: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/memory/{memory_id}", tags=["Memory"])
    async def delete_memory(memory_id: str):
        """Delete a memory."""
        try:
            memory_tool = get_memory_tool()
            success = await memory_tool.delete_memory(memory_id)
            return {"deleted": success}
        except Exception as e:
            logger.error(f"Error deleting memory: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Task Routes ---

    @app.post("/api/tasks", response_model=dict, tags=["Tasks"])
    async def create_task(request: TaskCreate):
        """Create a new task."""
        try:
            task_tool = get_task_tool()
            result = await task_tool.create_task(
                title=request.title,
                description=request.description,
                priority=request.priority,
                context_mode=request.context_mode.value,
            )
            return result
        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/tasks", tags=["Tasks"])
    async def list_tasks(
        context_mode: str = "all",
        show_completed: bool = False,
    ):
        """List tasks."""
        try:
            task_tool = get_task_tool()
            tasks = await task_tool.list_tasks(
                context_mode=context_mode,
                show_completed=show_completed,
            )
            return tasks
        except Exception as e:
            logger.error(f"Error listing tasks: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/api/tasks/{task_id}", tags=["Tasks"])
    async def update_task(task_id: str, request: TaskUpdate):
        """Update a task."""
        try:
            task_tool = get_task_tool()
            data = request.model_dump(exclude_none=True)
            success = task_tool._db.update_task(task_id, **data)
            return {"updated": success}
        except Exception as e:
            logger.error(f"Error updating task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/tasks/{task_id}", tags=["Tasks"])
    async def delete_task(task_id: str):
        """Delete a task."""
        try:
            task_tool = get_task_tool()
            success = await task_tool.delete_task(task_id)
            return {"deleted": success}
        except Exception as e:
            logger.error(f"Error deleting task: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Diary Routes ---

    @app.post("/api/diary", tags=["Diary"])
    async def create_diary_entry(request: DiaryEntryCreate):
        """Create a diary entry."""
        try:
            diary_tool = get_diary_tool()
            result = await diary_tool.create_entry(
                content=request.content,
                mood=request.mood,
                context_mode=request.context_mode.value,
            )
            return result
        except Exception as e:
            logger.error(f"Error creating diary entry: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/diary", tags=["Diary"])
    async def get_diary_entries(
        context_mode: str = "all",
        limit: int = 20,
    ):
        """Get diary entries."""
        try:
            diary_tool = get_diary_tool()
            entries = await diary_tool.get_entries(
                context_mode=context_mode,
                limit=limit,
            )
            return entries
        except Exception as e:
            logger.error(f"Error fetching diary entries: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/diary/{entry_id}", tags=["Diary"])
    async def delete_diary_entry(entry_id: str):
        """Delete a diary entry."""
        try:
            diary_tool = get_diary_tool()
            success = await diary_tool.delete_entry(entry_id)
            return {"deleted": success}
        except Exception as e:
            logger.error(f"Error deleting diary entry: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Search Routes ---

    @app.get("/api/search", tags=["Search"])
    async def search(query: str, max_results: int = 5):
        """Search the web."""
        try:
            search_tool = get_search_tool()
            results = await search_tool.search(query, max_results)
            return results
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Console Routes ---

    @app.get("/api/console/dashboard", tags=["Console"])
    async def get_dashboard():
        """Get dashboard statistics."""
        try:
            db = get_structured_db()
            stats = db.get_stats()
            ring = RingBuffer.get_instance()
            ring_stats = ring.get_stats()

            db_stats = db.get_stats()

            return {
                "total_conversations": db_stats.get("conversation_log", 0),
                "total_tasks": db_stats.get("tasks", 0),
                "completed_tasks": db_stats.get("completed_tasks", 0),
                "total_memories": db_stats.get("diary_entries", 0),
                "total_diary_entries": db_stats.get("diary_entries", 0),
                "active_reminders": db_stats.get("active_reminders", 0),
                "uptime_hours": round((time.time() - START_TIME) / 3600, 2),
                "avg_response_time_ms": 0,  # TODO: Track response times
                "ring_buffer": ring_stats,
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/console/conversations", tags=["Console"])
    async def get_conversations(limit: int = 50, offset: int = 0):
        """Get conversation history."""
        try:
            db = get_structured_db()
            conversations = db.get_conversation_history(limit=limit, offset=offset)
            return conversations
        except Exception as e:
            logger.error(f"Error fetching conversations: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/console/system/health", tags=["Console"])
    async def system_health():
        """Detailed system health for console."""
        uptime = time.time() - START_TIME
        try:
            groq = get_groq_client()
            groq_ok = True
        except Exception:
            groq_ok = False

        try:
            db = get_structured_db()
            db_stats = db.get_stats()
            db_ok = True
        except Exception:
            db_ok = False
            db_stats = {}

        overall = "healthy" if groq_ok and db_ok else "degraded"

        return {
            "status": overall,
            "groq_api": groq_ok,
            "database": db_ok,
            "lancedb": True,  # TODO: actual check
            "tts_service": True,  # TODO: actual check
            "uptime_seconds": round(uptime, 2),
            "memory_usage_mb": 0.0,  # TODO: Add psutil
            "stats": db_stats,
        }

    @app.post("/api/auth/login", response_model=TokenResponse, tags=["Auth"])
    async def login(request: LoginRequest, settings: Settings = Depends(get_settings)):
        """Authenticate with passphrase."""
        from .utils.security import hash_password, verify_password, create_access_token
        from .utils.error_handler import AuthenticationError, ValidationError
        
        # Validate passphrase is not empty
        if not request.passphrase or not request.passphrase.strip():
            raise ValidationError("Passphrase is required", field="passphrase")
        
        # Check passphrase (in production, use hashed password comparison)
        if request.passphrase == settings.admin_passphrase:
            # Create JWT token with proper expiration
            token = create_access_token(
                data={"user": "admin", "role": "admin"},
                expires_delta=timedelta(hours=24),
            )
            return TokenResponse(access_token=token)
        
        raise AuthenticationError("Invalid passphrase")

    @app.get("/api/auth/me", tags=["Auth"])
    async def get_current_user(request: Request, settings: Settings = Depends(get_settings)):
        """Get current authenticated user info."""
        from .utils.security import decode_access_token
        from .utils.error_handler import AuthenticationError
        
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        payload = decode_access_token(token)
        
        if not payload:
            raise AuthenticationError("Invalid or expired token")
        
        return {
            "user": payload.get("user"),
            "role": payload.get("role"),
            "authenticated": True,
        }

    # --- AI Receptionist Routes ---

    @app.get("/api/receptionist/status", response_model=ReceptionistStatus, tags=["Receptionist"])
    async def receptionist_status():
        """Get receptionist system status."""
        try:
            from .tools.email_tool import get_email_tool
            from .tools.appointment_tool import get_appointment_tool
            from .tools.reminder_tool import get_reminder_tool

            db = get_structured_db()
            email_tool = get_email_tool()
            appt_tool = get_appointment_tool()
            reminder_tool = get_reminder_tool()

            # Count unread emails (simulated)
            unread = len([e for e in email_tool._local_inbox if not e.get("read", False)])

            # Count upcoming appointments
            from datetime import datetime, timedelta
            appts = await appt_tool.list_appointments(
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=7),
                status="confirmed",
            )

            reminders = await reminder_tool.list_reminders()

            settings = get_settings()
            return {
                "mode": "active",
                "business_name": settings.business_name,
                "working_hours": appt_tool._working_hours,
                "total_unread_emails": unread,
                "upcoming_appointments": len(appts),
                "active_reminders": len(reminders),
            }
        except Exception as e:
            logger.error(f"Error fetching receptionist status: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Calendar Routes ---

    @app.get("/api/calendar", tags=["Calendar"])
    async def get_calendar_events(
        start_date: str = "",
        end_date: str = "",
        max_results: int = 20,
    ):
        """List calendar events."""
        try:
            from .tools.calendar_tool import get_calendar_tool
            from datetime import datetime, timedelta

            cal = get_calendar_tool()
            start = datetime.fromisoformat(start_date) if start_date else datetime.now()
            end = datetime.fromisoformat(end_date) if end_date else start + timedelta(days=7)

            events = await cal.list_events(
                start_date=start,
                end_date=end,
                max_results=max_results,
            )
            return events
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/calendar", tags=["Calendar"])
    async def create_calendar_event(request: CalendarEventCreate):
        """Create a calendar event."""
        try:
            from .tools.calendar_tool import get_calendar_tool

            cal = get_calendar_tool()
            result = await cal.create_event(
                title=request.title,
                start_time=request.start_time,
                end_time=request.end_time,
                description=request.description,
                location=request.location,
                attendees=request.attendees,
            )
            return result
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/calendar/{event_id}", tags=["Calendar"])
    async def delete_calendar_event(event_id: str):
        """Delete a calendar event."""
        try:
            from .tools.calendar_tool import get_calendar_tool

            cal = get_calendar_tool()
            result = await cal.delete_event(event_id)
            return result
        except Exception as e:
            logger.error(f"Error deleting calendar event: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/calendar/availability", tags=["Calendar"])
    async def check_availability(request: AvailabilityRequest):
        """Check availability for a date."""
        try:
            from .tools.calendar_tool import get_calendar_tool
            from datetime import timedelta

            cal = get_calendar_tool()
            avail = await cal.get_availability(
                start_date=request.date,
                end_date=request.date + timedelta(days=1),
            )
            return avail
        except Exception as e:
            logger.error(f"Error checking availability: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Email Routes ---

    @app.get("/api/emails", tags=["Email"])
    async def get_emails(
        folder: str = "inbox",
        query: str = "",
        max_results: int = 20,
        unread_only: bool = False,
    ):
        """List emails."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            emails = await email.list_emails(
                folder=folder,
                query=query,
                max_results=max_results,
                unread_only=unread_only,
            )
            return emails
        except Exception as e:
            logger.error(f"Error fetching emails: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/emails", tags=["Email"])
    async def send_email(request: EmailSendRequest):
        """Send an email."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            result = await email.send_email(
                to=request.to,
                subject=request.subject,
                body=request.body,
                cc=request.cc,
            )
            return result
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/emails/{email_id}", tags=["Email"])
    async def read_email(email_id: str):
        """Read an email."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            result = await email.read_email(email_id)
            if result:
                return result
            raise HTTPException(status_code=404, detail="Email not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading email: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/emails/{email_id}", tags=["Email"])
    async def delete_email(email_id: str):
        """Delete an email."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            result = await email.delete_email(email_id)
            return result
        except Exception as e:
            logger.error(f"Error deleting email: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/emails/template", tags=["Email"])
    async def send_template_email(request: EmailTemplateRequest):
        """Send an email using a template."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            result = await email.send_template_email(
                to=request.to,
                template_name=request.template_name,
                variables=request.variables,
            )
            return result
        except Exception as e:
            logger.error(f"Error sending template email: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/emails/templates", tags=["Email"])
    async def get_email_templates():
        """Get available email templates."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            return email.get_templates()
        except Exception as e:
            logger.error(f"Error fetching templates: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/emails/demo/receive", tags=["Email"])
    async def receive_demo_email(
        sender: str = "John Doe",
        subject: str = "Meeting Request",
        body: str = "Hi, I'd like to schedule a meeting for next week.",
    ):
        """Receive a simulated email (for demo purposes)."""
        try:
            from .tools.email_tool import get_email_tool

            email = get_email_tool()
            result = await email.receive_simulated_email(
                sender=sender,
                subject=subject,
                body=body,
            )
            return result
        except Exception as e:
            logger.error(f"Error receiving demo email: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Reminder Routes ---

    @app.get("/api/reminders", tags=["Reminders"])
    async def get_reminders(
        context_mode: str = "all",
        show_inactive: bool = False,
    ):
        """List reminders."""
        try:
            from .tools.reminder_tool import get_reminder_tool

            reminder = get_reminder_tool()
            result = await reminder.list_reminders(
                context_mode=context_mode,
                show_inactive=show_inactive,
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching reminders: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/reminders", tags=["Reminders"])
    async def create_reminder(request: ReminderCreate):
        """Create a reminder."""
        try:
            from .tools.reminder_tool import get_reminder_tool

            reminder = get_reminder_tool()
            result = await reminder.create_reminder(
                message=request.message,
                remind_at=request.remind_at,
                repeat=request.repeat,
                context_mode=request.context_mode.value,
            )
            return result
        except Exception as e:
            logger.error(f"Error creating reminder: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/reminders/{reminder_id}", tags=["Reminders"])
    async def delete_reminder(reminder_id: str):
        """Delete a reminder."""
        try:
            from .tools.reminder_tool import get_reminder_tool
            from .services.scheduler_service import cancel_reminder

            reminder = get_reminder_tool()
            result = await reminder.delete_reminder(reminder_id)
            await cancel_reminder(reminder_id)
            return result
        except Exception as e:
            logger.error(f"Error deleting reminder: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- Appointment Routes ---

    @app.get("/api/appointments", tags=["Appointments"])
    async def get_appointments(
        start_date: str = "",
        end_date: str = "",
        status: str = "all",
    ):
        """List appointments."""
        try:
            from .tools.appointment_tool import get_appointment_tool
            from datetime import datetime, timedelta

            appt = get_appointment_tool()
            start = datetime.fromisoformat(start_date) if start_date else datetime.now()
            end = datetime.fromisoformat(end_date) if start_date else start + timedelta(days=30)

            result = await appt.list_appointments(
                start_date=start,
                end_date=end,
                status=status,
            )
            return result
        except Exception as e:
            logger.error(f"Error fetching appointments: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/appointments", tags=["Appointments"])
    async def book_appointment(request: AppointmentRequest):
        """Book an appointment."""
        try:
            from .tools.appointment_tool import get_appointment_tool

            appt = get_appointment_tool()
            result = await appt.book_appointment(
                start_time=request.start_time,
                end_time=request.end_time,
                client_name=request.client_name,
                client_contact=request.client_contact,
                appointment_type=request.appointment_type,
                notes=request.notes,
            )
            return result
        except Exception as e:
            logger.error(f"Error booking appointment: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/api/appointments/{appointment_id}", tags=["Appointments"])
    async def cancel_appointment(appointment_id: str, reason: str = ""):
        """Cancel an appointment."""
        try:
            from .tools.appointment_tool import get_appointment_tool

            appt = get_appointment_tool()
            result = await appt.cancel_appointment(
                appointment_id=appointment_id,
                reason=reason,
            )
            return result
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/appointments/slots", tags=["Appointments"])
    async def get_available_slots(date: str):
        """Get available appointment slots for a date."""
        try:
            from .tools.appointment_tool import get_appointment_tool
            from datetime import datetime

            appt = get_appointment_tool()
            d = datetime.fromisoformat(date)
            result = await appt.get_available_slots(date=d)
            return result
        except Exception as e:
            logger.error(f"Error fetching slots: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    # --- TTS/STT Routes with Fallback ---

    @app.post("/api/tts", tags=["Voice"])
    async def text_to_speech(
        text: str,
        voice: str = "",
        speed: float = 1.0,
    ):
        """Convert text to speech audio with automatic provider fallback.

        Fallback order: Groq → ElevenLabs → xAI → Browser
        If all providers fail, returns None (frontend uses browser SpeechSynthesis).
        """
        try:
            from .services.voice_fallback import get_voice_fallback_manager
            from fastapi.responses import StreamingResponse
            import io

            manager = get_voice_fallback_manager()
            audio, provider = await manager.synthesize_with_fallback(
                text=text,
                voice=voice or None,
                speed=speed,
            )

            if audio:
                return StreamingResponse(
                    io.BytesIO(audio),
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": 'inline; filename="speech.wav"',
                        "X-TTS-Provider": provider,
                    },
                )

            # No audio - frontend should use browser SpeechSynthesis
            return JSONResponse(
                status_code=200,
                content={
                    "text": text,
                    "provider": provider,
                    "use_browser_tts": True,
                },
            )
        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)
            # Return text for browser fallback on error
            return JSONResponse(
                status_code=200,
                content={
                    "text": text,
                    "provider": "browser",
                    "use_browser_tts": True,
                },
            )

    @app.post("/api/stt", tags=["Voice"])
    async def speech_to_text(audio: bytes):
        """Transcribe audio to text with automatic provider fallback.

        Fallback order: Groq → ElevenLabs → xAI → Browser
        If all providers fail, returns None (frontend uses Web Speech API).
        """
        try:
            from .services.voice_fallback import get_voice_fallback_manager

            manager = get_voice_fallback_manager()
            text, provider = await manager.transcribe_with_fallback(
                audio_data=audio,
                language="en",
            )

            if text:
                return {
                    "text": text,
                    "provider": provider,
                }

            # No text - frontend should use Web Speech API
            return JSONResponse(
                status_code=200,
                content={
                    "text": None,
                    "provider": provider,
                    "use_browser_stt": True,
                },
            )
        except Exception as e:
            logger.error(f"STT error: {e}", exc_info=True)
            # Return browser fallback on error
            return JSONResponse(
                status_code=200,
                content={
                    "text": None,
                    "provider": "browser",
                    "use_browser_stt": True,
                },
            )

    @app.get("/api/voice/providers", tags=["Voice"])
    async def get_voice_providers():
        """Get available TTS/STT providers and their priority order."""
        try:
            from .services.voice_fallback import get_voice_fallback_manager

            manager = get_voice_fallback_manager()
            providers = manager.get_available_providers()
            return providers
        except Exception as e:
            logger.error(f"Error fetching voice providers: {e}", exc_info=True)
            return {"tts": ["browser"], "stt": ["browser"]}

    @app.get("/api/branding", tags=["Branding"])
    async def get_branding():
        """Get white-label branding configuration for the frontend."""
        settings = get_settings()
        return {
            "app_name": settings.app_name,
            "app_description": settings.app_description,
            "app_logo_emoji": settings.app_logo_emoji,
            "brand_primary_color": settings.brand_primary_color,
            "brand_secondary_color": settings.brand_secondary_color,
            "business_name": settings.business_name,
        }

    # --- AI Settings Routes ---

    @app.get("/api/ai-settings", tags=["AI Settings"])
    async def get_ai_settings():
        """Get current AI settings (personality, voice, model parameters)."""
        try:
            from .database import get_ai_settings
            # Use a default user_id for now (single user mode)
            settings = await get_ai_settings(user_id="default")
            return settings
        except Exception as e:
            logger.error(f"Error fetching AI settings: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.put("/api/ai-settings", tags=["AI Settings"])
    async def update_ai_settings(request: dict):
        """Update AI settings (personality, voice, model parameters)."""
        try:
            from .database import update_ai_settings
            # Use a default user_id for now (single user mode)
            settings = await update_ai_settings(user_id="default", **request)
            return settings
        except Exception as e:
            logger.error(f"Error updating AI settings: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/ai-settings/reset", tags=["AI Settings"])
    async def reset_ai_settings():
        """Reset AI settings to defaults."""
        try:
            from .database import reset_ai_settings
            # Use a default user_id for now (single user mode)
            settings = await reset_ai_settings(user_id="default")
            return settings
        except Exception as e:
            logger.error(f"Error resetting AI settings: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/ai-settings/options", tags=["AI Settings"])
    async def get_ai_settings_options():
        """Get available options for AI settings (tones, voices, etc.)."""
        return {
            "personality_tone": {
                "options": [
                    {"value": "warm", "label": "Warm & Supportive", "description": "Friendly and empathetic"},
                    {"value": "professional", "label": "Professional", "description": "Formal and business-focused"},
                    {"value": "casual", "label": "Casual", "description": "Relaxed and conversational"},
                    {"value": "formal", "label": "Formal", "description": "Very proper and structured"},
                    {"value": "humorous", "label": "Humorous", "description": "Playful with occasional wit"},
                    {"value": "empathetic", "label": "Empathetic", "description": "Highly understanding and caring"},
                ],
                "default": "warm"
            },
            "response_length": {
                "options": [
                    {"value": "concise", "label": "Concise", "description": "Brief and to the point"},
                    {"value": "balanced", "label": "Balanced", "description": "Medium length responses"},
                    {"value": "detailed", "label": "Detailed", "description": "Comprehensive and thorough"},
                ],
                "default": "balanced"
            },
            "emotion": {
                "options": [
                    {"value": "neutral", "label": "Neutral", "description": "Balanced emotional tone"},
                    {"value": "cheerful", "label": "Cheerful", "description": "Upbeat and positive"},
                    {"value": "calm", "label": "Calm", "description": "Soothing and relaxed"},
                    {"value": "energetic", "label": "Energetic", "description": "Enthusiastic and dynamic"},
                ],
                "default": "neutral"
            },
            "tts_voice": {
                "options": [
                    {"value": "autumn", "label": "Autumn", "description": "Warm female voice"},
                    {"value": "echo", "label": "Echo", "description": "Deep male voice"},
                    {"value": "onyx", "label": "Onyx", "description": "Rich male voice"},
                    {"value": "nova", "label": "Nova", "description": "Clear female voice"},
                ],
                "default": "autumn"
            },
            "tts_provider": {
                "options": [
                    {"value": "groq", "label": "Groq", "description": "Fast, efficient TTS"},
                    {"value": "elevenlabs", "label": "ElevenLabs", "description": "Premium quality voices"},
                    {"value": "openai", "label": "OpenAI", "description": "High-quality TTS"},
                ],
                "default": "groq"
            },
            "formality_level": {
                "min": 1,
                "max": 10,
                "default": 5,
                "labels": {
                    "1": "Very Casual",
                    "5": "Balanced",
                    "10": "Very Formal"
                }
            },
            "tts_speed": {
                "min": 0.5,
                "max": 2.0,
                "default": 1.0,
                "step": 0.1
            },
            "llm_temperature": {
                "min": 0.1,
                "max": 1.0,
                "default": 0.7,
                "step": 0.05,
                "description": "Lower = more focused, Higher = more creative"
            },
            "llm_max_tokens": {
                "min": 256,
                "max": 4096,
                "default": 1024,
                "step": 256,
                "description": "Maximum response length"
            }
        }

    # --- WebSocket Route ---

    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket endpoint for streaming voice chat."""
        await websocket.accept()

        session_id = "default"
        context_mode = ContextMode.NEUTRAL

        try:
            while True:
                data = await websocket.receive_json()

                if data.get("type") == "message":
                    msg = data.get("content", "")

                    await websocket.send_json({
                        "type": "status",
                        "content": "Thinking...",
                    })

                    if data.get("context_mode"):
                        context_mode = ContextMode(data["context_mode"])

                    response = await process_message(
                        message=msg,
                        context_mode=context_mode,
                        session_id=session_id,
                    )

                    await websocket.send_json({
                        "type": "text",
                        "content": response.response,
                        "metadata": {
                            "intent": response.intent,
                            "context_mode": response.context_mode.value,
                        },
                    })

                    await websocket.send_json({
                        "type": "complete",
                    })

                elif data.get("type") == "context_switch":
                    context_mode = ContextMode(data["context_mode"])
                    await websocket.send_json({
                        "type": "status",
                        "content": f"Context switched to {context_mode.value}",
                    })

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            try:
                await websocket.close()
            except RuntimeError:
                pass

    return app


# Create default app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )