#!/bin/bash

echo "=== Starting Multi-Agent Pipeline ==="

# 1. Start Ollama in background if not already running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[+] Starting Ollama server..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
else
    echo "[✓] Ollama is already running."
fi

# 2. Verify Ollama port availability
until curl -s http://localhost:11434/ > /dev/null; do
    echo "[...] Waiting for Ollama to become ready..."
    sleep 2
done
echo "[✓] Ollama is ready on port 11434."

# 3. Start Uvicorn / FastAPI server if not running
if ! pgrep -f "uvicorn" > /dev/null; then
    echo "[+] Starting FastAPI app..."
    uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    sleep 3
else
    echo "[✓] FastAPI app is already running."
fi

echo "=== System Ready for Requests ==="
