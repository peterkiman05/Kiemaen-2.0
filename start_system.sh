#!/bin/bash

echo "=== Kiemaen AI Control Daemon ==="

# 1. Start Ollama Server
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "[+] Starting Ollama..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 2
else
    echo "[✓] Ollama running."
fi

# 2. Start Uvicorn Backend
if ! pgrep -f "uvicorn main:app" > /dev/null; then
    echo "[+] Starting FastAPI/Uvicorn Server..."
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
    sleep 2
else
    echo "[✓] Uvicorn running."
fi

# 3. Start SSH Tunnel (Pinggy / Localhost.run)
if ! pgrep -f "ssh -R" > /dev/null; then
    echo "[+] Establishing Remote SSH Tunnel..."
    # Using Pinggy HTTPS tunnel (fallback to localhost.run if needed)
    nohup ssh -p 443 -R0:localhost:8000 qr@a.pinggy.io > tunnel.log 2>&1 &
    sleep 4
else
    echo "[✓] Tunnel running."
fi

echo "=== Services Initialized ==="
echo "Fetching Public URL from tunnel log..."
grep -o 'https://[^"]*' tunnel.log | head -n 1 || echo "Check tunnel.log for live URL"
