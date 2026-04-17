#!/usr/bin/env python3
"""
token-optimization-mcp  v0.2.0
================================
Production-ready FastMCP server for token counting, prompt compression,
model routing and semantic caching. Works with Claude Code, Copilot,
Cursor and any MCP-native orchestration platform.

Run:
    uv run main.py            # stdio (default)
    uv run main.py --sse      # SSE  http://127.0.0.1:8001/sse
"""

import argparse
import hashlib
import json
import os
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

import redis as redis_lib
from fastmcp import FastMCP

# ─── Config ─────────────────────────────────────────────────────────────────────────────────
REDIS_URL     = os.getenv("REDIS_URL", "redis://localhost:6379/1")
USE_REDIS     = os.getenv("USE_REDIS", "false").lower() == "true"
CACHE_TTL     = int(os.getenv("CACHE_TTL_SECONDS", 86400))
RATE_LIMIT_PM = int(os.getenv("RATE_LIMIT_PER_MIN", 120))
AUDIT         = os.getenv("AUDIT_LOG_ENABLED", "true").lower() == "true"

# ─── Backend ──────────────────────────────────────────────────────────────────────────────────
_mem: dict[str, dict] = {}
_redis: Optional[redis_lib.Redis] = None
_rate_store: dict[str, list[float]] = defaultdict(list)
_session_savings: dict[str, int] = defaultdict(int)

if USE_REDIS:  # pragma: no cover
    try:
        _redis = redis_lib.from_url(REDIS_URL, decode_responses=True)
        _redis.ping()
        print("✅ Redis backend active")
    except Exception as exc:
        print(f"⚠️  Redis unavailable ({exc}), falling back to in-memory")
        _redis = None

# ─── Helpers ──────────────────────────────────────────────────────────────────────────────────

def _rate_check(client: str = "default") -> None:
    now = time.time()
    _rate_store[client] = [t for t in _rate_store[client] if now - t < 60]
    if len(_rate_store[client]) >= RATE_LIMIT_PM:
        raise PermissionError(f"Rate limit exceeded ({RATE_LIMIT_PM}/min)")
    _rate_store[client].append(now)


def _audit(action: str, **kw) -> None:
    if AUDIT:
        ts = datetime.now(timezone.utc).isoformat()
        print(f"AUDIT [{ts}] {action} | {' '.join(f'{k}={v}' for k, v in kw.items())}")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ─── Token counting (tiktoken-free, calibrated approximation) ──────────────────────
_TOKEN_RATIOS: dict[str, float] = {
    "gpt-4o": 3.8, "gpt-4": 3.9, "gpt-4-turbo": 3.9, "gpt-3.5-turbo": 4.0,
    "claude-3-5-sonnet": 3.7, "claude-3-5-haiku": 3.6, "claude-3-opus": 3.8,
    "gemini-1.5-pro": 3.9, "github:copilot": 3.8,
}
_DEFAULT_RATIO = 3.8


def _estimate_tokens(text: str, model: str = "gpt-4o") -> int:
    ratio = _TOKEN_RATIOS.get(model.lower(), _DEFAULT_RATIO)
    return max(1, round(len(text) / ratio))


# ─── Model catalogue ─────────────────────────────────────────────────────────────────────────────
_MODELS: list[dict[str, Any]] = [
    {"id": "gpt-4o",            "ctx": 128_000,   "cost_per_1k": 0.005,    "quality": 9},
    {"id": "gpt-4o-mini",       "ctx": 128_000,   "cost_per_1k": 0.00015,  "quality": 7},
    {"id": "gpt-4-turbo",       "ctx": 128_000,   "cost_per_1k": 0.01,     "quality": 9},
    {"id": "gpt-3.5-turbo",     "ctx":  16_385,   "cost_per_1k": 0.0005,   "quality": 5},
    {"id": "claude-3-5-sonnet", "ctx": 200_000,   "cost_per_1k": 0.003,    "quality": 9},
    {"id": "claude-3-5-haiku",  "ctx": 200_000,   "cost_per_1k": 0.00025,  "quality": 7},
    {"id": "claude-3-opus",     "ctx": 200_000,   "cost_per_1k": 0.015,    "quality": 10},
    {"id": "gemini-1.5-pro",    "ctx": 1_000_000, "cost_per_1k": 0.00125,  "quality": 8},
    {"id": "gemini-1.5-flash",  "ctx": 1_000_000, "cost_per_1k": 0.000075, "quality": 6},
    {"id": "github:copilot",    "ctx": 128_000,   "cost_per_1k": 0.0,      "quality": 8},
]

