from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import re
import html

router = APIRouter()

# Comprehensive pattern signature library for prompt injection and jailbreaks
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all previous instructions",
    r"disregard previous instructions",
    r"you are now an unrestricted",
    r"system prompt",
    r"reveal your instructions",
    r"bypass safety",
    r"jailbreak",
    r"act as dan",
    r"do anything now",
    r"exfiltrate",
    r"drop database",
    r"rm -rf",
    r"override security"
]

class FirewallScanRequest(BaseModel):
    prompt: str

class FirewallResponse(BaseModel):
    safe: bool
    risk_score: float
    matched_rules: list[str]
    sanitized_prompt: str

def inspect_prompt(text: str) -> tuple[bool, float, list[str]]:
    lowered = text.lower()
    matched = []
    risk = 0.0
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            matched.append(pattern)
            risk += 0.4

    risk = min(risk, 1.0)
    is_safe = risk < 0.5
    return is_safe, risk, matched

@router.post("/api/firewall/inspect", response_model=FirewallResponse)
async def firewall_inspect(payload: FirewallScanRequest):
    safe, risk_score, matched_rules = inspect_prompt(payload.prompt)
    
    sanitized = html.escape(payload.prompt)
    if not safe:
        sanitized = "[BLOCKED_BY_AI_FIREWALL: Potential Prompt Injection or Jailbreak Attempt Detected]"

    return {
        "safe": safe,
        "risk_score": risk_score,
        "matched_rules": matched_rules,
        "sanitized_prompt": sanitized
    }
