# Ollama Setup Guide — Local LLM Installation & Configuration

**Purpose:** Configure local Ollama instance for CyberSecSuite development and testing
**Supported Platforms:** Linux, macOS (Intel/Apple Silicon), Windows (WSL2)
**Python Integration:** Async health checks, model discovery, GPU detection
**Documentation Updated:** Phase 1 Backend Infrastructure

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Ollama](#running-ollama)
5. [Model Management](#model-management)
6. [Integration with CyberSecSuite](#integration-with-cybersecsuite)
7. [Health Checks](#health-checks)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Specifications

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **RAM** | 8 GB | Recommended 16 GB+ for larger models |
| **Disk** | 50 GB free | Models consume 4-13 GB each |
| **GPU** | Optional | Supported: NVIDIA, AMD, Apple Silicon, Intel Arc |
| **CPU** | 4+ cores | Performance improves with more cores |
| **Network** | 512 Mbps | For model downloads & API requests |

### Supported Operating Systems

- **Linux:** Ubuntu 20.04+, Fedora 35+, Debian 11+
- **macOS:** 11.0+ (Intel & Apple Silicon M1/M2/M3/M4)
- **Windows:** Windows 11 22H2+ (via WSL2)

### GPU Support

| GPU Type | Driver Required | VRAM | Model Support |
|----------|-----------------|------|---------------|
| **NVIDIA** | CUDA 12.0+ | 6 GB+ | Most models, optimal performance |
| **AMD** | ROCm 5.6+ | 8 GB+ | Supported, slightly slower than NVIDIA |
| **Apple Silicon** | Native (M-series) | Shared with RAM | Supported, good performance |
| **Intel Arc** | Intel Extension for PyTorch | 8 GB+ | Limited support, emerging |

---

## Installation

### Linux (Ubuntu/Debian)

```bash
# Download Ollama installer
curl -fsSL https://ollama.ai/install.sh | sh

# Or use package manager (Ubuntu 22.04+)
sudo apt-get install ollama

# Verify installation
ollama --version
# Expected output: ollama version 0.x.x
```

### macOS (Intel & Apple Silicon)

```bash
# Download DMG installer
# Visit: https://ollama.ai/download/mac

# Or use Homebrew
brew install ollama

# Launch Ollama
# Either: Open Applications > Ollama
# Or: ollama serve

# Verify installation
ollama --version
```

### Windows (WSL2)

```bash
# Enable WSL2 (PowerShell as Administrator)
wsl --install

# Install Ubuntu 22.04 in WSL2
wsl --install -d Ubuntu-22.04

# In WSL2 Ubuntu terminal, follow Linux installation:
curl -fsSL https://ollama.ai/install.sh | sh

# Enable GPU support (NVIDIA)
# Install NVIDIA CUDA Toolkit for WSL2
# Download: https://developer.nvidia.com/cuda-downloads

# Start Ollama in WSL2
ollama serve
```

### Docker (All Platforms)

```bash
# Pull Ollama Docker image
docker pull ollama/ollama

# Run with GPU support (NVIDIA)
docker run --gpus all -d -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama ollama/ollama

# Run CPU only
docker run -d -v ollama:/root/.ollama -p 11434:11434 \
  --name ollama ollama/ollama

# Check status
docker logs ollama
```

---

## Configuration

### Environment Variables

Create `~/.ollama/environment` or set in shell:

```bash
# HTTP server configuration
export OLLAMA_HOST=0.0.0.0:11434

# Model storage location (default: ~/.ollama/models)
export OLLAMA_MODELS=/path/to/models

# GPU device selection (NVIDIA)
export CUDA_VISIBLE_DEVICES=0

# Logging level (debug, info, warn, error)
export OLLAMA_DEBUG=false

# Number of parallel requests
export OLLAMA_NUM_PARALLEL=1

# Context window size
export OLLAMA_NUM_CTX=2048
```

### Configuration File (systemd)

**File:** `/etc/systemd/system/ollama.service`

```ini
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_MODELS=/var/lib/ollama/models"
User=ollama
Group=ollama

[Install]
WantedBy=multi-user.target
```

**Enable service:**
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
sudo systemctl status ollama
```

### Configuration File (Docker Compose)

**File:** `docker-compose.ollama.yml`

```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
      - OLLAMA_DEBUG=false
    volumes:
      - ollama-models:/root/.ollama
      - ./models:/models
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ollama-models:
```

**Start:**
```bash
docker-compose -f docker-compose.ollama.yml up -d
docker-compose -f docker-compose.ollama.yml logs -f
```

---

## Running Ollama

### Start Server (Manual)

```bash
# Foreground (see logs)
ollama serve

# Expected output:
# time=2026-04-26T10:30:15.123Z level=INFO msg="Listening on 127.0.0.1:11434"
```

### Start Server (Background)

```bash
# Linux/macOS
nohup ollama serve > ~/.ollama/ollama.log 2>&1 &

# Check process
ps aux | grep ollama

# View logs
tail -f ~/.ollama/ollama.log
```

### Stop Server

```bash
# Find PID
lsof -i :11434

# Kill process
kill -9 <PID>

# Or on systemd
sudo systemctl stop ollama
```

### Verify Server is Running

```bash
# Check HTTP endpoint
curl http://localhost:11434

# Expected response:
# Ollama is running

# Check API health
curl http://localhost:11434/api/tags

# Expected response:
# {"models":[]}  (empty if no models downloaded)
```

---

## Model Management

### Available Models

Browse models: https://ollama.ai/library

| Model | Size | VRAM | Speed | Use Case |
|-------|------|------|-------|----------|
| **mistral** | 7B | 4 GB | Fast | General-purpose, best speed/quality |
| **llama2** | 7B/13B | 4/8 GB | Medium | Common baseline, good quality |
| **neural-chat** | 7B | 4 GB | Fast | Optimized for conversations |
| **codellama** | 7B/13B | 4/8 GB | Medium | Code generation & explanation |
| **openchat** | 7B | 4 GB | Fast | Efficient, good performance |
| **dolphin-mixtral** | 8x7B | 20 GB | Slow | Top-tier quality, very slow |

### Pull Models

```bash
# Pull model (auto-downloads to ~/.ollama/models)
ollama pull mistral

# Pull specific version
ollama pull llama2:13b

# List downloaded models
ollama list

# Output:
# NAME              ID              SIZE      MODIFIED
# mistral:latest    a2e8e58d8d18    4.1 GB    2 minutes ago
# llama2:13b        2c51f66d34c1    7.4 GB    1 hour ago
```

### Remove Models

```bash
# Delete model
ollama rm mistral

# Verify deletion
ollama list
```

### Model Configuration (Modelfile)

Create custom model: `Modelfile`

```modelfile
FROM mistral

# Set parameters
PARAMETER temperature 0.7
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER num_ctx 2048

# System prompt
SYSTEM "You are a security analyst. Provide concise, technical responses about CVEs and vulnerabilities."

# Custom templates (optional)
TEMPLATE """{{ if .System }}<s>[INST] <<SYS>>
{{ .System }}
<</SYS>>

{{ end }}{{ .Prompt }} [/INST]"""
```

**Build and use:**
```bash
ollama create cybersec-analyst -f Modelfile
ollama run cybersec-analyst "What is CVE-2024-1234?"
```

---

## Integration with CyberSecSuite

### Python Health Check

**File:** `src/ai_proxy/health.py` provides async health checking:

```python
from ai_proxy.health import check_ollama_health, detect_gpu

# Check Ollama instance health
health = await check_ollama_health(
    base_url="http://localhost:11434",
    timeout_seconds=5
)

print(f"Status: {health.status}")
print(f"Models: {health.models}")
print(f"GPU: {health.gpu_info.provider if health.gpu_info else 'None'}")

# Detect GPU info
gpu_info = await detect_gpu()
print(f"GPU Provider: {gpu_info.provider}")
print(f"GPU Memory: {gpu_info.memory_gb} GB")
```

### API Endpoints

**Health check endpoint:**
```bash
curl http://localhost:8000/v1/health/ollama
```

**Response:**
```json
{
  "status": "healthy",
  "base_url": "http://localhost:11434",
  "models": ["mistral:latest"],
  "response_time_ms": 45,
  "gpu_info": {
    "provider": "NVIDIA",
    "available": true,
    "memory_gb": 12
  }
}
```

### Configuration in FastAPI

**File:** `src/ai_proxy/config.py`

```python
from pydantic import BaseSettings

class OllamaConfig(BaseSettings):
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 30
    health_check_interval: int = 60
    default_model: str = "mistral:latest"
    
    class Config:
        env_prefix = "OLLAMA_"

config = OllamaConfig()
```

**Environment setup:**
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_TIMEOUT_SECONDS=30
export OLLAMA_DEFAULT_MODEL=mistral:latest
```

---

## Health Checks

### Manual Verification

```bash
# 1. Check server is listening
nc -zv localhost 11434
# Expected: Connection successful

# 2. Check API response
curl -i http://localhost:11434/

# 3. List models
curl http://localhost:11434/api/tags

# 4. Generate a response (test inference)
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:latest",
    "prompt": "Why is Python good for security?",
    "stream": false
  }'

# 5. Check performance
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:latest",
    "prompt": "Say \"OK\"",
    "stream": false
  }' | jq '.eval_duration'
```

### Automated Health Check (Python)

```python
import asyncio
from src.ai_proxy.health import check_ollama_health

async def main():
    health = await check_ollama_health()
    
    if health.status == "healthy":
        print("✅ Ollama is healthy")
        print(f"   Models: {health.models}")
        print(f"   Response time: {health.response_time_ms}ms")
    else:
        print(f"❌ Ollama health check failed: {health.error}")

asyncio.run(main())
```

### Integration with FastAPI Startup

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check Ollama health
    health = await check_ollama_health()
    if health.status != "healthy":
        raise RuntimeError(f"Ollama not available: {health.error}")
    print("✅ Ollama health check passed")
    
    yield
    
    # Shutdown: Cleanup if needed
    print("Shutting down Ollama connection")

app = FastAPI(lifespan=lifespan)
```

---

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port 11434
lsof -i :11434

# Kill the process
kill -9 <PID>

# Or use different port
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

### Issue: Out of Memory (OOM)

**Symptom:** Ollama crashes with "Cannot allocate memory"

```bash
# Check available RAM
free -h

# Reduce model size or context window
export OLLAMA_NUM_CTX=1024  # Reduce from 2048

# Or limit GPU memory
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_NUM_GPU=1

# Run smaller model
ollama run mistral  # 7B model, 4 GB VRAM
```

### Issue: GPU Not Detected

**Symptom:** Ollama runs on CPU only, very slow

```bash
# Check NVIDIA GPU
nvidia-smi
# If no output, GPU drivers not installed

# Install NVIDIA drivers (Ubuntu)
sudo ubuntu-drivers autoinstall
sudo reboot

# Install CUDA Toolkit (Ubuntu)
wget https://developer.nvidia.com/compute/cuda/12.0/local_installers/cuda_12.0.0_525.60.13_linux.run
sudo sh cuda_12.0.0_525.60.13_linux.run

# Check CUDA
nvcc --version
```

**For AMD GPU:**
```bash
# Install ROCm
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install rocm-dkms

# Verify
rocm-smi
```

### Issue: Models Not Downloading

**Symptom:** `ollama pull mistral` hangs or fails

```bash
# Check internet connection
curl https://registry.ollama.ai/

# Try manual download with wget
wget https://registry.ollama.ai/library/mistral

# Check disk space
df -h ~/.ollama/

# If full, clean old models
ollama rm llama2:13b
```

### Issue: Slow Inference

**Symptom:** Responses take >30 seconds

**Diagnosis:**
```bash
# Check GPU utilization
nvidia-smi -l 1  # Update every second

# Check model precision
ollama list
# Look for model size — larger models (13B+) are slower on CPU

# Profile a single request
time ollama run mistral "What is 2+2?"
```

**Solutions:**
1. Use smaller model (7B instead of 13B)
2. Enable GPU support (check `nvidia-smi`)
3. Reduce context window: `OLLAMA_NUM_CTX=1024`
4. Increase temperature for faster, less accurate responses

### Issue: Connection Refused from Python

**Symptom:** `httpx.ConnectError: Unable to connect to http://localhost:11434`

```python
# Add retry logic
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def connect_ollama():
    async with httpx.AsyncClient() as client:
        return await client.get("http://localhost:11434")

# Or check if Ollama is running
import socket
def is_ollama_running():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 11434))
    sock.close()
    return result == 0
```

### Issue: Model Inference Gives Inconsistent Results

**Symptom:** Same prompt gives different answers every time

```bash
# Set temperature to 0 for deterministic output
# In Modelfile or API request
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "mistral:latest",
    "prompt": "2+2=",
    "temperature": 0,
    "stream": false
  }'
```

### Performance Optimization Tips

1. **Use quantized models** (smaller, faster)
   ```bash
   ollama pull mistral:7b  # Default quantization
   ```

2. **Increase parallel requests** (if more VRAM)
   ```bash
   export OLLAMA_NUM_PARALLEL=2
   ```

3. **Pre-load model on startup**
   ```bash
   ollama run mistral "Warm up"
   ```

4. **Use faster models for simple tasks**
   ```bash
   # Fast: neural-chat, openchat (7B)
   # Medium: llama2-7b, mistral (7B)
   # Slow: dolphin-mixtral, llama2-13b (13B+)
   ```

---

## References

- **Ollama Website:** https://ollama.ai/
- **Model Library:** https://ollama.ai/library
- **API Documentation:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **GitHub Issues:** https://github.com/ollama/ollama/issues
- **Discord Community:** https://discord.gg/ollama

---

## Support & Feedback

**Issue Report:** `/home/daen/Projects/cybersecsuite/issues`
**Documentation Update:** Submit PR to `/docs/getting-started/ollama-setup.md`
