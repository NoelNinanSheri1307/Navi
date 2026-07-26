"""
run_fuzzy_demo.py
-----------------
Standalone demo for the Fuzzy Logic System.

What it does:
  1. Loads VANET.csv  (samples up to MAX_SAMPLE_ROWS rows for inference)
  2. Builds the fuzzy system with DEFAULT (mid-point) parameters
  3. Plots all 5 input membership functions + the output MF
  4. Runs the fuzzy system on the sample rows and collects green times
  5. Plots green time distribution + per-lane allocation bar chart
  6. Prints a console table of sample rows with predicted green times

Usage:
    cd backend
    python run_fuzzy_demo.py
"""

# Max rows to use for fuzzy inference (full 195k rows is very slow)
MAX_SAMPLE_ROWS = 500

import sys
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ─── colour palette ───────────────────────────────────────────────────────────
COLORS = {
    'low':    '#4fc3f7',
    'medium': '#81c784',
    'high':   '#ef9a9a',
    'short':  '#4fc3f7',
    'long':   '#ef9a9a',
    'line':   '#37474f',
    'fill_alpha': 0.30,
    'bg':     '#0d1117',
    'panel':  '#161b22',
    'text':   '#e6edf3',
    'grid':   '#30363d',
}

matplotlib.rcParams.update({
    'figure.facecolor':  COLORS['bg'],
    'axes.facecolor':    COLORS['panel'],
    'axes.edgecolor':    COLORS['grid'],
    'axes.labelcolor':   COLORS['text'],
    'xtick.color':       COLORS['text'],
    'ytick.color':       COLORS['text'],
    'text.color':        COLORS['text'],
    'grid.color':        COLORS['grid'],
    'grid.linewidth':    0.6,
    'font.family':       'DejaVu Sans',
    'legend.facecolor':  COLORS['panel'],
    'legend.edgecolor':  COLORS['grid'],
})

# ─── Load dataset ─────────────────────────────────────────────────────────────
CSV_PATH = "../vanet.csv"
if not os.path.isfile(CSV_PATH):
    alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vanet.csv")
    if os.path.isfile(alt):
        CSV_PATH = alt
    else:
        raise FileNotFoundError(
            "vanet.csv not found. Place it in the Navi root directory."
        )

df = pd.read_csv(CSV_PATH)
print(f"[OK] Loaded dataset: {len(df)} rows  columns: {list(df.columns)}")

# Sample for inference (keeps plots fast on large datasets)
if len(df) > MAX_SAMPLE_ROWS:
    df_sample = df.sample(MAX_SAMPLE_ROWS, random_state=42).reset_index(drop=True)
    print(f"[INFO] Sampling {MAX_SAMPLE_ROWS} rows from {len(df)} for fuzzy inference.")
else:
    df_sample = df.copy()

# ─── Compute stats ────────────────────────────────────────────────────────────
stats = {
    'cp_min':  df['congestion_pressure'].min(),
    'cp_max':  df['congestion_pressure'].max(),
    'den_min': df['density_veh_per_km'].min(),
    'den_max': df['density_veh_per_km'].max(),
    'que_min': df['queue_length_veh'].min(),
    'que_max': df['queue_length_veh'].max(),
    'wt_min':  df['avg_wait_time_s'].min(),
    'wt_max':  df['avg_wait_time_s'].max(),
    'fl_min':  df['flow_veh_per_hr'].min(),
    'fl_max':  df['flow_veh_per_hr'].max(),
}

# ─── Default params (evenly spaced breakpoints) ───────────────────────────────
DEFAULT_PARAMS = np.array([
    0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,  # congestion_pressure
    0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,  # density_veh_per_km
    0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,  # queue_length_veh
    0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,  # avg_wait_time_s
    0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,  # flow_veh_per_hr
])

