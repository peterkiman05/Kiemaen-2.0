from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter()

class TelegramWebhookPayload(BaseModel):
    update_id: int
    message: dict = {}

class SlackWebhookPayload(BaseModel):
    token: Optional[str] = None
    team_id: Optional[str] = None
    event: dict = {}
    type: Optional[str] = None
    challenge: Optional[str] = None

@router.post("/api/channels/telegram/webhook")
async def telegram_webhook(payload: TelegramWebhookPayload):
    msg = payload.message
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "")
    
    # Process incoming command via Telegram bot bridge
    return {
        "status": "processed",
        "channel": "telegram",
        "chat_id": chat_id,
        "echo": f"Jarvis received: {text}"
    }

@router.post("/api/channels/slack/webhook")
async def slack_webhook(payload: SlackWebhookPayload):
    if payload.type == "url_verification":
        return {"challenge": payload.challenge}
        
    event_data = payload.event
    return {
        "status": "processed",
        "channel": "slack",
        "event_type": event_data.get("type")
    }
