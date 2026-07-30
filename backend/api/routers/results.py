from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter(prefix="/results", tags=["Results"])

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output", "results")

@router.get("")
async def get_results_list():
    """Lists completed result JSON records stored in the output directory."""
    if not os.path.exists(RESULTS_DIR):
        return []
    
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_result.json")]
    results = []
    for filename in files:
        algo = filename.replace("_result.json", "").upper()
        results.append({
            "algorithm": algo,
            "filename": filename,
            "path": f"/api/v1/results/{filename}"
        })
    return results

@router.get("/{filename}")
async def get_result_by_file(filename: str):
    """Retrieves full detailed result schema values for a specific algorithm file."""
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Result file not found.")
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read result: {str(e)}")
