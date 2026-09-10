#!/bin/bash
export GROQ_API_KEY="${GROQ_API_KEY}"
nohup uvicorn main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
echo "Service successfully started with PID $!."
echo "Logs streaming to server.log"
