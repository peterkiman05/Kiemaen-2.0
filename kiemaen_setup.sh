#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "== Kiemaen AI :: Termux one-shot setup =="

# 1. System packages
pkg update -y
pkg install -y python

# 2. Python packages
pip install --upgrade pip
pip install fastapi uvicorn httpx pydantic

# 3. Write main.py directly (no manual file editing needed)
cat > main.py << 'KIEMAEN_EOF'
import json
import sqlite3
import uuid
from contextlib import closing
from typing import Optional

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

DB_PATH = "chat_sessions.db"
OLLAMA_HOST = "http://127.0.0.1:11434"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                model TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


init_db()


def save_message(session_id: str, role: str, content: str, model: Optional[str] = None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, model) VALUES (?, ?, ?, ?)",
            (session_id, role, content, model),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"
    model: Optional[str] = "llama3"


# ---------------------------------------------------------------------------
# Front-end (single-file, matches existing --bg-primary/--bg-secondary theme)
# ---------------------------------------------------------------------------
FULL_STACK_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiemaen AI</title>
    <style>
        :root {
            --bg-primary: #07090e;
            --bg-secondary: #0d1322;
            --bg-card: #151c2c;
            --border-color: #26334a;
            --accent-color: #818cf8;
            --accent-hover: #6366f1;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --online: #4ade80;
        }
        * { box-sizing: border-box; }
        body {
            background: var(--bg-primary);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            height: 100vh;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .app-wrapper {
            display: flex;
            width: 100%;
            max-width: 480px;
            height: 100vh;
            background: var(--bg-secondary);
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 25px rgba(0,0,0,0.8);
            flex-direction: column;
            padding: 12px;
        }

        /* ---- Header ---- */
        .header-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 4px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 8px;
        }
        .header-left, .header-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header-btn {
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 18px;
            cursor: pointer;
            padding: 4px;
            border-radius: 6px;
        }
        .header-btn:hover { background: rgba(255,255,255,0.08); }
        .title-dropdown {
            font-size: 0.9rem;
            color: var(--text-main);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
            background: rgba(255,255,255,0.05);
            padding: 6px 10px;
            border-radius: 20px;
            position: relative;
        }
        .status-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: var(--online);
            box-shadow: 0 0 6px var(--online);
        }

        /* ---- Model dropdown panel ---- */
        #model-panel {
            position: absolute;
            top: 40px;
            left: 0;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            min-width: 200px;
            max-height: 240px;
            overflow-y: auto;
            display: none;
            z-index: 30;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
        #model-panel.open { display: block; }
        .model-item {
            padding: 10px 14px;
            font-size: 13px;
            cursor: pointer;
            border-bottom: 1px solid var(--border-color);
        }
        .model-item:last-child { border-bottom: none; }
        .model-item:hover { background: rgba(255,255,255,0.06); }
        .model-item.active { color: var(--accent-color); font-weight: 600; }

        /* ---- Session drawer ---- */
        #drawer-scrim {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 40;
            display: none;
        }
        #drawer-scrim.open { display: block; }
        #session-drawer {
            position: fixed;
            top: 0; bottom: 0; left: 0;
            width: 78%;
            max-width: 300px;
            background: var(--bg-card);
            z-index: 50;
            transform: translateX(-100%);
            transition: transform 0.25s ease-out;
            display: flex;
            flex-direction: column;
            box-shadow: 4px 0 24px rgba(0,0,0,0.6);
        }
        #session-drawer.open { transform: translateX(0); }
        .drawer-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px;
            border-bottom: 1px solid var(--border-color);
        }
        .drawer-header b { font-size: 15px; }
        #session-list {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
        }
        .session-item {
            padding: 10px 12px;
            border-radius: 10px;
            margin-bottom: 6px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        .session-item:hover { background: rgba(255,255,255,0.05); }
        .session-item.active { background: rgba(129,140,248,0.15); }
        .session-item .s-title {
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .session-item .s-meta {
            font-size: 11px;
            color: var(--text-muted);
        }
        .new-session-btn {
            margin: 8px;
            padding: 10px;
            border-radius: 10px;
            background: var(--accent-color);
            color: var(--bg-primary);
            text-align: center;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
        }

        /* ---- Chat ---- */
        #chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            margin-bottom: 8px;
            scroll-behavior: smooth;
        }
        .msg-container {
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-width: 90%;
        }
        .msg-container.user { align-self: flex-end; }
        .msg-container.assistant { align-self: flex-start; }
        .msg {
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
            white-space: pre-wrap;
        }
        .msg.user {
            background: var(--bg-card);
            color: var(--text-main);
            border-bottom-right-radius: 4px;
            border: 1px solid var(--border-color);
        }
        .msg.assistant {
            background: transparent;
            color: var(--text-main);
            padding-left: 2px;
        }
        .msg.assistant.streaming::after {
            content: '▍';
            animation: blink 1s step-start infinite;
            color: var(--accent-color);
        }
        @keyframes blink { 50% { opacity: 0; } }
        .response-actions {
            display: flex;
            gap: 10px;
            padding-left: 4px;
        }
        .action-icon-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 14px;
            padding: 4px;
            transition: color 0.2s;
        }
        .action-icon-btn:hover { color: var(--text-main); }
        .action-icon-btn.active { color: var(--accent-color); }

        /* ---- Input pill ---- */
        .pill-input-container {
            display: flex;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 32px;
            padding: 6px 12px;
            gap: 8px;
            margin-top: auto;
            margin-bottom: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        }
        .pill-input-container input {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 14px;
            outline: none;
            padding: 8px 4px;
        }
        .pill-icon-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 16px;
            padding: 6px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .pill-icon-btn:hover { background: rgba(255,255,255,0.08); color: var(--text-main); }
        .pill-send-btn {
            background: var(--accent-color);
            color: var(--bg-primary);
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
        }
        .pill-send-btn:hover { background: var(--accent-hover); }
        #file-input { display: none; }
        .attach-chip {
            font-size: 11px;
            color: var(--accent-color);
            padding: 2px 4px;
        }
    </style>
