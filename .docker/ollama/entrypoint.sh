#!/usr/bin/env bash
set -euo pipefail

echo "[cybersec-ollama] Starting Ollama with CyberSecSuite model setup..."

# Start the Ollama server in the background
/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready (health check)
echo "[cybersec-ollama] Waiting for Ollama to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[cybersec-ollama] Ollama is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "[cybersec-ollama] ERROR: Ollama failed to start after 30s"
    kill $OLLAMA_PID || true
    exit 1
  fi
  sleep 1
done

# Check if the custom CyberSecSuite model exists
echo "[cybersec-ollama] Checking for CyberSecSuite model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "cybersec-suite"; then
  echo "[cybersec-ollama] CyberSecSuite model not found. Creating from Modelfile..."
  
  # Create the model from Modelfile
  if [ -f "/modelfile/Modelfile" ]; then
    echo "[cybersec-ollama] Building model from /modelfile/Modelfile..."
    /bin/ollama create cybersec-suite -f /modelfile/Modelfile
    
    if [ $? -eq 0 ]; then
      echo "[cybersec-ollama] ✓ CyberSecSuite model created successfully"
    else
      echo "[cybersec-ollama] ERROR: Failed to create CyberSecSuite model"
      kill $OLLAMA_PID || true
      exit 1
    fi
  else
    echo "[cybersec-ollama] WARNING: Modelfile not found at /modelfile/Modelfile"
    echo "[cybersec-ollama] Model creation skipped. Ensure base model (qwen3.5:0.8b-q4_K_M) is available."
  fi
else
  echo "[cybersec-ollama] ✓ CyberSecSuite model already exists"
fi

# List available models
echo "[cybersec-ollama] Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "[cybersec-ollama] (could not list models)"

echo "[cybersec-ollama] Setup complete. Ollama is ready for requests on port 11434"

# Keep the server running
wait $OLLAMA_PID
