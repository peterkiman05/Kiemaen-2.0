from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
import time
from collections import defaultdict

router = APIRouter()

# In-memory adaptive rate tracker: IP -> { 'requests': [timestamps], 'penalty_multiplier': float }
REQUEST_HISTORY = defaultdict(lambda: {"requests": [], "penalty": 1.0})

BASE_LIMIT = 15  # Base max requests per window
TIME_WINDOW = 60 # Window size in seconds

class RateLimitStatus(BaseModel):
    client_ip: str
    current_requests: int
    penalty_multiplier: float
    allowed: bool

@router.get("/api/security/rate-limit-status", response_model=RateLimitStatus)
async def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    data = REQUEST_HISTORY[client_ip]
    # Filter timestamps within the current sliding window
    data["requests"] = [t for t in data["requests"] if now - t < TIME_WINDOW]
    
    effective_limit = max(2, int(BASE_LIMIT / data["penalty"]))
    current_count = len(data["requests"])
    
    return {
        "client_ip": client_ip,
        "current_requests": current_count,
        "penalty_multiplier": data["penalty"],
        "allowed": current_count < effective_limit
    }

def verify_adaptive_rate(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    data = REQUEST_HISTORY[client_ip]
    data["requests"] = [t for t in data["requests"] if now - t < TIME_WINDOW]
    
    effective_limit = max(2, int(BASE_LIMIT / data["penalty"]))
    
    if len(data["requests"]) >= effective_limit:
        # Increase penalty multiplier adaptively on abuse (max penalty factor 4x)
        data["penalty"] = min(4.0, data["penalty"] + 0.5)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Adaptive Firewall Triggered: Rate limit exceeded. Penalty factor increased to {data['penalty']}x."
        )
    
    # Record current valid hit
    data["requests"].append(now)
    # Slowly decay penalty over time if client behaves
    if data["penalty"] > 1.0:
        data["penalty"] = max(1.0, data["penalty"] - 0.05)