</head>
<body>
    <div id="drawer-scrim" onclick="closeDrawer()"></div>
    <aside id="session-drawer">
        <div class="drawer-header">
            <b>Sessions</b>
            <button class="header-btn" onclick="closeDrawer()">✕</button>
        </div>
        <div class="new-session-btn" onclick="newSession()">+ New Chat</div>
        <div id="session-list"></div>
    </aside>

    <div class="app-wrapper">
        <div class="header-bar">
            <div class="header-left">
                <button class="header-btn" title="Menu" onclick="openDrawer()">☰</button>
                <div class="title-dropdown" onclick="toggleModelPanel()">
                    <span class="status-dot"></span>
                    <span id="model-label">llama3</span>
                    <span>▾</span>
                    <div id="model-panel"></div>
                </div>
            </div>
            <div class="header-right">
                <button class="header-btn" title="New Chat" onclick="newSession()">✏️</button>
                <button class="header-btn" title="Share Chat" onclick="shareChat()">↗</button>
                <button class="header-btn" title="More Options">⋮</button>
            </div>
        </div>

        <div id="chat-box">
            <div class="msg-container assistant">
                <div class="msg assistant">Backend connected with SQLite persistence, live streaming & Ollama routing ready! Type your message below.</div>
            </div>
        </div>

        <div class="pill-input-container">
            <button class="pill-icon-btn" title="Add attachment" onclick="document.getElementById('file-input').click()">+</button>
            <input type="file" id="file-input" onchange="handleFile(event)">
            <input type="text" id="user-input" placeholder="Ask Kiemaen..." autofocus onkeydown="handleKey(event)">
            <button class="pill-icon-btn" id="mic-btn" title="Voice Input" onclick="toggleVoice()">🎤</button>
            <button class="pill-send-btn" id="send-btn" title="Send" onclick="sendMessage()">↑</button>
        </div>
    </div>

    <script>
        let currentSession = localStorage.getItem('kiemaen_session') || crypto.randomUUID();
        let currentModel = 'llama3';
        let lastUserPrompt = '';
        let pendingAttachment = null;
        localStorage.setItem('kiemaen_session', currentSession);

        const chatBox = document.getElementById('chat-box');
        const input = document.getElementById('user-input');

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        function escapeHtml(text) {
            const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        function actionsHtml() {
            return `
                <div class="response-actions">
                    <button class="action-icon-btn" onclick="toggleReaction(this)">👍</button>
                    <button class="action-icon-btn" onclick="toggleReaction(this)">👎</button>
                    <button class="action-icon-btn" onclick="copyMessage(this)">📋</button>
                    <button class="action-icon-btn" onclick="regenerateResponse()">🔄</button>
                </div>`;
        }

        // ---------------- Sending + SSE streaming ----------------
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            lastUserPrompt = text;
            input.value = '';

            const userContainer = document.createElement('div');
            userContainer.className = 'msg-container user';
            let userHtml = `<div class="msg user">${escapeHtml(text)}</div>`;
            if (pendingAttachment) {
                userHtml += `<span class="attach-chip">📎 ${escapeHtml(pendingAttachment.name)}</span>`;
            }
            userContainer.innerHTML = userHtml;
            chatBox.appendChild(userContainer);
            chatBox.scrollTop = chatBox.scrollHeight;

            await streamAssistantReply(text);
            pendingAttachment = null;
        }

        async function streamAssistantReply(promptText) {
            const aiContainer = document.createElement('div');
            aiContainer.className = 'msg-container assistant';
            aiContainer.innerHTML = `<div class="msg assistant streaming" id="live-msg"></div>`;
            chatBox.appendChild(aiContainer);
            chatBox.scrollTop = chatBox.scrollHeight;
            const liveMsg = aiContainer.querySelector('#live-msg');

            let finalPrompt = promptText;
            if (pendingAttachment) {
                finalPrompt = `${promptText}\\n\\n[Attached file: ${pendingAttachment.name}]\\n${pendingAttachment.content}`;
            }

            try {
                const res = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: finalPrompt, session_id: currentSession, model: currentModel })
                });

                if (!res.ok || !res.body) {
                    liveMsg.textContent = 'Connection error to backend.';
                    liveMsg.classList.remove('streaming');
                    return;
                }

                const reader = res.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let full = '';

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    buffer += decoder.decode(value, { stream: true });

                    const frames = buffer.split('\\n\\n');
                    buffer = frames.pop();
                    for (const frame of frames) {
                        const line = frame.trim();
                        if (!line.startsWith('data:')) continue;
                        const payload = line.slice(5).trim();
                        if (payload === '[DONE]') continue;
                        try {
                            const obj = JSON.parse(payload);
                            if (obj.chunk) {
                                full += obj.chunk;
                                liveMsg.textContent = full;
                                chatBox.scrollTop = chatBox.scrollHeight;
                            }
                            if (obj.error) {
                                full += `\\n[${obj.error}]`;
                                liveMsg.textContent = full;
                            }
                        } catch (e) { /* ignore partial frame */ }
                    }
                }

                liveMsg.classList.remove('streaming');
                liveMsg.id = '';
                aiContainer.insertAdjacentHTML('beforeend', actionsHtml());
            } catch (err) {
                liveMsg.textContent = 'Connection error to backend.';
                liveMsg.classList.remove('streaming');
            }
        }

        function regenerateResponse() {
            if (!lastUserPrompt) return;
            streamAssistantReply(lastUserPrompt);
        }

        // ---------------- Sessions ----------------
        function openDrawer() {
            document.getElementById('session-drawer').classList.add('open');
            document.getElementById('drawer-scrim').classList.add('open');
            loadSessions();
        }
        function closeDrawer() {
            document.getElementById('session-drawer').classList.remove('open');
            document.getElementById('drawer-scrim').classList.remove('open');
        }

        async function loadSessions() {
            const list = document.getElementById('session-list');
            list.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted)">Loading...</div>';
            try {
                const res = await fetch('/api/sessions');
                const data = await res.json();
                list.innerHTML = '';
                data.sessions.forEach(s => {
                    const item = document.createElement('div');
                    item.className = 'session-item' + (s.session_id === currentSession ? ' active' : '');
                    item.innerHTML = `
                        <span class="s-title">${escapeHtml(s.preview || 'New chat')}</span>
                        <span class="s-meta">${escapeHtml(s.model || '')} · ${escapeHtml(s.last_active || '')}</span>`;
                    item.onclick = () => switchSession(s.session_id);
                    list.appendChild(item);
                });
                if (data.sessions.length === 0) {
                    list.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted)">No sessions yet.</div>';
                }
            } catch (e) {
                list.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted)">Could not load sessions.</div>';
            }
        }

        function newSession() {
            currentSession = crypto.randomUUID();
            localStorage.setItem('kiemaen_session', currentSession);
            chatBox.innerHTML = `
                <div class="msg-container assistant">
                    <div class="msg assistant">New session started.</div>
                </div>`;
            closeDrawer();
        }

        async function switchSession(sessionId) {
            currentSession = sessionId;
            localStorage.setItem('kiemaen_session', currentSession);
            closeDrawer();
            chatBox.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted)">Loading history...</div>';
            try {
                const res = await fetch(`/api/history/${sessionId}`);
                const data = await res.json();
                chatBox.innerHTML = '';
                data.messages.forEach(m => {
                    const container = document.createElement('div');
                    container.className = 'msg-container ' + m.role;
                    let html = `<div class="msg ${m.role}">${escapeHtml(m.content)}</div>`;
                    if (m.role === 'assistant') html += actionsHtml();
                    container.innerHTML = html;
                    chatBox.appendChild(container);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (e) {
                chatBox.innerHTML = '<div style="padding:12px;font-size:12px;color:var(--text-muted)">Could not load history.</div>';
            }
        }

        // ---------------- Models ----------------
        async function toggleModelPanel() {
            const panel = document.getElementById('model-panel');
            const isOpen = panel.classList.contains('open');
            if (isOpen) { panel.classList.remove('open'); return; }
            panel.innerHTML = '<div style="padding:10px;font-size:12px;color:var(--text-muted)">Loading models...</div>';
            panel.classList.add('open');
            try {
                const res = await fetch('/api/models');
                const data = await res.json();
                panel.innerHTML = '';
                if (data.models.length === 0) {
                    panel.innerHTML = '<div style="padding:10px;font-size:12px;color:var(--text-muted)">No models found. Is Ollama running?</div>';
                }
                data.models.forEach(name => {
                    const item = document.createElement('div');
                    item.className = 'model-item' + (name === currentModel ? ' active' : '');
                    item.textContent = name;
                    item.onclick = (ev) => {
                        ev.stopPropagation();
                        currentModel = name;
                        document.getElementById('model-label').textContent = name;
                        panel.classList.remove('open');
                    };
                    panel.appendChild(item);
                });
            } catch (e) {
                panel.innerHTML = '<div style="padding:10px;font-size:12px;color:var(--text-muted)">Could not reach Ollama.</div>';
            }
        }
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('model-panel');
            if (panel.classList.contains('open') && !e.target.closest('.title-dropdown')) {
                panel.classList.remove('open');
            }
        });

        // ---------------- Misc actions ----------------
        function toggleReaction(btn) { btn.classList.toggle('active'); }

        function copyMessage(btn) {
            const msgDiv = btn.closest('.msg-container').querySelector('.msg');
            navigator.clipboard.writeText(msgDiv.textContent).then(() => {
                const orig = btn.textContent;
                btn.textContent = '✓';
                setTimeout(() => btn.textContent = orig, 1200);
            });
        }

        let recognizing = false;
        function toggleVoice() {
            const micBtn = document.getElementById('mic-btn');
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                alert("Speech recognition not supported.");
                return;
            }
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            if (!recognizing) {
                recognition.onstart = () => { recognizing = true; micBtn.style.color = 'var(--accent-color)'; };
                recognition.onresult = (e) => { input.value = e.results[0][0].transcript; };
                recognition.onend = () => { recognizing = false; micBtn.style.color = ''; };
                recognition.start();
            }
        }

        function shareChat() {
            if (navigator.share) {
                navigator.share({ title: 'Kiemaen AI', url: window.location.href });
            } else {
                alert("Link copied!");
            }
        }

        // ---------------- Attachments ----------------
        function handleFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                pendingAttachment = { name: file.name, content: e.target.result.slice(0, 4000) };
                input.placeholder = `Attached: ${file.name} — add a message...`;
                input.focus();
            };
            if (file.type.startsWith('text/') || /\\.(md|py|js|json|csv|txt|html|css)$/i.test(file.name)) {
                reader.readAsText(file);
            } else {
                pendingAttachment = { name: file.name, content: '[Binary file — content not extracted]' };
                input.placeholder = `Attached: ${file.name} — add a message...`;
            }
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return FULL_STACK_UI


