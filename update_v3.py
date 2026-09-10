code = '''import os
import sqlite3
import subprocess
import tempfile
import sympy as sp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
from tavily import TavilyClient

app = FastAPI(title="Kiemaen Universal API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None

DB_NAME = "kiemaen_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    \"\"\")
    conn.commit()
    conn.close()

init_db()

def save_chat_memory(role: str, content: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO conversation_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def tool_solve_math(expression: str) -> str:
    try:
        result = sp.sympify(expression)
        return f"Exact Result: {result} | Decimal Approximation: {float(result.evalf())}"
    except Exception as e:
        return f"Math calculation error: {str(e)}"

def tool_workspace_audit() -> str:
    try:
        files = [f for f in os.listdir(".") if os.path.isfile(f) and not f.startswith(".")]
        return f"Workspace File Inventory: {', '.join(files)}"
    except Exception as e:
        return f"Audit error: {str(e)}"

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "llama-3.3-70b-versatile"
    messages: list[Message]
    temperature: float = 0.7
    stream: bool = False

class CodeExecutionRequest(BaseModel):
    code: str

class FileWriteRequest(BaseModel):
    filename: str
    content: str

@app.get("/")
def home():
    return {
        "status": "ONLINE",
        "agent": "Kiemaen",
        "version": "3.0.0 - Agentic Edition",
        "endpoints": ["/v1/chat/completions", "/v1/models", "/execute-code", "/files/list", "/files/read", "/files/write", "/chat"]
    }

@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "llama-3.3-70b-versatile", "object": "model", "owned_by": "kiemaen"},
            {"id": "llama3-8b-8192", "object": "model", "owned_by": "kiemaen"},
            {"id": "mixtral-8x7b-32768", "object": "model", "owned_by": "kiemaen"}
        ]
    }

@app.post("/v1/chat/completions")
def chat_completions(payload: ChatCompletionRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing.")

    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    user_message = payload.messages[-1].content
    save_chat_memory("user", user_message)

    tool_output = ""
    lower_msg = user_message.lower()

    if "math:" in lower_msg or "calculate:" in lower_msg:
        prefix = "math:" if "math:" in lower_msg else "calculate:"
        expr = user_message.split(prefix)[-1].strip()
        tool_output = f"\\n\\n[Tool Execution - SymPy Math Solver]: {tool_solve_math(expr)}"
    elif "audit workspace" in lower_msg or "file status" in lower_msg:
        tool_output = f"\\n\\n[Tool Execution - Workspace Audit]: {tool_workspace_audit()}"

    search_context = ""
    if tavily_client and any(keyword in lower_msg for keyword in ["news", "latest", "current", "weather", "price", "who is", "what happened", "2026"]):
        try:
            search_result = tavily_client.search(query=user_message, search_depth="basic", max_results=3)
            search_context = "\\n\\nLive Web Search Results:\\n" + str(search_result)
        except Exception as e:
            print(f"Web search error: {e}")

    system_prompt = (
        "You are Kiemaen, a helpful, highly intelligent, and versatile general-purpose AI assistant. "
        "Incorporate tool outputs, real-time data, or search context provided below if it helps answer the user accurately."
        f"{tool_output}{search_context}"
    )

    formatted_messages = [{"role": "system", "content": system_prompt}]
    for m in payload.messages:
        formatted_messages.append({"role": m.role, "content": m.content})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    target_model = payload.model if payload.model in ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"] else "llama-3.3-70b-versatile"

    data = {
        "model": target_model,
        "messages": formatted_messages,
        "temperature": payload.temperature
    }

    try:
        response = requests.post(GROQ_CHAT_URL, headers=headers, json=data, timeout=30)
        res_data = response.json()
        
        if "choices" not in res_data:
            raise HTTPException(status_code=500, detail=f"LLM API Error: {res_data}")
        
        reply_text = res_data["choices"][0]["message"]["content"]
        save_chat_memory("assistant", reply_text)

        return {
            "id": "chatcmpl-kiemaen",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": reply_text},
                "finish_reason": "stop"
            }]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-code")
def execute_python_code(payload: CodeExecutionRequest):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(payload.code.encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        return {
            "status": "SUCCESS" if result.returncode == 0 else "ERROR",
            "output": output
        }
    except subprocess.TimeoutExpired:
        return {"status": "FAILED", "output": "Execution timed out (exceeded 10 seconds limit)."}
    except Exception as e:
        return {"status": "FAILED", "output": str(e)}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/files/list")
def list_workspace_files():
    try:
        files = [f for f in os.listdir(".") if os.path.isfile(f) and not f.startswith(".")]
        return {"status": "SUCCESS", "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/read")
def read_workspace_file(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found.")
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "SUCCESS", "filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files/write")
def write_workspace_file(payload: FileWriteRequest):
    try:
        with open(payload.filename, "w", encoding="utf-8") as f:
            f.write(payload.content)
        return {"status": "SUCCESS", "message": f"File '{payload.filename}' written successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat", response_class=HTMLResponse)
def serve_chat_ui():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiemaen AI Interface</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121212; color: #e0e0e0; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background: #1e1e1e; padding: 15px; text-align: center; font-weight: bold; border-bottom: 1px solid #333; }
        #chat-container { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; word-wrap: break-word; }
        .user { align-self: flex-end; background: #007acc; color: white; }
        .assistant { align-self: flex-start; background: #2d2d2d; color: #e0e0e0; border: 1px solid #404040; }
        #input-area { display: flex; padding: 15px; background: #1e1e1e; border-top: 1px solid #333; gap: 10px; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #252525; color: white; outline: none; }
        button { padding: 12px 20px; background: #007acc; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0062a3; }
    </style>
</head>
<body>
    <header>Kiemaen Universal AI (Agentic v3.0)</header>
    <div id="chat-container">
        <div class="message assistant">Hello! I am Kiemaen v3.0. Tool registry for math calculation and file auditing is now active. How can I assist you?</div>
    </div>
    <div id="input-area">
        <input type="text" id="user-input" placeholder="Type a message (e.g. math: 2**10 or audit workspace)..." autofocus>
        <button onclick="sendMessage()">Send</button>
    </div>
    <script>
        const chatContainer = document.getElementById("chat-container");
        const userInput = document.getElementById("user-input");
        let messageHistory = [{ role: "assistant", content: "Hello! I am Kiemaen v3.0. Tool registry for math calculation and file auditing is now active. How can I assist you?" }];

        userInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") sendMessage();
        });

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            messageHistory.push({ role: "user", content: text });
            appendMessage("user", text);
            userInput.value = "";
            chatContainer.scrollTop = chatContainer.scrollHeight;

            try {
                const response = await fetch("/v1/chat/completions", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ model: "llama-3.3-70b-versatile", messages: messageHistory })
                });
                const data = await response.json();
                const reply = data.choices[0].message.content;
                
                messageHistory.push({ role: "assistant", content: reply });
                appendMessage("assistant", reply);
            } catch (err) {
                appendMessage("assistant", "Error: Could not reach backend server.");
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function appendMessage(role, text) {
            const div = document.createElement("div");
            div.className = "message " + role;
            div.innerText = text;
            chatContainer.appendChild(div);
        }
    </script>
</body>
</html>'''
'''

with open("main.py", "w") as f:
    f.write(code)
print("SUCCESS: main.py successfully generated via update_v3.py!")
