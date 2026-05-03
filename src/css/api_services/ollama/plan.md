# Ollama SDK (`ollama`)

**Provider**: Ollama (Local)  
**SDK Package**: `ollama>=0.1.0`  
**Installation**: `ollama pull <model>`  
**OpenAPI Compatible**: ⚠️ Partial (Supports OpenAI-compatible endpoint mode)

---

## SDK Features

| Feature | Supported | Notes |
|---------|-----------|-------|
| Streaming | ✅ | Real-time streaming |
| Vision | ✅ | Multimodal models |
| Tool Use | ⚠️ | Limited support |
| JSON Mode | ✅ | Format parameter |
| Embeddings | ✅ | Embedding models |
| Async/Await | ✅ | Native async |
| Local Only | ✅ | No API calls |
| Free | ✅ | Open-source |

---

## Built-in Tools & Methods

### Core API
- `client.generate()` — Generate text
- `client.embeddings()` — Generate embeddings
- `client.pull()` — Download models
- `client.list()` — List models

### Error Handling
- `ResponseError` — Request failed
- `RequestError` — Connection failed

---

## Model Support

- `llama2` — Meta Llama 2
- `mistral` — Mistral 7B
- `neural-chat` — Intel neural chat
- 100+ community models

---

**Status**: ✅ Complete | **Last Updated**: 2026-05-03