# ─── Cache helpers ─────────────────────────────────────────────────────────────────────────────

def _cache_get(key: str) -> Optional[dict]:
    if _redis:
        raw = _redis.get(key)
        return json.loads(raw) if raw else None
    return _mem.get(key)


def _cache_set(key: str, value: dict, ttl: int = CACHE_TTL) -> None:
    if _redis:
        _redis.setex(key, ttl, json.dumps(value))
    else:
        _mem[key] = value


def _cache_delete(key: str) -> bool:
    if _redis:
        return bool(_redis.delete(key))
    return bool(_mem.pop(key, None))


# ─── FastMCP Server ──────────────────────────────────────────────────────────────────────────────
mcp = FastMCP(
    "token-optimization-mcp",
    instructions=(
        "Token optimisation suite. "
        "estimate_tokens → count, compress_prompt → shrink, "
        "route_model → cheapest capable model, "
        "cache_lookup/cache_store → semantic reuse, "
        "analyze_context → conversation health, "
        "savings_report → dashboard."
    ),
)


@mcp.tool(description=(
    "Estimate token count for a text string. "
    "Uses calibrated chars/token ratios per model. "
    "Example: estimate_tokens(text='Hello world', model='gpt-4o') → {tokens: 2, ...}"
))
def estimate_tokens(text: str, model: str = "gpt-4o") -> dict[str, Any]:
    _rate_check()
    count = _estimate_tokens(text, model)
    m = next((x for x in _MODELS if x["id"] == model), None)
    ctx = m["ctx"] if m else 128_000
    return {
        "tokens": count, "model": model, "chars": len(text),
        "chars_per_token": _TOKEN_RATIOS.get(model.lower(), _DEFAULT_RATIO),
        "fits_in_context": count < ctx, "context_window": ctx,
        "context_used_pct": round(count / ctx * 100, 1),
    }


@mcp.tool(description=(
    "Compress a prompt to reduce token usage. "
    "strategy: 'trim' (whitespace/blanks), 'summarize_hint' (mark long sections), "
    "'aggressive' (strip comments, examples, filler). "
    "Returns compressed text + savings stats."
))
def compress_prompt(
    prompt: str,
    strategy: str = "trim",
    target_tokens: Optional[int] = None,
    model: str = "gpt-4o",
) -> dict[str, Any]:
    _rate_check()
    orig_tokens = _estimate_tokens(prompt, model)
    c = prompt

    if strategy == "trim":
        c = re.sub(r"\n{3,}", "\n\n", c)
        c = re.sub(r"[ \t]{2,}", " ", c).strip()
    elif strategy == "summarize_hint":
        def _hint(p: str) -> str:
            return f"[SUMMARIZE: {p[:80].strip()}…]" if len(p) > 200 else p
        c = "\n\n".join(_hint(p) for p in c.split("\n\n"))
    elif strategy == "aggressive":
        c = re.sub(r"#.*$", "", c, flags=re.MULTILINE)
        c = re.sub(r"(for example|e\.g\.|note:|tip:|hint:)[^\n]*\n?", "", c, flags=re.IGNORECASE)
        c = re.sub(r"\n{2,}", "\n", c).strip()
    else:
        return {"error": f"Unknown strategy '{strategy}'. Use trim|summarize_hint|aggressive"}

    comp_tokens = _estimate_tokens(c, model)
    saved = orig_tokens - comp_tokens
    _audit("compress", strategy=strategy, saved=saved)
    return {
        "compressed_prompt": c,
        "original_tokens": orig_tokens, "compressed_tokens": comp_tokens,
        "tokens_saved": saved, "reduction_pct": round(saved / max(orig_tokens, 1) * 100, 1),
        "strategy": strategy, "target_met": target_tokens is None or comp_tokens <= target_tokens,
    }


