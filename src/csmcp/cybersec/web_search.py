"""Web search tools — routes to first available engine: Perplexity > Serper > Brave > Tavily."""
from __future__ import annotations

import os
from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


def _perplexity_key() -> str | None:
    return os.environ.get("PERPLEXITY_API_KEY") or os.environ.get("PERPLEXITY_KEY")


def _serper_key() -> str | None:
    return os.environ.get("SERPER_API_KEY") or os.environ.get("SERPER_KEY")


def _brave_key() -> str | None:
    return os.environ.get("BRAVE_API_KEY") or os.environ.get("BRAVE_KEY")


def _tavily_key() -> str | None:
    return os.environ.get("TAVILY_API_KEY") or os.environ.get("TAVILY_KEY")


async def _perplexity_search(query: str, limit: int) -> list[dict[str, Any]]:
    import httpx
    key = _perplexity_key()
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": query}],
        "search_recency_filter": "month",
        "return_related_questions": False,
        "return_citations": True,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    citations = data.get("citations", [])
    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    results = [
        {"title": f"Result {i+1}", "url": url, "snippet": answer[:300] if i == 0 else "", "engine": "perplexity", "rank": i + 1}
        for i, url in enumerate(citations[:limit])
    ]
    if not results:
        results = [{"title": query, "url": "", "snippet": answer[:500], "engine": "perplexity", "rank": 1}]
    return results


async def _serper_search(query: str, limit: int) -> list[dict[str, Any]]:
    import httpx
    key = _serper_key()
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": key, "Content-Type": "application/json"},
            json={"q": query, "num": limit},
        )
        r.raise_for_status()
        data = r.json()
    organic = data.get("organic", [])
    return [
        {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", ""), "engine": "serper", "rank": i + 1}
        for i, item in enumerate(organic[:limit])
    ]


async def _brave_search(query: str, limit: int) -> list[dict[str, Any]]:
    import httpx
    key = _brave_key()
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": key},
            params={"q": query, "count": limit, "result_filter": "web"},
        )
        r.raise_for_status()
        data = r.json()
    items = data.get("web", {}).get("results", [])
    return [
        {"title": item.get("title", ""), "url": item.get("url", ""), "snippet": item.get("description", ""), "engine": "brave", "rank": i + 1}
        for i, item in enumerate(items[:limit])
    ]


async def _tavily_search(query: str, limit: int) -> list[dict[str, Any]]:
    import httpx
    key = _tavily_key()
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": key, "query": query, "max_results": limit, "search_depth": "basic"},
        )
        r.raise_for_status()
        data = r.json()
    items = data.get("results", [])
    return [
        {"title": item.get("title", ""), "url": item.get("url", ""), "snippet": item.get("content", "")[:300], "engine": "tavily", "rank": i + 1}
        for i, item in enumerate(items[:limit])
    ]


_ENGINE_MAP = {
    "perplexity": (_perplexity_key, _perplexity_search),
    "serper": (_serper_key, _serper_search),
    "brave": (_brave_key, _brave_search),
    "tavily": (_tavily_key, _tavily_search),
}


@tool(
    "web_search",
    "Web search via Perplexity/Serper/Brave/Tavily — title, URL, snippet. Engine auto-selected from available API keys.",
    {
        "query": {"type": "string", "description": "Search query"},
        "engine": {"type": "string", "enum": ["auto", "perplexity", "serper", "brave", "tavily"], "default": "auto"},
        "limit": {"type": "integer", "default": 10},
    },
)
async def web_search(args: dict[str, Any]) -> JsonDict:
    query = args.get("query", "").strip()
    if not query:
        return sdk_error("query is required")

    engine = args.get("engine", "auto")
    limit = min(int(args.get("limit") or 10), 20)

    if engine == "auto":
        order = ["perplexity", "serper", "brave", "tavily"]
        selected = next((e for e in order if _ENGINE_MAP[e][0]()), None)
    else:
        selected = engine if _ENGINE_MAP[engine][0]() else None

    if selected is None:
        return sdk_error(
            "No web search API key found. Set one of: PERPLEXITY_API_KEY, SERPER_API_KEY, BRAVE_API_KEY, TAVILY_API_KEY"
        )

    try:
        _, search_fn = _ENGINE_MAP[selected]
        results = await search_fn(query, limit)
    except Exception as exc:
        return sdk_error(f"Search failed via {selected}: {exc}")

    return sdk_result({
        "status": "success",
        "query": query,
        "engine": selected,
        "count": len(results),
        "results": results,
    })


ALL_TOOLS = [web_search]
