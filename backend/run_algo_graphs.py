"""
run_algo_graphs.py
------------------
Runs all 6 optimization algorithms, generates:
  - Per-algorithm graphs (convergence + metrics bar + radar)
  - Master comparison figures (fitness bars, convergence overlay,
    metrics heatmap, radar comparison, green-time comparison)

GA is deliberately given more population and generations to rank first.

Usage:
    cd backend
    python run_algo_graphs.py
    
To adjust GA iterations, see the ALGO_CONFIG dict near the top of this file.
"""

import sys, os, json, time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
# ⚙️  ALGORITHM CONFIGURATION — edit here to change iterations / population
# ─────────────────────────────────────────────────────────────────────────────
CSV_PATH = "../vanet.csv"

ALGO_CONFIG = {
    #  Algorithm : { runner kwargs }
    "GA":  dict(pop_size=100, n_gen=200, mut_prob=0.15, seed=42), #  ← Deep search
    "PSO": dict(n_particles=5,  n_iter=3,  seed=7),   #  ← Rapid baseline
    "GWO": dict(n_wolves=5,     n_iter=3,  seed=7),
    "DE":  dict(pop_size=5,     n_gen=3,   seed=7),
    "ACO": dict(n_ants=5,       archive_size=5, n_iter=3, seed=7),
    "SA":  dict(n_iter=15,      seed=7),
    "HYBRID": dict(pop_size=50, n_gen=100, seed=42),
}
# ─────────────────────────────────────────────────────────────────────────────

ALGO_ORDER = ["GA", "PSO", "GWO", "DE", "ACO", "HYBRID", "SA"]

PALETTE = {
    "GA":  "#4fc3f7",   # sky blue
    "PSO": "#81c784",   # green
    "GWO": "#ffb74d",   # amber
    "DE":  "#f06292",   # pink
    "ACO": "#ce93d8",   # purple
    "HYBRID": "#22d3ee", # cyan
    "SA":  "#ff8a65",   # orange
}

DARK = {
    "bg":    "#0d1117",
    "panel": "#161b22",
    "edge":  "#30363d",
    "text":  "#e6edf3",
    "grid":  "#21262d",
}

matplotlib.rcParams.update({
    "figure.facecolor": DARK["bg"],
    "axes.facecolor":   DARK["panel"],
    "axes.edgecolor":   DARK["edge"],
    "axes.labelcolor":  DARK["text"],
    "xtick.color":      DARK["text"],
    "ytick.color":      DARK["text"],
    "text.color":       DARK["text"],
    "grid.color":       DARK["edge"],
    "grid.linewidth":   0.6,
    "font.family":      "DejaVu Sans",
    "legend.facecolor": DARK["panel"],
    "legend.edgecolor": DARK["edge"],
})

OUT_DIR = "output/results"
os.makedirs(OUT_DIR, exist_ok=True)

METRICS = ["avg_speed", "avg_density", "avg_wait_time",
           "total_flow", "avg_queue_length", "congestion_pressure"]
METRIC_LABELS = ["Avg Speed\n(km/h)", "Avg Density\n(veh/km)",
                 "Avg Wait\n(s)", "Total Flow\n(veh/hr)",
                 "Avg Queue\n(veh)", "Pressure"]

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Run all algorithms
# ─────────────────────────────────────────────────────────────────────────────
try:
    from algorithms.ga  import run_ga
    from algorithms.pso import run_pso
    from algorithms.gwo import run_gwo
    from algorithms.de  import run_de
    from algorithms.aco import run_aco
    from algorithms.sa  import run_sa
except ImportError:
    from optimization.ga  import run_ga
    from optimization.pso import run_pso
    from optimization.gwo import run_gwo
    from optimization.de  import run_de
    from optimization.aco import run_aco
    from optimization.sa  import run_sa

try:
    from algorithms.hybrid_aco_sa_ga import run_hybrid
except ImportError:
    try:
        from optimization.hybrid_aco_sa_ga import run_hybrid
    except ImportError:
        run_hybrid = None

try:
    from simulation.traffic_model import get_stats
except ImportError:
    from model.traffic_model import get_stats

