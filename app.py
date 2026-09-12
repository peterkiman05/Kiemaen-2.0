import sqlite3
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI(title="Kiemaen AI Advanced")


def init_db():
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = "default"
    model: Optional[str] = "llama3"


FULL_STACK_UI = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiemaen AI - Advanced Mode</title>
    <!-- Marked.js for markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.js"></script>
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
            gap: 12px;
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
            font-size: 0.95rem;
            color: var(--text-main);
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }
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
        .msg-container.assistant { align-self: flex-start; width: 100%; }
        .msg {
            padding: 12px 16px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
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
        .msg.assistant p { margin: 0 0 10px 0; }
        .msg.assistant p:last-child { margin-bottom: 0; }
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
    </style>
</head>
<body>
    <div class="app-wrapper">
        <div class="header-bar">
            <div class="header-left">
                <button class="header-btn" title="Menu">☰</button>
                <div class="title-dropdown" id="model-selector" onclick="switchModel()">llama3 ▾</div>
            </div>
            <div class="header-right">
                <button class="header-btn" title="New Chat" onclick="clearChat()">✏️</button>
                <button class="header-btn" title="Share Chat" onclick="shareChat()">↗</button>
            </div>
        </div>

        <div id="chat-box">
            <div class="msg-container assistant">
                <div class="msg assistant">Advanced Kiemaen AI engine online with real-time token streaming & Markdown parsing. Let's build!</div>
                <div class="response-actions">
                    <button class="action-icon-btn" onclick="toggleReaction(this, '👍')">👍</button>
                    <button class="action-icon-btn" onclick="toggleReaction(this, '👎')">👎</button>
                    <button class="action-icon-btn" onclick="copyMessage(this)">📋</button>
                    <button class="action-icon-btn" onclick="regenerateResponse(this)">🔄</button>
                </div>
            </div>
        </div>

        <div class="pill-input-container">
            <button class="pill-icon-btn" title="Add attachment">+</button>
            <input type="text" id="user-input" placeholder="Ask Kiemaen..." autofocus onkeydown="handleKey(event)">
            <button class="pill-icon-btn" id="mic-btn" title="Voice Input" onclick="toggleVoice()">🎤</button>
            <button class="pill-send-btn" title="Send" onclick="sendMessage()">↑</button>
        </div>
    </div>

    <script>
        let currentSession = "default";
        let currentModel = "llama3";

        function switchModel() {
            const models = ["llama3", "llama3:latest", "mistral", "gemma"];
            let idx = models.indexOf(currentModel);
            currentModel = models[(idx + 1) % models.length];
            document.getElementById('model-selector').textContent = currentModel + " ▾";
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if (!text) return;

            const chatBox = document.getElementById('chat-box');

            // Append User message
            const userContainer = document.createElement('div');
            userContainer.className = 'msg-container user';
            userContainer.innerHTML = `<div class="msg user">${escapeHtml(text)}</div>`;
            chatBox.appendChild(userContainer);

            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            // Append streaming assistant message container
            const aiContainer = document.createElement('div');
            aiContainer.className = 'msg-container assistant';
            const msgBodyId = 'msg-' + Date.now();
            aiContainer.innerHTML = `
                <div class="msg assistant" id="${msgBodyId}"></div>
                <div class="response-actions">
                    <button class="action-icon-btn" onclick="toggleReaction(this, '👍')">👍</button>
                    <button class="action-icon-btn" onclick="toggleReaction(this, '👎')">👎</button>
                    <button class="action-icon-btn" onclick="copyMessage(this)">📋</button>
                    <button class="action-icon-btn" onclick="regenerateResponse(this)">🔄</button>
                </div>
            `;
            chatBox.appendChild(aiContainer);
            chatBox.scrollTop = chatBox.scrollHeight;

            const msgElement = document.getElementById(msgBodyId);
            let fullMarkdownText = "";

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: text, session_id: currentSession, model: currentModel })
                });

                if (!response.ok) throw new Error("Network response was not ok");

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                if (data.token) {
                                    fullMarkdownText += data.token;
                                    msgElement.innerHTML = marked.parse(fullMarkdownText);
                                    chatBox.scrollTop = chatBox.scrollHeight;
                                }
                            } catch (e) {}
                        }
                    }
                }
            } catch (err) {
                msgElement.innerHTML = "Connection error to advanced backend.";
            }
        }

        function clearChat() {
            document.getElementById('chat-box').innerHTML = `
                <div class="msg-container assistant">
                    <div class="msg assistant">New advanced session started.</div>
                    <div class="response-actions">
                        <button class="action-icon-btn" onclick="toggleReaction(this, '👍')">👍</button>
                        <button class="action-icon-btn" onclick="toggleReaction(this, '👎')">👎</button>
                        <button class="action-icon-btn" onclick="copyMessage(this)">📋</button>
                        <button class="action-icon-btn" onclick="regenerateResponse(this)">🔄</button>
                    </div>
                </div>
            `;
        }

        function toggleReaction(btn, type) { btn.classList.toggle('active'); }

        function copyMessage(btn) {
            const msgDiv = btn.closest('.msg-container').querySelector('.msg');
            navigator.clipboard.writeText(msgDiv.innerText).then(() => {
                const orig = btn.textContent;
                btn.textContent = '✓';
                setTimeout(() => btn.textContent = orig, 1200);
            });
        }

        function regenerateResponse(btn) { alert("Regeneration triggered."); }

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
                recognition.onstart = () => { recognizing = true; micBtn.style.color = '#818cf8'; };
                recognition.onresult = (e) => { document.getElementById('user-input').value = e.results[0][0].transcript; };
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

        function escapeHtml(text) {
            const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
    </script>
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
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (req.session_id, "user", req.prompt),
    )
    conn.commit()
    conn.close()

    async def event_generator():
        full_reply = ""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {"model": req.model, "prompt": req.prompt, "stream": True}
                async with client.stream(
                    "POST", "http://127.0.0.1:11434/api/generate", json=payload
                ) as response:
                    async for chunk in response.aiter_text():
                        for line in chunk.splitlines():
                            if line.strip():
                                data = json.loads(line)
                                token = data.get("response", "")
                                full_reply += token
                                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            fallback = f"Echo from Advanced Kiemaen Backend: {req.prompt} (Local LLM server error: {str(e)})"
            full_reply = fallback
            yield f"data: {json.dumps({'token': fallback})}\n\n"

        # Save assistant full reply post-stream
        conn_db = sqlite3.connect("chat_sessions.db")
        cur_db = conn_db.cursor()
        cur_db.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (req.session_id, "assistant", full_reply),
        )
        conn_db.commit()
        conn_db.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
