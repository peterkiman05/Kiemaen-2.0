from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import hashlib

router = APIRouter()

class HashCheckRequest(BaseModel):
    data: str
    target_hash: str
    algorithm: str = "sha256"

class HashCheckResponse(BaseModel):
    is_match: bool
    computed_hash: str
    algorithm: str

@router.post("/api/security/verify-hash", response_model=HashCheckResponse)
async def verify_hash(payload: HashCheckRequest):
    algo = payload.algorithm.lower()
    
    if algo == "sha256":
        computed = hashlib.sha256(payload.data.encode()).hexdigest()
    elif algo == "sha512":
        computed = hashlib.sha512(payload.data.encode()).hexdigest()
    elif algo == "md5":
        computed = hashlib.md5(payload.data.encode()).hexdigest()
    else:
        raise HTTPException(status_code=400, detail="Unsupported hashing algorithm. Use sha256, sha512, or md5.")

    is_match = computed.lower() == payload.target_hash.lower()

    return {
        "is_match": is_match,
        "computed_hash": computed,
        "algorithm": algo
    }
