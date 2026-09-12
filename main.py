import os
import io
import sqlite3
import httpx
import asyncio
from fastapi import FastAPI, Response, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from gtts import gTTS

app = FastAPI()

DB_FILE = "chat.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            persona TEXT DEFAULT 'tactical'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class TtsRequest(BaseModel):
    text: str

class ResearchRequest(BaseModel):
    topic: str

# Persona System Prompts
PERSONAS = {
    "tactical": "You are KIM, an elite military-grade tactical AI assistant modeled after advanced holographic interfaces. Be concise, precise, professional, and address the user as Commander or Operator.",
    "coder": "You are KIM's Code Execution Unit. You write clean, production-ready code, isolate bugs instantly, and provide robust technical explanations with complete snippets.",
    "researcher": "You are KIM's Deep Research Engine. You synthesize thorough, highly detailed, and deeply analytical reports with clear sections and structured breakdowns."
}

@app.get("/api/history")
async def get_history():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, persona FROM messages ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        
        history = [{"role": row[0], "content": row[1], "persona": row[2]} for row in rows]
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")

class ChatRequest(BaseModel):
    prompt: str
    persona: str = "tactical"

async def chat_completions(message: str = Form(...), persona: str = Form("tactical"), file: UploadFile = File(None)):
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set.")
        
        final_message = message
        if file:
            file_bytes = await file.read()
            try:
                file_content = file_bytes.decode('utf-8', errors='ignore')
                final_message = f"[Attached File: {file.filename}]\n{file_content}\n\nUser Directive: {message}"
            except Exception:
                final_message = f"[Attached Binary File: {file.filename}]\nUser Directive: {message}"

        system_prompt = PERSONAS.get(persona, PERSONAS["tactical"])

        # Load recent chat history
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 10")
        past_rows = cursor.fetchall()
        
        messages_payload = [{"role": "system", "content": system_prompt}]
        for r, c in reversed(past_rows):
            messages_payload.append({"role": r, "content": c})
        messages_payload.append({"role": "user", "content": final_message})

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "openai/gpt-oss-20b",
                    "messages": messages_payload
                },
                timeout=45.0
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            
            cursor.execute("INSERT INTO messages (role, content, persona) VALUES (?, ?, ?)", ("user", final_message, persona))
            cursor.execute("INSERT INTO messages (role, content, persona) VALUES (?, ?, ?)", ("assistant", reply, persona))
            conn.commit()
            conn.close()
            
            return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research")
