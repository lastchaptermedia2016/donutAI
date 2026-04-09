"""Groq LLM client with thin abstraction layer."""

import asyncio
import logging
from typing import AsyncIterator

from groq import AsyncGroq

from .config import Settings, get_settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Thin wrapper around Groq async client with retry logic."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._client = AsyncGroq(api_key=self._settings.groq_api_key)

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """Get chat completion from Groq.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to configured llm_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate (defaults to 400 for concise responses)
            stream: Whether to stream the response

        Returns:
            Full response string or async iterator of chunks if streaming
        """
        model = model or self._settings.llm_model
        
        # Default to 400 tokens for concise responses (2-4 sentences)
        # This can be overridden by passing a specific max_tokens value
        if max_tokens is None:
            max_tokens = 400

        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise

        if stream:
            return self._stream_completion(response)
        else:
            return response.choices[0].message.content or ""

    async def _stream_completion(
        self,
        response: AsyncIterator,
    ) -> AsyncIterator[str]:
        """Stream completion chunks."""
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def classify_intent(
        self,
        user_message: str,
    ) -> dict:
        """Classify user intent using the fast intent model.

        Returns a dict with 'intent' and 'confidence' keys.
        """
        system_prompt = """You are an intent classifier for a personal assistant called Donut.
Classify the user's message into ONE of these intents:

- question: Asking for information
- task_create: Creating or adding a task/to-do
- task_list: Wanting to see tasks
- diary_entry: Writing a journal/diary entry
- diary_read: Wanting to read past diary entries
- email_send: Wanting to send an email
- email_read: Wanting to read emails
- calendar_query: Asking about calendar/schedule
- calendar_create: Creating a calendar event
- reminder_create: Setting a reminder
- reminder_list: Wanting to see reminders
- web_search: Wanting to search the web
- memory_store: Storing a memory ("remember that...")
- memory_recall: Recalling a memory ("what did I say about...")
- context_switch: Switching between business/personal mode
- chit_chat: Casual conversation, greetings
- unknown: Cannot determine intent

Respond ONLY with a JSON object: {"intent": "the_intent", "confidence": 0.0-1.0}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            response = await self._client.chat.completions.create(
                model=self._settings.intent_model,
                messages=messages,
                temperature=0.1,
                max_tokens=50,
            )
            content = response.choices[0].message.content or '{"intent": "unknown", "confidence": 0.0}'
            # Simple JSON parsing - in production, use json.loads with error handling
            import json
            result = json.loads(content)
            return result
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {"intent": "unknown", "confidence": 0.0}


# Singleton instance
_client: GroqClient | None = None


def get_groq_client() -> GroqClient:
    """Get or create Groq client singleton."""
    global _client
    if _client is None:
        _client = GroqClient()
    return _client