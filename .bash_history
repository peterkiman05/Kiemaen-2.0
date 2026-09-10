                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        chunk = obj.get("response", "")
                        if chunk:
                            full_reply += chunk
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                        if obj.get("done"):
                            break
        except Exception as e:
            msg = f"Local LLM server unreachable: {str(e)}"
            full_reply = f"Echo from Kiemaen Backend: {req.prompt} ({msg})"
            yield f"data: {json.dumps({'chunk': full_reply})}\n\n"

        save_message(req.session_id, "assistant", full_reply, req.model)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Sessions + history
# ---------------------------------------------------------------------------
@app.get("/api/sessions")
async def list_sessions():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT session_id,
                   MAX(timestamp) AS last_active,
                   (SELECT content FROM messages m2
                     WHERE m2.session_id = m1.session_id AND m2.role = 'user'
                     ORDER BY m2.id ASC LIMIT 1) AS preview,
                   (SELECT model FROM messages m3
                     WHERE m3.session_id = m1.session_id
                     ORDER BY m3.id DESC LIMIT 1) AS model
            FROM messages m1
            GROUP BY session_id
            ORDER BY last_active DESC
            """
        ).fetchall()
    sessions = [dict(r) for r in rows]
    for s in sessions:
        if s["preview"] and len(s["preview"]) > 48:
            s["preview"] = s["preview"][:48] + "…"
    return JSONResponse({"sessions": sessions})


@app.get("/api/history/{session_id}")
async def get_history(session_id: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT role, content, model, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return JSONResponse({"messages": [dict(r) for r in rows]})


@app.get("/api/history/{session_id}/paginated")
async def get_paginated(session_id: str, limit: int = 50, offset: int = 0):
    """Pagination support for lazy-loading older messages (currently unused but available)."""
    messages = get_paginated_history(session_id, limit, offset)
    return JSONResponse({"messages": messages})


# ---------------------------------------------------------------------------
# Models (live from Ollama)
# ---------------------------------------------------------------------------
@app.get("/api/models")
async def list_models():
    try:
        res = await http_client.get(f"{OLLAMA_HOST}/api/tags", timeout=10.0)
        if res.status_code == 200:
            data = res.json()
            names = [m["name"] for m in data.get("models", [])]
            return JSONResponse({"models": names})
        return JSONResponse({"models": [], "error": f"Ollama status {res.status_code}"})
    except Exception as e:
        return JSONResponse({"models": [], "error": str(e)})


# ---------------------------------------------------------------------------
# Document parsing — real text extraction for PDF / DOCX attachments
# ---------------------------------------------------------------------------
MAX_EXTRACTED_CHARS = 6000


@app.post("/api/parse-file")
async def parse_file(file: UploadFile = File(...)):
    name = file.filename or "upload"
    lower = name.lower()
    raw = await file.read()
    text = ""

    try:
        if lower.endswith(".pdf"):
            if PdfReader is None:
                return JSONResponse({"filename": name, "text": "", "error": "pypdf not installed on server"})
            import io
            reader = PdfReader(io.BytesIO(raw))
            pages = [p.extract_text() or "" for p in reader.pages]
            text = "\n".join(pages)
        elif lower.endswith(".docx"):
            if docx_lib is None:
                return JSONResponse({"filename": name, "text": "", "error": "python-docx not installed on server"})
            import io
            document = docx_lib.Document(io.BytesIO(raw))
            text = "\n".join(p.text for p in document.paragraphs)
        else:
            try:
                text = raw.decode("utf-8", errors="ignore")
            except Exception:
                text = ""
    except Exception as e:
        return JSONResponse({"filename": name, "text": "", "error": str(e)})

    text = text.strip()[:MAX_EXTRACTED_CHARS]
    return JSONResponse({"filename": name, "text": text})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
KEOF

echo "✓ Kiemaen ready on http://127.0.0.1:8000"
python3 main.py
pkill -f "python3 main.py"
cp ~/storage/downloads/main_fixed.py ~/main.py
cd ~
python3 main.py
# Stop the server
ctrl+c
# Replace main.py with the super-simple version
cat > main.py << 'EOF'
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import httpx
import json
import sqlite3
from contextlib import closing, asynccontextmanager
from typing import Optional

http_client = None

@asynccontextmanager
async def lifespan(app):
    global http_client
    http_client = httpx.AsyncClient(timeout=None)
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(lifespan=lifespan)

SIMPLE_UI = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Kiemaen</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #07090e; color: #f3f4f6; font-family: system-ui; height: 100vh; }
        .app { display: flex; flex-direction: column; height: 100vh; }
        .header { padding: 12px; border-bottom: 1px solid #26334a; }
        #chat { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 12px; }
        .msg { padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; word-break: break-word; white-space: pre-wrap; max-width: 90%; }
        .user { align-self: flex-end; background: #818cf8; color: #07090e; }
        .ai { align-self: flex-start; background: #151c2c; border: 1px solid #26334a; }
        .input-row { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #26334a; }
        .input-row input { flex: 1; background: #151c2c; border: none; color: #f3f4f6; padding: 8px 12px; border-radius: 6px; font-size: 14px; }
        .input-row button { background: #818cf8; color: #07090e; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
<div class="app">
    <div class="header">Kiemaen AI</div>
    <div id="chat"></div>
    <div class="input-row">
        <input type="text" id="msg" placeholder="Ask..." autofocus>
        <button onclick="go()">↑</button>
    </div>
</div>

<script>
let sid = localStorage.getItem('s') || crypto.randomUUID();
localStorage.setItem('s', sid);

function go() {
    let text = document.getElementById('msg').value.trim();
    if (!text) return;
    document.getElementById('msg').value = '';
    
    let chat = document.getElementById('chat');
    chat.innerHTML += '<div class="msg user">' + text + '</div>';
    chat.innerHTML += '<div class="msg ai" id="r">...</div>';
    chat.scrollTop = chat.scrollHeight;
    
    fetch('/api/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: text, session_id: sid, model: 'llama3.2:1b'})
    }).then(r => r.body.getReader()).then(rdr => {
        let out = '';
        let el = document.getElementById('r');
        function read() {
            rdr.read().then(x => {
                if (x.done) return;
                let s = new TextDecoder().decode(x.value);
                let ln = s.split('\\n\\n');
                for (let l of ln) {
                    if (l.startsWith('data: ')) {
                        try {
                            let o = JSON.parse(l.slice(6));
                            if (o.chunk) { out += o.chunk; el.textContent = out; chat.scrollTop = chat.scrollHeight; }
                        } catch(e) {}
                    }
                }
                read();
            });
        }
        read();
    }).catch(e => {
        document.getElementById('r').textContent = 'Error: ' + e;
    });
}

document.getElementById('msg').onkeypress = e => { if (e.key == 'Enter') go(); };
</script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(SIMPLE_UI)

@app.post("/api/chat/stream")
async def stream(req: dict):
    async def gen():
        try:
            async with http_client.stream("POST", "http://127.0.0.1:11434/api/generate", 
                json={"model": req.get("model", "llama3.2:1b"), "prompt": req.get("prompt", ""), "stream": True}) as r:
                async for line in r.aiter_lines():
                    if line:
                        try:
                            o = json.loads(line)
                            if o.get("response"):
                                yield f"data: {json.dumps({'chunk': o['response']})}\n\n"
                        except: pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(gen(), media_type="

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
curl -X POST "http://127.0.0.1:8000/api/chat" -H "Content-Type: application/json" -d '{"prompt": "Hello!"}'
curl -X POST "http://127.0.0.1:8000/api/chat"      -H "Content-Type: application/json"      -d '{"prompt": "Hello!", "history": []}'
ps aux | grep uvicorn
from fastapi.responses import HTMLResponse
@app.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
@app.get("/dpa", response_class=HTMLResponse)
async def data_processing_agreement():
nano main.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
nano main.py
[200~uvicorn main:app --host 0.0.0.0 --port 8000 --reload
~uvicorn main:app --host 0.0.0.0 --port 8000 --reload
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pkill -f uvicorn
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
nano main.py
[200~pkill -f uvicorn
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
nano main.py
ollama pull llama3.2:1b
ollama pull qwen2.5:7b
pkill -f uvicorn
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
which ollama
pkg install ollama
ollama serve
cp /home/claude/kiemaen/main.py ~/main.py
cd ~
python3 main.py
# Stop old server
pkill -f "python3 main.py"
# Copy debug version
cp /home/claude/kiemaen/main_debug.py ~/main.py
# Start it
cd ~
python3 main.py
cat > main.py << 'ENDCODE'
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import httpx, json
from contextlib import asynccontextmanager

http_client = None

@asynccontextmanager
async def lifespan(app):
    global http_client
    http_client = httpx.AsyncClient(timeout=None)
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(lifespan=lifespan)

UI = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiemaen Debug</title>
    <style>
        body { background: #07090e; color: #f3f4f6; font-family: system-ui; margin: 0; padding: 12px; }
        .box { background: #151c2c; border: 1px solid #26334a; border-radius: 8px; padding: 12px; margin: 12px 0; }
        button { background: #818cf8; color: #07090e; border: none; padding: 10px 16px; border-radius: 6px; font-size: 16px; cursor: pointer; margin: 8px 0; }
        input { background: #151c2c; color: #f3f4f6; border: 1px solid #26334a; padding: 10px; border-radius: 6px; font-size: 14px; width: 100%; max-width: 300px; margin: 8px 0; }
        .msg { padding: 8px 12px; border-radius: 6px; margin: 4px 0; font-size: 13px; }
        .user { background: #818cf8; color: #07090e; }
        .ai { background: #26334a; }
        .error { background: #ef4444; color: white; }
        .success { background: #4ade80; color: #07090e; }
    </style>
</head>
<body>
<h2>Kiemaen - Diagnostics</h2>

<div class="box">
    <b>Is Ollama Running?</b>
    <button onclick="testOllama()">Test Connection</button>
    <div id="status"></div>
</div>

<div class="box">
    <b>Send Message</b>
    <input type="text" id="msg" placeholder="Ask Kiemaen..." autofocus>
    <button onclick="send()">Send</button>
    <div id="chat"></div>
</div>

<script>
function testOllama() {
    let el = document.getElementById('status');
    el.innerHTML = '<div class="msg ai">Checking...</div>';
    fetch('/api/health').then(r => r.json()).then(d => {
        if (d.ok) {
            el.innerHTML = '<div class="msg success">✓ Ollama is running!</div>';
        } else {
            el.innerHTML = '<div class="msg error">✗ Ollama error: ' + d.error + '</div>';
        }
    }).catch(e => {
        el.innerHTML = '<div class="msg error">✗ Cannot reach server: ' + e + '</div>';
    });
}

function send() {
    let text = document.getElementById('msg').value.trim();
    if (!text) return;
    document.getElementById('msg').value = '';
    
    let chat = document.getElementById('chat');
    chat.innerHTML += '<div class="msg user">' + text + '</div>';
    
    let responseEl = document.createElement('div');
    responseEl.className = 'msg ai';
    responseEl.id = 'response';
    responseEl.textContent = 'Streaming...';
    chat.appendChild(responseEl);
    chat.scrollTop = 9999;
    
    fetch('/api/chat/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: text, session_id: 'test', model: 'llama3.2:1b'})
    }).then(r => r.body.getReader()).then(reader => {
        let output = '';
        let decoder = new TextDecoder();
        function read() {
            reader.read().then(({done, value}) => {
                if (done) return;
                let chunk = decoder.decode(value, {stream: true});
                for (let line of chunk.split('\\n\\n')) {
                    if (line.startsWith('data: ')) {
                        try {
                            let obj = JSON.parse(line.slice(6));
                            if (obj.chunk) output += obj.chunk;
                            if (obj.error) output = 'ERROR: ' + obj.error;
                        } catch(e) {}
                    }
                }
                responseEl.textContent = output || '(empty)';
                chat.scrollTop = 9999;
                read();
            });
        }
        read();
    }).catch(e => {
        responseEl.textContent = 'Failed: ' + e;
    });
}

document.getElementById('msg').onkeypress = e => { if (e.key == 'Enter') send(); };
testOllama();
</script>
</body>
</html>
"""