# ---------------------------------------------------------------------------
# Non-streaming endpoint (kept for compatibility / fallback clients)
# ---------------------------------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    save_message(req.session_id, "user", req.prompt, req.model)

    reply = ""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": req.model, "prompt": req.prompt, "stream": False},
            )
            if res.status_code == 200:
                reply = res.json().get("response", "Received empty response from model.")
            else:
                reply = f"Ollama Error: Status {res.status_code}"
    except Exception as e:
        reply = f"Echo from Kiemaen Backend: {req.prompt} (Local LLM server unreachable: {str(e)})"

    save_message(req.session_id, "assistant", reply, req.model)
    return JSONResponse({"reply": reply, "session_id": req.session_id})


# ---------------------------------------------------------------------------
# Streaming endpoint (SSE-style frames over a POST body, consumed via fetch())
# ---------------------------------------------------------------------------
@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    save_message(req.session_id, "user", req.prompt, req.model)

    async def event_generator():
        full_reply = ""
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_HOST}/api/generate",
                    json={"model": req.model, "prompt": req.prompt, "stream": True},
                ) as res:
                    if res.status_code != 200:
                        msg = f"Ollama Error: Status {res.status_code}"
                        yield f"data: {json.dumps({'error': msg})}\n\n"
                        full_reply = msg
                    else:
                        async for line in res.aiter_lines():
                            if not line:
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


# ---------------------------------------------------------------------------
# Models (live from Ollama)
# ---------------------------------------------------------------------------
@app.get("/api/models")
async def list_models():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"{OLLAMA_HOST}/api/tags")
            if res.status_code == 200:
                data = res.json()
                names = [m["name"] for m in data.get("models", [])]
                return JSONResponse({"models": names})
            return JSONResponse({"models": [], "error": f"Ollama status {res.status_code}"})
    except Exception as e:
        return JSONResponse({"models": [], "error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
KIEMAEN_EOF

echo "== Files written. Starting Kiemaen AI on http://127.0.0.1:8000 =="
echo "Open that address in your phone browser. Ctrl+C to stop."
python3 main.py
