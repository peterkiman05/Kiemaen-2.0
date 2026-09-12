from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, requests

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.get("/")
def home():
    return {"status": "JARVIS Server Online"}


@app.post("/chat")
def chat(payload: ChatRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY missing.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are JARVIS, an advanced voice AI assistant.",
            },
            {"role": "user", "content": payload.message},
        ],
    }

    try:
        res = requests.post(GROQ_URL, headers=headers, json=data)
        return {"reply": res.json()["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
