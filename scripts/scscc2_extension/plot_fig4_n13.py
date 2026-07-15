#!/usr/bin/env python3
"""
plot_fig4_n13.py — regenerate Fig 4 cross-check figure with n=13 cohort.

Replaces the n=4 version with the full INVEST shortlist. Each molecule is one
marker plotted as ΔE_ST(ADC(2)) vs ΔE_ST(SCS-CC2). Diagonal y=x line for
reference; both axes negative for INVEST.
"""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

EXT = Path("/home/nudt_cleng/2026/results/scscc2_extension_n13")
CSV = EXT / "cross_check_n13.csv"
STATS = json.load(open(EXT / "stats_n13.json"))

# Times New Roman per project standard
plt.rcParams.update({
    "font.family": "Times New Roman",
    "mathtext.fontset": "custom",
    "mathtext.rm": "Times New Roman",
    "mathtext.it": "Times New Roman:italic",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 11,
})

rows = list(csv.DictReader(open(CSV)))
adc2_vals = np.array([float(r["ADC2_dEST_meV"]) for r in rows])
scscc2_vals = np.array([float(r["SCSCC2_dEST_meV"]) for r in rows])
labels = [r["mol_id"].replace("Hz_", "") for r in rows]
batch = [r["batch"] for r in rows]

# Color by batch
colors = {"historical": "#1f77b4", "phase2.2": "#ff7f0e", "phase2.4": "#2ca02c"}
marker_colors = [colors[b] for b in batch]

fig, ax = plt.subplots(figsize=(6.5, 6.0))

# Reference y=x line
lo, hi = min(adc2_vals.min(), scscc2_vals.min()) - 50, 0
ax.plot([lo, hi], [lo, hi], "k--", lw=0.8, alpha=0.5, label="y = x (perfect agreement)")

# INVEST quadrant shading (both negative)
ax.axhspan(lo, 0, xmin=0, xmax=(0 - lo) / (hi - lo), facecolor="#e8f5e8", alpha=0.4, zorder=0)

# Plot scatter
for i, (x, y) in enumerate(zip(adc2_vals, scscc2_vals)):
    ax.scatter(x, y, c=marker_colors[i], s=70, edgecolors="black",
               linewidth=0.6, zorder=3)
    # Label offset
    offset_y = 8 if i % 2 == 0 else -16
    ax.annotate(labels[i], (x, y), xytext=(6, offset_y),
                textcoords="offset points", fontsize=7, alpha=0.85)

# Axes
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_xlabel(r"$\Delta E_\mathrm{ST}$ at RI-ADC(2)/def2-SVP (meV)")
ax.set_ylabel(r"$\Delta E_\mathrm{ST}$ at SCS-CC2/def2-SVP (meV)")
ax.set_aspect("equal")
ax.grid(alpha=0.25, ls=":")
ax.axhline(0, color="grey", lw=0.4)
ax.axvline(0, color="grey", lw=0.4)

# Legend
legend_handles = [
    mpatches.Patch(facecolor=colors["historical"], edgecolor="black", label=f"Historical SCS-CC2 (n=4)"),
    mpatches.Patch(facecolor=colors["phase2.2"], edgecolor="black", label=f"Phase 2.2 extension (n=2)"),
    mpatches.Patch(facecolor=colors["phase2.4"], edgecolor="black", label=f"Phase 2.4 extension (n=7)"),
]
ax.legend(handles=legend_handles, loc="lower right", fontsize=8, frameon=True,
          fancybox=False, edgecolor="black", framealpha=0.95)

# Title-bar stat
n = STATS["n_total"]
k = STATS["n_sign_retain"]
ci = STATS["clopper_pearson_95_CI"]
ax.text(0.02, 0.98,
        f"Sign agreement: {k}/{n} = 100%\n"
        f"Clopper–Pearson 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]\n"
        f"|ΔΔ$E_\\mathrm{{ST}}$| range: {STATS['abs_ddEST_meV_summary']['min']:.0f}–{STATS['abs_ddEST_meV_summary']['max']:.0f} meV\n"
        f"|ΔΔ$E_\\mathrm{{ST}}$| mean: {STATS['abs_ddEST_meV_summary']['mean']:.0f} meV",
        transform=ax.transAxes, fontsize=8, va="top",
        bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.4", lw=0.5))

plt.tight_layout()

# Save to all 3 figure locations
out_paths = [
    "/home/nudt_cleng/2026/paper_overleaf_v8_jcim_20260502/figures/Fig4_crosscheck.pdf",
    "/home/nudt_cleng/2026/paper_overleaf_v8_jcim_20260502/figures/Fig4_crosscheck.png",
    "/home/nudt_cleng/2026/github_upload/figures/Fig4_crosscheck.pdf",
    "/home/nudt_cleng/2026/github_upload/figures/Fig4_crosscheck.png",
    "/home/nudt_cleng/2026/overleaf_package/figures/Fig4_crosscheck.pdf",
]
for p in out_paths:
    plt.savefig(p, dpi=300, bbox_inches="tight")
    print(f"saved {p}")

# Also update caption_data JSON
cap_data = {
    "n_total": n,
    "n_sign_retain": k,
    "sign_retain_rate_pct": 100.0,
    "clopper_pearson_95_CI": ci,
    "abs_ddEST_meV_min": STATS["abs_ddEST_meV_summary"]["min"],
    "abs_ddEST_meV_max": STATS["abs_ddEST_meV_summary"]["max"],
    "abs_ddEST_meV_mean": STATS["abs_ddEST_meV_summary"]["mean"],
    "abs_ddEST_meV_median": STATS["abs_ddEST_meV_summary"]["median"],
    "molecules": [
        {"mol_id": r["mol_id"], "adc2_meV": float(r["ADC2_dEST_meV"]),
         "scscc2_meV": float(r["SCSCC2_dEST_meV"]), "batch": r["batch"]}
        for r in rows
    ],
    "data_source": "results/scscc2_extension_n13/cross_check_n13.csv",
    "stats_source": "results/scscc2_extension_n13/stats_n13.json",
}
cap_path = "/home/nudt_cleng/2026/paper_overleaf_v8_jcim_20260502/figures/caption_data/Fig4_crosscheck.json"
json.dump(cap_data, open(cap_path, "w"), indent=2, ensure_ascii=False)
print(f"updated {cap_path}")

print(f"\nFig 4 done: n={n}, sign retain {k}/{n}, CI {ci}")
