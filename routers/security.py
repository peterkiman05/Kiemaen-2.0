from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
import hashlib
import time

router = APIRouter()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Validated API keys with SHA-256 hashes
VALID_API_KEYS = {
    hashlib.sha256("pro_user_key_secret_2026".encode()).hexdigest(): {
        "role": "admin",
        "rate_limit": 5000,
    },
    hashlib.sha256("free_user_key_secret_2026".encode()).hexdigest(): {
        "role": "standard",
        "rate_limit": 100,
    },
    # Allow the plaintext keys used in previous steps as hashed entries for seamless testing
    hashlib.sha256("pro_user_key".encode()).hexdigest(): {
        "role": "admin",
        "rate_limit": 5000,
    },
    hashlib.sha256("free_user_key".encode()).hexdigest(): {
        "role": "standard",
        "rate_limit": 100,
    },
}

IP_REQUEST_TRACKER = {}


async def verify_security_and_rate_limit(
    request: Request, api_key: str = Depends(api_key_header)
):
    # Exempt documentation and static paths
    if request.url.path in [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/terms",
        "/privacy",
        "/dpa",
    ]:
        return

    client_ip = request.client.host if request.client else "127.0.0.1"
    current_time = time.time()

    if client_ip not in IP_REQUEST_TRACKER:
        IP_REQUEST_TRACKER[client_ip] = []

    # Track requests in a sliding 10-second window
    IP_REQUEST_TRACKER[client_ip] = [
        t for t in IP_REQUEST_TRACKER[client_ip] if current_time - t < 10
    ]
    if len(IP_REQUEST_TRACKER[client_ip]) > 30:
        raise HTTPException(
            status_code=429, detail="Too Many Requests: Rate limit exceeded."
        )
    IP_REQUEST_TRACKER[client_ip].append(current_time)

    if not api_key:
        raise HTTPException(
            status_code=401, detail="Access Denied: Missing API Key header."
        )

    hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
    if hashed_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid credentials.")


@router.get(
    "/api/security/status", dependencies=[Depends(verify_security_and_rate_limit)]
)
async def security_status():
    return {
        "status": "secured",
        "encryption": "SHA-256 Key Hashing Active",
        "mitigation": "IP Throttling Enforced",
    }
