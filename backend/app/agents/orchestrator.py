"""LangGraph-based agent orchestrator with dual-context management."""

import json
import logging
from datetime import datetime
from typing import Literal

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from ..config import Settings, get_settings
from ..llm import get_groq_client
from ..memory.ring_buffer import RingBuffer
from ..schemas import ContextMode, IntentType

logger = logging.getLogger(__name__)


# --- LangGraph State Definition ---

class AgentState(TypedDict):
    """State maintained throughout the agent's graph execution."""
    # User input
    user_message: str
    session_id: str

    # Context
    context_mode: ContextMode

    # Classified intent
    intent_type: IntentType
    intent_confidence: float

    # Conversation history (from ring buffer)
    conversation_history: list[dict]

    # Extracted entities (for tool execution)
    extracted_entities: dict

    # Tool execution result
    tool_result: str | None

    # Final response
    response: str

    # Metadata
    action_taken: str | None
    timestamp: str


# --- Node Functions ---

async def classify_intent_node(state: AgentState) -> dict:
    """Node: Classify user intent using Groq."""
    groq = get_groq_client()
    result = await groq.classify_intent(state["user_message"])

    intent_type = result.get("intent", "unknown")
    confidence = result.get("confidence", 0.0)

    # Handle context switch intent specially
    if intent_type == "context_switch":
        # Detect target context from message
        msg = state["user_message"].lower()
        if "business" in msg or "work" in msg:
            new_context = ContextMode.BUSINESS
        elif "personal" in msg or "private" in msg:
            new_context = ContextMode.PERSONAL
        else:
            new_context = ContextMode.NEUTRAL

        return {
            "intent_type": IntentType.CONTEXT_SWITCH,
            "intent_confidence": confidence,
            "context_mode": new_context,
            "response": f"Switched to {new_context.value} mode.",
            "action_taken": f"context_switch:{new_context.value}",
        }

    return {
        "intent_type": IntentType(intent_type),
        "intent_confidence": confidence,
    }


async def load_context_node(state: AgentState) -> dict:
    """Node: Load relevant context from memory and conversation history."""
    session_id = state["session_id"]
    ring_buffer = RingBuffer.get_instance()
    history = ring_buffer.get_session_messages(session_id)

    # Format history for LLM context
    formatted_history = []
    for msg in history:
        formatted_history.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    return {"conversation_history": formatted_history}


