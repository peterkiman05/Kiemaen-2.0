from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
import time
from collections import defaultdict

router = APIRouter()

# DDoS Mitigation Memory Store: IP -> { 'connection_count': int, 'blocked_until': float, 'violation_streak': int }
DDOS_TRACKER = defaultdict(
    lambda: {"connection_count": 0, "blocked_until": 0.0, "violation_streak": 0}
)

# Threshold configuration for DDoS response
BURST_THRESHOLD = 40  # Max requests in a short burst window
BLOCK_DURATION = 300  # Temporary IP ban duration in seconds (5 minutes)


class DDoSStatusResponse(BaseModel):
    client_ip: str
    is_mitigated: bool
    blocked_until: float
    violation_streak: int


@router.get("/api/security/ddos-status", response_model=DDoSStatusResponse)
async def check_ddos_status(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    data = DDOS_TRACKER[client_ip]
    now = time.time()

    is_blocked = now < data["blocked_until"]
    return {
        "client_ip": client_ip,
        "is_mitigated": is_blocked,
        "blocked_until": data["blocked_until"] if is_blocked else 0.0,
        "violation_streak": data["violation_streak"],
    }


def enforce_ddos_defense(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    data = DDOS_TRACKER[client_ip]
    now = time.time()

    # Check if IP is currently under a mitigation lockout block
    if now < data["blocked_until"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"DDoS Mitigation Active: IP {client_ip} temporarily quarantined due to flood behavior. Try again later.",
        )

    # Track rapid request frequency (burst detection)
    data["connection_count"] += 1

    # Reset connection counter periodically or trigger mitigation block if burst limit is breached
    if data["connection_count"] > BURST_THRESHOLD:
        data["violation_streak"] += 1
        # Exponentially scale block duration on repeat offenses
        penalty_block = BLOCK_DURATION * data["violation_streak"]
        data["blocked_until"] = now + penalty_block
        data["connection_count"] = 0

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"DDoS Flood Detected: Automated quarantine enforced for {penalty_block} seconds.",
        )
