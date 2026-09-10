from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import ast

router = APIRouter()

class CodeVerificationRequest(BaseModel):
    code: str
    language: str = "python"

class CodeVerificationResponse(BaseModel):
    is_valid_syntax: bool
    error_message: str | None
    detected_constructs: list[str]

@router.post("/api/security/verify-code", response_model=CodeVerificationResponse)
async def verify_code(payload: CodeVerificationRequest):
    if payload.language.lower() != "python":
        raise HTTPException(status_code=400, detail="Only Python syntax verification is currently supported.")
    
    constructs = []
    try:
        tree = ast.parse(payload.code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                constructs.append(f"Function: {node.name}")
            elif isinstance(node, ast.ClassDef):
                constructs.append(f"Class: {node.name}")
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                constructs.append("Import statement")
                
        return {
            "is_valid_syntax": True,
            "error_message": None,
            "detected_constructs": list(set(constructs))
        }
    except SyntaxError as e:
        return {
            "is_valid_syntax": False,
            "error_message": f"Line {e.lineno}, Offset {e.offset}: {e.text.strip() if e.text else ''} ({e.msg})",
            "detected_constructs": []
        }