async def route_to_tools_node(state: AgentState) -> dict:
    """Node: Route to appropriate tool based on intent."""
    intent = state["intent_type"]

    # Import tools lazily to avoid circular imports
    from ..tools.diary_tool import get_diary_tool
    from ..tools.task_tool import get_task_tool
    from ..tools.search_tool import get_search_tool
    from ..tools.memory_tool import get_memory_tool
    from ..tools.email_tool import get_email_tool
    from ..tools.calendar_tool import get_calendar_tool
    from ..tools.reminder_tool import get_reminder_tool
    from ..tools.appointment_tool import get_appointment_tool

    tool_result = None
    action_taken = None
    response_note = ""
    msg = state["user_message"]

    if intent == IntentType.MEMORY_STORE:
        memory_tool = get_memory_tool()
        result = await memory_tool.store_memory(
            content=msg,
            context_mode=state["context_mode"],
        )
        tool_result = json.dumps(result)
        action_taken = "memory_stored"
        response_note = "I've remembered that for you."

    elif intent == IntentType.MEMORY_RECALL:
        memory_tool = get_memory_tool()
        results = await memory_tool.recall_memories(
            query=msg,
            context_mode=state["context_mode"],
        )
        if results:
            memories_text = "\n".join([r["content"] for r in results[:3]])
            tool_result = memories_text
            response_note = f"Here's what I found: {memories_text}"
        else:
            tool_result = "No relevant memories found."
            response_note = "I don't have any memories related to that."

    elif intent == IntentType.TASK_CREATE:
        task_tool = get_task_tool()
        result = await task_tool.create_task(
            title=msg,
            context_mode=state["context_mode"],
        )
        tool_result = json.dumps(result)
        action_taken = f"task_created:{result.get('id', 'unknown')}"
        response_note = "Task created successfully."

    elif intent == IntentType.TASK_LIST:
        task_tool = get_task_tool()
        tasks = await task_tool.list_tasks(
            context_mode=state["context_mode"],
        )
        if tasks:
            tasks_text = "\n".join([f"- {t['title']} ({t['priority']})" for t in tasks[:10]])
            tool_result = tasks_text
            response_note = f"Here are your tasks:\n{tasks_text}"
        else:
            tool_result = "No tasks found."
            response_note = "You have no pending tasks."

    elif intent == IntentType.DIARY_ENTRY:
        diary_tool = get_diary_tool()
        result = await diary_tool.create_entry(
            content=msg,
            context_mode=state["context_mode"],
        )
        tool_result = json.dumps(result)
        action_taken = f"diary_created:{result.get('id', 'unknown')}"
        response_note = "Diary entry saved."

    elif intent == IntentType.DIARY_READ:
        diary_tool = get_diary_tool()
        entries = await diary_tool.get_entries(
            context_mode=state["context_mode"],
            limit=3,
        )
        if entries:
            entries_text = "\n\n".join([
                f"[{e['created_at'][:10]}]\n{e['content']}"
                for e in entries
            ])
            tool_result = entries_text
            response_note = f"Here are your recent entries:\n\n{entries_text}"
        else:
            tool_result = "No diary entries found."
            response_note = "You haven't written any diary entries yet."

    elif intent == IntentType.WEB_SEARCH:
        search_tool = get_search_tool()
        results = await search_tool.search(query=msg)
        if results:
            results_text = "\n".join([f"- {r['title']}: {r['snippet']}" for r in results[:5]])
            tool_result = results_text
            response_note = f"Here's what I found:\n{results_text}"
        else:
            tool_result = "No results found."
            response_note = "I couldn't find any relevant results."

    elif intent == IntentType.EMAIL_SEND:
        email_tool = get_email_tool()
        result = await email_tool.send_email(
            to="contact@example.com",  # Will be improved with entity extraction
            subject="Message via Donut Receptionist",
            body=msg,
        )
        tool_result = json.dumps(result)
        action_taken = "email_sent"
        response_note = "Email has been sent."

    elif intent == IntentType.EMAIL_READ:
        email_tool = get_email_tool()
        emails = await email_tool.list_emails(max_results=5)
        if emails:
            emails_text = "\n".join([
                f"- [{e.get('sender', 'Unknown')}] {e.get('subject', 'No subject')}"
                for e in emails[:5]
            ])
            tool_result = emails_text
            response_note = f"Recent emails:\n{emails_text}"
        else:
            tool_result = "No emails found."
            response_note = "You have no unread emails."

    elif intent == IntentType.CALENDAR_QUERY:
        cal_tool = get_calendar_tool()
        events = await cal_tool.list_events(max_results=10)
        if events:
            events_text = "\n".join([
                f"- {e['title']}: {str(e['start'])[:16]}"
                for e in events[:10]
            ])
            tool_result = events_text
            response_note = f"Upcoming events:\n{events_text}"
        else:
            tool_result = "No upcoming events."
            response_note = "Your calendar is clear."

    elif intent == IntentType.CALENDAR_CREATE:
        cal_tool = get_calendar_tool()
        from datetime import datetime, timedelta
        start = datetime.now() + timedelta(days=1, hours=2)
        end = start + timedelta(hours=1)
        result = await cal_tool.create_event(
            title=msg,
            start_time=start,
            end_time=end,
        )
        tool_result = json.dumps(result)
        action_taken = "event_created"
        response_note = "Calendar event created."

    elif intent == IntentType.REMINDER_CREATE:
        reminder_tool = get_reminder_tool()
        from datetime import datetime, timedelta
        remind_time = datetime.now() + timedelta(hours=1)
        result = await reminder_tool.create_reminder(
            message=msg,
            remind_at=remind_time,
            context_mode=state["context_mode"].value,
        )
        tool_result = json.dumps(result)
        action_taken = "reminder_created"
        response_note = "Reminder has been set."

    elif intent == IntentType.REMINDER_LIST:
        reminder_tool = get_reminder_tool()
        reminders = await reminder_tool.list_reminders(
            context_mode=state["context_mode"].value,
        )
        if reminders:
            rem_text = "\n".join([
                f"- {r['message']} (at {str(r['remind_at'])[:16]})"
                for r in reminders[:10]
            ])
            tool_result = rem_text
            response_note = f"Active reminders:\n{rem_text}"
        else:
            tool_result = "No active reminders."
            response_note = "You have no pending reminders."

    else:
        # No tool needed - general question or chit-chat
        tool_result = None
        action_taken = None

    return {
        "tool_result": tool_result,
        "action_taken": action_taken,
        "_response_note": response_note,
    }


