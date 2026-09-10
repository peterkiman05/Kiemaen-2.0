from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from graph import graph
from schemas import TaskResponse, AgentState
from database import log_run

router = APIRouter(prefix="/blueprints", tags=["Cashflow Blueprints"])

class TradingStrategyRequest(BaseModel):
    asset_class: str = Field(..., example="XAUUSD")
    timeframe: str = Field(..., example="15m")
    strategy_style: str = Field(..., example="Breakout Momentum")

class ArbitrageRequest(BaseModel):
    source_platform: str = Field(..., example="Supplier A")
    target_platform: str = Field(..., example="Zoey")
    category: str = Field(..., example="Electronics")

class LeadGenRequest(BaseModel):
    target_niche: str = Field(..., example="Civil Engineering Consultants")
    location: str = Field(..., example="Johannesburg")
    offer_summary: str = Field(..., example="Automated structural calculation tool")


@router.post("/trading-strategy", response_model=TaskResponse)
def generate_trading_strategy(req: TradingStrategyRequest):
    task_prompt = f"Design a complete automated trading strategy for {req.asset_class} on timeframe {req.timeframe}. Style: {req.strategy_style}. Include precise entry/exit rules and risk management."
    return execute_graph(task_prompt)


@router.post("/ecommerce-arbitrage", response_model=TaskResponse)
def generate_arbitrage_spec(req: ArbitrageRequest):
    task_prompt = f"Design an automated price & inventory tracking script logic between {req.source_platform} and {req.target_platform} for category {req.category}. Include logic for fee calculations and margin checks."
    return execute_graph(task_prompt)


@router.post("/lead-gen-outreach", response_model=TaskResponse)
def generate_lead_campaign(req: LeadGenRequest):
    task_prompt = f"Create a high-converting B2B cold email sequence targeting {req.target_niche} in {req.location}. Offer: {req.offer_summary}. Provide follow-up variants."
    return execute_graph(task_prompt)


def execute_graph(task: str) -> TaskResponse:
    initial_state: AgentState = {
        "task": task,
        "worker_output": None,
        "review_status": None,
        "feedback": None,
        "iteration": 0,
        "max_iterations": 2
    }
    try:
        final_state = graph.invoke(initial_state)
        status = "SUCCESS" if final_state.get("review_status") == "APPROVED" else "MAX_ITERATIONS_REACHED"
        iterations = final_state.get("iteration", 0)
        output = final_state.get("worker_output", "No output generated.")
        feedback = final_state.get("feedback", "")

        # Log to DB
        log_run(task, status, iterations, output, feedback)

        return TaskResponse(
            status=status,
            iterations_used=iterations,
            final_output=output,
            review_feedback=feedback
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
