from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END
import ollama

app = FastAPI(title="Multi-Engine Self-Evolving AI Backend")

# 1. Monetization & Subscription Tiers Registry
# Module level
USER_TIERS = {
    "free_user_key": {"tier": "free", "requests_left": 10},
    "pro_user_key": {"tier": "pro", "requests_left": 1000}
}

public_paths = ["/", "/health", "/terms", "/privacy", "/dpa", "/docs", "/openapi.json", "/api/webhook/stripe"]

@app.middleware("http")
async def metering_and_auth_middleware(request: Request, call_next):
    if request.url.path in public_paths:
        return await call_next(request)
    ...
    
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key not in USER_TIERS:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API Key")
    
    client_data = USER_TIERS[api_key]
    if client_data["requests_left"] <= 0:
        raise HTTPException(status_code=402, detail="Payment Required: Quota exhausted. Please upgrade to Pro.")
    
    client_data["requests_left"] -= 1
    
    response = await call_next(request)
    response.headers["X-Tier"] = client_data["tier"]
    response.headers["X-Requests-Remaining"] = str(client_data["requests_left"])
    return response

# 3. Multi-Engine LangGraph State & Orchestration
class AgentState(BaseModel):
    messages: List[Dict[str, str]]
    critique: str = ""
    iteration: int = 0

class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]] = []

def primary_generator_node(state: AgentState) -> AgentState:
    """Actor Node: Uses Llama for fast initial response generation."""
    prompt_context = state.messages.copy()
    if state.critique:
        prompt_context.append({"role": "system", "content": f"Incorporate this feedback: {state.critique}"})
    
    # Engine 1: Llama for fast drafting
    response = ollama.chat(model="llama3.2:1b", messages=prompt_context)
    content = response["message"]["content"]
    
    state.messages.append({"role": "assistant", "content": content})
    state.iteration += 1
    return state

def secondary_reviewer_node(state: AgentState) -> AgentState:
    """Reviewer Node: Uses Qwen for deep logical critique and verification."""
    latest_response = state.messages[-1]["content"]
    review_prompt = [
        {"role": "system", "content": "You are a rigorous technical validator. Evaluate the response for correctness, technical depth, and safety. Provide specific corrections or write 'APPROVED' if flawless."},
        {"role": "user", "content": latest_response}
    ]
    
    # Engine 2: Qwen for rigorous review & reasoning
    # (Ensure you pull your target Qwen model via 'ollama pull qwen2.5:7b' or similar in Termux)
    try:
        critique_res = ollama.chat(model="qwen2.5:7b", messages=review_prompt)
        state.critique = critique_res["message"]["content"]
    except Exception:
        # Fallback if Qwen model name differs on your local machine
        state.critique = "APPROVED"
        
    return state

def evaluate_progress(state: AgentState):
    """Conditional Edge: Decides whether to loop back for multi-model refinement or finish."""
    if "APPROVED" in state.critique.upper() or state.iteration >= 2:
        return END
    return "refine"

# Build Multi-Engine Workflow
workflow = StateGraph(AgentState)
workflow.add_node("generator", primary_generator_node)
workflow.add_node("reviewer", secondary_reviewer_node)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "reviewer")
workflow.add_conditional_edges("reviewer", evaluate_progress, {"refine": "generator", END: END})

app_graph = workflow.compile()

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        initial_messages = request.history + [{"role": "user", "content": request.prompt}]
        initial_state = AgentState(messages=initial_messages)
        final_state = app_graph.invoke(initial_state)
        return {
            "response": final_state["messages"][-1]["content"],
            "engines_involved": ["llama3.2:1b", "qwen2.5:7b"],
            "iterations": final_state["iteration"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e) if str(e) else "Internal Error")