# ─── Helper: generate breakpoints ─────────────────────────────────────────────
def gen_vals(lo, hi, params):
    span = hi - lo
    p = np.sort(lo + np.clip(params, 0.0, 1.0) * span)
    return [lo, p[0], p[1], p[2], p[3], p[4], p[5], p[6], hi]

# ─── Build fuzzy universes & MFs ──────────────────────────────────────────────
def build_mfs(params=DEFAULT_PARAMS):
    s = stats
    cp_v = gen_vals(s['cp_min'],  s['cp_max'],  params[0:7])
    d_v  = gen_vals(s['den_min'], s['den_max'], params[7:14])
    q_v  = gen_vals(s['que_min'], s['que_max'], params[14:21])
    w_v  = gen_vals(s['wt_min'],  s['wt_max'],  params[21:28])
    f_v  = gen_vals(s['fl_min'],  s['fl_max'],  params[28:35])

    n = 300
    universes = {
        'congestion_pressure': np.linspace(s['cp_min'],  s['cp_max'],  n),
        'density_veh_per_km':  np.linspace(s['den_min'], s['den_max'], n),
        'queue_length_veh':    np.linspace(s['que_min'], s['que_max'], n),
        'avg_wait_time_s':     np.linspace(s['wt_min'],  s['wt_max'],  n),
        'flow_veh_per_hr':     np.linspace(s['fl_min'],  s['fl_max'],  n),
        'green_time':          np.arange(10, 91, 1),
    }

    mfs = {
        'congestion_pressure': {
            'low':    fuzz.trapmf(universes['congestion_pressure'], [cp_v[0], cp_v[0], cp_v[1], cp_v[2]]),
            'medium': fuzz.trimf(universes['congestion_pressure'],  [cp_v[3], cp_v[4], cp_v[5]]),
            'high':   fuzz.trapmf(universes['congestion_pressure'], [cp_v[6], cp_v[7], cp_v[8], cp_v[8]]),
        },
        'density_veh_per_km': {
            'low':    fuzz.trapmf(universes['density_veh_per_km'], [d_v[0], d_v[0], d_v[1], d_v[2]]),
            'medium': fuzz.trimf(universes['density_veh_per_km'],  [d_v[3], d_v[4], d_v[5]]),
            'high':   fuzz.trapmf(universes['density_veh_per_km'], [d_v[6], d_v[7], d_v[8], d_v[8]]),
        },
        'queue_length_veh': {
            'short':  fuzz.trapmf(universes['queue_length_veh'], [q_v[0], q_v[0], q_v[1], q_v[2]]),
            'medium': fuzz.trimf(universes['queue_length_veh'],  [q_v[3], q_v[4], q_v[5]]),
            'long':   fuzz.trapmf(universes['queue_length_veh'], [q_v[6], q_v[7], q_v[8], q_v[8]]),
        },
        'avg_wait_time_s': {
            'low':    fuzz.trapmf(universes['avg_wait_time_s'], [w_v[0], w_v[0], w_v[1], w_v[2]]),
            'medium': fuzz.trimf(universes['avg_wait_time_s'],  [w_v[3], w_v[4], w_v[5]]),
            'high':   fuzz.trapmf(universes['avg_wait_time_s'], [w_v[6], w_v[7], w_v[8], w_v[8]]),
        },
        'flow_veh_per_hr': {
            'low':    fuzz.trapmf(universes['flow_veh_per_hr'], [f_v[0], f_v[0], f_v[1], f_v[2]]),
            'medium': fuzz.trimf(universes['flow_veh_per_hr'],  [f_v[3], f_v[4], f_v[5]]),
            'high':   fuzz.trapmf(universes['flow_veh_per_hr'], [f_v[6], f_v[7], f_v[8], f_v[8]]),
        },
        'green_time': {
            'short':  fuzz.trimf(universes['green_time'], [10, 25, 40]),
            'medium': fuzz.trimf(universes['green_time'], [35, 50, 65]),
            'long':   fuzz.trimf(universes['green_time'], [60, 75, 90]),
        },
    }
    return universes, mfs

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Membership Functions (6 subplots)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOT 1] Drawing membership function plots ...")