@mcp.tool(description=(
    "Recommend the cheapest capable model for a task. "
    "Filter by min_quality (1-10, default 7) and max_cost_per_1k USD. "
    "Returns ranked candidates with per-call cost estimate."
))
def route_model(
    estimated_tokens: int,
    min_quality: int = 7,
    max_cost_per_1k: float = 0.01,
    prefer_free: bool = False,
    require_long_context: bool = False,
) -> dict[str, Any]:
    _rate_check()
    candidates = []
    for m in _MODELS:
        if m["quality"] < min_quality: continue
        if m["cost_per_1k"] > max_cost_per_1k: continue
        if m["ctx"] < estimated_tokens: continue
        if require_long_context and m["ctx"] <= 128_000: continue
        cost = round(estimated_tokens / 1000 * m["cost_per_1k"], 6)
        candidates.append({**m, "estimated_cost_usd": cost})

    key_fn = (lambda x: (x["cost_per_1k"], -x["quality"])) if prefer_free \
        else (lambda x: x["cost_per_1k"] * 0.6 - x["quality"] * 0.4)
    candidates.sort(key=key_fn)
    return {
        "recommendation": candidates[0] if candidates else None,
        "all_candidates": candidates,
        "estimated_tokens": estimated_tokens,
    }


@mcp.tool(description=(
    "Look up a cached result by prompt text or pre-computed cache key. "
    "Returns {hit: true, result, tokens_saved} or {hit: false}."
))
def cache_lookup(
    prompt: Optional[str] = None,
    cache_key: Optional[str] = None,
    client_id: str = "default",
) -> dict[str, Any]:
    _rate_check(client_id)
    if not prompt and not cache_key:
        return {"error": "Provide prompt or cache_key"}
    key = cache_key or _hash(prompt)  # type: ignore[arg-type]
    entry = _cache_get(f"cache:{key}")
    if entry:
        _session_savings[client_id] += entry.get("tokens_saved", 0)
        _audit("cache_hit", key=key, client=client_id)
        return {"hit": True, "key": key, **entry}
    _audit("cache_miss", key=key, client=client_id)
    return {"hit": False, "key": key}


@mcp.tool(description=(
    "Store a prompt+result in the cache. "
    "Provide prompt (auto-hashed), result text, tokens_saved estimate, "
    "optional TTL override and metadata dict."
))
def cache_store(
    prompt: str,
    result: str,
    tokens_saved: int,
    ttl_seconds: Optional[int] = None,
    client_id: str = "default",
    metadata: Optional[dict] = None,
) -> dict[str, Any]:
    _rate_check(client_id)
    key = _hash(prompt)
    entry: dict[str, Any] = {
        "result": result, "tokens_saved": tokens_saved,
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "client_id": client_id,
    }
    if metadata:
        entry["metadata"] = metadata
    _cache_set(f"cache:{key}", entry, ttl=ttl_seconds or CACHE_TTL)
    _audit("cache_store", key=key, tokens_saved=tokens_saved, client=client_id)
    return {"stored": True, "key": key, "tokens_saved": tokens_saved,
            "ttl": ttl_seconds or CACHE_TTL, "backend": "redis" if _redis else "in-memory"}


@mcp.tool(description=(
    "Invalidate one or all cache entries. "
    "Pass cache_key to remove one entry, or flush_all=true to wipe everything."
))
def cache_invalidate(
    cache_key: Optional[str] = None,
    flush_all: bool = False,
) -> dict[str, Any]:
    _rate_check()
    if flush_all:
        if _redis:
            keys = _redis.keys("cache:*")
            deleted = len(keys)
            if keys:
                _redis.delete(*keys)
        else:
            deleted = len(_mem)
            _mem.clear()
        _audit("cache_flush", deleted=deleted)
        return {"deleted": deleted, "flush_all": True}
    if cache_key:
        ok = _cache_delete(f"cache:{cache_key}")
        return {"deleted": 1 if ok else 0, "key": cache_key}
    return {"error": "Provide cache_key or flush_all=true"}


