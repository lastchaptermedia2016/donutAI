"""Supabase database client for Donut AI with SQLite fallback.

This module provides:
- Supabase client initialization
- SQLite fallback for when Supabase is unavailable
- Database operations for all tables
- pgvector integration for semantic search
- Row Level Security (RLS) support
"""

import logging
import sqlite3
import json
import os
from typing import Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# SQLite fallback for AI Settings
_SQLITE_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "donut_local.db"
)

def _get_sqlite_connection():
    """Get SQLite connection for fallback storage."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(_SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init_sqlite_ai_settings():
    """Initialize SQLite table for AI settings fallback."""
    try:
        conn = _get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_settings (
                user_id TEXT PRIMARY KEY,
                personality_tone TEXT DEFAULT 'warm',
                response_length TEXT DEFAULT 'balanced',
                formality_level INTEGER DEFAULT 5,
                emotion TEXT DEFAULT 'neutral',
                tts_voice TEXT DEFAULT 'autumn',
                tts_speed REAL DEFAULT 1.0,
                tts_provider TEXT DEFAULT 'groq',
                llm_temperature REAL DEFAULT 0.7,
                llm_max_tokens INTEGER DEFAULT 1024
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize SQLite AI settings table: {e}")

# Global Supabase client
_supabase_client: Optional[Any] = None


def get_supabase_client() -> Any:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        try:
            from supabase import create_client, Client
            from .config import get_settings
            
            settings = get_supabase_settings()
            _supabase_client = create_client(settings["url"], settings["key"])
            logger.info("✅ Supabase client initialized")
        except ImportError:
            logger.error("supabase-py not installed. Run: pip install supabase")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            raise
    return _supabase_client


def get_supabase_settings() -> dict:
    """Get Supabase settings from environment."""
    from .config import get_settings
    settings = get_settings()
    
    return {
        "url": settings.supabase_url,
        "key": settings.supabase_key,
    }


# ============================================
# Profile Operations
# ============================================

async def get_profile(user_id: str) -> Optional[dict]:
    """Get user profile by user_id."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return None


async def create_profile(user_id: str, email: str, display_name: str = "") -> Optional[dict]:
    """Create a new user profile."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "email": email,
            "display_name": display_name or email.split("@")[0],
            "context_mode": "neutral",
            "brand_color": "#8B0000",
            "brand_name": "Donut",
        }
        response = supabase.table("profiles").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        return None


async def update_profile(user_id: str, **kwargs) -> Optional[dict]:
    """Update user profile fields."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("profiles").update(kwargs).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return None


# ============================================
# Memory Operations (with pgvector)
# ============================================

async def store_memory(
    user_id: str,
    content: str,
    embedding: list[float],
    context_mode: str = "neutral",
    context_tag: Optional[str] = None,
    importance: float = 0.5,
) -> Optional[dict]:
    """Store a memory with vector embedding."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "content": content,
            "embedding": embedding,
            "context_mode": context_mode,
            "context_tag": context_tag,
            "importance": importance,
        }
        response = supabase.table("memories").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return None


async def search_memories(
    user_id: str,
    query_embedding: list[float],
    limit: int = 5,
    context_mode: Optional[str] = None,
) -> list[dict]:
    """Search memories using vector similarity."""
    try:
        supabase = get_supabase_client()
        
        # Build query
        query = supabase.table("memories").select("*").eq("user_id", user_id)
        
        if context_mode:
            query = query.eq("context_mode", context_mode)
        
        # Execute and get results
        response = query.order("created_at", desc=True).limit(limit * 2).execute()
        
        if not response.data:
            return []
        
        # Calculate cosine similarity manually
        import numpy as np
        
        def cosine_similarity(a, b):
            a = np.array(a)
            b = np.array(b)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        # Score and sort by similarity
        scored = []
        for memory in response.data:
            if memory.get("embedding"):
                similarity = cosine_similarity(query_embedding, memory["embedding"])
                scored.append((similarity, memory))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return []


async def get_all_memories(
    user_id: str,
    limit: int = 50,
    context_mode: Optional[str] = None,
) -> list[dict]:
    """Get all memories for a user."""
    try:
        supabase = get_supabase_client()
        query = supabase.table("memories").select("*").eq("user_id", user_id)
        
        if context_mode:
            query = query.eq("context_mode", context_mode)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        return []


async def delete_memory(user_id: str, memory_id: str) -> bool:
    """Delete a memory."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("memories").delete().eq("id", memory_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        return False


# ============================================
# Task Operations
# ============================================

