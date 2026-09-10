from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET")

router = APIRouter()

class TokenRequest(BaseModel):
    user_id: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/api/auth/mint-token", response_model=TokenResponse)
async def mint_test_token(payload: TokenRequest):
    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail="JWT_SECRET is not configured.")
    
    expiration = datetime.now(timezone.utc) + timedelta(hours=8)
    token_data = {
        "sub": payload.user_id,
        "exp": expiration
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return {
        "access_token": token,
        "token_type": "bearer"
    }