universes, mfs = build_mfs()

var_info = [
    ('congestion_pressure', 'Congestion Pressure',   ['low', 'medium', 'high']),
    ('density_veh_per_km',  'Density (veh/km)',       ['low', 'medium', 'high']),
    ('queue_length_veh',    'Queue Length (veh)',     ['short', 'medium', 'long']),
    ('avg_wait_time_s',     'Avg Wait Time (s)',      ['low', 'medium', 'high']),
    ('flow_veh_per_hr',     'Flow (veh/hr)',          ['low', 'medium', 'high']),
    ('green_time',          'Green Time (s) — OUTPUT',['short', 'medium', 'long']),
]

fig1, axes = plt.subplots(2, 3, figsize=(16, 8))
fig1.suptitle('Fuzzy Membership Functions — VANET Traffic Controller',
              fontsize=15, fontweight='bold', color=COLORS['text'], y=1.01)
fig1.patch.set_facecolor(COLORS['bg'])

label_color_map = {
    'low': COLORS['low'], 'short': COLORS['short'],
    'medium': COLORS['medium'],
    'high': COLORS['high'], 'long': COLORS['long'],
}

for ax, (var, title, labels) in zip(axes.flat, var_info):
    u  = universes[var]
    mf = mfs[var]
    for label in labels:
        c = label_color_map[label]
        ax.plot(u, mf[label], color=c, lw=2.2, label=label.capitalize())
        ax.fill_between(u, mf[label], alpha=COLORS['fill_alpha'], color=c)

    ax.set_title(title, fontsize=10, fontweight='bold', color=COLORS['text'])
    ax.set_xlabel('Universe', fontsize=8)
    ax.set_ylabel('Membership', fontsize=8)
    ax.set_ylim(-0.05, 1.15)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7)

plt.tight_layout()
out1 = "output/results/fuzzy_membership_functions.png"
os.makedirs("output/results", exist_ok=True)
plt.savefig(out1, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
print(f"  Saved → {out1}")
plt.close(fig1)


# ─────────────────────────────────────────────────────────────────────────────
# Build fuzzy control system and compute green times for all rows
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[INFO] Running fuzzy inference on {len(df_sample)} sampled rows ...")

from fuzzy.fuzzy_system import set_dataset_stats, build_fuzzy_system, compute_green_time

set_dataset_stats(stats)
fuzzy_sim = build_fuzzy_system(DEFAULT_PARAMS)

green_times_all = []
for idx, (_, row) in enumerate(df_sample.iterrows()):
    gt = compute_green_time(fuzzy_sim, row.to_dict())
    green_times_all.append(gt)
    if (idx + 1) % 100 == 0:
        print(f"  ... {idx+1}/{len(df_sample)} rows processed")

df_sample['predicted_green_time'] = green_times_all
df = df_sample   # use sample for all subsequent plots
print(f"  Green time range: {min(green_times_all):.1f}s – {max(green_times_all):.1f}s")
print(f"  Mean green time : {np.mean(green_times_all):.2f}s")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Green Time Distribution + Scatter
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOT 2] Drawing green time analysis plots ...")

fig2, axes2 = plt.subplots(1, 3, figsize=(17, 5))
fig2.suptitle('Fuzzy Green Time Predictions on VANET Dataset',
              fontsize=13, fontweight='bold', color=COLORS['text'])
fig2.patch.set_facecolor(COLORS['bg'])

# — Histogram —
ax = axes2[0]
ax.hist(green_times_all, bins=20, color='#7c4dff', edgecolor='#b388ff',
        alpha=0.85, linewidth=0.8)
ax.axvline(np.mean(green_times_all), color='#ffeb3b', lw=2,
           linestyle='--', label=f'Mean={np.mean(green_times_all):.1f}s')