async def create_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[datetime] = None,
    context_mode: str = "neutral",
    tags: list[str] = [],
) -> Optional[dict]:
    """Create a new task."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None,
            "context_mode": context_mode,
            "tags": tags,
        }
        response = supabase.table("tasks").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return None


async def get_tasks(
    user_id: str,
    context_mode: Optional[str] = None,
    show_completed: bool = False,
) -> list[dict]:
    """Get tasks for a user."""
    try:
        supabase = get_supabase_client()
        query = supabase.table("tasks").select("*").eq("user_id", user_id)
        
        if context_mode and context_mode != "all":
            query = query.eq("context_mode", context_mode)
        
        if not show_completed:
            query = query.eq("completed", False)
        
        response = query.order("created_at", desc=True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []


async def update_task(user_id: str, task_id: str, **kwargs) -> Optional[dict]:
    """Update a task."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("tasks").update(kwargs).eq("id", task_id).eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return None


async def delete_task(user_id: str, task_id: str) -> bool:
    """Delete a task."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return False


# ============================================
# Diary Operations
# ============================================

async def create_diary_entry(
    user_id: str,
    content: str,
    mood: Optional[str] = None,
    context_mode: str = "neutral",
    tags: list[str] = [],
) -> Optional[dict]:
    """Create a diary entry."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "content": content,
            "mood": mood,
            "context_mode": context_mode,
            "tags": tags,
        }
        response = supabase.table("diary_entries").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating diary entry: {e}")
        return None


