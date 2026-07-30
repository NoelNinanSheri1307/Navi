import sys
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Ensure the parent directory is in the path to resolve local imports cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routers import (
    health,
    datasets,
    algorithms,
    architecture,
    asm,
    results,
    benchmark,
    simulation
)
from api.services.simulation_service import SimulationService

app = FastAPI(
    title="Navi API Service",
    description="Service-oriented API wrapper for Navi Adaptive Traffic Intelligence Framework.",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

def get_cors_origins():
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    origins = []
    for origin in raw_origins.split(","):
        origin = origin.strip()
        if origin:
            # Browsers send the Origin header without trailing slashes. 
            # Strip them here to ensure exact string matching in CORSMiddleware.
            if origin.endswith("/"):
                origin = origin[:-1]
            origins.append(origin)
    return origins


# Enable CORS for frontend clients (Vite dev servers and deployed Vercel/Render fronts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers with versioned route prefixes
app.include_router(health.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(algorithms.router, prefix="/api/v1")
app.include_router(architecture.router, prefix="/api/v1")
app.include_router(asm.router, prefix="/api/v1")
app.include_router(results.router, prefix="/api/v1")
app.include_router(benchmark.router, prefix="/api/v1")
app.include_router(simulation.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # Register the asyncio loop inside the SimulationService singleton
    loop = asyncio.get_running_loop()
    SimulationService().register_loop(loop)
    print("[INFO] Navi API Service initialized successfully on startup event.")
