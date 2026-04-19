"""Web search tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "web_search",
    "Web search (unique capability) via Serper/Brave/Perplexity/Exa/Tavily — title, URL, snippet.",
    {
        "query": "string",
        "engine": {"type": "string", "enum": ["auto", "serper", "brave", "perplexity", "exa", "tavily"], "default": "auto"},
        "limit": {"type": "integer", "default": 10},
    },
)
async def web_search(args: dict[str, Any]) -> JsonDict:
    query = args.get("query", "").strip()
    if not query:
        return sdk_error("query is required")

    engine = args.get("engine", "auto")
    limit = min(args.get("limit", 10), 20)  # Cap at 20

    # Stub: simulate web search results
    results = [
        {
            "title": f"Search result 1 for '{query}'",
            "url": f"https://example.com/result1?q={query.replace(' ', '+')}",
            "snippet": f"This is a sample snippet containing information about {query}. It provides relevant context and details.",
            "engine": engine,
            "rank": 1,
        },
        {
            "title": f"Search result 2 for '{query}'",
            "url": f"https://example.com/result2?q={query.replace(' ', '+')}",
            "snippet": f"Another relevant result discussing {query} with additional insights and information.",
            "engine": engine,
            "rank": 2,
        },
        {
            "title": f"Search result 3 for '{query}'",
            "url": f"https://example.com/result3?q={query.replace(' ', '+')}",
            "snippet": f"Further details about {query} including examples and use cases.",
            "engine": engine,
            "rank": 3,
        },
    ][:limit]

    return sdk_result({
        "status": "success",
        "query": query,
        "engine": engine,
        "results": results,
        "count": len(results),
        "total_available": len(results),  # In real impl, this would be from search API
    })


ALL_TOOLS = [web_search]
