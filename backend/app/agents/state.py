"""LangGraph state definitions for Donut AI agent.

This module provides:
- Agent state schema for LangGraph
- State management utilities
- Context tracking structures
"""

from typing import TypedDict, Annotated, Sequence, Optional, Any
from datetime import datetime
from operator import add


class AgentState(TypedDict):
    """Main state for the Donut AI agent graph.
    
    This state is passed through all nodes in the LangGraph
    and tracks the complete context of a conversation.
    """
    # User input
    user_message: str
    user_id: str
    session_id: str
    
    # Context mode (business/personal/neutral)
    context_mode: str
    
    # Classified intent
    intent_type: str
    intent_confidence: float
    
    # Conversation history (from ring buffer)
    conversation_history: list[dict[str, str]]
    
    # Extracted entities (for tool execution)
    extracted_entities: dict[str, Any]
    
    # Tool execution result
    tool_result: Optional[str]
    tool_name: Optional[str]
    
    # Final response
    response: str
    
    # Metadata
    action_taken: Optional[str]
    timestamp: str
    
    # Error tracking
    error: Optional[str]


class ToolInput(TypedDict, total=False):
    """Input schema for tool execution."""
    user_id: str
    message: str
    context_mode: str
    entities: dict[str, Any]


class ToolOutput(TypedDict, total=False):
    """Output schema for tool execution."""
    success: bool
    result: Any
    message: str
    error: Optional[str]


class MemoryEntry(TypedDict):
    """Schema for a memory entry."""
    content: str
    context_mode: str
    context_tag: Optional[str]
    importance: float
    embedding: Optional[list[float]]


class TaskEntry(TypedDict, total=False):
    """Schema for a task entry."""
    title: str
    description: str
    priority: str
    due_date: Optional[str]
    context_mode: str
    tags: list[str]


class DiaryEntry(TypedDict, total=False):
    """Schema for a diary entry."""
    content: str
    mood: Optional[str]
    context_mode: str
    tags: list[str]


# ============================================
# State Helper Functions
# ============================================

def create_initial_state(
    user_message: str,
    user_id: str,
    session_id: str,
    context_mode: str = "neutral",
    conversation_history: list[dict[str, str]] = None,
) -> AgentState:
    """Create initial agent state for a new conversation turn.
    
    Args:
        user_message: The user's input message
        user_id: User identifier
        session_id: Session identifier
        context_mode: Current context mode (business/personal/neutral)
        conversation_history: Previous conversation messages
        
    Returns:
        Initialized AgentState
    """
    return AgentState(
        user_message=user_message,
        user_id=user_id,
        session_id=session_id,
        context_mode=context_mode,
        intent_type="unknown",
        intent_confidence=0.0,
        conversation_history=conversation_history or [],
        extracted_entities={},
        tool_result=None,
        tool_name=None,
        response="",
        action_taken=None,
        timestamp=datetime.utcnow().isoformat(),
        error=None,
    )


def update_state_intent(
    state: AgentState,
    intent_type: str,
    confidence: float,
) -> AgentState:
    """Update state with classified intent.
    
    Args:
        state: Current agent state
        intent_type: Classified intent
        confidence: Confidence score
        
    Returns:
        Updated AgentState
    """
    state["intent_type"] = intent_type
    state["intent_confidence"] = confidence
    return state


def update_state_tool_result(
    state: AgentState,
    tool_name: str,
    result: Any,
    action_taken: str = None,
) -> AgentState:
    """Update state with tool execution result.
    
    Args:
        state: Current agent state
        tool_name: Name of the tool executed
        result: Tool execution result
        action_taken: Description of action taken
        
    Returns:
        Updated AgentState
    """
    state["tool_name"] = tool_name
    state["tool_result"] = str(result) if result else None
    state["action_taken"] = action_taken or f"{tool_name}_executed"
    return state


def update_state_response(
    state: AgentState,
    response: str,
) -> AgentState:
    """Update state with final response.
    
    Args:
        state: Current agent state
        response: Final response to user
        
    Returns:
        Updated AgentState
    """
    state["response"] = response
    return state


def update_state_error(
    state: AgentState,
    error: str,
) -> AgentState:
    """Update state with error information.
    
    Args:
        state: Current agent state
        error: Error message
        
    Returns:
        Updated AgentState
    """
    state["error"] = error
    state["response"] = f"Sorry, I encountered an error: {error}"
    return state


def get_state_context(state: AgentState) -> dict:
    """Extract relevant context from state for logging/debugging.
    
    Args:
        state: Current agent state
        
    Returns:
        Dictionary with context information
    """
    return {
        "user_id": state.get("user_id"),
        "session_id": state.get("session_id"),
        "context_mode": state.get("context_mode"),
        "intent_type": state.get("intent_type"),
        "intent_confidence": state.get("intent_confidence"),
        "tool_name": state.get("tool_name"),
        "action_taken": state.get("action_taken"),
        "timestamp": state.get("timestamp"),
        "has_error": state.get("error") is not None,
    }


# ============================================
# Routing Functions
# ============================================

def should_use_tool(state: AgentState) -> bool:
    """Determine if a tool should be used based on intent.
    
    Args:
        state: Current agent state
        
    Returns:
        True if a tool should be executed
    """
    tool_intents = {
        "task_create",
        "task_list",
        "task_complete",
        "diary_entry",
        "diary_read",
        "memory_store",
        "memory_recall",
        "web_search",
    }
    return state.get("intent_type") in tool_intents


def is_simple_interaction(state: AgentState) -> bool:
    """Determine if this is a simple interaction that doesn't need tools.
    
    Args:
        state: Current agent state
        
    Returns:
        True if this is a simple greeting or chit-chat
    """
    simple_intents = {"greeting", "chit_chat", "context_switch"}
    return state.get("intent_type") in simple_intents


def get_tool_for_intent(intent: str) -> Optional[str]:
    """Get the tool name for a given intent.
    
    Args:
        intent: Intent type
        
    Returns:
        Tool name or None
    """
    intent_to_tool = {
        "task_create": "planner",
        "task_list": "planner",
        "task_complete": "planner",
        "diary_entry": "diary",
        "diary_read": "diary",
        "memory_store": "memory",
        "memory_recall": "memory",
        "web_search": "search",
    }
    return intent_to_tool.get(intent)