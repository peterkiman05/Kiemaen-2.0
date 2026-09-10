from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import ollama
from routers.security import verify_security_and_rate_limit

router = APIRouter()

class TutorRequest(BaseModel):
    subject: str
    problem_statement: str

@router.post("/api/tutor/solve", dependencies=[Depends(verify_security_and_rate_limit)])
async def solve_academic_problem(request: TutorRequest):
    system_prompt = f"You are an elite academic tutor specializing in {request.subject}. Provide a rigorous, step-by-step solution breakdown."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.problem_statement}
    ]
    try:
        response = ollama.chat(model="qwen2.5:7b", messages=messages)
        solution_content = response["message"]["content"]
    except Exception:
        fallback_res = ollama.chat(model="llama3.2:1b", messages=messages)
        solution_content = fallback_res["message"]["content"]

    return {
        "subject": request.subject,
        "solution": solution_content,
        "status": "success",
        "monetization_tier": "pro_student_access"
    }
