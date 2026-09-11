import time
import logging
from fastapi import Request

logger = logging.getLogger("uvicorn.error")

async def add_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} | Path: {request.url.path} | "
        f"Status: {response.status_code} | Latency: {duration:.2f}ms"
    )
    return response