@app.get("/")
async def home():
    return HTMLResponse(UI)

@app.get("/api/health")
async def health():
    try:
        async with http_client.get("http://127.0.0.1:11434/api/tags", timeout=3.0) as r:
            return JSONResponse({"ok": r.status_code == 200, "error": None if r.status_code == 200 else f"HTTP {r.status_code}"})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)})

@app.post("/api/chat/stream")
async def stream(req: Request):
    data = await req.json()
    async def gen():
        try:
            async with http_client.stream("POST", "http://127.0.0.1:11434/api/generate",
                json={"model": data.get("model"), "prompt": data.get("prompt"), "stream": True}, timeout=120) as r:
                async for line in r.aiter_lines():
                    if line:
                        try:
                            obj = json.loads(line)
                            if obj.get("response"):
                                yield f"data: {json.dumps({'chunk': obj['response']})}\n\n"
                        except: pass
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
ENDCODE

python3 main.py
# Stop current server
pkill -f "python3 main.py"
# Copy polished version
cp /home/claude/kiemaen/main_polished.py ~/main.py
# Start it
cd ~
python3 main.py
import sqlite3
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
app = FastAPI(title="Kiemaen AI Advanced")
def init_db():
init_db() class ChatRequest(BaseModel):
<html lang="en">
<head>
</head>
<body>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return FULL_STACK_UI

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", 
if __name__ == "__main__":;     import uvicorn;     uvicorn.run(app, host="127.0.0.1", port=8000)
nano app.py
pip install fastapi uvicorn httpx pydantic
python app.py
ollama --version
curl http://localhost:11434/api/tags
nano main.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
python -m pip install fastapi uvicorn langgraph ollama pydantic
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
