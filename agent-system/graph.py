import requests
from langgraph.graph import StateGraph, END
from schemas import AgentState
from tools import get_live_market_data

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def call_llm(prompt: str) -> str:
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"LLM Error: {str(e)}"


def worker_agent(state: AgentState) -> dict:
    task = state["task"]
    feedback = state.get("feedback")
    iteration = state.get("iteration", 0)

    # Check if task is trading related and extract market data if applicable
    market_context = ""
    words = task.replace(",", " ").split()
    for word in words:
        if "=" in word or word.isupper() and len(word) in [3, 6, 7]:
            if (
                "=" in word
                or word.endswith("USD")
                or word.startswith("EUR")
                or word.startswith("GBP")
            ):
                data = get_live_market_data(word)
                if "Error" not in data and "No live price" not in data:
                    market_context += f"\n\n[LIVE MARKET DATA]\n{data}\n"
                    break

    prompt = f"""You are an Expert AI Execution Agent.
Task: {task}
{market_context}
"""
    if feedback and iteration > 0:
        prompt += f"\nPrevious Reviewer Feedback to address: {feedback}\n"

    prompt += "\nProvide a complete, actionable, high-quality solution."

    output = call_llm(prompt)
    return {"worker_output": output, "iteration": iteration + 1}


def reviewer_agent(state: AgentState) -> dict:
    task = state["task"]
    output = state.get("worker_output", "")

    prompt = f"""You are a Strict QA and Code/Strategy Reviewer Agent.
Task: {task}
Worker Output:
{output}

Review criteria:
1. Is the solution accurate, realistic, and complete?
2. Are risk parameters (stop loss, take profit, position sizing) clearly defined if applicable?

Respond strictly in the following format:
STATUS: APPROVED or REJECTED
FEEDBACK: <detailed reasons or improvements required>
"""

    review_res = call_llm(prompt)

    if "STATUS: APPROVED" in review_res.upper():
        status = "APPROVED"
    else:
        status = "REJECTED"

    return {"review_status": status, "feedback": review_res}


def should_continue(state: AgentState) -> str:
    if state.get("review_status") == "APPROVED":
        return END
    if state.get("iteration", 0) >= state.get("max_iterations", 2):
        return END
    return "worker"


workflow = StateGraph(AgentState)
workflow.add_node("worker", worker_agent)
workflow.add_node("reviewer", reviewer_agent)

workflow.set_entry_point("worker")
workflow.add_edge("worker", "reviewer")
workflow.add_conditional_edges(
    "reviewer", should_continue, {"worker": "worker", END: END}
)

graph = workflow.compile()
