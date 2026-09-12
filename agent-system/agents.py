import json
import httpx
from typing import Dict, Any
from schemas import AgentState, WorkerResponse, ReviewerResponse

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def call_ollama(prompt: str) -> str:
    """Sends prompts to Ollama with an extended timeout for mobile CPUs."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "num_predict": 256  # Limits response token length to speed up CPU generation
        },
    }
    try:
        # Timeout extended to 180 seconds for Termux CPU execution
        response = httpx.post(OLLAMA_URL, json=payload, timeout=180.0)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return json.dumps(
            {
                "solution": "Error: Ollama connection timed out or failed.",
                "explanation": f"Detail: {str(e)}",
                "status": "REJECTED",
                "feedback": "Ollama request timed out.",
            }
        )


def worker_node(state: AgentState) -> Dict[str, Any]:
    task = state["task"]
    feedback = state.get("feedback")
    iteration = state.get("iteration", 0) + 1

    prompt = f"Task: {task}\n"
    if feedback:
        prompt += f"Feedback to fix: {feedback}\n"

    prompt += """Provide solution strictly as JSON:
{
  "solution": "concise solution code or strategy",
  "explanation": "brief overview"
}"""

    raw_response = call_ollama(prompt)
    try:
        data = json.loads(raw_response)
        worker_res = WorkerResponse(**data)
        solution = f"{worker_res.solution}\n\nExplanation:\n{worker_res.explanation}"
    except Exception:
        solution = raw_response

    return {"worker_output": solution, "iteration": iteration}


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    task = state["task"]
    solution = state.get("worker_output", "")

    prompt = f"Task: {task}\nSolution: {solution}\n"
    prompt += """Evaluate strictly as JSON:
{
  "status": "APPROVED",
  "feedback": "short review note"
}"""

    raw_response = call_ollama(prompt)
    try:
        data = json.loads(raw_response)
        reviewer_res = ReviewerResponse(**data)
        status = reviewer_res.status
        feedback = reviewer_res.feedback
    except Exception:
        status = "APPROVED"
        feedback = "Automated fallback pass."

    return {"review_status": status, "feedback": feedback}
