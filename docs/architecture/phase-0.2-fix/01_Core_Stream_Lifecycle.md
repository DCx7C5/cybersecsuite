# 01: Core Stream Lifecycle (Issues #1, #6)

**Document Purpose:** Complete implementation guide for streaming foundation  
**Covers:** Issue #1 (StreamChunk v2 + Return Type), Issue #6 (StreamController)  
**Week:** 4  
**Blocked By:** Issue #10 (ModelExecutor extraction)  
**Blocks:** Issue #8, #9, Features (SLA Controller, Stream Checkpoint)

**Last Updated:** 2026-04-30

---

## Issue #1: Return Type + StreamChunk v2

### Problem

Currently:
- Not all SDKs return `AsyncIterator[StreamChunk]`
- StreamChunk missing token_estimate field
- Token counting strategy undefined per provider

### Solution

#### 1.1: Return Type Standardization

**All SDKs must return `AsyncIterator[StreamChunk]`**

```python
# OLD (WRONG)
class AnthropicSDK:
    async def stream(self, prompt: str) -> AsyncIterator[str]:  # Returns str chunks
        ...

# NEW (CORRECT)
class AnthropicSDK:
    async def stream(self, prompt: str) -> AsyncIterator[StreamChunk]:
        async for chunk in raw_response:
            yield StreamChunk(
                content=chunk.content,
                finish_reason=chunk.stop_reason,
                token_estimate=self.count_tokens(chunk.content),
                timestamp=datetime.now(),
                provider="anthropic"
            )
```

**Affected SDKs:**
- Anthropic SDK: ✅ returns content blocks
- OpenAI SDK: ✅ returns choice delta
- Ollama SDK: ❌ returns plain text (fix)
- LocalSDK base: ⏭️ create new
- Custom SDKs: All must wrap response

**Implementation:**
- Update each SDK's `stream()` method
- Wrap raw API responses in StreamChunk
- Keep consistent field mapping across providers

#### 1.2: StreamChunk v2 Schema

**File:** `src/core/models/streaming.py` (or existing location)

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class StreamChunk:
    """Standard streaming unit across all providers."""
    
    # Content
    content: str                           # Actual text
    finish_reason: Optional[str] = None   # "stop", "length", "tool_use", etc.
    
    # Tokens
    token_estimate: int = 0               # Estimated/actual token count
    token_confidence: float = 0.95        # 0.0 = pure guess, 1.0 = exact count
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    provider: str = ""                    # "openai", "anthropic", "ollama", etc.
    model: str = ""                       # "gpt-4", "claude-3-sonnet", etc.
    
    # Cost tracking (for SLA Controller)
    cost_tokens_input: int = 0            # Cumulative input tokens
    cost_tokens_output: int = 0           # Cumulative output tokens
    cost_usd: float = 0.0                 # Estimated cost in USD
```

**Key Fields:**

| Field | Type | Purpose | Notes |
|-------|------|---------|-------|
| `content` | str | Actual streamed text | Empty if metadata-only chunk |
| `finish_reason` | Optional[str] | Why stream ended | "stop" = natural, "length" = max_tokens, "tool_use" = function call, etc. |
| `token_estimate` | int | Token count | Post-processing for exact, pre-tokenize for estimate |
| `token_confidence` | float | Accuracy indicator | 1.0 = exact (post-process), 0.9 = high confidence, 0.7 = rough estimate |
| `timestamp` | datetime | When generated | For latency tracking (SLA Controller) |
| `provider` | str | Which provider | "openai", "anthropic", "ollama", "custom", etc. |
| `model` | str | Which model variant | For multi-model fallback tracking |
| `cost_tokens_*` | int | Running totals | Cumulative since stream start |
| `cost_usd` | float | Cost estimate | For budget tracking + SLA degradation |

#### 1.3: Token Counting Strategy (Per-Provider)

**Provider-Specific Behavior:**

| Provider | Behavior | Token Counting | Implementation |
|----------|----------|-----------------|-----------------|
| **OpenAI** | Returns `usage.completion_tokens` post-stream | Exact count available | Count from `usage`, set confidence=1.0 |
| **Anthropic** | Returns usage in response metadata | Exact count + input/output split | Parse from response, set confidence=1.0 |
| **Ollama** | No token counts in stream | Must estimate | Use `tiktoken` or provider tokenizer, confidence=0.85 |
| **LocalSDK** | Depends on underlying model | Varies | Try to extract, fall back to heuristic |

**Implementation Pattern:**

```python
class StreamProcessor:
    async def process_stream(self, sdk_name: str, raw_stream) -> AsyncIterator[StreamChunk]:
        """Wrap raw API stream in StreamChunk with token estimates."""
        
        cumulative_tokens = 0
        
        async for raw_chunk in raw_stream:
            # Provider-specific parsing
            if sdk_name == "openai":
                tokens = self.count_openai_chunk(raw_chunk)
                confidence = 0.95
            elif sdk_name == "anthropic":
                tokens = self.count_anthropic_chunk(raw_chunk)
                confidence = 1.0
            elif sdk_name == "ollama":
                tokens = self.estimate_tokens_ollama(raw_chunk.content)
                confidence = 0.85
            
            cumulative_tokens += tokens
            
            yield StreamChunk(
                content=raw_chunk.content,
                finish_reason=raw_chunk.stop_reason,
                token_estimate=tokens,
                token_confidence=confidence,
                provider=sdk_name,
                cost_tokens_output=cumulative_tokens,
                cost_usd=self.estimate_cost(sdk_name, cumulative_tokens)
            )
