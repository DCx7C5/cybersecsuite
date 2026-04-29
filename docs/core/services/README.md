# Shared Services

**Status**: 🚀 PENDING (Stage 1 Team C/D)

## Components

### RateLimiter
```python
class RateLimiter:
    async def check(self, account_id: str, provider: str) -> bool: ...
    async def record(self, account_id: str, provider: str) -> None: ...
```

### TokenCounter
```python
class TokenCounter:
    async def count(self, messages) -> int: ...
    def estimate(self, text: str) -> int: ...
```

### UsageTracker
```python
class UsageTracker:
    async def record(self, account_id: str, provider: str, tokens: int, cost: float) -> None: ...
    async def get_usage(self, account_id: str, period: str) -> Dict: ...
```

### ToolRunner
```python
class ToolRunner:
    async def execute(self, tool_call: ToolCall) -> ToolResult: ...
```

## From Legacy
src/legacy/ai_proxy/services/

## Cannot Use
(Will document as found)