@mcp.tool(description=(
    "Analyze a list of chat messages ({role, content}) for token usage and issues. "
    "Detects bloated system prompts, near-full context windows, and repeated content. "
    "Returns per-role breakdown, issues list, and recommendations."
))
def analyze_context(
    messages: list[dict[str, str]],
    model: str = "gpt-4o",
) -> dict[str, Any]:
    _rate_check()
    role_totals: dict[str, int] = defaultdict(int)
    per_msg = []
    for i, msg in enumerate(messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        tokens = _estimate_tokens(content, model)
        role_totals[role] += tokens
        per_msg.append({"index": i, "role": role, "tokens": tokens})

    total = sum(role_totals.values())
    m = next((x for x in _MODELS if x["id"] == model), None)
    ctx = m["ctx"] if m else 128_000

    issues: list[str] = []
    if role_totals.get("system", 0) > 2000:
        issues.append(f"System prompt is large ({role_totals['system']} tokens) — compress it.")
    if total > ctx * 0.8:
        issues.append(f"Context at {round(total/ctx*100)}% of window — risk of truncation.")

    # Repeated word detection
    words = " ".join(m.get("content", "") for m in messages).lower().split()
    freq: dict[str, int] = defaultdict(int)
    for w in words:
        if len(w) > 6:
            freq[w] += 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:3]
    if top and top[0][1] > 8:
        issues.append(f"High repetition: '{top[0][0]}' ×{top[0][1]} — consider deduplicate_messages.")

    return {
        "total_tokens": total, "context_window": ctx,
        "context_used_pct": round(total / ctx * 100, 1),
        "role_breakdown": dict(role_totals), "per_message": per_msg,
        "issues": issues,
        "recommendations": [
            "compress_prompt(strategy='trim') on large messages.",
            "cache_store frequent tool outputs.",
            "route_model with require_long_context=true if needed.",
        ] if issues else ["Context healthy ✅"],
    }


@mcp.tool(description=(
    "Token savings dashboard for the current session. "
    "Shows cache hits, tokens saved, and estimated USD savings per client."
))
def savings_report(model: str = "gpt-4o") -> dict[str, Any]:
    _rate_check()
    m = next((x for x in _MODELS if x["id"] == model), None)
    cost_per_1k = m["cost_per_1k"] if m else 0.005
    report = [
        {"client_id": c, "tokens_saved": s, "usd_saved": round(s / 1000 * cost_per_1k, 6)}
        for c, s in _session_savings.items()
    ]
    grand = sum(_session_savings.values())
    cache_size = len(_redis.keys("cache:*")) if _redis else len(_mem)  # type: ignore[union-attr]
    return {
        "session_savings": report,
        "grand_total_tokens": grand,
        "grand_total_usd": round(grand / 1000 * cost_per_1k, 6),
        "cache_entries": cache_size,
        "backend": "redis" if _redis else "in-memory",
        "model_for_cost_calc": model,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool(description=(
    "Remove duplicate messages from a conversation (keeps last occurrence). "
    "Returns deduplicated list + tokens saved."
))
def deduplicate_messages(
    messages: list[dict[str, str]],
    model: str = "gpt-4o",
) -> dict[str, Any]:
    _rate_check()
    seen: dict[str, int] = {}
    for i, msg in enumerate(messages):
        seen[f"{msg.get('role')}::{msg.get('content', '')}"] = i
    keep = set(seen.values())
    deduped = [m for i, m in enumerate(messages) if i in keep]
    orig  = sum(_estimate_tokens(m.get("content", ""), model) for m in messages)
    after = sum(_estimate_tokens(m.get("content", ""), model) for m in deduped)
    return {
        "deduplicated_messages": deduped,
        "original_count": len(messages), "deduped_count": len(deduped),
        "removed": len(messages) - len(deduped),
        "tokens_before": orig, "tokens_after": after, "tokens_saved": orig - after,
    }


# ─── Entry point ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sse", action="store_true", help="Run as SSE server (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    if args.sse:
        print(f"🚀 token-optimization-mcp SSE → http://{args.host}:{args.port}/sse")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("🚀 token-optimization-mcp running on stdio")
        mcp.run(transport="stdio")
