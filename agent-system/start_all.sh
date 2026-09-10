#!/bin/bash

echo "🚀 Restarting Ecosystem Services..."

# Kill old running instances
pkill -f "uvicorn"
pkill -f "python bot.py"
proot-distro login ubuntu -- pkill -f "ollama"

termux-wake-lock
sleep 1

# 1. Start Ollama
echo "1/3 Launching Ollama Engine..."
proot-distro login ubuntu -- ollama serve > /dev/null 2>&1 &
sleep 3

# 2. Start FastAPI Backend
echo "2/3 Launching FastAPI Server (localhost:8000)..."
cd ~/agent-system
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
sleep 2

# 3. Start Telegram Bot
echo "3/3 Launching Async Telegram Bot..."
nohup python bot.py > bot.log 2>&1 &
sleep 1

echo "✅ All processes initiated!"
