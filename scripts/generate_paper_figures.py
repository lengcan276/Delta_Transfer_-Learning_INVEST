#!/usr/bin/env python3
"""Generate publication-quality figures for INVEST discovery paper.

Targets: JCTC / JCIM level SCI journal
Style: Times New Roman, 300 DPI, single/double column width
Color scheme: Nature-inspired palette, colorblind-friendly
"""

import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIG_DIR = os.path.join(ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Global style ──
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "mathtext.fontset": "stix",
})

# Nature-style color palette (colorblind-friendly)
C_BLUE = "#4878CF"
C_RED = "#E45756"
C_GREEN = "#54A24B"
C_ORANGE = "#F58518"
C_PURPLE = "#B279A2"
C_GRAY = "#9D9D9D"
C_DARK = "#2D2D2D"
C_LIGHT_BLUE = "#A7C6ED"
C_LIGHT_RED = "#F4A8A7"
C_LIGHT_GREEN = "#A8D5A2"


# ======================================================================
# Figure 1: Delta Transfer Learning Ablation (Innovation 1 + 2)
# ======================================================================
def fig1_ablation():
    """Bar chart comparing ablation configurations with error indicators."""
    data = pd.read_csv(os.path.join(ROOT, "results", "round1_eval", "p0a_ablation_multiseed.csv"))
    summary = data.groupby("config").agg(
        MAE_mean=("MAE", "mean"),
        sign_acc=("sign_accuracy", "mean"),
        n_physics=("n_physics", "first"),
        n_feat=("n_delta_features", "first"),
    ).reset_index()

    order = ["rdkit_only", "no_stda_no_ksod", "no_stda", "no_ksod", "no_dft", "full"]
    labels = [
        "RDKit only\n(baseline)",
        "No sTDA\n+ No KS-OD",
        "No sTDA",
        "No KS-OD",
        "No DFT",
        "Full\n(all features)",
    ]
    summary = summary.set_index("config").loc[order].reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.35})

    # Panel (a): MAE
    x = np.arange(len(order))
    colors = [C_GREEN if i == 0 else C_RED if i == len(order)-1 else C_BLUE for i in range(len(order))]
    bars = ax1.bar(x, summary["MAE_mean"] * 1000, width=0.6, color=colors, edgecolor="white", linewidth=0.5, zorder=3)

    # Add value labels
    for bar, val in zip(bars, summary["MAE_mean"]):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f"{val*1000:.1f}", ha="center", va="bottom", fontsize=7.5, color=C_DARK)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=7.5)
    ax1.set_ylabel("LOO-CV MAE (meV)")
    ax1.set_title("(a) Prediction accuracy", fontweight="bold", fontsize=10, pad=8)
    ax1.set_ylim(50, 57)
    ax1.axhline(y=summary.loc[summary["config"]=="rdkit_only", "MAE_mean"].values[0]*1000,
                color=C_GREEN, ls="--", lw=0.8, alpha=0.6, zorder=1)
    ax1.grid(axis="y", alpha=0.2, zorder=0)

    # Arrow annotation
    best_idx = 0  # rdkit_only
    worst_idx = 5  # full
    best_val = summary.iloc[best_idx]["MAE_mean"] * 1000
    worst_val = summary.iloc[worst_idx]["MAE_mean"] * 1000
    ax1.annotate("", xy=(worst_idx, worst_val + 0.5), xytext=(best_idx, best_val + 0.5),
                 arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.5))
    mid_x = (best_idx + worst_idx) / 2
    ax1.text(mid_x, (best_val + worst_val)/2 + 1.0,
             f"+{worst_val - best_val:.1f} meV\nnegative transfer",
             ha="center", va="bottom", fontsize=7.5, color=C_RED, fontstyle="italic")

    # Panel (b): Number of physics features
    n_phys = summary["n_physics"].values
    bars2 = ax2.bar(x, n_phys, width=0.6, color=[C_ORANGE if n > 0 else C_GRAY for n in n_phys],
                    edgecolor="white", linewidth=0.5, zorder=3)
    for bar, val in zip(bars2, n_phys):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                     str(int(val)), ha="center", va="bottom", fontsize=8, color=C_DARK)

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=7.5)
    ax2.set_ylabel("Number of physics features")
    ax2.set_title("(b) Feature composition", fontweight="bold", fontsize=10, pad=8)
    ax2.grid(axis="y", alpha=0.2, zorder=0)

    fig.savefig(os.path.join(FIG_DIR, "Fig1_ablation.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "Fig1_ablation.png"))
    plt.close(fig)
    print("  Fig1: Ablation study → Fig1_ablation.pdf")


# ======================================================================
# Figure 2: UQ Failure Mode Taxonomy (Innovation 3)
# ======================================================================
def fig2_uq_failure():
    """Coverage-width diagnostic plot for conformal vs bootstrap UQ."""
    with open(os.path.join(ROOT, "results", "round1_eval", "p0b_conformal_calibration.json")) as f:
        uq = json.load(f)

    nominals = [r["nominal_coverage"] for r in uq["results"]]
    conf_test = [r["conformal_test_coverage"] for r in uq["results"]]
    boot_test = [r["bootstrap_test_coverage"] for r in uq["results"]]
    conf_width = [r["conformal_width"] for r in uq["results"]]
    boot_width = [r["bootstrap_test_mean_width"] for r in uq["results"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"wspace": 0.35})

    # Panel (a): Coverage reliability diagram
    ax1.plot([0.4, 1.05], [0.4, 1.05], "--", color=C_GRAY, lw=0.8, label="Ideal", zorder=1)
    ax1.plot(nominals, conf_test, "o-", color=C_BLUE, ms=6, lw=1.5, label="Conformal", zorder=3)
    ax1.plot(nominals, boot_test, "s-", color=C_RED, ms=6, lw=1.5, label="Bootstrap", zorder=3)

    # Shade failure zone
    ax1.axhspan(0, 0.85, color=C_LIGHT_RED, alpha=0.15, zorder=0)
    ax1.text(0.52, 0.15, "Undercoverage\nzone", fontsize=8, color=C_RED, alpha=0.7, ha="center")

    ax1.set_xlabel("Nominal coverage")
    ax1.set_ylabel("Empirical coverage (test set)")
    ax1.set_title("(a) Reliability diagram", fontweight="bold", fontsize=10, pad=8)
    ax1.set_xlim(0.45, 1.0)
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=C_GRAY, framealpha=0.9)
    ax1.grid(alpha=0.15)

    # Panel (b): Interval width comparison
    ax2.plot(nominals, [w * 1000 for w in conf_width], "o-", color=C_BLUE, ms=6, lw=1.5,
             label="Conformal", zorder=3)
    ax2.plot(nominals, [w * 1000 for w in boot_width], "s-", color=C_RED, ms=6, lw=1.5,
             label="Bootstrap", zorder=3)

    # Naive baseline
    baseline_width = uq["fixed_baseline"]["width"] * 1000
    ax2.axhline(baseline_width, color=C_ORANGE, ls=":", lw=1.2, zorder=2)
    ax2.text(0.52, baseline_width + 8, f"Naive baseline ({baseline_width:.0f} meV)",
             fontsize=8, color=C_ORANGE, va="bottom")

    ax2.set_xlabel("Nominal coverage")
    ax2.set_ylabel("Mean interval width (meV)")
    ax2.set_title("(b) Interval width", fontweight="bold", fontsize=10, pad=8)
    ax2.set_xlim(0.45, 1.0)
    ax2.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=C_GRAY, framealpha=0.9)
    ax2.grid(alpha=0.15)

    fig.savefig(os.path.join(FIG_DIR, "Fig2_uq_failure.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "Fig2_uq_failure.png"))
    plt.close(fig)
    print("  Fig2: UQ failure taxonomy → Fig2_uq_failure.pdf")


# ======================================================================
# Figure 3: INVEST Classification Landscape (Innovation 5)
# ======================================================================
def fig3_classification():
    """ΔEST vs fosc scatter plot with classification coloring."""
    df = pd.read_csv(os.path.join(ROOT, "results", "validated_candidates_master.csv"))

    fig, ax = plt.subplots(figsize=(5.0, 4.0))

    class_colors = {
        "negative_gap": C_BLUE,
        "dark_negative_gap": C_PURPLE,
        "borderline_near_zero": C_ORANGE,
        "positive_gap": C_GRAY,
    }
    class_labels = {
        "negative_gap": r"Negative gap ($\Delta E_\mathrm{ST} < -30$ meV)",
        "dark_negative_gap": r"Dark negative gap ($f_\mathrm{osc} < 0.001$)",
        "borderline_near_zero": r"Borderline ($|\Delta E_\mathrm{ST}| \leq 30$ meV)",
        "positive_gap": r"Positive gap ($\Delta E_\mathrm{ST} > 30$ meV)",
    }
    class_markers = {
        "negative_gap": "o",
        "dark_negative_gap": "D",
        "borderline_near_zero": "^",
        "positive_gap": "s",
    }

    for cls in ["positive_gap", "borderline_near_zero", "negative_gap", "dark_negative_gap"]:
        sub = df[df["classification"] == cls]
        if len(sub) == 0:
            continue
        ax.scatter(sub["DEST_eV"] * 1000, sub["fosc"], c=class_colors[cls],
                   marker=class_markers[cls], s=45, label=class_labels[cls],
                   edgecolors="white", linewidth=0.4, zorder=3, alpha=0.85)

    # Threshold lines
    ax.axvline(-30, color=C_DARK, ls="--", lw=0.7, alpha=0.5, zorder=1)
    ax.axvline(30, color=C_DARK, ls="--", lw=0.7, alpha=0.5, zorder=1)
    ax.axhline(0.001, color=C_DARK, ls=":", lw=0.7, alpha=0.5, zorder=1)

    # Shade INVEST region
    ax.axvspan(ax.get_xlim()[0], -30, color=C_LIGHT_BLUE, alpha=0.08, zorder=0)
    ax.text(-250, ax.get_ylim()[1] * 0.92, "INVEST\nregion", fontsize=9, color=C_BLUE,
            alpha=0.6, ha="center", fontstyle="italic")

    # Label key molecules with manual offset to avoid overlap
    key_mols_offsets = {
        "Hz_NH23": (20, 10),
        "Hz_DMAC1_NPh21_CF31": (15, -15),
        "Hz_POZ1_NPh21_CF31": (-60, 15),
        "Hz_NPh21_Cz2": (15, 10),
    }
    for mol, offset in key_mols_offsets.items():
        row = df[df["mol_id"] == mol]
        if len(row) > 0:
            r = row.iloc[0]
            name_short = mol.replace("Hz_", "")
            ax.annotate(name_short, (r["DEST_eV"] * 1000, r["fosc"]),
                        xytext=offset, textcoords="offset points",
                        fontsize=6, color=C_DARK, alpha=0.8,
                        arrowprops=dict(arrowstyle="-", color=C_DARK, alpha=0.3, lw=0.5))

    ax.set_xlabel(r"$\Delta E_\mathrm{ST}$ (meV)")
    ax.set_ylabel(r"Oscillator strength ($f_\mathrm{osc}$)")
    ax.set_yscale("log")
    ax.set_ylim(1e-7, 1)
    ax.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=C_GRAY,
              framealpha=0.9, fontsize=7.5, borderpad=0.6)
    ax.grid(alpha=0.12)

    fig.savefig(os.path.join(FIG_DIR, "Fig3_classification.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "Fig3_classification.png"))
    plt.close(fig)
    print("  Fig3: INVEST classification → Fig3_classification.pdf")


# ======================================================================
# Figure 4: Multi-Level Verification Cross-Check (Innovation 5)
# ======================================================================
def fig4_crosscheck():
    """ADC(2) vs SCS-CC2 ΔEST comparison with confidence annotations."""
    scscc2 = pd.read_csv(os.path.join(ROOT, "results", "scscc2_batch2_summary.csv"))
    adc2_b2 = pd.read_csv(os.path.join(ROOT, "results", "adc2_batch2_summary.csv"))
    master_mol = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

    # Build ADC(2) lookup from ORIGINAL sources (not SCS-CC2 overridden master)
    adc2_lookup = {}
    for _, r in adc2_b2.iterrows():
        adc2_lookup[r["name"]] = r["DEST_eV"]
    # R1 deployment molecules from master_molecule_table (original ADC(2))
    for _, r in master_mol[master_mol["adc2_available"] == True].iterrows():
        if r["mol_id"] not in adc2_lookup and pd.notna(r.get("adc2_dest_ev")):
            adc2_lookup[r["mol_id"]] = r["adc2_dest_ev"]

    rows = []
    for _, r in scscc2.iterrows():
        if r["name"] in adc2_lookup:
            rows.append({"name": r["name"], "DEST_eV_scs": r["DEST_eV"],
                         "DEST_eV_adc2": adc2_lookup[r["name"]]})
    merged = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(4.5, 4.2))

    # Diagonal - extend to cover Hz_NH23
    lim = [-0.70, 0.10]
    ax.plot(lim, lim, "--", color=C_GRAY, lw=0.8, zorder=1)

    # ±50 meV bands
    ax.fill_between(lim, [l - 0.05 for l in lim], [l + 0.05 for l in lim],
                    color=C_LIGHT_GREEN, alpha=0.3, zorder=0, label=r"$|\Delta\Delta E_\mathrm{ST}| \leq 50$ meV")

    # Plot points
    ax.scatter(merged["DEST_eV_adc2"], merged["DEST_eV_scs"],
               c=C_BLUE, s=70, edgecolors="white", linewidth=0.8, zorder=4)

    # Label each point
    for _, r in merged.iterrows():
        name_short = r["name"].replace("Hz_", "")
        ddest = abs(r["DEST_eV_adc2"] - r["DEST_eV_scs"]) * 1000
        offset_x, offset_y = 10, -15
        if "NH23" in r["name"]:
            offset_x, offset_y = 12, 10
        elif "POZ1" in r["name"]:
            offset_x, offset_y = 10, 10
        elif "DMAC1" in r["name"]:
            offset_x, offset_y = -70, -10
        elif "NPh22" in r["name"]:
            offset_x, offset_y = -65, 5

        ax.annotate(f"{name_short}\n({ddest:.0f} meV)",
                    (r["DEST_eV_adc2"], r["DEST_eV_scs"]),
                    xytext=(offset_x, offset_y), textcoords="offset points",
                    fontsize=6.5, color=C_DARK,
                    arrowprops=dict(arrowstyle="-", color=C_DARK, alpha=0.4, lw=0.5))

    ax.set_xlabel(r"$\Delta E_\mathrm{ST}$ ADC(2)/def2-SVP (eV)")
    ax.set_ylabel(r"$\Delta E_\mathrm{ST}$ SCS-CC2/def2-SVP (eV)")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", frameon=True, fancybox=False, edgecolor=C_GRAY, fontsize=8)

    # Quadrant labels
    ax.text(-0.55, 0.05, "Sign\ndisagreement", fontsize=7.5, color=C_RED, alpha=0.5, ha="center")
    ax.text(-0.45, -0.55, "Both\nnegative", fontsize=7.5, color=C_GREEN, alpha=0.5, ha="center")

    ax.grid(alpha=0.12)

    fig.savefig(os.path.join(FIG_DIR, "Fig4_crosscheck.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "Fig4_crosscheck.png"))
    plt.close(fig)
    print("  Fig4: ADC(2) vs SCS-CC2 → Fig4_crosscheck.pdf")


# ======================================================================
# Figure 5: Active Learning Value (Innovation 4)
# ======================================================================
def fig5_al_value():
    """Scaffold-level INVEST rate comparison + subspace elimination."""
    master = pd.read_csv(os.path.join(ROOT, "results", "validated_candidates_master.csv"))

    # Count by scaffold
    scaffolds = master.groupby("scaffold").agg(
        total=("mol_id", "count"),
        invest=("classification", lambda x: sum(x.isin(["negative_gap", "dark_negative_gap"]))),
    ).reset_index()
    scaffolds["rate"] = scaffolds["invest"] / scaffolds["total"]
    scaffolds = scaffolds.sort_values("rate", ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"wspace": 0.35, "width_ratios": [1.2, 1]})

    # Panel (a): INVEST rate by scaffold
    x = np.arange(len(scaffolds))
    colors_bar = [C_BLUE if r > 0 else C_GRAY for r in scaffolds["rate"].values]
    bars = ax1.bar(x, scaffolds["rate"] * 100, width=0.55, color=colors_bar,
                   edgecolor="white", linewidth=0.5, zorder=3)

    for bar, row in zip(bars, scaffolds.itertuples()):
        label = f"{row.invest}/{row.total}"
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 label, ha="center", va="bottom", fontsize=8, color=C_DARK)

    ax1.set_xticks(x)
    ax1.set_xticklabels(scaffolds["scaffold"], fontsize=9)
    ax1.set_ylabel("INVEST rate (%)")
    ax1.set_title("(a) INVEST rate by scaffold", fontweight="bold", fontsize=10, pad=8)
    ax1.set_ylim(0, 75)
    ax1.grid(axis="y", alpha=0.15)

    # Fisher exact p-value annotation
    ax1.annotate("Fisher exact\np = 0.031 *",
                 xy=(0.5, 55), fontsize=8, ha="center", color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=C_LIGHT_BLUE, alpha=0.3, edgecolor=C_BLUE))

    # Panel (b): AL value decomposition (stacked)
    categories = ["Hit rate\n(INVEST found)", "Subspace\nelimination", "Model\nimprovement"]
    al_values = [46.7, 100, 33.3]  # 7/15=46.7%, 5AP fully eliminated, MAE 0.078→0.052
    random_values = [88.0, 0, 0]  # 13.2/15=88%

    x2 = np.arange(len(categories))
    w = 0.3
    ax2.bar(x2 - w/2, al_values, w, label="Active learning", color=C_BLUE, edgecolor="white", zorder=3)
    ax2.bar(x2 + w/2, random_values, w, label="Random", color=C_GRAY, edgecolor="white", zorder=3)

    ax2.set_xticks(x2)
    ax2.set_xticklabels(categories, fontsize=8)
    ax2.set_ylabel("Score (%)")
    ax2.set_title("(b) AL vs random value", fontweight="bold", fontsize=10, pad=8)
    ax2.legend(loc="upper right", frameon=True, fancybox=False, edgecolor=C_GRAY, fontsize=8)
    ax2.grid(axis="y", alpha=0.15)

    fig.savefig(os.path.join(FIG_DIR, "Fig5_al_value.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "Fig5_al_value.png"))
    plt.close(fig)
    print("  Fig5: AL value → Fig5_al_value.pdf")


# ======================================================================
# Table 1: Key validation results (Innovation 5)
# ======================================================================
def table1_validation():
    """Generate LaTeX table for main text."""
    df = pd.read_csv(os.path.join(ROOT, "results", "validated_candidates_master.csv"))

    # Only INVEST candidates (negative + dark + borderline)
    invest = df[df["classification"].isin(["negative_gap", "dark_negative_gap", "borderline_near_zero"])]
    invest = invest.sort_values("DEST_eV")

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{INVEST candidate molecules identified by multi-level verification. "
                 r"Classification thresholds: $|\Delta E_\mathrm{ST}| \leq 30$~meV (borderline), "
                 r"$f_\mathrm{osc} < 0.001$ (dark). Confidence: medium = single ADC(2) or "
                 r"$|\Delta\Delta E_\mathrm{ST}| > 50$~meV between methods.}")
    lines.append(r"\label{tab:invest_candidates}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lccccc}")
    lines.append(r"\toprule")
    lines.append(r"Molecule & $\Delta E_\mathrm{ST}$ (eV) & $f_\mathrm{osc}$ & Classification & Confidence & Verification \\")
    lines.append(r"\midrule")

    scscc2_mols = {"Hz_DMAC1_NPh21_CF31", "Hz_NPh22_SO2Ph1", "Hz_POZ1_NPh21_CF31", "Hz_NH23"}

    for _, r in invest.iterrows():
        mol_tex = r["mol_id"].replace("_", r"\_")
        dest_str = f"{r['DEST_eV']:+.3f}"
        fosc_str = f"{r['fosc']:.4f}" if r["fosc"] >= 0.001 else f"{r['fosc']:.1e}"
        cls_short = {"negative_gap": "Neg.", "dark_negative_gap": "Dark neg.", "borderline_near_zero": "Borderline"}
        cls = cls_short.get(r["classification"], r["classification"])
        conf = r["confidence"].capitalize()
        verif = "ADC(2) + SCS-CC2" if r["mol_id"] in scscc2_mols else "ADC(2)"

        lines.append(f"{mol_tex} & {dest_str} & {fosc_str} & {cls} & {conf} & {verif} \\\\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    table_tex = "\n".join(lines)
    with open(os.path.join(ROOT, "results", "Table1_invest_candidates.tex"), "w") as f:
        f.write(table_tex)
    print(f"  Table1: INVEST candidates → Table1_invest_candidates.tex")


# ======================================================================
# Table 2: Method comparison summary
# ======================================================================
def table2_summary():
    """Generate LaTeX summary table."""
    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Summary of computational methods and key findings.}")
    lines.append(r"\label{tab:method_summary}")
    lines.append(r"\small")
    lines.append(r"\begin{tabular}{lll}")
    lines.append(r"\toprule")
    lines.append(r"Innovation & Method & Key result \\")
    lines.append(r"\midrule")
    lines.append(r"Delta TL & XGBoost LOO-CV & MAE = 52 meV \\")
    lines.append(r"Negative transfer & 5-way ablation & RDKit-only best (52 meV vs 55 meV) \\")
    lines.append(r"UQ failure & Conformal + Bootstrap & Both fail under OOD \\")
    lines.append(r"AL reframing & Hz vs 5AP Fisher & $p = 0.031$ (scaffold effect) \\")
    lines.append(r"Multi-level & ADC(2) + SCS-CC2 & 13 INVEST / 35 total \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    with open(os.path.join(ROOT, "results", "Table2_method_summary.tex"), "w") as f:
        f.write("\n".join(lines))
    print(f"  Table2: Method summary → Table2_method_summary.tex")


# ======================================================================
# Main
# ======================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Generating publication figures (300 DPI, Times New Roman)")
    print("=" * 60)

    fig1_ablation()
    fig2_uq_failure()
    fig3_classification()
    fig4_crosscheck()
    fig5_al_value()
    table1_validation()
    table2_summary()

    print("\nAll figures and tables generated successfully.")
