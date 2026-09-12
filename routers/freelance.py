from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import ollama
from routers.security import verify_security_and_rate_limit

router = APIRouter()


class FreelanceTaskRequest(BaseModel):
    task_type: (
        str  # e.g., "code_debug", "technical_docs", "marketing_copy", "data_synthesis"
    )
    client_prompt: str
    tone: Optional[str] = "professional"


@router.post(
    "/api/freelance/execute", dependencies=[Depends(verify_security_and_rate_limit)]
)
async def execute_freelance_task(request: FreelanceTaskRequest):
    """
    Executes specialized micro-studio tasks using multi-engine local processing,
    tailored for rapid client delivery across freelancing platforms.
    """
    system_prompts = {
        "code_debug": "You are an expert software architect. Analyze the provided code, identify bugs, optimize performance, and output clean, production-ready code with explanations.",
        "technical_docs": "You are a senior technical writer. Create comprehensive, structured documentation, API guides, or README files with precise markdown formatting.",
        "marketing_copy": f"You are a conversion copywriter. Write engaging, high-impact marketing copy with a {request.tone} tone designed to drive engagement and sales.",
        "data_synthesis": "You are a data analyst. Synthesize raw information into clear, structured insights, bullet points, and executive summaries.",
    }

    selected_system_prompt = system_prompts.get(
        request.task_type,
        "You are an expert multi-disciplinary AI assistant delivering high-precision professional work.",
    )

    messages = [
        {"role": "system", "content": selected_system_prompt},
        {"role": "user", "content": request.client_prompt},
    ]

    try:
        # Utilize primary analytical engine (Qwen) for complex client outputs
        response = ollama.chat(model="qwen2.5:7b", messages=messages)
        output_content = response["message"]["content"]
    except Exception:
        # Fallback to Llama if needed
        fallback_res = ollama.chat(model="llama3.2:1b", messages=messages)
        output_content = fallback_res["message"]["content"]

    return {
        "task_type": request.task_type,
        "deliverable": output_content,
        "status": "success",
        "studio_mode": "active",
    }
