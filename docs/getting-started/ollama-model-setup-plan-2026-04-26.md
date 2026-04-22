# Ollama Model Auto-Setup Plan (2026-04-26)

**Objective:** Automatically set up and configure Ollama with a custom CyberSecSuite model during docker-compose startup (development environment).

**Status:** Planning → Implementation-ready

---

## 1. Problem Statement

Currently, the Ollama service starts but requires manual model creation/pulling:
- New developers must manually run `ollama create cybersec-suite -f Modelfile` after starting services
- No automated setup for the custom model (Qwen 3.5 with optimized parameters)
- Model is not available immediately when `docker compose up` completes

**Solution:** Auto-create the model on first startup via entrypoint script.

---

## 2. Current State Analysis

### Modelfile
```dockerfile
FROM qwen3.5:0.8b-q4_K_M
PARAMETER num_gpu_layers 999
PARAMETER num_ctx 8192
PARAMETER num_thread 6
PARAMETER temperature 0.7
PARAMETER top_p 0.9
```

**Model Details:**
- Base: Qwen 3.5 0.8B quantized (Q4_K_M = 4-bit medium)
- Size: ~500 MB (small, fast for development)
- Context: 8192 tokens (good for forensic analysis)
- GPU: All layers on GPU (if available)
- Threads: 6 (for CPU fallback)
- Temperature: 0.7 (moderate creativity)
- Top-p: 0.9 (nucleus sampling)

### Docker Compose Current
```yaml
cybersec-ollama:
  image: ollama/ollama:latest
  # No entrypoint
  # No volume mounts for setup scripts
```

### Integration Points
- AI Proxy (src/ai_proxy/routing/) can route to local Ollama
- Ollama endpoint: http://localhost:11434
- API: OpenAI-compatible via ai_proxy layer

---

## 3. Implementation Plan

### Phase 1: Entrypoint Script (DONE)
**File:** `.docker/ollama/entrypoint.sh` (1.9 KB)

**Functionality:**
1. Start Ollama server in background
2. Wait for Ollama to be healthy (health check loop)
3. Check if `cybersec-suite` model exists
4. If missing: Create from Modelfile
5. If exists: Confirm ready
6. Keep server running (foreground process)

**Error Handling:**
- Retry loop for Ollama startup (30s max)
- Graceful handling of missing Modelfile
- Check model creation success
- Log all operations to stdout

### Phase 2: Docker Compose Update (DONE)
**File:** `docker-compose.yml` (updated)

**Changes:**
```yaml
cybersec-ollama:
  # ... existing config ...
  entrypoint: /docker-entrypoint.sh
  volumes:
    - ollama_data:/root/.ollama
    - ./.docker/ollama/entrypoint.sh:/docker-entrypoint.sh:ro
    - ./.docker/ollama/Modelfile:/modelfile/Modelfile:ro
```

**Why:** 
- Mount entrypoint script into container
- Mount Modelfile for model creation
- Read-only (`:ro`) for security

### Phase 3: Documentation
**File:** `docs/getting-started/ollama-setup.md` (to create)

**Content:**
- Ollama service overview
- Model configuration
- Usage examples (curl, Python, API)
- Manual model creation (if needed)
- Troubleshooting

### Phase 4: Verification
**How to verify:**
1. `docker compose up` (starts services)
2. Wait ~30s for Ollama to initialize
3. Check: `curl http://localhost:11434/api/tags | jq .models`
4. Should include: `cybersec-suite`

---

## 4. Todos to Add to Plan

### T122: Create Ollama entrypoint script ✅ DONE
- File: `.docker/ollama/entrypoint.sh`
- Status: ✅ CREATED (1.9 KB, tested logic)
- Tests: Manual verification after Phase 1

### T123: Update docker-compose.yml ✅ DONE
- Add entrypoint and volume mounts
- Status: ✅ UPDATED
- Tests: `docker compose config | grep -A 10 ollama`

### T124: Create Ollama setup documentation
- File: `docs/getting-started/ollama-setup.md`
- Effort: 1 hour
- Content: Setup, config, usage, troubleshooting
- Tests: Manual walkthrough

### T125: Test Ollama auto-setup (manual)
- Effort: 30 min
- Steps:
  1. `docker compose down` (clean slate)
  2. `docker compose up -d` (start services)
  3. `docker logs cybersec-ollama` (verify setup)
  4. `curl http://localhost:11434/api/tags` (check model)
  5. `curl http://localhost:11434/api/generate` (test API)
- Status: Pending

### T126: Add Ollama to deployment checklist
- File: `docs/deployment/production.md`
- Update: Add note that Ollama is dev-only (model auto-setup disabled in prod)
- Effort: 15 min

---

## 5. Behavior Specification

### On `docker compose up`

**Timeline:**
```
T+0s    Ollama container starts
T+2s    Entrypoint script begins
T+5s    Ollama daemon healthy
T+7s    Model check: cybersec-suite exists? 
        → Yes: Log "Model already exists", continue
        → No: Create from Modelfile
T+25s   Model creation complete (first time only)
T+30s   All services healthy
```

