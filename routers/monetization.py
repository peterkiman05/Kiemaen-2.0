from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

USER_TIERS = {
    "free_user_key": {"tier": "free", "requests_left": 10},
    "pro_user_key": {"tier": "pro", "requests_left": 1000},
}


@router.post("/api/webhook/stripe")
async def stripe_webhook(payload: dict):
    if payload.get("type") == "checkout.session.completed":
        pass
    return {"status": "received"}