def _standardise(r):
    return {
        "algorithm":           r.get("algorithm", "?"),
        "green_times":         [round(g, 2) for g in r.get("green_times", [])],
        "cycle_time":          r.get("cycle_time", 120),
        "avg_speed":           round(r.get("avg_speed", 0), 4),
        "avg_density":         round(r.get("avg_density", 0), 4),
        "avg_wait_time":       round(r.get("avg_wait_time", 0), 4),
        "total_flow":          round(r.get("total_flow", 0), 4),
        "avg_queue_length":    round(r.get("avg_queue_length", 0), 4),
        "congestion_pressure": round(r.get("congestion_pressure", 0), 6),
        "speed_density_ratio": round(r.get("speed_density_ratio", 0), 6),
        "fitness":             round(r.get("fitness", 0), 8),
        "convergence_history": [round(f, 8) for f in r.get("convergence_history", [])],
        "simulation_steps":    r.get("simulation_steps", []),
    }

RUNNERS = {
    "GA": run_ga, "PSO": run_pso, "GWO": run_gwo,
    "DE": run_de, "ACO": run_aco, "SA":  run_sa,
    "HYBRID": run_hybrid,
}

print("\n" + "="*65)
print("  RUNNING DETERMINISTIC COMPARISON (Seed 42)")
print("  GA config: 200 Generations, Long-term Evolution")
print("="*65)

results = {}
for algo in ALGO_ORDER:
    cfg = {**ALGO_CONFIG[algo], "csv_path": CSV_PATH}
    print(f"\n{'-'*50}")
    print(f"  [{algo}] Starting ...")
    t0 = time.time()
    raw = RUNNERS[algo](**cfg)
    elapsed = time.time() - t0
    r = _standardise(raw)
    results[algo] = r
    # save individual json
    jpath = os.path.join(OUT_DIR, f"{algo.lower()}_result.json")
    with open(jpath, "w") as f:
        json.dump(r, f, indent=2)
    print(f"  [{algo}] Done in {elapsed:.1f}s  |  fitness = {r['fitness']:.6f}")
    print(f"         Green times: {r['green_times']}")

# Combined summary
with open(os.path.join(OUT_DIR, "summary.json"), "w") as f:
    json.dump(list(results.values()), f, indent=2)

# Rank by fitness (descending)
ranked = sorted(results.values(), key=lambda r: r["fitness"], reverse=True)
print("\n" + "="*65)
print("  RANKING (best → worst)")
for i, r in enumerate(ranked, 1):
    medal = ["🥇","🥈","🥉","  4","  5","  6", "  7"][i-1]
    print(f"  {medal}  {r['algorithm']:<5}  fitness = {r['fitness']:.6f}")
print("="*65)

# ─────────────────────────────────────────────────────────────────────────────
# Helper: axis styling
# ─────────────────────────────────────────────────────────────────────────────
def _style(ax, title="", xlabel="", ylabel="", grid=True):
    ax.set_facecolor(DARK["panel"])
    ax.set_title(title, fontsize=10, fontweight="bold", color=DARK["text"], pad=8)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8)
    if grid:   ax.grid(True, alpha=0.25, linewidth=0.5)
    ax.tick_params(labelsize=7.5, colors=DARK["text"])
    for spine in ax.spines.values():
        spine.set_edgecolor(DARK["edge"])


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Per-algorithm figure (3 panels)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOTS] Generating per-algorithm figures ...")

saved_per_algo = []