async def deep_research(req: ResearchRequest):
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set.")
        
        prompt = f"Conduct an exhaustive deep research synthesis on the following topic: {req.topic}. Structure the output with a Executive Summary, Core Technical Analysis, Key Considerations, and Strategic Recommendations."
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "openai/gpt-oss-20b",
                    "messages": [{"role": "system", "content": PERSONAS["researcher"]}, {"role": "user", "content": prompt}]
                },
                timeout=60.0
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            
            data = resp.json()
            report = data["choices"][0]["message"]["content"]
            return {"report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(req: TtsRequest):
    try:
        tts = gTTS(text=req.text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return Response(fp.read(), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat", response_class=HTMLResponse)
async def chat_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>KIM // Advanced HUD & Canvas Interface</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {
                --hud-cyan: #00e5ff;
                --hud-dim: rgba(0, 229, 255, 0.15);
                --hud-border: rgba(0, 229, 255, 0.35);
                --hud-bg: rgba(5, 12, 18, 0.9);
                --hud-text: #c0f0ff;
            }
            body {
                background: #02060a;
                color: var(--hud-text);
                font-family: 'Courier New', Courier, monospace, sans-serif;
                margin: 0; padding: 0;
                display: flex; flex-direction: column; height: 100vh;
                overflow: hidden;
            }
            body::before {
                content: " ";
                display: block; position: absolute;
                top: 0; left: 0; bottom: 0; right: 0;
                background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
                z-index: 999; background-size: 100% 4px, 6px 100%;
                pointer-events: none;
            }
            #header {
                background: var(--hud-bg);
                border-bottom: 1px solid var(--hud-border);
                padding: 10px 20px;
                display: flex; justify-content: space-between; align-items: center;
                box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
                z-index: 10;
            }
            .hud-title {
                font-weight: bold; letter-spacing: 2px; color: var(--hud-cyan);
                text-shadow: 0 0 8px var(--hud-cyan);
                font-size: 14px;
            }
            .reactor-container {
                display: flex; align-items: center; gap: 10px;
            }
            .arc-reactor {
                width: 26px; height: 26px; border-radius: 50%;
                border: 2px solid var(--hud-cyan);
                position: relative;
                box-shadow: 0 0 10px var(--hud-cyan), inset 0 0 8px var(--hud-cyan);
                display: flex; align-items: center; justify-content: center;
            }
            .arc-core {
                width: 8px; height: 8px; background: var(--hud-cyan);
                border-radius: 50%; box-shadow: 0 0 12px var(--hud-cyan);
                animation: core-pulse 2s infinite ease-in-out;
            }
            @keyframes core-pulse {
                0% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 5px var(--hud-cyan); }
                50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 20px var(--hud-cyan); }
                100% { transform: scale(0.8); opacity: 0.5; box-shadow: 0 0 5px var(--hud-cyan); }
            }
            .arc-reactor.active {
                animation: reactor-spin 1.5s linear infinite;
            }
            @keyframes reactor-spin {
                0% { border-color: var(--hud-cyan); box-shadow: 0 0 15px var(--hud-cyan); }
                50% { border-color: #ff0055; box-shadow: 0 0 20px #ff0055; }
                100% { border-color: var(--hud-cyan); box-shadow: 0 0 15px var(--hud-cyan); }
            }
            .toolbar-controls { display: flex; gap: 10px; align-items: center; }
            select {
                background: rgba(0, 0, 0, 0.7); color: var(--hud-cyan);
                border: 1px solid var(--hud-border); padding: 4px 8px; font-family: monospace;
                border-radius: 2px; outline: none; font-size: 11px;
            }
            #main-layout {
                display: flex; flex: 1; overflow: hidden; position: relative;
            }
            #chat-pane {
                flex: 1; display: flex; flex-direction: column; overflow: hidden;
                border-right: 1px solid transparent; transition: all 0.3s ease;
            }
            #chat-pane.split { border-right: 1px solid var(--hud-border); flex: 1.2; }
            #chat-box {
                flex: 1; overflow-y: auto; padding: 20px;
                display: flex; flex-direction: column; gap: 15px;
                background: radial-gradient(circle at center, #051322 0%, #02060a 100%);
            }
            /* Canvas Pane */
            #canvas-pane {
                flex: 1; display: none; flex-direction: column; background: #03080e;
                padding: 15px; box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.05);
                position: relative;
            }
            #canvas-pane.active { display: flex; }
            .canvas-header {
                display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid var(--hud-border); padding-bottom: 8px; margin-bottom: 10px;
                font-size: 12px; color: var(--hud-cyan); letter-spacing: 1px;
            }
            #canvas-editor {
                flex: 1; background: #010408; border: 1px solid var(--hud-border);
                color: #e0f0ff; padding: 12px; font-family: monospace; font-size: 12px;
                resize: none; outline: none; border-radius: 2px; line-height: 1.4;
            }
            .message-container {
                display: flex; flex-direction: column; max-width: 85%; position: relative;
            }
            .user-container { align-self: flex-end; }
            .assistant-container { align-self: flex-start; width: 100%; max-width: 90%; }
            .message {
                padding: 12px 16px; border-radius: 4px;
                line-height: 1.5; word-break: break-word; white-space: pre-wrap;
                font-size: 13px; letter-spacing: 0.5px;
            }
            .user {
                background: rgba(0, 123, 255, 0.2);
                border: 1px solid rgba(0, 123, 255, 0.5);
                color: #ffffff;
                box-shadow: 0 0 10px rgba(0, 123, 255, 0.2);
            }
            .assistant {
                background: var(--hud-bg);
                border: 1px solid var(--hud-border);
                color: var(--hud-text);
                box-shadow: 0 0 12px rgba(0, 229, 255, 0.08);
                width: 100%; position: relative;
            }
            .assistant::before, .user::before {
                content: ""; position: absolute; top: 0; left: 0;
                width: 6px; height: 6px; border-top: 2px solid var(--hud-cyan); border-left: 2px solid var(--hud-cyan);
            }
            .assistant::after, .user::after {
                content: ""; position: absolute; bottom: 0; right: 0;
                width: 6px; height: 6px; border-bottom: 2px solid var(--hud-cyan); border-right: 2px solid var(--hud-cyan);
            }
            .btn-row { display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap; }
            .action-btn {
                background: rgba(0, 229, 255, 0.1);
                color: var(--hud-cyan); border: 1px solid var(--hud-border);
                font-size: 10px; font-family: monospace; letter-spacing: 1px;
                padding: 4px 10px; border-radius: 2px; cursor: pointer;
                text-transform: uppercase; transition: all 0.2s;
            }
            .action-btn:hover { background: var(--hud-cyan); color: #02060a; box-shadow: 0 0 8px var(--hud-cyan); }
            #input-area {
                display: flex; padding: 12px; background: var(--hud-bg);
                border-top: 1px solid var(--hud-border); gap: 8px; z-index: 10; align-items: center;
            }
            input[type="text"] {
                flex: 1; padding: 10px; border-radius: 2px;
                border: 1px solid var(--hud-border); background: rgba(0, 0, 0, 0.6);
                color: var(--hud-cyan); outline: none; font-family: monospace; font-size: 13px;
            }
            input[type="text"]:focus { border-color: var(--hud-cyan); box-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }
            .file-upload-lbl {
                background: rgba(0, 229, 255, 0.1); color: var(--hud-cyan);
                border: 1px solid var(--hud-border); padding: 8px 10px; border-radius: 2px;
                cursor: pointer; font-size: 12px; transition: all 0.2s;
            }
            .file-upload-lbl:hover { background: var(--hud-cyan); color: #02060a; }
            #file-input { display: none; }
            button.main-btn {
                background: rgba(0, 229, 255, 0.2); color: var(--hud-cyan);
                border: 1px solid var(--hud-cyan); padding: 10px 18px; border-radius: 2px;
                cursor: pointer; font-family: monospace; font-weight: bold; letter-spacing: 1px;
                transition: all 0.2s;
            }
            button.main-btn:hover { background: var(--hud-cyan); color: #02060a; box-shadow: 0 0 10px var(--hud-cyan); }
            button.kim-toggle {
                background: rgba(40, 167, 69, 0.2); color: #28a745;
                border: 1px solid #28a745; padding: 10px 14px; border-radius: 2px;
                cursor: pointer; font-family: monospace; font-weight: bold; letter-spacing: 1px;
            }
            button.kim-toggle.active {
                background: rgba(220, 53, 69, 0.2); color: #dc3545;
                border-color: #dc3545; box-shadow: 0 0 10px #dc3545;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
    </head>
    <body onload="loadHistory()">
        <div id="header">
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="reactor-container">
                    <div class="arc-reactor" id="reactor-icon">
                        <div class="arc-core"></div>
                    </div>
                </div>
                <span class="hud-title">KIM // GEMINI-INTEGRATED HUD</span>
            </div>
            <div class="toolbar-controls">
                <select id="persona-select">
                    <option value="tactical">GEM: Tactical HUD</option>
                    <option value="coder">GEM: Python Dev Expert</option>
                    <option value="researcher">GEM: Deep Research Specialist</option>
                </select>
                <button class="action-btn" onclick="triggerDeepResearch()">[ DEEP RESEARCH ]</button>
                <span id="status-text" style="font-size:11px; color:var(--hud-cyan);">SYS: READY</span>
            </div>
        </div>
        <div id="main-layout">
            <div id="chat-pane">
                <div id="chat-box"></div>
                <div id="input-area">
                    <label class="file-upload-lbl" for="file-input" title="Upload File">📁<span id="file-indicator"></span></label>
                    <input type="file" id="file-input" onchange="updateFileIndicator()" />
                    <input type="text" id="user-input" placeholder="Enter directive or activate voice mode..." autofocus />
                    <button class="kim-toggle" id="kim-btn" onclick="toggleKimMode()">KIM: OFF</button>
                    <button class="main-btn" onclick="sendMessage()">TRANSMIT</button>
                </div>
            </div>
            <div id="canvas-pane">
                <div class="canvas-header">
                    <span id="canvas-title">WORKSPACE CANVAS // REPO DRAFT</span>
                    <button class="action-btn" onclick="toggleCanvas(false)">[ CLOSE CANVAS ]</button>
                </div>
                <textarea id="canvas-editor"></textarea>
            </div>
        </div>
        <script>
            let kimActive = false;
            let recognition = null;
            let isProcessing = false;
            let silenceTimer = null;
            let transcriptBuffer = '';

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onresult = function(event) {
                    let interim = '';
                    let final = '';
                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            final += event.results[i][0].transcript;
                        } else {
                            interim += event.results[i][0].transcript;
                        }
                    }

                    transcriptBuffer = final || interim;
                    document.getElementById('user-input').value = transcriptBuffer;

                    clearTimeout(silenceTimer);
                    if (transcriptBuffer.trim().length > 0) {
                        silenceTimer = setTimeout(() => {
                            if (kimActive && !isProcessing && transcriptBuffer.trim().length > 0) {
                                try { recognition.stop(); } catch(e) {}
                                sendMessage();
                            }
                        }, 700);
                    }
                };

                recognition.onerror = function() {
                    if (kimActive && !isProcessing) {
                        setTimeout(startListening, 1000);
                    }
                };

                recognition.onend = function() {
                    if (kimActive && !isProcessing) {
                        setTimeout(startListening, 300);
                    }
                };
            }

            async function loadHistory() {
                try {
                    const res = await fetch('/api/history');
                    const data = await res.json();
                    const chatBox = document.getElementById('chat-box');
                    chatBox.innerHTML = '';
                    
                    if (data.history.length === 0) {
                        chatBox.innerHTML = `
                            <div class="message-container assistant-container">
                                <div class="message assistant">ONLINE. Gemini Persona & Canvas modules loaded. Toggle Kim Voice Mode for real-time duplex speech.</div>
                                <div class="btn-row">
                                    <button class="action-btn" onclick="copyText(this)">[ COPY ]</button>
                                    <button class="action-btn" onclick="speakText(this, null)">[ SYNTHESIZE AUDIO ]</button>
                                    <button class="action-btn" onclick="openCanvas(this)">[ OPEN IN CANVAS ]</button>
                                </div>
                            </div>`;
                    } else {
                        data.history.forEach(item => {
                            const isUser = item.role === 'user';
                            chatBox.innerHTML += `
                                <div class="message-container ${isUser ? 'user-container' : 'assistant-container'}">
                                    <div class="message ${isUser ? 'user' : 'assistant'}">${escapeHtml(item.content)}</div>
                                    ${!isUser ? `
                                    <div class="btn-row">
                                        <button class="action-btn" onclick="copyText(this)">[ COPY ]</button>
                                        <button class="action-btn" onclick="speakText(this)">[ SYNTHESIZE AUDIO ]</button>
                                        <button class="action-btn" onclick="openCanvas(this)">[ OPEN IN CANVAS ]</button>
                                    </div>` : ''}
                                </div>`;
                        });
                    }
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch(e) {
                    console.error("Failed to load history", e);
                }
            }

            function updateFileIndicator() {
                const fileInput = document.getElementById('file-input');
                const indicator = document.getElementById('file-indicator');
                if (fileInput.files.length > 0) {
                    indicator.textContent = ' ✓';
                } else {
                    indicator.textContent = '';
                }
            }

            function setStatus(text, isActive = false) {
                document.getElementById('status-text').textContent = text;
                const reactor = document.getElementById('reactor-icon');
                if (isActive) {
                    reactor.classList.add('active');
                } else {
                    reactor.classList.remove('active');
                }
            }

            function toggleKimMode() {
                kimActive = !kimActive;
                const btn = document.getElementById('kim-btn');
                
                if (kimActive) {
                    btn.textContent = 'KIM: ACTIVE';
                    btn.classList.add('active');
                    setStatus('SYS: LISTENING', true);
                    isProcessing = false;
                    startListening();
                } else {
                    btn.textContent = 'KIM: OFF';
                    btn.classList.remove('active');
                    setStatus('SYS: READY', false);
                    isProcessing = false;
                    clearTimeout(silenceTimer);
                    if (recognition) recognition.stop();
                }
            }

            function startListening() {
                if (!kimActive || isProcessing) return;
                try {
                    if (recognition) {
                        setStatus('SYS: LISTENING', true);
                        recognition.start();
                    }
                } catch(e) {}
            }

            function toggleCanvas(show) {
                const canvas = document.getElementById('canvas-pane');
                const chatPane = document.getElementById('chat-pane');
                if (show) {
                    canvas.classList.add('active');
                    chatPane.classList.add('split');
                } else {
                    canvas.classList.remove('active');
                    chatPane.classList.remove('split');
                }
            }

            function openCanvas(button) {
                const text = button.parentElement.previousElementSibling.innerText;
                document.getElementById('canvas-editor').value = text;
                toggleCanvas(true);
            }

            async function triggerDeepResearch() {
                const topic = prompt("Enter research topic or objective for Deep Research Engine:");
                if (!topic) return;
                
                setStatus('SYS: RESEARCHING', true);
                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML += `
                    <div class="message-container user-container">
                        <div class="message user">[DEEP RESEARCH INITIATED]: ${escapeHtml(topic)}</div>
                    </div>`;
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const res = await fetch('/api/research', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ topic: topic })
                    });
                    const data = await res.json();
                    const report = data.report || "Research compilation failed.";

                    chatBox.innerHTML += `
                        <div class="message-container assistant-container">
                            <div class="message assistant">${escapeHtml(report)}</div>
                            <div class="btn-row">
                                <button class="action-btn" onclick="copyText(this)">[ COPY ]</button>
                                <button class="action-btn" onclick="speakText(this)">[ SYNTHESIZE AUDIO ]</button>
                                <button class="action-btn" onclick="openCanvas(this)">[ OPEN IN CANVAS ]</button>
                            </div>
                        </div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                    document.getElementById('canvas-editor').value = report;
                    toggleCanvas(true);
                    setStatus('SYS: READY', false);
                } catch(e) {
                    setStatus('SYS: READY', false);
                }
            }

            function copyText(button) {
                const text = button.parentElement.previousElementSibling.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    const original = button.textContent;
                    button.textContent = '[ COPIED ]';
                    setTimeout(() => button.textContent = original, 2000);
                });
            }

            async function speakText(button, callback) {
                const targetText = typeof button === 'string' ? button : button.parentElement.previousElementSibling.innerText;
                const originalText = button && button.tagName === 'BUTTON' ? button.textContent : '';
                if (button && button.tagName === 'BUTTON') button.textContent = '[ SPEAKING... ]';

                try {
                    setStatus('SYS: SPEAKING', true);
                    const res = await fetch('/api/tts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: targetText })
                    });
                    if (!res.ok) throw new Error('TTS failed');
                    
                    const blob = await res.blob();
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);
                    
                    audio.play();
                    audio.onended = () => {
                        if (button && button.tagName === 'BUTTON') button.textContent = originalText;
                        if (callback) callback();
                    };
                    audio.onerror = () => {
                        if (button && button.tagName === 'BUTTON') button.textContent = originalText;
                        if (callback) callback();
                    };
                } catch (err) {
                    if (button && button.tagName === 'BUTTON') button.textContent = originalText;
                    if (callback) callback();
                }
            }

            async function sendMessage() {
                if (isProcessing) return;
                clearTimeout(silenceTimer);
                
                const input = document.getElementById('user-input');
                const fileInput = document.getElementById('file-input');
                const personaSelect = document.getElementById('persona-select');
                const text = (input.value || transcriptBuffer).trim();
                const file = fileInput.files[0];
                const persona = personaSelect.value;

                if (!text && !file) return;
                isProcessing = true;
                transcriptBuffer = '';

                if (recognition) {
                    try { recognition.stop(); } catch(e) {}
                }

                input.value = '';
                fileInput.value = '';
                document.getElementById('file-indicator').textContent = '';

                const chatBox = document.getElementById('chat-box');
                chatBox.innerHTML += `
                    <div class="message-container user-container">
                        <div class="message user">${escapeHtml(text + (file ? ' [File: ' + file.name + ']' : ''))}</div>
                    </div>`;
                chatBox.scrollTop = chatBox.scrollHeight;

                setStatus('SYS: COMPUTING', true);

                try {
                    const formData = new FormData();
                    formData.append('message', text || 'Analyze this attached file.');
                    formData.append('persona', persona);
                    if (file) {
                        formData.append('file', file);
                    }

                    const res = await fetch('/v1/chat/completions', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    const reply = data.reply || data.detail || "Error occurred";
                    
                    chatBox.innerHTML += `
                        <div class="message-container assistant-container">
                            <div class="message assistant">${escapeHtml(reply)}</div>
                            <div class="btn-row">
                                <button class="action-btn" onclick="copyText(this)">[ COPY ]</button>
                                <button class="action-btn" onclick="speakText(this)">[ SYNTHESIZE AUDIO ]</button>
                                <button class="action-btn" onclick="openCanvas(this)">[ OPEN IN CANVAS ]</button>
                            </div>
                        </div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;

                    if (kimActive) {
                        speakText(reply, () => {
                            isProcessing = false;
                            if (kimActive) {
                                startListening();
                            }
                        });
                    } else {
                        isProcessing = false;
                        setStatus('SYS: READY', false);
                    }
                } catch (err) {
                    isProcessing = false;
                    if (kimActive) {
                        startListening();
                    } else {
                        setStatus('SYS: READY', false);
                    }
                }
            }

            function escapeHtml(text) {
                return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
            }

            document.getElementById('user-input').addEventListener('keypress', function (e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    """

@app.post("/v1/chat/completions")

class ChatRequest(BaseModel):
    prompt: str
    persona: str = "tactical"

async def chat_completions(req: ChatRequest):
    user_msg = req.message.strip()

    # Context-Aware Tool Interception & Chaining
    tool_outputs = []
    if user_msg.lower().startswith("math:") or "calc" in user_msg.lower():
        expr = user_msg.split(":", 1)[-1].strip() if ":" in user_msg else user_msg
        tool_outputs.append(execute_math(expr))

    if "audit" in user_msg.lower() or "workspace" in user_msg.lower():
        tool_outputs.append(audit_workspace())

    augmented_prompt = user_msg
    if tool_outputs:
        augmented_prompt += "\n\n[System Tool Executions:\n" + "\n".join(tool_outputs) + "\n]"

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are Kiemaen v3.0, an advanced assistant."},
            {"role": "user", "content": augmented_prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            res_data = response.json()
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=res_data)

            reply = res_data["choices"][0]["message"]["content"]

            # Save to SQLite
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("user", req.message))
            cursor.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("assistant", reply))
            conn.commit()
            conn.close()

            return {"reply": reply}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
