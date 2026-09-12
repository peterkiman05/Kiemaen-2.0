from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import ollama

router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]] = []


@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        messages = request.history + [{"role": "user", "content": request.prompt}]
        response = ollama.chat(model="llama3.2:1b", messages=messages)
        return {"response": response["message"]["content"], "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
