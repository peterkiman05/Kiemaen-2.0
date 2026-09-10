from graph import graph
from db import init_db, log_execution

init_db()

def run_blueprint_execution(task: str, max_iterations: int = 2) -> dict:
    initial_state = {
        "task": task,
        "iteration": 0,
        "max_iterations": max_iterations
    }
    final_state = graph.invoke(initial_state)
    
    worker_output = final_state.get("worker_output", "")
    review_status = final_state.get("review_status", "PENDING")
    feedback = final_state.get("feedback", "")
    
    # Save run to SQLite
    log_execution(task, worker_output, review_status, feedback)
    
    return {
        "worker_output": worker_output,
        "review_status": review_status,
        "feedback": feedback
    }