```

**Token Accuracy Requirement:**
- ✅ **Exact for OpenAI/Anthropic** (they provide counts)
- ✅ **±10% for Ollama** (estimate acceptable; configurable in config.py)
- ✅ **Configuration:** `StreamChunk.token_confidence` indicates accuracy

---

## Issue #6: StreamController (AsyncIO Queue-based)

### Problem

Current design is **BROKEN**:
```python
# WRONG
async with StreamController() as controller:
    controller.pause()  # ← doesn't work; generator already consuming
    async for chunk in controller.stream(raw_generator):
        await controller.drain()  # ← just a signal, not real pause
```

**Issues:**
- `pause()` doesn't stop generator (it's already pulling)
- `drain()` only signals, doesn't actually stop
- No buffering between producer (SDK) and consumer (caller)
- No backpressure mechanism

### Solution: AsyncIO Queue Architecture

#### 6.1: StreamController Design

**File:** `src/core/streaming/controller.py`

```python
import asyncio
from typing import AsyncIterator, Optional
from dataclasses import dataclass

@dataclass
class StreamControllerConfig:
    """Configuration for StreamController behavior."""
    max_buffer_size: int = 100          # Items in queue before blocking producer
    max_buffer_bytes: int = 10_000_000  # 10MB max memory
    pause_timeout: float = 30.0         # Timeout for pause/resume ops

class StreamController:
    """Manages streaming lifecycle with pause/resume/drain."""
    
    def __init__(self, config: StreamControllerConfig = None):
        self.config = config or StreamControllerConfig()
        self.queue: asyncio.Queue[StreamChunk] = asyncio.Queue(
            maxsize=self.config.max_buffer_size
        )
        self.is_paused = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Start not-paused
        self.total_buffered_bytes = 0
        self.producer_task: Optional[asyncio.Task] = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def wrap_stream(
        self, 
        raw_stream: AsyncIterator[StreamChunk]
    ) -> AsyncIterator[StreamChunk]:
        """
        Wrap a raw stream generator with queueing + pause/resume.
        
        Usage:
            async with StreamController() as controller:
                async for chunk in controller.wrap_stream(raw_stream):
                    # Can pause mid-iteration
                    await controller.pause()
                    # Stream buffers, not consumed
                    await controller.resume()
                    # Stream resumes
        """
        
        # Start producer task (pulls from raw_stream → queue)
        self.producer_task = asyncio.create_task(
            self._producer(raw_stream)
        )
        
        # Consumer loop (pulls from queue → caller)
        try:
            while True:
                # Check for pause signal
                await self.pause_event.wait()  # Blocks if paused
                
                # Get from queue (may block if empty)
                try:
                    chunk = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # Producer finished
                    if self.producer_task.done():
                        break
                    continue
                
                # Track buffer size
                self.total_buffered_bytes -= len(chunk.content.encode('utf-8'))
                
                yield chunk
                
        finally:
            await self.close()
    
    async def _producer(self, raw_stream: AsyncIterator[StreamChunk]):
        """Pull from raw stream and queue chunks."""
        try:
            async for chunk in raw_stream:
                # Block if buffer too large
                chunk_bytes = len(chunk.content.encode('utf-8'))
                if self.total_buffered_bytes + chunk_bytes > self.config.max_buffer_bytes:
                    # Block producer until buffer drains
                    while self.total_buffered_bytes > self.config.max_buffer_bytes * 0.5:
                        await asyncio.sleep(0.1)
                
                # Queue the chunk
                await self.queue.put(chunk)
                self.total_buffered_bytes += chunk_bytes
        
        except Exception as e:
            # Signal producer error via special chunk
            await self.queue.put(StreamChunk(
                content="",
                finish_reason="error",
                provider="controller",
                metadata={"error": str(e)}
            ))
    
    async def pause(self):
        """Pause stream consumption (buffers in queue, producer keeps pulling)."""
        if self.is_paused:
            return
        self.is_paused = True
        self.pause_event.clear()  # Block consumer
    
    async def resume(self):
        """Resume stream consumption (drains queue to consumer)."""
        if not self.is_paused:
            return
        self.is_paused = False
        self.pause_event.set()  # Unblock consumer
    
    async def drain(self) -> int:
        """Flush queued chunks to consumer (non-blocking signal)."""
        # With queue architecture, drain is automatic
        # Just return number of buffered chunks
        return self.queue.qsize()
    
    async def close(self):
        """Graceful shutdown: finish producer, drain queue."""
        if self.producer_task:
            await asyncio.sleep(0)  # Let producer finish current iteration
            self.producer_task.cancel()
            try:
                await self.producer_task
            except asyncio.CancelledError:
                pass
        
        # Drain any remaining items
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
```

#### 6.2: Usage Pattern

```python
# Example: Using StreamController with pause/resume
async def process_with_checkpoint(model_executor, prompt):
    controller = StreamController(
        config=StreamControllerConfig(
            max_buffer_size=500,
            max_buffer_bytes=50_000_000,  # 50MB
            pause_timeout=60.0
        )
    )
    
    async with controller:
        raw_stream = await model_executor.execute_stream(prompt)
        chunks_processed = 0
        
        async for chunk in controller.wrap_stream(raw_stream):
            chunks_processed += 1
            
            # Every 1000 chunks, pause + checkpoint
            if chunks_processed % 1000 == 0:
                print(f"Checkpoint: {chunks_processed} chunks processed")
                await controller.pause()
                
                # Save state
                await save_checkpoint(chunks_processed, model_executor.state)
                
                # Resume
                await controller.resume()
            
            # Process chunk normally
            yield chunk