async def generate_response_node(state: AgentState) -> dict:
    """Node: Generate final response using Groq with full context."""
    groq = get_groq_client()

    context_mode = state["context_mode"].value
    intent = state["intent_type"].value
    tool_result = state.get("tool_result")
    response_note = state.get("_response_note", "")

    # Build system prompt based on context
    system_prompt = f"""You are Donut, an executive function co-pilot.

Current context mode: {context_mode}
- In BUSINESS mode: Be professional, concise, work-focused
- In PERSONAL mode: Be warm, conversational, life-focused
- In NEUTRAL mode: Adapt to the user's tone

Your capabilities include: managing tasks, diary entries, reminders, storing/recalling memories, web search, and calendar management.

Be helpful and proactive. If you executed a tool, acknowledge it naturally.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for msg in state.get("conversation_history", []):
        messages.append(msg)

    # Add tool result context if available
    if tool_result and intent not in [IntentType.CHIT_CHAT.value, IntentType.QUESTION.value]:
        messages.append({
            "role": "system",
            "content": f"Tool execution result: {tool_result}",
        })

    # Add user message
    messages.append({"role": "user", "content": state["user_message"]})

    response = await groq.chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )

    # Save to ring buffer
    ring_buffer = RingBuffer.get_instance()
    ring_buffer.add_message(
        session_id=state["session_id"],
        role="user",
        content=state["user_message"],
        context_mode=state["context_mode"],
    )
    ring_buffer.add_message(
        session_id=state["session_id"],
        role="assistant",
        content=response,
        context_mode=state["context_mode"],
    )

    return {
        "response": response or "I'm sorry, I couldn't process that request.",
        "timestamp": datetime.utcnow().isoformat(),
    }


# --- Edge Functions ---

def route_after_intent(
    state: AgentState,
) -> Literal["route_to_tools", "generate_response"]:
    """Routing decision after intent classification."""
    intent = state["intent_type"]
    tool_intents = {
        IntentType.MEMORY_STORE,
        IntentType.MEMORY_RECALL,
        IntentType.TASK_CREATE,
        IntentType.TASK_LIST,
        IntentType.DIARY_ENTRY,
        IntentType.DIARY_READ,
        IntentType.WEB_SEARCH,
    }

    if intent in tool_intents:
        return "route_to_tools"
    else:
        return "generate_response"


def route_after_tools(state: AgentState) -> Literal["generate_response", END]:
    """After tools execute, always generate response."""
    return "generate_response"


# --- Graph Builder ---

def build_agent_graph() -> StateGraph:
    """Build and compile the LangGraph state machine."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("load_context", load_context_node)
    graph.add_node("route_to_tools", route_to_tools_node)
    graph.add_node("generate_response", generate_response_node)

    # Edges
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "load_context")

    # Conditional routing after context load
    graph.add_conditional_edges(
        "load_context",
        route_after_intent,
        {
            "route_to_tools": "route_to_tools",
            "generate_response": "generate_response",
        },
    )

    # After tools, generate response
    graph.add_conditional_edges(
        "route_to_tools",
        route_after_tools,
        {"generate_response": "generate_response"},
    )

    graph.add_edge("generate_response", END)

    return graph


# Singleton graph instance
_graph = None


def get_agent_graph() -> StateGraph:
    """Get or build the agent graph singleton."""
    global _graph
    if _graph is None:
        _graph = build_agent_graph().compile()
    return _graph


async def run_agent(
    user_message: str,
    context_mode: ContextMode = ContextMode.NEUTRAL,
    session_id: str = "default",
) -> dict:
    """Run the agent with a user message.

    Returns:
        dict with response, intent, action_taken, etc.
    """
    graph = get_agent_graph()

    initial_state: AgentState = {
        "user_message": user_message,
        "session_id": session_id,
        "context_mode": context_mode,
        "intent_type": IntentType.UNKNOWN,
        "intent_confidence": 0.0,
        "conversation_history": [],
        "extracted_entities": {},
        "tool_result": None,
        "response": "",
        "action_taken": None,
        "timestamp": datetime.utcnow().isoformat(),
    }

    result = await graph.ainvoke(initial_state)

    return {
        "response": result.get("response", ""),
        "intent": result.get("intent_type", IntentType.UNKNOWN),
        "context_mode": result.get("context_mode", context_mode),
        "action_taken": result.get("action_taken"),
        "session_id": session_id,
    }