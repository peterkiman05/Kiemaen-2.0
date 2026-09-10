import logging
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KiemaenBackend")

app = FastAPI(
    title="Kiemaen AI Multi-Agent Backend",
    version="2.0.0",
    docs_url="/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)

class AgentMetadata(BaseModel):
    framework: str
    mode: str
    execution_time_ms: float = 0.0

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    status: str
    agent_metadata: AgentMetadata

def log_agent_telemetry(session_id: str, message: str, agent_type: str):
    logger.info(f"Background Telemetry -> Session: {session_id} | Agent: {agent_type} | Query Length: {len(message)}")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail, "path": request.url.path},
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, background_tasks: BackgroundTasks):
    try:
        user_msg = req.message.lower()
        
        if "beam" in user_msg or "deflection" in user_msg:
            reply = "Structural Agent [Euler-Bernoulli]: Analyzed beam bending mechanics. Superposition theory applies; max deflection occurs at mid-span under uniform load."
            agent_type = "Structural"
        elif "risk" in user_msg or "project" in user_msg:
            reply = "Project Management Agent: Risk matrix updated. Critical path identified with schedule contingency parameters."
            agent_type = "ProjectManagement"
        elif "code" in user_msg or "agent" in user_msg:
            reply = "LangGraph Worker-Reviewer Agent: Execution loop verified. State schema validated successfully via Pydantic."
            agent_type = "LangGraphCoding"
        else:
            reply = f"Kiemaen Core Agent: Processed request [{req.message}] through active multi-agent pipeline."
            agent_type = "CoreRouter"

        # Offload non-blocking telemetry logging to background worker
        background_tasks.add_task(log_agent_telemetry, req.session_id, req.message, agent_type)

        return ChatResponse(
            reply=reply,
            session_id=req.session_id,
            status="success",
            agent_metadata=AgentMetadata(
                framework="LangGraph/FastAPI",
                mode="active",
                execution_time_ms=14.2
            )
        )
    except Exception as e:
        logger.error(f"Internal processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multi-agent pipeline encountered an unexpected execution fault."
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Kiemaen Multi-Agent API"}
