from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
import json
import os

router = APIRouter()
EVOLUTION_STORE = "evolution_memory.json"

def load_evolution_memory() -> dict:
    if os.path.exists(EVOLUTION_STORE):
        try:
            with open(EVOLUTION_STORE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"optimized_instructions": "Be concise and technically precise.", "evolution_generation": 1}

def save_evolution_memory(data: dict):
    with open(EVOLUTION_STORE, "w") as f:
        json.dump(data, f, indent=2)

class FeedbackPayload(BaseModel):
    user_query: str
    ai_response: str
    user_rating: str

@router.post("/api/evolve/feedback")
async def process_autonomous_feedback(feedback: FeedbackPayload):
    memory = load_evolution_memory()
    memory["evolution_generation"] += 1
    save_evolution_memory(memory)
    return {"status": "evolved", "current_generation": memory["evolution_generation"]}

@router.get("/api/evolve/state")
async def get_evolution_state():
    return load_evolution_memory()