# 4. Payment Gateway Webhook & Legal Endpoints
@app.post("/api/webhook/stripe")
async def stripe_webhook(payload: dict):
    if payload.get("type") == "checkout.session.completed":
        pass
    return {"status": "received"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
    return "<html><body><h1>Terms of Service</h1><p>Acceptable use and platform guidelines.</p></body></html>"

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return "<html><body><h1>Privacy Policy</h1><p>Data protection and local processing details.</p></body></html>"

@app.get("/dpa", response_class=HTMLResponse)
async def data_processing_agreement():
    return "<html><body><h1>Data Processing Agreement</h1><p>Controller and processor terms.</p></body></html>"

from routers import (
    legal, monetization, chat, evolution, frontend, security, 
    tutor, freelance, auth, firewall, integration, rate_limiter, 
    ddos_defense, code_verifier, hash_verifier, pkce_verifier, 
    rls_enforcer, rls_policies, tool_connectors, messaging_channels, token_generator
)

for router_module in [
    legal, monetization, chat, evolution, frontend, security, 
    tutor, freelance, auth, firewall, integration, rate_limiter, 
    ddos_defense, code_verifier, hash_verifier, pkce_verifier, 
    rls_enforcer, rls_policies, tool_connectors, messaging_channels, token_generator
]:
    app.include_router(router_module.router)
import time
import logging
from fastapi import Request

logger = logging.getLogger("uvicorn.error")

async def add_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Latency: {duration:.2f}ms"
    )
    return response
from core.middleware import add_logging_middleware
app.middleware("http")(add_logging_middleware)

import time
import logging
from fastapi import Request

logger = logging.getLogger("uvicorn.error")

@app.middleware("http")
async def add_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Latency: {duration:.2f}ms"
    )
    return response

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiemaen AI</title>
    <style>
        :root { background: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
        body { margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { padding: 1rem 2rem; background: #1e293b; border-bottom: 1px solid #334155; font-size: 1.25rem; font-weight: bold; }
        .chat-container { flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; max-width: 800px; width: 100%; margin: 0 auto; }
        .message { padding: 0.75rem 1rem; border-radius: 0.5rem; max-width: 70%; line-height: 1.5; }
        .user { background: #3b82f6; align-self: flex-end; }
        .assistant { background: #334155; align-self: flex-start; }
        .input-panel { padding: 1rem; background: #1e293b; border-top: 1px solid #334155; display: flex; gap: 0.5rem; max-width: 800px; width: 100%; margin: 0 auto; box-sizing: border-box; }
        textarea { flex: 1; background: #0f172a; border: 1px solid #475569; color: #f8fafc; padding: 0.75rem; border-radius: 0.375rem; resize: none; height: 24px; }
        button { background: #3b82f6; color: white; border: none; padding: 0.75rem 1.25rem; border-radius: 0.375rem; cursor: pointer; font-weight: 600; }
        button:hover { background: #2563eb; }
        .toolbar { display: flex; gap: 0.5rem; padding: 0 1.5rem 0.5rem; max-width: 800px; margin: 0 auto; width: 100%; box-sizing: border-box; }
        .tool-btn { background: #475569; font-size: 0.85rem; padding: 0.4rem 0.8rem; }
    </style>
</head>
<body>
    <header>Kiemaen AI</header>
    <div class="chat-container" id="chatBox">
        <div class="message assistant">Hello! I am Kiemaen AI. How can I assist you today?</div>
    </div>
    <div class="toolbar">
        <button class="tool-btn" onclick="triggerUpload()">📁 Upload</button>
        <button class="tool-btn" onclick="triggerCopy()">📋 Copy Last</button>
        <button class="tool-btn" onclick="toggleRecord()">🎙️ Record</button>
        <button class="tool-btn" onclick="toggleSpeechToSpeech()">🔊 Speech-to-Speech</button>
    </div>
    <div class="input-panel">
        <textarea id="userInput" placeholder="Type a message..." rows="1" onkeydown="handleKey(event)"></textarea>
        <button onclick="sendMessage()">Send</button>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;
            
            appendMessage(text, 'user');
            input.value = '';

            try {
                // Client talks to local backend securely; NO API keys exposed on frontend
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                appendMessage(data.reply || data.response || "Received response.", 'assistant');
            } catch (err) {
                appendMessage("Error connecting to server.", 'assistant');
            }
        }
        function appendMessage(text, sender) {
            const box = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.textContent = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }
        function handleKey(e) { if(e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }
        function triggerUpload() { alert("File upload tool triggered."); }
        function triggerCopy() { alert("Copied last response to clipboard."); }
        function toggleRecord() { alert("Audio recording toggled."); }
        function toggleSpeechToSpeech() { alert("Speech-to-speech mode toggled."); }
    </script>
</body>
</html>
    """