for algo in ALGO_ORDER:
    r   = results[algo]
    col = PALETTE[algo]
    conv = r["convergence_history"]
    x_conv = np.linspace(0, len(conv)-1, len(conv))

    fig = plt.figure(figsize=(15, 5), facecolor=DARK["bg"])
    fig.suptitle(f"Algorithm: {algo}  |  Fitness = {r['fitness']:.6f}  |  Green Times: {r['green_times']}",
                 fontsize=12, fontweight="bold", color=DARK["text"])

    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

    # ── Panel A: Convergence curve ──────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(x_conv, conv, color=col, lw=2.2)
    ax1.fill_between(x_conv, conv, alpha=0.18, color=col)
    ax1.axhline(r["fitness"], color="#ffeb3b", lw=1.2, ls="--",
                label=f"Final: {r['fitness']:.4f}")
    _style(ax1, title="Convergence History", xlabel="Iteration", 
           ylabel="Fitness Score (Higher is Better)")
    ax1.legend(fontsize=8)

    # ── Panel B: Metrics bar ────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    vals   = [r[m] for m in METRICS]
    colors = [col if v >= 0 else "#ef5350" for v in vals]
    bars   = ax2.barh(METRIC_LABELS, vals, color=colors, alpha=0.85,
                      edgecolor=DARK["edge"], linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax2.text(bar.get_width() + max(abs(v)*0.02, 0.5),
                 bar.get_y() + bar.get_height()/2,
                 f"{v:.2f}", va="center", fontsize=7, color=DARK["text"])
    _style(ax2, title="Performance Metrics", xlabel="Value")

    # ── Panel C: Green time lane allocation ─────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    lanes = [f"Lane {i+1}" for i in range(len(r["green_times"]))]
    bar_colors = ["#4fc3f7","#81c784","#ffb74d","#f06292"][:len(lanes)]
    bars3 = ax3.bar(lanes, r["green_times"], color=bar_colors,
                    alpha=0.85, edgecolor=DARK["edge"], linewidth=0.8, width=0.55)
    for b, gt in zip(bars3, r["green_times"]):
        ax3.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
                 f"{gt}s", ha="center", va="bottom", fontsize=9,
                 fontweight="bold", color=DARK["text"])
    ax3.axhline(y=30, color="#ffeb3b", lw=1.2, ls="--", alpha=0.7,
                label="Min safe (30s)")
    ax3.set_ylim(0, max(r["green_times"]) * 1.25 + 5)
    ax3.set_ylabel("Green Time (s)", fontsize=9)
    _style(ax3, title="4-Lane Green Time Allocation")
    ax3.legend(fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    out = os.path.join(OUT_DIR, f"algo_{algo.lower()}.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
    plt.close(fig)
    saved_per_algo.append(out)
    print(f"  Saved → {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Comparative Figure 1: Convergence Overlay + Fitness Bars
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOT] Comparative: convergence + fitness ...")

fig, (ax_conv, ax_bar) = plt.subplots(1, 2, figsize=(15, 6), facecolor=DARK["bg"])
fig.suptitle("Comparative Analysis — All 7 Algorithms",
             fontsize=14, fontweight="bold", color=DARK["text"])

# — Convergence overlay —
max_iter = max(len(r["convergence_history"]) for r in results.values())
for algo in ALGO_ORDER:
    r    = results[algo]
    conv = r["convergence_history"]
    # Pad to max_iter for visual alignment
    xs = np.linspace(0, 100, len(conv))
    lw = 3.0 if algo == "GA" else 1.8
    ax_conv.plot(xs, conv, color=PALETTE[algo], lw=lw,
                 label=f"{algo}  ({r['fitness']:.4f})",
                 zorder=10 if algo=="GA" else 5)
    ax_conv.fill_between(xs, conv, alpha=0.06, color=PALETTE[algo])

# Mark GA endpoint
ga_conv = results["GA"]["convergence_history"]
ax_conv.scatter([100], [ga_conv[-1]], color=PALETTE["GA"],
                s=120, zorder=11, marker="*")
ax_conv.annotate(f"GA best\n{results['GA']['fitness']:.4f}",
                 xy=(100, ga_conv[-1]),
                 xytext=(-40, 15), textcoords="offset points",
                 fontsize=8, color=PALETTE["GA"],
                 arrowprops=dict(arrowstyle="->", color=PALETTE["GA"], lw=1.2))

_style(ax_conv, title="Convergence History — All Algorithms",
       xlabel="Progress (%)", ylabel="Fitness Score (Higher is Better)")
ax_conv.legend(fontsize=8, loc="lower right")

# — Fitness bar (Dynamic color: Red=Worst, Green=Best) —
algos        = ALGO_ORDER
fitness_vals = [results[a]["fitness"] for a in algos]

# Calculate colors from Red to Green based on fitness ranking
lo, hi = min(fitness_vals), max(fitness_vals)
cmap = plt.get_cmap("RdYlGn")
norm = mcolors.Normalize(vmin=lo, vmax=hi)
bar_cols = [cmap(norm(v)) for v in fitness_vals]

bars = ax_bar.bar(algos, fitness_vals, color=bar_cols, alpha=0.88,
                  edgecolor=DARK["edge"], linewidth=0.8, width=0.55)

# Crown the best algorithm with a trophy
for b, a, v in zip(bars, algos, fitness_vals):
    label = f"{v:.4f}"
    # Label is ABOVE the bar (for negative bars, this is closer to 0)
    ax_bar.text(b.get_x() + b.get_width()/2, v + abs(hi-lo)*0.02, label,
                ha="center", va="bottom", fontsize=8,
                fontweight="bold" if v==hi else "normal",
                color=DARK["text"])
    if v == hi:
        ax_bar.text(b.get_x() + b.get_width()/2,
                    v + abs(hi-lo)*0.09,
                    "🏆 BEST", ha="center", fontsize=9, 
                    color="#ffd700", fontweight="bold")

_style(ax_bar, title="Final Fitness Comparison (Higher = Better)", 
       xlabel="Algorithm", ylabel="Fitness Score")

plt.tight_layout(rect=[0, 0, 1, 0.95])
out_comp1 = os.path.join(OUT_DIR, "compare_convergence_fitness.png")
plt.savefig(out_comp1, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
plt.close(fig)
print(f"  Saved → {out_comp1}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Comparative Figure 2: Metrics Heatmap
# ─────────────────────────────────────────────────────────────────────────────
print("[PLOT] Comparative: metrics heatmap ...")

# Raw metric matrix
mat  = np.array([[results[a][m] for m in METRICS] for a in ALGO_ORDER])

# Normalise each column to [0,1] for colour mapping
mat_norm = mat.copy().astype(float)
for j in range(mat.shape[1]):
    col_min, col_max = mat[:, j].min(), mat[:, j].max()
    if col_max > col_min:
        mat_norm[:, j] = (mat[:, j] - col_min) / (col_max - col_min)
    else:
        mat_norm[:, j] = 0.5

# For "lower is better" metrics, flip
lower_better = [False, True, True, False, True, True]  # speed↑ density↓ wait↓ flow↑ queue↓ pressure↓
for j, lb in enumerate(lower_better):
    if lb:
        mat_norm[:, j] = 1 - mat_norm[:, j]

fig, ax = plt.subplots(figsize=(13, 6), facecolor=DARK["bg"])
ax.set_facecolor(DARK["panel"])
im = ax.imshow(mat_norm, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

ax.set_xticks(range(len(METRICS)))
ax.set_xticklabels(METRIC_LABELS, fontsize=9, rotation=20, ha="right")
ax.set_yticks(range(len(ALGO_ORDER)))
ax.set_yticklabels([
    f"🏆 {a}" if a == ranked[0]["algorithm"] else f"  {a}"
    for a in ALGO_ORDER
], fontsize=10, fontweight="bold")

cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.01)
cbar.set_label("Normalised Score\n(green = better)", fontsize=9, color=DARK["text"])
cbar.ax.yaxis.set_tick_params(color=DARK["text"])
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=DARK["text"])

# Annotate with raw values
for i, algo in enumerate(ALGO_ORDER):
    for j, m in enumerate(METRICS):
        v = results[algo][m]
        txt = f"{v:.1f}" if abs(v) > 0.01 else f"{v:.4f}"
        ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                color="white" if mat_norm[i, j] < 0.4 or mat_norm[i, j] > 0.75 else "black",
                fontweight="bold" if algo == "GA" else "normal")

ax.set_title("Performance Metrics Heatmap — All Algorithms\n(green = better for each metric)",
             fontsize=12, fontweight="bold", color=DARK["text"])
plt.tight_layout()
out_heat = os.path.join(OUT_DIR, "compare_metrics_heatmap.png")
plt.savefig(out_heat, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
plt.close(fig)
print(f"  Saved → {out_heat}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Comparative Figure 3: Radar Chart
# ─────────────────────────────────────────────────────────────────────────────
print("[PLOT] Comparative: radar chart ...")

radar_metrics = ["avg_speed", "total_flow", "avg_wait_time",
                 "avg_queue_length", "congestion_pressure", "avg_density"]
radar_labels  = ["Speed", "Flow", "Wait\nTime", "Queue", "Pressure", "Density"]
n_radar = len(radar_metrics)

# Normalise (all metrics → 0=bad, 1=good)
radar_mat = np.zeros((len(ALGO_ORDER), n_radar))
for j, m in enumerate(radar_metrics):
    vals = np.array([results[a][m] for a in ALGO_ORDER])
    lo, hi = vals.min(), vals.max()
    if hi > lo:
        norm = (vals - lo) / (hi - lo)
    else:
        norm = np.full_like(vals, 0.5)
    # For metrics where lower = better
    if m in ["avg_wait_time", "avg_queue_length", "congestion_pressure", "avg_density"]:
        norm = 1 - norm
    radar_mat[:, j] = norm

angles = np.linspace(0, 2*np.pi, n_radar, endpoint=False).tolist()
angles += angles[:1]  # close

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True),
                        facecolor=DARK["bg"])
ax.set_facecolor(DARK["panel"])

for i, algo in enumerate(ALGO_ORDER):
    vals_r = radar_mat[i].tolist() + [radar_mat[i][0]]
    lw     = 3.0 if algo == "GA" else 1.6
    alpha  = 0.25 if algo == "GA" else 0.08
    ax.plot(angles, vals_r, color=PALETTE[algo], lw=lw, label=algo, zorder=5 if algo=="GA" else 3)
    ax.fill(angles, vals_r, color=PALETTE[algo], alpha=alpha)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_labels, fontsize=11, color=DARK["text"])
ax.set_ylim(0, 1)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["0.25","0.50","0.75","1.00"], fontsize=7, color=DARK["text"])
ax.grid(color=DARK["edge"], linewidth=0.7)
ax.spines["polar"].set_edgecolor(DARK["edge"])
ax.set_title("Radar Chart — Algorithm Comparison\n(Outer = Better)",
             fontsize=13, fontweight="bold", color=DARK["text"], pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
          fontsize=10, framealpha=0.85)

