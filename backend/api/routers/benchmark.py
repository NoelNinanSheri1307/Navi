from fastapi import APIRouter, Query, HTTPException
import os
import json
from typing import List, Optional

router = APIRouter(prefix="/benchmark", tags=["Benchmark"])

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output", "results")

@router.get("")
async def get_benchmarks(
    sort_by: str = Query("fitness", enum=["fitness", "avg_wait_time", "total_flow"]),
    algorithms: Optional[List[str]] = Query(None)
):
    """Retrieves comparative statistics and ranks across completed runs."""
    summary_path = os.path.join(RESULTS_DIR, "summary.json")
    
    # Fallback compilation if summary does not exist
    if not os.path.isfile(summary_path):
        # Scan and compile on the fly
        if not os.path.exists(RESULTS_DIR):
            raise HTTPException(status_code=404, detail="No benchmark results directory found.")
        files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_result.json")]
        records = []
        for filename in files:
            try:
                with open(os.path.join(RESULTS_DIR, filename), "r") as f:
                    records.append(json.load(f))
            except Exception:
                continue
    else:
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                records = json.load(f)
        except Exception:
            records = []

    if not records:
        return []

    # Filter algorithms
    if algorithms:
        upper_algos = [a.upper() for a in algorithms]
        records = [r for r in records if r.get("algorithm", "").upper() in upper_algos]

    # Sort records
    if sort_by == "fitness":
        # Fitness is negative, so sort descending (closer to 0 is better)
        records.sort(key=lambda x: x.get("fitness", -1.0), reverse=True)
    elif sort_by == "avg_wait_time":
        # Waiting time is positive, sort ascending (lower wait is better)
        records.sort(key=lambda x: x.get("avg_wait_time", 9999.0))
    elif sort_by == "total_flow":
        # Throughput is positive, sort descending (higher flow is better)
        records.sort(key=lambda x: x.get("total_flow", 0.0), reverse=True)

    # Inject ranks
    for idx, r in enumerate(records):
        r["rank"] = idx + 1

    return records
