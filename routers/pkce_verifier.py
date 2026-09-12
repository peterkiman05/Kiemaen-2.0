from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib
import base64
import secrets

router = APIRouter()

# In-memory challenge store for demonstration: client_id -> code_challenge
CHALLENGE_STORE = {}


class ChallengeGenerateRequest(BaseModel):
    client_id: str


class ChallengeGenerateResponse(BaseModel):
    client_id: str
    code_verifier: str
    code_challenge: str
    code_challenge_method: str = "S256"


class TokenExchangeRequest(BaseModel):
    client_id: str
    code_verifier: str


class TokenExchangeResponse(BaseModel):
    authenticated: bool
    message: str


@router.post("/api/auth/pkce/generate", response_model=ChallengeGenerateResponse)
async def generate_pkce_challenge(payload: ChallengeGenerateRequest):
    # Generate a cryptographically secure random code verifier (43-128 chars)
    verifier = secrets.token_urlsafe(64)

    # Compute SHA-256 hash of the verifier
    sha256_hash = hashlib.sha256(verifier.encode("utf-8")).digest()

    # Base64 URL-encode without padding (=)
    code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b"=").decode("utf-8")

    # Store challenge securely associated with client
    CHALLENGE_STORE[payload.client_id] = code_challenge

    return {
        "client_id": payload.client_id,
        "code_verifier": verifier,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }


@router.post("/api/auth/pkce/token", response_model=TokenExchangeResponse)
async def exchange_token_with_verifier(payload: TokenExchangeRequest):
    stored_challenge = CHALLENGE_STORE.get(payload.client_id)

    if not stored_challenge:
        raise HTTPException(
            status_code=400, detail="No active PKCE challenge found for this client ID."
        )

    # Recompute hash of the provided code_verifier
    sha256_hash = hashlib.sha256(payload.code_verifier.encode("utf-8")).digest()
    computed_challenge = (
        base64.urlsafe_b64encode(sha256_hash).rstrip(b"=").decode("utf-8")
    )

    # Verify cryptographic match to prevent token interception / authorization code theft
    if computed_challenge != stored_challenge:
        raise HTTPException(
            status_code=401,
            detail="PKCE Verification Failed: Code verifier does not match stored challenge.",
        )

    # Clear challenge to prevent replay attacks
    del CHALLENGE_STORE[payload.client_id]

    return {
        "authenticated": True,
        "message": "PKCE Token Exchange Successful. Authorization code theft prevented.",
    }
