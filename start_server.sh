#!/bin/bash
echo "Starting Universal Multi-Agent Engine with Uvicorn..."
pkill -9 -f uvicorn

nohup uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2 > uvicorn.log 2>&1 &
sleep 2

echo "Engine live on http://localhost:8000"
echo "To expose to public web via SSH tunnel, run:"
echo "ssh -R 80:localhost:8000 ssh.localhost.run"
