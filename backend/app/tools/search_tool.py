"""Web search tool using DuckDuckGo."""

import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for web search via DuckDuckGo."""

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict]:
        """Search the web and return results."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
            return formatted
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def news_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[dict]:
        """Search news articles."""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
            
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "source": r.get("source", ""),
                    "date": r.get("date", ""),
                    "snippet": r.get("body", ""),
                })
            return formatted
        except Exception as e:
            logger.error(f"News search error: {e}")
            return []


_tool: SearchTool | None = None


def get_search_tool() -> SearchTool:
    """Get search tool singleton."""
    global _tool
    if _tool is None:
        _tool = SearchTool()
    return _tool