ax.set_title('Green Time Distribution', fontweight='bold')
ax.set_xlabel('Green Time (s)')
ax.set_ylabel('Frequency')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.25)

# — Scatter: congestion_pressure vs green_time —
ax = axes2[1]
sc = ax.scatter(df['congestion_pressure'], df['predicted_green_time'],
                c=df['queue_length_veh'], cmap='plasma',
                alpha=0.7, s=25, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Queue Length (veh)', color=COLORS['text'], fontsize=8)
cbar.ax.yaxis.set_tick_params(color=COLORS['text'])
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=COLORS['text'])
ax.set_title('Congestion Pressure vs Green Time', fontweight='bold')
ax.set_xlabel('Congestion Pressure')
ax.set_ylabel('Predicted Green Time (s)')
ax.grid(True, alpha=0.25)

# — Scatter: avg_wait_time_s vs green_time —
ax = axes2[2]
sc2 = ax.scatter(df['avg_wait_time_s'], df['predicted_green_time'],
                 c=df['flow_veh_per_hr'], cmap='cool',
                 alpha=0.7, s=25, edgecolors='none')
cbar2 = plt.colorbar(sc2, ax=ax)
cbar2.set_label('Flow (veh/hr)', color=COLORS['text'], fontsize=8)
cbar2.ax.yaxis.set_tick_params(color=COLORS['text'])
plt.setp(cbar2.ax.yaxis.get_ticklabels(), color=COLORS['text'])
ax.set_title('Wait Time vs Green Time', fontweight='bold')
ax.set_xlabel('Avg Wait Time (s)')
ax.set_ylabel('Predicted Green Time (s)')
ax.grid(True, alpha=0.25)

plt.tight_layout()
out2 = "output/results/fuzzy_green_time_analysis.png"
plt.savefig(out2, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
print(f"  Saved → {out2}")
plt.close(fig2)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — 4-Lane Intersection: Sample Green Time Allocation
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOT 3] Drawing 4-lane green time allocation ...")

# Sample 5 different 4-lane scenarios
np.random.seed(42)
scenarios = []
for i in range(5):
    idx  = np.random.choice(len(df), 4, replace=False)
    rows = [df.iloc[j] for j in idx]
    gts  = [compute_green_time(fuzzy_sim, r.to_dict()) for r in rows]
    # Scale to budget
    total = sum(gts)
    budget = 120 - 16   # 4s amber per lane
    scale  = min(budget / total, 1.0) if total > 0 else 1.0
    gts = [max(10.0, min(g * scale, 90.0)) for g in gts]
    scenarios.append(gts)

fig3, ax3 = plt.subplots(figsize=(12, 6))
fig3.patch.set_facecolor(COLORS['bg'])
ax3.set_facecolor(COLORS['panel'])

lanes    = ['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4']
x        = np.arange(4)
width    = 0.14
pal      = ['#4fc3f7', '#81c784', '#ffb74d', '#f06292', '#ce93d8']

for s_i, (gts, col) in enumerate(zip(scenarios, pal)):
    bars = ax3.bar(x + s_i * width, gts, width, label=f'Scenario {s_i+1}',
                   color=col, alpha=0.85, edgecolor=COLORS['panel'], linewidth=0.5)
    for bar, gt in zip(bars, gts):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f'{gt:.0f}s', ha='center', va='bottom', fontsize=7,
                 color=COLORS['text'])

ax3.axhline(y=30, color='#ffeb3b', lw=1.2, linestyle='--', alpha=0.6, label='Min safety (30s)')
ax3.set_xticks(x + width * 2)
ax3.set_xticklabels(lanes, fontsize=11, fontweight='bold')
ax3.set_ylabel('Green Time (seconds)', fontsize=11)
ax3.set_title('Fuzzy Green Time Allocation — 5 Sample 4-Lane Scenarios',
              fontsize=13, fontweight='bold', color=COLORS['text'])
