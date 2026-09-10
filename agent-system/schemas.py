from typing import Optional, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Shared state passed through the agent loop
class AgentState(TypedDict):
    task: str
    worker_output: Optional[str]
    review_status: Optional[Literal["APPROVED", "REJECTED"]]
    feedback: Optional[str]
    iteration: int
    max_iterations: int

# Worker agent output format
class WorkerResponse(BaseModel):
    solution: str = Field(description="The code or solution to the task.")
    explanation: str = Field(description="Brief explanation of the approach.")

# Reviewer agent output format
class ReviewerResponse(BaseModel):
    status: Literal["APPROVED", "REJECTED"] = Field(description="Approval decision.")
    feedback: str = Field(description="Feedback or changes requested.")

# FastAPI request format
class TaskRequest(BaseModel):
    task: str
    max_iterations: Optional[int] = 3

# FastAPI response format
class TaskResponse(BaseModel):
    status: str
    iterations_used: int
    final_output: str
    review_feedback: Optional[str] = None