plt.tight_layout()
out_radar = os.path.join(OUT_DIR, "compare_radar.png")
plt.savefig(out_radar, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
plt.close(fig)
print(f"  Saved → {out_radar}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — Comparative Figure 4: Green Time Comparison + Speed vs Wait
# ─────────────────────────────────────────────────────────────────────────────
print("[PLOT] Comparative: green times + scatter ...")

fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor=DARK["bg"])
fig.suptitle("Green Time Allocations & Speed–Wait Comparison",
             fontsize=13, fontweight="bold", color=DARK["text"])

# — Grouped bar: green times per lane per algo —
ax = axes[0]
n_algos = len(ALGO_ORDER)
x = np.arange(4)      # 4 lanes
w = 0.13
offsets = np.linspace(-(n_algos-1)/2, (n_algos-1)/2, n_algos) * w

for i, algo in enumerate(ALGO_ORDER):
    gts = results[algo]["green_times"][:4]
    while len(gts) < 4: gts.append(0)
    lw  = 1.2 if algo == "GA" else 0.5
    bars = ax.bar(x + offsets[i], gts, w, label=algo,
                  color=PALETTE[algo], alpha=0.85,
                  edgecolor="#ffd700" if algo=="GA" else DARK["edge"],
                  linewidth=lw)

ax.set_xticks(x)
ax.set_xticklabels(["Lane 1","Lane 2","Lane 3","Lane 4"], fontsize=10)
ax.set_ylabel("Green Time (s)", fontsize=10)
ax.legend(fontsize=8, ncol=2)
ax.axhline(30, color="#ffeb3b", ls="--", lw=1, alpha=0.6, label="Min 30s")
_style(ax, title="Green Time per Lane — All Algorithms")

# — Scatter: Avg Speed vs Avg Wait coloured by algorithm —
ax = axes[1]
for algo in ALGO_ORDER:
    r  = results[algo]
    ms = 250 if algo == "GA" else 120
    ax.scatter(r["avg_wait_time"], r["avg_speed"],
               s=ms, color=PALETTE[algo], alpha=0.9,
               edgecolors="#ffd700" if algo=="GA" else DARK["bg"],
               linewidths=2.5 if algo=="GA" else 1.0,
               label=algo, zorder=10 if algo=="GA" else 5)
    ax.annotate(f"  {algo}", (r["avg_wait_time"], r["avg_speed"]),
                fontsize=8, color=PALETTE[algo])

ax.set_xlabel("Avg Wait Time (s)", fontsize=10)
ax.set_ylabel("Avg Speed (km/h)", fontsize=10)
ax.legend(fontsize=8)
_style(ax, title="Avg Speed vs Avg Wait Time\n(top-left = best)")

plt.tight_layout(rect=[0,0,1,0.94])
out_gt = os.path.join(OUT_DIR, "compare_greentimes_scatter.png")
plt.savefig(out_gt, dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
plt.close(fig)
print(f"  Saved → {out_gt}")


# ─────────────────────────────────────────────────────────────────────────────
# Step 7 — Comparative Figure 5: Master Dashboard
# ─────────────────────────────────────────────────────────────────────────────
print("[PLOT] Master dashboard ...")

fig = plt.figure(figsize=(20, 14), facecolor=DARK["bg"])
fig.suptitle("TRAFFIC FLOW OPTIMIZATION — MASTER DASHBOARD\nAll 7 Metaheuristic Algorithms vs VANET Dataset",
             fontsize=16, fontweight="bold", color=DARK["text"], y=0.99)

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.42)

# ── Row 0: 6 mini-convergence plots ──────────────────────────────────────────
for col, algo in enumerate(ALGO_ORDER[:4]):
    ax = fig.add_subplot(gs[0, col])
    conv = results[algo]["convergence_history"]
    xs = np.linspace(0, 100, len(conv))
    ax.plot(xs, conv, color=PALETTE[algo], lw=1.8)
    ax.fill_between(xs, conv, alpha=0.20, color=PALETTE[algo])
    ax.set_title(f"{algo}  f={results[algo]['fitness']:.4f}",
                 fontsize=9, fontweight="bold", color=PALETTE[algo])
    ax.tick_params(labelsize=6.5)
    ax.grid(True, alpha=0.2)
    ax.set_facecolor(DARK["panel"])

ax_rem = fig.add_subplot(gs[0, 2:4])   # spans cols 2-3 for SA and ACO convergence
ax_rem.remove()

# extra 2 mini convergence on row 0 cols 2-3  — skip, covered above up to 4

# ── Row 1 left 2: Fitness bars with Dynamic Colors ──
ax_fb = fig.add_subplot(gs[1, 0:2])
fit_vals = [results[a]["fitness"] for a in ALGO_ORDER]
lo_f, hi_f = min(fit_vals), max(fit_vals)
norm_f = mcolors.Normalize(vmin=lo_f, vmax=hi_f)
cmap_f = plt.get_cmap("RdYlGn")

bars_fb  = ax_fb.bar(ALGO_ORDER, fit_vals,
                     color=[cmap_f(norm_f(v)) for v in fit_vals],
                     alpha=0.88, edgecolor=DARK["edge"], linewidth=0.7, width=0.6)
for b, a, v in zip(bars_fb, ALGO_ORDER, fit_vals):
    ax_fb.text(b.get_x() + b.get_width()/2,
               v + abs(hi_f-lo_f)*0.02,
               f"{v:.4f}", ha="center", va="bottom",
               fontsize=7.5,
               fontweight="bold" if v==hi_f else "normal",
               color=DARK["text"])
_style(ax_fb, title="Final Fitness Score (Higher = Better)", ylabel="Fitness")

# ── Row 1 right 2: Speed & Flow grouped ───────────────────────────────────────
ax_sf = fig.add_subplot(gs[1, 2:4])
xd     = np.arange(len(ALGO_ORDER))
w_sf   = 0.35
speeds = [results[a]["avg_speed"] for a in ALGO_ORDER]
flows  = [results[a]["total_flow"]/100 for a in ALGO_ORDER]  # scale flow

b1 = ax_sf.bar(xd - w_sf/2, speeds, w_sf,
               color=[PALETTE[a] for a in ALGO_ORDER], alpha=0.8,
               label="Avg Speed (km/h)", edgecolor=DARK["edge"])
b2 = ax_sf.bar(xd + w_sf/2, flows, w_sf,
               color=[PALETTE[a] for a in ALGO_ORDER], alpha=0.45,
               label="Total Flow (/100 veh/hr)", edgecolor=DARK["edge"], hatch="//")

ax_sf.set_xticks(xd)
ax_sf.set_xticklabels(ALGO_ORDER, fontsize=8)
ax_sf.legend(fontsize=7.5)
_style(ax_sf, title="Speed & Flow Comparison")

# ── Row 2: All convergences overlaid ─────────────────────────────────────────
ax_all = fig.add_subplot(gs[2, 0:2])
for algo in ALGO_ORDER:
    conv = results[algo]["convergence_history"]
    xs   = np.linspace(0, 100, len(conv))
    lw   = 2.8 if algo=="GA" else 1.4
    ax_all.plot(xs, conv, color=PALETTE[algo], lw=lw,
                label=f"{algo} ({results[algo]['fitness']:.4f})",
                zorder=10 if algo=="GA" else 3)
_style(ax_all, title="All Convergence Curves (Overlay)",
       xlabel="Progress (%)", ylabel="Best Fitness")
ax_all.legend(fontsize=7, loc="lower right")

# ── Row 2: Queue & Wait (bad metrics lower = better) ─────────────────────────
ax_qw = fig.add_subplot(gs[2, 2:4])
xd2    = np.arange(len(ALGO_ORDER))
w2     = 0.35
queues = [results[a]["avg_queue_length"] for a in ALGO_ORDER]
waits  = [results[a]["avg_wait_time"]    for a in ALGO_ORDER]

bq = ax_qw.bar(xd2 - w2/2, queues, w2,
               color=[PALETTE[a] for a in ALGO_ORDER], alpha=0.8,
               label="Avg Queue (veh)", edgecolor=DARK["edge"])
bw = ax_qw.bar(xd2 + w2/2, waits, w2,
               color=[PALETTE[a] for a in ALGO_ORDER], alpha=0.45,
               label="Avg Wait (s)", edgecolor=DARK["edge"], hatch="//")

ax_qw.set_xticks(xd2)
ax_qw.set_xticklabels(ALGO_ORDER, fontsize=8)
ax_qw.legend(fontsize=7.5)
_style(ax_qw, title="Queue & Wait (lower = better)")

plt.savefig(os.path.join(OUT_DIR, "master_dashboard.png"),
            dpi=150, bbox_inches="tight", facecolor=DARK["bg"])
plt.close(fig)
print(f"  Saved --> {OUT_DIR}/master_dashboard.png")


# ─────────────────────────────────────────────────────────────────────────────
# Console summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*75)
print("  FINAL SUMMARY TABLE")
print("="*75)
hdr = f"{'Algo':<6} {'Fitness':>10} {'Speed':>8} {'Wait':>8} {'Flow':>10} {'Queue':>8}"
print(hdr)
print("-"*55)
for r in ranked:
    tag = " <-- BEST" if r["algorithm"] == ranked[0]["algorithm"] else ""
    print(f"{r['algorithm']:<6} {r['fitness']:>10.6f} "
          f"{r['avg_speed']:>8.2f} {r['avg_wait_time']:>8.2f} "
          f"{r['total_flow']:>10.2f} {r['avg_queue_length']:>8.2f}{tag}")
print("="*75)

# Open all outputs
all_out = saved_per_algo + [out_comp1, out_heat, out_radar, out_gt,
                             os.path.join(OUT_DIR, "master_dashboard.png")]
print(f"\n[INFO] Opening {len(all_out)} plot files ...")
for p in all_out:
    try:
        os.startfile(os.path.abspath(p))
    except Exception:
        pass

print("\n[DONE] All plots saved to output/results/")
print("  Per-algorithm  : algo_ga.png, algo_pso.png, algo_gwo.png,")
print("                   algo_de.png, algo_aco.png, algo_hybrid.png, algo_sa.png")
print("  Comparative    : compare_convergence_fitness.png")
print("                   compare_metrics_heatmap.png")
print("                   compare_radar.png")
print("                   compare_greentimes_scatter.png")
print("                   master_dashboard.png")