ax3.legend(fontsize=9, loc='upper right')
ax3.set_ylim(0, 100)
ax3.grid(True, axis='y', alpha=0.25)
ax3.tick_params(labelsize=9)

plt.tight_layout()
out3 = "output/results/fuzzy_lane_allocation.png"
plt.savefig(out3, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
print(f"  Saved → {out3}")
plt.close(fig3)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — Feature Correlation Heatmap
# ─────────────────────────────────────────────────────────────────────────────
print("\n[PLOT 4] Drawing feature correlation heatmap ...")

fig4, ax4 = plt.subplots(figsize=(8, 6))
fig4.patch.set_facecolor(COLORS['bg'])
ax4.set_facecolor(COLORS['panel'])

cols_plot = ['congestion_pressure','density_veh_per_km','queue_length_veh',
             'avg_wait_time_s','flow_veh_per_hr','predicted_green_time']
corr = df[cols_plot].corr()

import matplotlib.colors as mcolors
cmap = plt.cm.RdYlGn

im = ax4.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1, aspect='auto')
plt.colorbar(im, ax=ax4, label='Pearson r')
ax4.set_xticks(range(len(cols_plot)))
ax4.set_yticks(range(len(cols_plot)))
short_names = ['Cong.', 'Density', 'Queue', 'Wait', 'Flow', 'GreenTime']
ax4.set_xticklabels(short_names, rotation=30, ha='right', fontsize=9)
ax4.set_yticklabels(short_names, fontsize=9)
ax4.set_title('Feature Correlation Matrix (incl. Predicted Green Time)',
              fontsize=11, fontweight='bold')

# Annotate cells
for i in range(len(cols_plot)):
    for j in range(len(cols_plot)):
        ax4.text(j, i, f'{corr.values[i,j]:.2f}',
                 ha='center', va='center', fontsize=8,
                 color='black' if abs(corr.values[i,j]) < 0.5 else 'white')

plt.tight_layout()
out4 = "output/results/fuzzy_correlation_heatmap.png"
plt.savefig(out4, dpi=150, bbox_inches='tight', facecolor=COLORS['bg'])
print(f"  Saved → {out4}")
plt.close(fig4)


# ─────────────────────────────────────────────────────────────────────────────
# Console output table — first 10 rows
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*90)
print("  FUZZY SYSTEM — SAMPLE PREDICTIONS (first 10 rows of VANET.csv)")
print("="*90)
cols_show = ['congestion_pressure','density_veh_per_km','queue_length_veh',
             'avg_wait_time_s','flow_veh_per_hr','predicted_green_time']
header = f"{'Row':>4} {'CongP':>8} {'Den':>8} {'Queue':>7} {'Wait':>7} {'Flow':>8} {'GreenT':>8}"
print(header)
print("-"*60)
for i, row in df[cols_show].head(10).iterrows():
    print(
        f"{i:>4} "
        f"{row['congestion_pressure']:>8.3f} "
        f"{row['density_veh_per_km']:>8.2f} "
        f"{row['queue_length_veh']:>7.1f} "
        f"{row['avg_wait_time_s']:>7.2f} "
        f"{row['flow_veh_per_hr']:>8.1f} "
        f"{row['predicted_green_time']:>8.1f}s"
    )
print("="*90)

print(f"\n[DONE] All 4 plots saved to output/results/")
print(f"  1. fuzzy_membership_functions.png")
print(f"  2. fuzzy_green_time_analysis.png")
print(f"  3. fuzzy_lane_allocation.png")
print(f"  4. fuzzy_correlation_heatmap.png")

# ─── Open all saved plots (Windows) ──────────────────────────────────────────
all_plots = [out1, out2, out3, out4]
print("\n[INFO] Opening all plots ...")
for p in all_plots:
    abs_p = os.path.abspath(p)
    os.startfile(abs_p)
