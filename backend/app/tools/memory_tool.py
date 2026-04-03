"""Memory tool for storing and recalling semantic memories."""

import logging
from ..memory.structured_db import get_structured_db
from ..memory.vector_store import VectorStore, get_vector_store

logger = logging.getLogger(__name__)


class MemoryTool:
    """Tool for storing and recalling semantic memories via vector DB."""

    def __init__(self):
        self._vector_store: VectorStore | None = None

    async def _get_store(self) -> VectorStore:
        """Lazy init vector store."""
        if self._vector_store is None:
            self._vector_store = await get_vector_store()
        return self._vector_store

    async def store_memory(
        self,
        content: str,
        context_mode: str = "neutral",
        tags: list[str] | None = None,
    ) -> dict:
        """Store a memory in the vector DB."""
        store = await self._get_store()
        record = await store.store_memory(
            content=content,
            context_mode=context_mode,
            tags=tags or [],
        )
        logger.info(f"Memory stored: {record.id}")
        return {
            "id": record.id,
            "content": record.content,
            "context_mode": record.context_mode,
        }

    async def recall_memories(
        self,
        query: str,
        limit: int = 5,
        context_mode: str | None = None,
    ) -> list[dict]:
        """Recall memories by semantic similarity."""
        store = await self._get_store()
        return await store.search_memories(
            query=query,
            limit=limit,
            context_mode=context_mode,
        )

    async def get_all_memories(
        self,
        limit: int = 50,
    ) -> list[dict]:
        """Get all memories (for console)."""
        store = await self._get_store()
        return await store.get_all_memories(limit=limit)

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        store = await self._get_store()
        return await store.delete_memory(memory_id)


_tool: MemoryTool | None = None


def get_memory_tool() -> MemoryTool:
    """Get memory tool singleton."""
    global _tool
    if _tool is None:
        _tool = MemoryTool()
    return _tool