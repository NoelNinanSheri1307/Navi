from fastapi import APIRouter

router = APIRouter(prefix="/asm", tags=["ASM"])

ASM_METADATA = {
    "capabilities": {
        "GA": [5, 3, 2],
        "DE": [4, 3, 3],
        "PSO": [2, 5, 1],
        "GWO": [3, 4, 2],
        "ACO": [4, 3, 3],
        "SA": [1, 2, 5]
    },
    "needs_rules": {
        "Exploration": "Triggered by high diversity decay rates and flat convergence progress. Encourages global search space diversification.",
        "Exploitation": "Triggered by rapid fitness progression. Highlights local parameter fine-tuning.",
        "Escape": "Triggered by long periods of stagnated search stability (zero fitness change over iterations). Forces stochastic coordinates changes."
    },
    "safety_controller_thresholds": {
        "confidence_threshold": 0.03,
        "minimum_runtime_steps": 5,
        "cooldown_steps": 5
    }
}

@router.get("")
async def get_asm_spec():
    """Returns the ASM capability configuration parameters dynamically."""
    return ASM_METADATA
