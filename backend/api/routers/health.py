from fastapi import APIRouter
import time
import sys
import os

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def get_health():
    """Returns the API service health, python environment, and system diagnostics."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "python_version": sys.version,
        "platform": sys.platform,
        "server_pid": os.getpid(),
        "active_modules": [
            "FastAPI Server Core",
            "Fuzzy Inference Module",
            "Optimizer Layer Framework",
            "WebSocket Telemetry Dispatcher"
        ]
    }
