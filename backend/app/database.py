"""Supabase database client for Donut AI.

This module provides:
- Supabase client initialization
- Database operations for all tables
- pgvector integration for semantic search
- Row Level Security (RLS) support
"""

import logging
from typing import Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

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