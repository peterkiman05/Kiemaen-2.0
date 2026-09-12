import os
import sys

print("=" * 60)
print("EXECUTING PRE-PUBLISH BLUEPRINT STAGES")
print("=" * 60)

# ---------------------------------------------------------
# STAGE 1: Sandbox Execution Timeout Protection
# ---------------------------------------------------------
print("\n[STAGE 1] Adding 5-second Execution Timeout to core/code_engine.py...")

with open("core/code_engine.py", "w") as f:
    f.write("""import io
import sys
import math
import json
import signal
import traceback

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Execution timed out (5s limit reached).")

def execute_python(code_string: str, timeout_seconds: int = 5):
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    # Set signal-based execution alarm for Termux resource protection
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

    try:
        cleaned = code_string.replace("```python", "").replace("```", "").strip()
        if cleaned.lower().startswith("run"):
            cleaned = cleaned[3:].strip()

        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool,
                "dict": dict, "enumerate": enumerate, "float": float,
                "int": int, "len": len, "list": list, "map": map,
                "max": max, "min": min, "print": print, "range": range,
                "set": set, "str": str, "sum": sum, "tuple": tuple,
                "zip": zip,
            },
            "math": math,
            "json": json,
        }

        exec(cleaned, safe_globals)
        output = redirected_output.getvalue()
        status = "success"
    except TimeoutException as te:
        output = str(te)
        status = "timeout_error"
    except Exception:
        output = traceback.format_exc()
        status = "error"
    finally:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)  # Disable alarm
        sys.stdout = old_stdout

    return {
        "status": status,
        "output": output if output else "Executed successfully with no output."
    }
""")

print("✓ Timeout protection injected into core/code_engine.py.")

# ---------------------------------------------------------
# STAGE 2: API Key Authentication Middleware in core/router.py
# ---------------------------------------------------------
print("\n[STAGE 2] Building Secure Production FastAPI Router (core/router.py)...")

with open("core/router.py", "w") as f:
    f.write("""from fastapi import FastAPI, Header, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from core.code_engine import execute_python
from core.db import log_execution

API_KEY_NAME = "X-API-Key"
DEFAULT_PRODUCTION_KEY = "sk-termux-agent-secret-key-2026"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == DEFAULT_PRODUCTION_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Unauthorized: Invalid or missing X-API-Key header.")

app = FastAPI(title="Production Multi-Agent Engineering Sandbox API")

class ExecutionRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    return {"status": "online", "sandbox": "secured", "timeout": "5s"}

@app.post("/run")
def run_code_engine(request: ExecutionRequest, api_key: str = Depends(verify_api_key)):
    result = execute_python(request.prompt)
    log_execution(request.prompt, result["status"], result["output"])
    return {
        "status": result["status"],
        "result": result["output"]
    }
""")

print("✓ API Authentication and /health endpoint injected into core/router.py.")

# ---------------------------------------------------------
# STAGE 3: Production Background Process Controller
# ---------------------------------------------------------
print("\n[STAGE 3] Creating Production Launcher Script (start_production.sh)...")

with open("start_production.sh", "w") as f:
    f.write("""#!/bin/bash
export PYTHONDONTWRITEBYTECODE=1

echo "Starting Production Agent Framework Service in Background..."
nohup uvicorn core.router:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
echo $! > server.pid

echo "Service successfully started with PID $(cat server.pid)."
echo "Logs streaming to server.log"
""")

os.system("chmod +x start_production.sh")
print("✓ Created start_production.sh launcher.")

print("\n" + "=" * 60)
print("ALL MISSING PUBLISHING PHASES BUILT SUCCESSFULLY!")
print("=" * 60)
