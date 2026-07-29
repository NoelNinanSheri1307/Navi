from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from pydantic import BaseModel
import time
from api.services.simulation_service import SimulationService

router = APIRouter(prefix="/simulation", tags=["Simulation"])
sim_service = SimulationService()

class StartRequest(BaseModel):
    algorithm: str
    dataset: str = "vanet.csv"
    pop_size: int = 15
    n_gen: int = 20

@router.post("/start")
async def start_sim(req: StartRequest):
    """Starts the background optimization simulation run thread."""
    try:
        sim_service.start_simulation(
            algorithm=req.algorithm,
            dataset=req.dataset,
            pop_size=req.pop_size,
            n_gen=req.n_gen
        )
        return {"status": "started", "algorithm": req.algorithm}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pause")
async def pause_sim():
    """Pauses the active stepping loop checks."""
    sim_service.pause()
    sim_service.broadcast_sync({
        "type": "event",
        "event": "Simulation Paused",
        "timestamp": time.time(),
        "payload": {}
    })
    return {"status": "paused"}

@router.post("/resume")
async def resume_sim():
    """Resumes the active stepping loop checks."""
    sim_service.resume()
    sim_service.broadcast_sync({
        "type": "event",
        "event": "Simulation Resumed",
        "timestamp": time.time(),
        "payload": {}
    })
    return {"status": "running"}

@router.post("/cancel")
async def cancel_sim():
    """Cancels the active optimization run immediately."""
    sim_service.cancel()
    return {"status": "cancelled"}

@router.post("/reset")
async def reset_sim():
    """Resets the simulator state back to baseline configurations."""
    sim_service.reset()
    return {"status": "reset"}

@router.post("/speed")
async def change_speed(multiplier: float = Query(1.0, ge=0.1, le=10.0)):
    """Adjusts the playback transition delays."""
    sim_service.set_speed(multiplier)
    return {"status": "speed_updated", "multiplier": multiplier}

@router.get("/status")
async def get_status():
    """Returns the current runtime status variables."""
    return {
        "running": sim_service.running,
        "paused": sim_service.paused,
        "current_step": sim_service.current_step,
        "total_steps": sim_service.total_steps,
        "active_algorithm": sim_service.active_algorithm,
        "active_dataset": sim_service.active_dataset,
        "speed_multiplier": sim_service.speed_multiplier
    }

@router.get("/history")
async def get_history_runs():
    """Returns completed simulation runs list cache."""
    return sim_service.history_records

@router.websocket("/ws")
async def websocket_telemetry(websocket: WebSocket):
    """
    WebSocket route establishing persistent full-duplex telemetry channels
    and handling command-triggered swaps dynamically.
    """
    await websocket.accept()
    sim_service.add_subscriber(websocket)
    
    # Broadcast initial system state
    await websocket.send_json({
        "type": "status",
        "status": {
            "running": sim_service.running,
            "paused": sim_service.paused,
            "current_step": sim_service.current_step,
            "active_algorithm": sim_service.active_algorithm,
            "speed_multiplier": sim_service.speed_multiplier
        }
    })

    try:
        while True:
            # Maintain socket connection, processing any client-side socket payloads if triggered
            data = await websocket.receive_json()
            cmd = data.get("command")
            if cmd == "pause":
                sim_service.pause()
            elif cmd == "resume":
                sim_service.resume()
            elif cmd == "cancel":
                sim_service.cancel()
            elif cmd == "speed":
                sim_service.set_speed(data.get("value", 1.0))
    except WebSocketDisconnect:
        pass
    finally:
        sim_service.remove_subscriber(websocket)
