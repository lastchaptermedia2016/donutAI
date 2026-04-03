"""LanceDB vector store for long-term semantic memory."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    import lancedb
    import numpy as np
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    lancedb = None
    np = None
    pa = None

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)

# Schema for LanceDB table
if LANCEDB_AVAILABLE:
    MEMORY_SCHEMA = pa.schema([
        ("id", pa.string()),
        ("content", pa.string()),
        ("context_mode", pa.string()),
        ("tags", pa.list_(pa.string())),
        ("embedding", pa.list_(pa.float32(), 384)),  # all-MiniLM-L6-v2 embedding size
        ("created_at", pa.timestamp("us")),
    ])
else:
    MEMORY_SCHEMA = None


@dataclass
class MemoryRecord:
    """A memory record with semantic embedding."""
    id: str
    content: str
    context_mode: str
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class VectorStore:
    """LanceDB-based semantic memory store."""

    _instance: "VectorStore | None" = None

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or get_settings()
        self._db: lancedb.AsyncConnection | None = None
        self._table = None
        self._embedding_model = None

    @classmethod
    async def create(cls, settings: Settings | None = None) -> "VectorStore":
        """Factory method for async initialization."""
        if not LANCEDB_AVAILABLE:
            logger.warning("LanceDB not available, vector store will be disabled")
            return cls(settings)
            
        instance = cls(settings)
        instance._db = await lancedb.connect_async(
            str(instance._settings.lancedb_path)
        )
        # Create table if not exists
        table_names = await instance._db.table_names()
        if "memories" not in table_names:
            await instance._db.create_table(
                "memories",
                schema=MEMORY_SCHEMA,
            )
        instance._table = await instance._db.open_table("memories")

        # Initialize embedding model
        from sentence_transformers import SentenceTransformer
        instance._embedding_model = SentenceTransformer(
            instance._settings.embedding_model
        )
        return instance

    def _embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        if not LANCEDB_AVAILABLE or self._embedding_model is None:
            return [0.0] * 384  # Return dummy embedding
        embedding = self._embedding_model.encode(text)
        return embedding.tolist()

    async def store_memory(
        self,
        content: str,
        context_mode: str = "neutral",
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        """Store a new memory with embedding."""
        if not LANCEDB_AVAILABLE or self._table is None:
            logger.warning("Vector store not available, memory not stored")
            return MemoryRecord(
                id=datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f"),
                content=content,
                context_mode=context_mode,
                tags=tags or [],
            )
            
        record = MemoryRecord(
            id=datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f"),
            content=content,
            context_mode=context_mode,
            tags=tags or [],
        )

        embedding = self._embed(content)

        await self._table.add([
            {
                "id": record.id,
                "content": record.content,
                "context_mode": record.context_mode,
                "tags": record.tags,
                "embedding": embedding,
                "created_at": record.created_at,
            }
        ])

        logger.info(f"Stored memory: {record.id}")
        return record

    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        context_mode: str | None = None,
    ) -> list[dict]:
        """Search memories by semantic similarity."""
        if not LANCEDB_AVAILABLE or self._table is None:
            return []
            
        query_embedding = self._embed(query)

        # Build search with vector similarity
        search_query = self._table.search(query_embedding)
        search_query = search_query.limit(limit * 3)  # Get more for filtering

        results = await search_query.to_list()

        # Filter by context mode if specified
        filtered = []
        for r in results:
            if context_mode and r.get("context_mode") != context_mode:
                continue
            filtered.append({
                "id": r["id"],
                "content": r["content"],
                "context_mode": r["context_mode"],
                "tags": r.get("tags", []),
                "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
                "score": r.get("_distance", 0.0),
            })
            if len(filtered) >= limit:
                break

        return filtered

    async def get_all_memories(
        self,
        limit: int = 50,
        offset: int = 0,
        context_mode: str | None = None,
    ) -> list[dict]:
        """Get all memories (for console view)."""
        if not LANCEDB_AVAILABLE or self._table is None:
            return []
            
        if context_mode:
            # Use parameterized query to prevent SQL injection
            results = await self._table.search(
                [0.0] * 384,  # Dummy query
            ).where(
                "context_mode = ?", context_mode
            ).limit(limit).to_list()
        else:
            results = await self._table.search(
                [0.0] * 384
            ).limit(limit).to_list()

        return [
            {
                "id": r["id"],
                "content": r["content"],
                "context_mode": r["context_mode"],
                "tags": r.get("tags", []),
                "created_at": r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
            }
            for r in results
        ]

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        if not LANCEDB_AVAILABLE or self._table is None:
            return False
            
        # Use parameterized query to prevent SQL injection
        await self._table.delete("id = ?", memory_id)
        logger.info(f"Deleted memory: {memory_id}")
        return True

    async def get_stats(self) -> dict:
        """Get vector store statistics."""
        if not LANCEDB_AVAILABLE or self._table is None:
            return {"total_memories": 0, "embedding_model": self._settings.embedding_model}
            
        try:
            results = await self._table.search([0.0] * 384).limit(1000).to_list()
            return {
                "total_memories": len(results),
                "embedding_model": self._settings.embedding_model,
            }
        except Exception:
            return {"total_memories": 0, "embedding_model": self._settings.embedding_model}


# Singleton
_store: VectorStore | None = None


async def get_vector_store() -> VectorStore:
    """Get or create vector store singleton."""
    global _store
    if _store is None:
        _store = await VectorStore.create()
    return _store