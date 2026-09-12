from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from blueprint_engine import run_blueprint_execution

app = FastAPI(title="Multi-Agent System API")


class TaskRequest(BaseModel):
    task: str
    max_iterations: int = 2


@app.get("/")
def read_root():
    return {"status": "online", "system": "Multi-Agent Engine"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/run_blueprint")
def execute_blueprint(request: TaskRequest):
    try:
        result = run_blueprint_execution(request.task, request.max_iterations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