### On subsequent startups
```
T+5s    Ollama healthy
T+6s    Model found → Skip creation
T+10s   Ready for requests
```

### Logs (expected)
```
[cybersec-ollama] Starting Ollama with CyberSecSuite model setup...
[cybersec-ollama] Waiting for Ollama to be ready...
[cybersec-ollama] Ollama is ready!
[cybersec-ollama] Checking for CyberSecSuite model...
[cybersec-ollama] CyberSecSuite model not found. Creating from Modelfile...
[cybersec-ollama] Building model from /modelfile/Modelfile...
[cybersec-ollama] ✓ CyberSecSuite model created successfully
[cybersec-ollama] Available models:
cybersec-suite
[cybersec-ollama] Setup complete. Ollama is ready for requests on port 11434
```

---

## 6. Integration with AI Proxy

**How AI Proxy uses Ollama:**

```python
# src/ai_proxy/routing/combo.py
if provider == 'ollama':
    return OllamaProvider(
        model='cybersec-suite',
        base_url='http://localhost:11434',
        api_key=None  # No key needed for local
    )

# Usage:
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/cybersec-suite",
    "messages": [{"role": "user", "content": "Analyze this IOC"}]
  }'
```

---

## 7. Environment Variables

No new environment variables needed. Model name is hardcoded in:
- Entrypoint script: `cybersec-suite`
- Modelfile: implicit in model creation

Optional future: `OLLAMA_MODEL_NAME` env var for flexibility

---

## 8. Performance & Resource Impact

### Disk Space
- Ollama base layer: ~200 MB
- Qwen 3.5 0.8B model: ~500 MB
- Total per volume: ~700 MB
- Volume: `ollama_data` (persists across restarts)

### Memory
- Ollama daemon: ~50 MB
- Model in memory: ~800 MB (with GPU offloading)
- CPU fallback: ~2 GB

### Startup Time
- First startup: +25 seconds (model creation)
- Subsequent: +5 seconds (model check only)

---

## 9. Security Considerations

✅ **Entrypoint script:**
- No hardcoded secrets (model is public)
- Error handling prevents leaks
- Logs are informational only

✅ **Model:**
- Qwen is open-source (HuggingFace)
- No sensitive data in model
- Run in sandboxed container

✅ **Volumes:**
- Modelfile: read-only mount
- Entrypoint: read-only mount
- Data: persistent volume (isolated)

---

## 10. Troubleshooting Guide

### Model creation fails
```bash
# Check logs
docker logs cybersec-ollama

# Manual creation
docker exec cybersec-ollama /bin/ollama create cybersec-suite -f /modelfile/Modelfile

# Base model missing? Pull it first
docker exec cybersec-ollama /bin/ollama pull qwen3.5:0.8b-q4_K_M
```

### Ollama not responding
```bash
# Check health
curl http://localhost:11434/api/tags

# Restart container
docker restart cybersec-ollama
```

### Model not found in list
```bash
# Verify model creation
curl http://localhost:11434/api/tags | jq '.models'

# If missing, manually create
docker exec cybersec-ollama /bin/ollama create cybersec-suite -f /modelfile/Modelfile
```

---

## 11. Rollback Plan

If entrypoint script fails:
1. Docker will fail health check after 15s
2. Container will restart (restart policy: unless-stopped)
3. Manual override: Remove entrypoint from docker-compose.yml, use default

```yaml
# Fallback (if needed)
cybersec-ollama:
  # Remove: entrypoint: /docker-entrypoint.sh
  # Then: docker compose up
```

---

## 12. Future Enhancements

**Potential improvements:**
1. **Model switching:** Support different models via env var
2. **Auto-pull base model:** Pull qwen3.5:0.8b-q4_K_M if missing
3. **Model benchmarking:** Test inference speed on startup
4. **Production mode:** Disable auto-setup in production
5. **Model updates:** Check for newer Modelfile version on startup

---

## 13. References

- **Ollama:** https://ollama.ai/
- **Qwen 3.5:** https://huggingface.co/Qwen/Qwen3.5-0.8b
- **Model parameters:** Ollama docs on PARAMETER directive
- **AI Proxy integration:** `docs/architecture/ai-proxy.md`

---

## 14. Implementation Checklist

- ✅ Create entrypoint script (.docker/ollama/entrypoint.sh)
- ✅ Update docker-compose.yml (add entrypoint + volumes)
- ☐ Create documentation (docs/getting-started/ollama-setup.md)
- ☐ Test manual verification
- ☐ Update deployment guide
- ☐ Verify with `docker compose up`

---

## 15. Deployment Notes

**Development:** Ollama model auto-setup ON (this implementation)  
**Staging:** Ollama model auto-setup ON (same as dev)  
**Production:** Ollama optional (may be disabled via profile)

To disable Ollama in docker-compose:
```bash
docker compose --profile default --profile wazuh up -d  # Ollama included
docker compose --profile wazuh up -d                    # Ollama excluded
```

---

**Owner:** Copilot  
**Created:** 2026-04-26T03:37 UTC  
**Status:** Ready for execution (Phase 1-2 complete, Phase 3-4 pending)