async def get_diary_entries(
    user_id: str,
    context_mode: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Get diary entries for a user."""
    try:
        supabase = get_supabase_client()
        query = supabase.table("diary_entries").select("*").eq("user_id", user_id)
        
        if context_mode and context_mode != "all":
            query = query.eq("context_mode", context_mode)
        
        response = query.order("created_at", desc=True).limit(limit).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting diary entries: {e}")
        return []


async def delete_diary_entry(user_id: str, entry_id: str) -> bool:
    """Delete a diary entry."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("diary_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error deleting diary entry: {e}")
        return False


# ============================================
# Conversation Operations
# ============================================

async def log_conversation(
    user_id: str,
    session_id: str,
    user_message: str,
    agent_response: str,
    intent: str = "unknown",
    context_mode: str = "neutral",
) -> Optional[dict]:
    """Log a conversation for analytics."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "agent_response": agent_response,
            "intent": intent,
            "context_mode": context_mode,
        }
        response = supabase.table("conversations").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error logging conversation: {e}")
        return None


async def get_conversation_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get conversation history for a user."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("conversations") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return []


# ============================================
# Reminder Operations
# ============================================

async def create_reminder(
    user_id: str,
    message: str,
    remind_at: datetime,
    repeat: str = "none",
    context_mode: str = "neutral",
) -> Optional[dict]:
    """Create a reminder."""
    try:
        supabase = get_supabase_client()
        data = {
            "user_id": user_id,
            "message": message,
            "remind_at": remind_at.isoformat(),
            "repeat": repeat,
            "context_mode": context_mode,
        }
        response = supabase.table("reminders").insert(data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        return None


async def get_reminders(
    user_id: str,
    active_only: bool = True,
) -> list[dict]:
    """Get reminders for a user."""
    try:
        supabase = get_supabase_client()
        query = supabase.table("reminders").select("*").eq("user_id", user_id)
        
        if active_only:
            query = query.eq("active", True)
        
        response = query.order("remind_at", desc=False).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error getting reminders: {e}")
        return []


async def delete_reminder(user_id: str, reminder_id: str) -> bool:
    """Delete a reminder."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("reminders").delete().eq("id", reminder_id).eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        return False


# ============================================
# Stats Operations
# ============================================

async def get_stats(user_id: str) -> dict:
    """Get dashboard statistics for a user."""
    try:
        supabase = get_supabase_client()
        
        # Get counts for each table
        tasks = supabase.table("tasks").select("id, completed", count="exact").eq("user_id", user_id).execute()
        memories = supabase.table("memories").select("id", count="exact").eq("user_id", user_id).execute()
        diary = supabase.table("diary_entries").select("id", count="exact").eq("user_id", user_id).execute()
        reminders = supabase.table("reminders").select("id", count="exact").eq("user_id", user_id).eq("active", True).execute()
        conversations = supabase.table("conversations").select("id", count="exact").eq("user_id", user_id).execute()
        
        # Count completed tasks
        completed_tasks = len([t for t in (tasks.data or []) if t.get("completed")])
        
        return {
            "total_tasks": tasks.count or 0,
            "completed_tasks": completed_tasks,
            "total_memories": memories.count or 0,
            "total_diary_entries": diary.count or 0,
            "active_reminders": reminders.count or 0,
            "total_conversations": conversations.count or 0,
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "total_memories": 0,
            "total_diary_entries": 0,
            "active_reminders": 0,
            "total_conversations": 0,
        }


# ============================================
# AI Settings Operations
# ============================================

# Default AI settings
DEFAULT_AI_SETTINGS = {
    "personality_tone": "warm",
    "response_length": "balanced",
    "formality_level": 5,
    "emotion": "neutral",
    "tts_voice": "autumn",
    "tts_speed": 1.0,
    "tts_provider": "groq",
    "llm_temperature": 0.7,
    "llm_max_tokens": 1024,
}


def _get_ai_settings_sqlite(user_id: str) -> Optional[dict]:
    """Get AI settings from SQLite fallback."""
    try:
        _init_sqlite_ai_settings()
        conn = _get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ai_settings WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            settings = dict(row)
            settings.pop("user_id", None)
            return {**DEFAULT_AI_SETTINGS, **settings}
        return None
    except Exception as e:
        logger.error(f"Error getting AI settings from SQLite: {e}")
        return None


def _update_ai_settings_sqlite(user_id: str, **kwargs) -> dict:
    """Update AI settings in SQLite fallback."""
    try:
        _init_sqlite_ai_settings()
        conn = _get_sqlite_connection()
        cursor = conn.cursor()
        
        # Filter out invalid keys and user_id
        valid_keys = set(DEFAULT_AI_SETTINGS.keys())
        data = {k: v for k, v in kwargs.items() if k in valid_keys}
        
        if not data:
            conn.close()
            return DEFAULT_AI_SETTINGS.copy()
        
        # Check if exists
        cursor.execute("SELECT user_id FROM ai_settings WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [user_id]
            cursor.execute(f"UPDATE ai_settings SET {set_clause} WHERE user_id = ?", values)
        else:
            # Insert
            data["user_id"] = user_id
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            cursor.execute(f"INSERT INTO ai_settings ({columns}) VALUES ({placeholders})", list(data.values()))
        
        conn.commit()
        conn.close()
        
        result = {**DEFAULT_AI_SETTINGS, **data}
        result.pop("user_id", None)
        return result
    except Exception as e:
        logger.error(f"Error updating AI settings in SQLite: {e}")
        return DEFAULT_AI_SETTINGS.copy()


async def get_ai_settings(user_id: str) -> dict:
    """Get AI settings for a user. Falls back to SQLite if Supabase fails."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("ai_settings").select("*").eq("user_id", user_id).execute()
        if response.data:
            # Merge with defaults for any missing fields
            settings = {**DEFAULT_AI_SETTINGS, **response.data[0]}
            # Remove user_id from returned settings
            settings.pop("user_id", None)
            return settings
        
        # Check SQLite fallback
        sqlite_settings = _get_ai_settings_sqlite(user_id)
        if sqlite_settings:
            logger.info(f"Using SQLite fallback for AI settings (user: {user_id})")
            return sqlite_settings
        
        return DEFAULT_AI_SETTINGS.copy()
    except Exception as e:
        logger.warning(f"Supabase failed for AI settings, using SQLite fallback: {e}")
        # Try SQLite fallback
        sqlite_settings = _get_ai_settings_sqlite(user_id)
        if sqlite_settings:
            return sqlite_settings
        return DEFAULT_AI_SETTINGS.copy()


async def update_ai_settings(user_id: str, **kwargs) -> dict:
    """Update AI settings for a user. Falls back to SQLite if Supabase fails."""
    try:
        supabase = get_supabase_client()
        
        # Filter out invalid keys
        valid_keys = set(DEFAULT_AI_SETTINGS.keys()) | {"user_id"}
        data = {k: v for k, v in kwargs.items() if k in valid_keys}
        
        if not data:
            return await get_ai_settings(user_id)
        
        # Check if settings exist for user
        existing = supabase.table("ai_settings").select("user_id").eq("user_id", user_id).execute()
        
        if existing.data:
            # Update existing
            response = supabase.table("ai_settings").update(data).eq("user_id", user_id).execute()
        else:
            # Insert new
            data["user_id"] = user_id
            response = supabase.table("ai_settings").insert(data).execute()
        
        if response.data:
            result = {**DEFAULT_AI_SETTINGS, **response.data[0]}
            result.pop("user_id", None)
            # Also update SQLite for backup
            _update_ai_settings_sqlite(user_id, **{k: v for k, v in result.items()})
            return result
        return await get_ai_settings(user_id)
    except Exception as e:
        logger.warning(f"Supabase failed for AI settings update, using SQLite fallback: {e}")
        # Fallback to SQLite
        return _update_ai_settings_sqlite(user_id, **kwargs)


async def reset_ai_settings(user_id: str) -> dict:
    """Reset AI settings to defaults for a user."""
    try:
        supabase = get_supabase_client()
        supabase.table("ai_settings").delete().eq("user_id", user_id).execute()
    except Exception as e:
        logger.error(f"Error resetting AI settings in Supabase: {e}")
    
    # Always reset SQLite as well
    try:
        conn = _get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ai_settings WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error resetting AI settings in SQLite: {e}")
    
    return DEFAULT_AI_SETTINGS.copy()