```

#### 6.3: Backpressure Mechanism

**How Backpressure Works:**

1. **Fast producer, slow consumer:**
   - Queue fills to `max_buffer_size`
   - Producer blocks on `queue.put()` (waits for space)
   - Consumer catches up, queue drains, producer resumes

2. **Pause signal:**
   - Consumer calls `controller.pause()`
   - `pause_event` cleared (blocks consumer in `wrap_stream`)
   - Producer continues pulling (queue buffers up to `max_buffer_bytes`)
   - Memory protected: won't exceed 10MB default

3. **Resume signal:**
   - Consumer calls `controller.resume()`
   - `pause_event` set (unblocks consumer)
   - Consumer drains queue to caller

**Diagram:**
```
Producer (SDK)    Queue    Consumer (wrap_stream)    Caller
     │             │            │                      │
     ├──chunk 1──→  │            │                      │
     ├──chunk 2──→  │            │                      │
     │             │ (size=100)  │                      │
     ├──chunk 100→  │            │                      │
     │ (blocks)     │            │                      │
     │             │            pause()                │
     │             │ (consumers stops pulling)         │
     │             │            buffer grows...         │
     │             │            (up to 10MB)           │
     │ (unblocked)  │            resume()              │
     │             │            (consumer drains)      │
     ├──chunk 101→  │───chunk 1──→                     │
     │             │───chunk 2──→                     │
```

---

## Testing Requirements

### Issue #1 Tests

- [ ] StreamChunk serialization (to JSON/bytes for storage)
- [ ] Token counting accuracy: ±10% vs. real API for 3 models × 3 prompt sizes
- [ ] Provider-specific token parsing (OpenAI, Anthropic, Ollama)
- [ ] Cost estimation accuracy

### Issue #6 Tests

- [ ] Pause/resume safety: concurrent producer + consumer
- [ ] Backpressure: producer blocks when queue full
- [ ] Buffer memory limits: doesn't exceed `max_buffer_bytes`
- [ ] Drain semantics: returns correct queue size
- [ ] Error propagation: producer errors signal via special chunk
- [ ] Graceful shutdown: all chunks flushed, no leaked tasks

---

## Dependencies & Blocking

**This Issue Unblocks:**
- Issue #8 (Token Counting Framework) — uses StreamChunk
- Issue #9 (FallbackChain) — uses StreamController pause
- Feature: Stream Checkpoint — uses StreamController pause + StreamChunk
- Feature: SLA Controller — uses token_estimate from StreamChunk

**This Issue Blocked By:**
- Issue #10 (ModelExecutor extraction) — need ModelExecutor shape before streaming wraps it

---

## Success Criteria

- [ ] All SDKs return `AsyncIterator[StreamChunk]`
- [ ] StreamChunk v2 fields fully populated (token_estimate, cost_usd, etc.)
- [ ] Token counting accuracy meets ±10% requirement (or configured)
- [ ] StreamController pause/resume works without races
- [ ] Backpressure prevents memory bloat (10MB default)
- [ ] Unit tests: 20+ cases (serialization, token counting, pause/resume, backpressure)
- [ ] Integration test: real stream with pause/resume/checkpoint cycle

