# core/router.py
import sqlite3
import os
import re
import subprocess
import tempfile
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq

router = APIRouter()


def init_db():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            prompt TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM presets")
    if cursor.fetchone()[0] == 0:
        default_presets = [
            (
                "Dev Copilot",
                "You are Kiemaen AI, an advanced local-first personal AI workstation running inside Termux. Be concise, technical, and precise.",
            ),
            (
                "Structural Tutor",
                "You are an expert civil engineering tutor specializing in structural mechanics, beam deflection, and numerical methods. Explain step-by-step with clear math formulas.",
            ),
            (
                "Python Refactorer",
                "You are a senior Python architect. Review code for performance, security flaws, and idiomatic correctness.",
            ),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO presets (name, prompt) VALUES (?, ?)",
            default_presets,
        )
    conn.commit()
    conn.close()


init_db()


def get_history(session_id: str, limit: int = 10):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, content FROM messages
        WHERE session_id = ? ORDER BY id DESC LIMIT ?
    """,
        (session_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]


def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def execute_python_sandbox(code: str) -> str:
    forbidden = ["import os", "import subprocess", "import sys", "shutil", "pathlib"]
    for word in forbidden:
        if word in code:
            return f"Execution Blocked: Security violation detected ({word})."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["python", temp_path], capture_output=True, text=True, timeout=5
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return output if output else "Process completed with no output."
    except subprocess.TimeoutExpired:
        return "Execution Error: Script timed out after 5 seconds."
    except Exception as e:
        return f"Execution Error: {str(e)}"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    model: str = "llama-3.3-70b-versatile"
    system_prompt: str = "You are Kiemaen AI, an advanced local-first personal AI workstation running inside Termux."


class RenameRequest(BaseModel):
    new_session_id: str


@router.get("/health")
async def health_check():
    api_key_configured = bool(os.environ.get("GROQ_API_KEY"))
    return {
        "status": "online",
        "api_key_configured": api_key_configured,
        "environment": "Termux / Python 3.14",
    }


@router.get("/presets")
async def get_presets():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, prompt FROM presets")
    presets = [{"name": row[0], "prompt": row[1]} for row in cursor.fetchall()]
    conn.close()
    return {"presets": presets}


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Groq API key not configured")

    save_message(req.session_id, "user", req.message)
    history = get_history(req.session_id, limit=10)

    client = Groq(api_key=api_key)
    messages = [{"role": "system", "content": req.system_prompt}] + history

    try:
        router_completion = client.chat.completions.create(
            model=req.model,
            messages=[
                {
                    "role": "system",
                    "content": "Analyze prompt. Reply with ONLY CODE if it needs code generation/execution, else REASONING.",
                },
                {"role": "user", "content": req.message},
            ],
            max_tokens=10,
        )
        route = router_completion.choices[0].message.content.strip().upper()
    except Exception:
        route = "REASONING"

    if "CODE" in route:
        try:
            code_res = client.chat.completions.create(
                model=req.model,
                messages=messages
                + [
                    {
                        "role": "user",
                        "content": "Write clean executable Python code inside ```python ``` block.",
                    }
                ],
                temperature=0.5,
            )
            response_text = code_res.choices[0].message.content or ""
            match = re.search(r"```python\n(.*?)\n```", response_text, re.DOTALL)
            code_to_exec = match.group(1) if match else response_text
            exec_output = execute_python_sandbox(code_to_exec)
            final_response = f"{response_text}\n\n**Execution Terminal:**\n```bash\n{exec_output}\n```"

            save_message(req.session_id, "assistant", final_response)

            async def code_stream():
                yield f"data: {json.dumps({'chunk': final_response, 'terminal': exec_output})}\n\n"

            return StreamingResponse(code_stream(), media_type="text/event-stream")
        except Exception as e:
            err_msg = f"Execution setup error: {str(e)}"
            save_message(req.session_id, "assistant", err_msg)

            async def err_stream():
                yield f"data: {json.dumps({'chunk': err_msg, 'terminal': str(e)})}\n\n"

            return StreamingResponse(err_stream(), media_type="text/event-stream")

    async def event_generator():
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=req.model, messages=messages, temperature=0.7, stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    yield f"data: {json.dumps({'chunk': delta})}\n\n"

            save_message(req.session_id, "assistant", full_response)
        except Exception as e:
            err_str = f"\n[Stream Error: {str(e)}]"
            full_response += err_str
            save_message(req.session_id, "assistant", full_response)
            yield f"data: {json.dumps({'chunk': err_str})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history/{session_id}")
async def fetch_history(session_id: str):
    return {"history": get_history(session_id, limit=50)}


@router.get("/sessions")
async def list_sessions():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT session_id FROM messages ORDER BY id DESC")
    sessions = [row[0] for row in cursor.fetchall()]
    conn.close()
    if not sessions:
        sessions = ["default"]
    return {"sessions": sessions}


@router.put("/session/{session_id}/rename")
async def rename_session(session_id: str, req: RenameRequest):
    new_id = req.new_session_id.strip()
    if not new_id:
        raise HTTPException(status_code=400, detail="New session name cannot be empty")
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE messages SET session_id = ? WHERE session_id = ?", (new_id, session_id)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "session_id": new_id}


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
