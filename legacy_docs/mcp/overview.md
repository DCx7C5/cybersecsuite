# MCP Tools — Overview

CyberSecSuite exposes **87 MCP tools** in one server.

---

## Server Summary

| Server       | Tools | Runtime     | Transport | Entry point                              |
|--------------|-------|-------------|-----------|------------------------------------------|
| **cybersec** | 87    | Python (uv) | stdio     | `uv run python -m csmcp.cybersec.server` |

Tool name prefix: `mcp__cybersec__*`

---

## SDK Pattern

All cybersec and dystopian tools use the same pattern:

```python
@tool("tool_name", "description", {"param": {"type": "string", "description": "..."}})
async def _tool_fn(args: dict[str, Any]) -> dict:
    value = args.get("param", "default")
    return sdk_result({"key": value})
```

Tools are explicitly assembled in `src/csmcp/cybersec/__init__.py` — each module exports `ALL_TOOLS` and they are concatenated into a single list passed to `create_sdk_mcp_server()`.

---

## Tool Return Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "{...json-encoded result...}"
    }
  ]
}
```

Error responses include `"error": true` and `"message": "..."` in the result dict.

---

---

## Tool References

- [tools.md](tools.md) — all 87 cybersec tools with parameters and backend notes (includes QoL Output Controls — `qol_get`, `qol_set`, `qol_reset`, `qol_presets`)
- [../configuration/mcp-json.md](../configuration/mcp-json.md) — server wiring
