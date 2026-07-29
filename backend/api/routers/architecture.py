from fastapi import APIRouter

router = APIRouter(prefix="/architecture", tags=["Architecture"])

ARCHITECTURE_METADATA = [
    {
        "id": "dataset",
        "title": "Traffic Dataset",
        "step": 1,
        "purpose": "Serves as the empirical basis for traffic scenarios, supplying real-world vehicle profiles and demands into the simulation.",
        "inputs": "None (initial database read).",
        "outputs": "Historical traffic flows, lane speeds, queue counts, congestion pressures.",
        "files": "vanet.csv",
        "moduleName": "vanet.csv Loader",
        "executionSequence": "1. Executed at startup inside simulation initialization.",
        "dependencies": "None."
    },
    {
        "id": "model",
        "title": "Traffic Model",
        "step": 2,
        "purpose": "Simulates vehicular flows and lane transitions microscopically based on speed-density and capacity relationships.",
        "inputs": "Green time phase durations, vehicle arrivals.",
        "outputs": "Average velocities, lane congestion densities, waiting times, queue backlogs.",
        "files": "backend/simulation/traffic_model.py",
        "moduleName": "simulation.traffic_model",
        "executionSequence": "2. Evaluated on each candidate parameter step to build queue configurations.",
        "dependencies": "Traffic Dataset configuration."
    },
    {
        "id": "fitness",
        "title": "Fitness Evaluation",
        "step": 3,
        "purpose": "Translates vehicular metrics into a standardized quality score, determining the efficiency of candidate timing parameters.",
        "inputs": "Average speed, total flow rate, waiting latency, queue lengths, congestion index.",
        "outputs": "Continuous score value (fitness) within [-1.0, 1.0].",
        "files": "backend/evaluation/fitness.py",
        "moduleName": "evaluation.fitness",
        "executionSequence": "3. Calculated inside the objective evaluator function for every candidate vector.",
        "dependencies": "Traffic Model output arrays."
    },
    {
        "id": "optimizer",
        "title": "Optimizer Layer",
        "step": 4,
        "purpose": "Runs continuous space parameter adjustments to find the best-performing membership breakpoint boundaries.",
        "inputs": "Fitness evaluation function, boundary dimensions, seed variables.",
        "outputs": "Updated population positions, global best parameter arrays.",
        "files": "backend/algorithms/ (ga.py, pso.py, gwo.py, de.py, aco.py, sa.py)",
        "moduleName": "algorithms.base.optimizer",
        "executionSequence": "4. Iteratively adjusts decision positions over generations during execution.",
        "dependencies": "Fitness Evaluation function."
    },
    {
        "id": "telemetry",
        "title": "Telemetry Collector",
        "step": 5,
        "purpose": "Records step-by-step search characteristics and fitness progress at the end of every optimization generation.",
        "inputs": "Population fitness lists, evaluations index, generation counter.",
        "outputs": "Immutably frozen TelemetrySnapshot entries stored in a rolling window deque.",
        "files": "backend/algorithms/operators/telemetry_engine.py",
        "moduleName": "algorithms.operators.telemetry_engine",
        "executionSequence": "5. Invoked inside the step handler immediately after optimizer evaluation.",
        "dependencies": "Optimizer Layer state outputs."
    },
    {
        "id": "extractor",
        "title": "Feature Extraction",
        "step": 6,
        "purpose": "Analyzes historical snapshot arrays to evaluate convergence gradients and stability rates.",
        "inputs": "Rolling window array of TelemetrySnapshot entries.",
        "outputs": "Progress Rate, Diversity Trend, Search Stability, Budget Pressure features.",
        "files": "backend/algorithms/operators/feature_extractor.py",
        "moduleName": "algorithms.operators.feature_extractor",
        "executionSequence": "6. Executed inside decision engine pre-processing pipeline.",
        "dependencies": "Telemetry Collector database."
    },
    {
        "id": "estimator",
        "title": "Need Estimation",
        "step": 7,
        "purpose": "Evaluates trend indicators to score demands for searching behavior across three distinct objectives.",
        "inputs": "Extracted feature trends (Progress Rate, Diversity Trend, Search Stability, Budget Pressure).",
        "outputs": "Ratings for Exploration, Exploitation, and Escape needs.",
        "files": "backend/algorithms/operators/need_estimator.py",
        "moduleName": "algorithms.operators.need_estimator",
        "executionSequence": "7. Executed to create the current demand profile before evaluation mapping.",
        "dependencies": "Feature Extraction outputs."
    },
    {
        "id": "decision",
        "title": "Decision Engine",
        "step": 8,
        "purpose": "Maps current needs to static optimizer capability profiles to score suitability.",
        "inputs": "Normalized search needs, static optimizer capability configurations.",
        "outputs": "Sorted capability scoring lists, target strategy recommendation.",
        "files": "backend/algorithms/operators/decision_engine.py, optimizer_capabilities.py",
        "moduleName": "algorithms.operators.decision_engine",
        "executionSequence": "8. Evaluates profiles on every step to yield a strategy choice.",
        "dependencies": "Need Estimation outputs, Capability configurations."
    },
    {
        "id": "controller",
        "title": "Adaptive Switch Controller",
        "step": 9,
        "purpose": "Validates switch safety thresholds and cooldown locks before triggering strategy transitions.",
        "inputs": "Best recommended optimizer, current active optimizer name, active optimizer runtime steps, steps since last switch.",
        "outputs": "Boolean transition decision, target strategy updates.",
        "files": "backend/algorithms/operators/adaptive_switch_controller.py, asm_controller.py",
        "moduleName": "algorithms.operators.adaptive_switch_controller",
        "executionSequence": "9. Executed at the beginning of the step loop before invoking sub-optimizers.",
        "dependencies": "Decision Engine recommendations."
    },
    {
        "id": "results",
        "title": "Results Output",
        "step": 10,
        "purpose": "Exports optimization records, convergence values, and timing configurations to local database files.",
        "inputs": "Optimized parameter lists, convergence arrays, simulation metrics.",
        "outputs": "JSON result records saved to output directories.",
        "files": "backend/output/results/",
        "moduleName": "main.py Results Exporter",
        "executionSequence": "10. Executed at the completion of optimization runs.",
        "dependencies": "Adaptive Switch Controller evaluations."
    }
]

@router.get("")
async def get_architecture():
    """Returns the architecture layers metadata dynamically."""
    return ARCHITECTURE_METADATA
