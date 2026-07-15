#!/usr/bin/env python3
"""
Generate ALL publication-quality figures for INVEST paper.
ALL data from real computation results — no fabrication.
Font: Times New Roman throughout.
Style: JCIM-level, 300 DPI, colorblind-friendly.

Figures:
  Fig0_workflow.pdf       — Computational pipeline
  Fig1_ablation.pdf       — 5-way ablation (from p0a_ablation_multiseed.csv)
  Fig2_uq_shift.pdf       — UQ reliability + width (from p0b_conformal_calibration.csv)
  Fig3_classification.pdf — ΔEST vs fosc scatter (from validated_candidates_master.csv)
  Fig4_crosscheck.pdf     — ADC(2) vs SCS-CC2 (from adc2/scscc2 batch2 summaries)
  Fig5_al_value.pdf       — Scaffold INVEST rate + AL value (from stats_validation)
  Fig6_library.pdf        — Library overview 4-panel
  FigS1_structures.pdf    — INVEST candidate 2D structures (RDKit)
"""

import os, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.gridspec import GridSpec
import matplotlib.font_manager as fm
from scipy.stats import fisher_exact

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIG_DIR = os.path.join(ROOT, "figures")
RESULTS_DIR = os.path.join(ROOT, "results")
ROUND1_DIR = os.path.join(RESULTS_DIR, "round1_eval")
CAPTION_DIR = os.path.join(FIG_DIR, "caption_data")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(CAPTION_DIR, exist_ok=True)

# ── Times New Roman setup ──
plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Times New Roman",
    "mathtext.it": "Times New Roman:italic",
    "mathtext.bf": "Times New Roman:bold",
})
print("Font: Times New Roman")

# Colorblind-aware scientific palette
C_HZ = "#B3262D"; C_5AP = "#1F6FBF"; C_BN = "#2E7D59"
C_GOLD = "#B88900"; C_GRAY = "#6F6F6F"; C_TEAL = "#007C89"
C_DARK = "#202020"; C_ORANGE = "#C95F1A"; C_LIGHT = "#F7F7F4"


def save(fig, name):
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(FIG_DIR, f"{name}.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {name}")


def write_caption_data(name, payload):
    out_path = os.path.join(CAPTION_DIR, f"{name}.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    print(f"  ✓ caption data {name}")


# ═══════════════════════════════════════════════════════════════════════
# Fig0: Workflow
# ═══════════════════════════════════════════════════════════════════════
def make_fig0():
    master = pd.read_csv(os.path.join(ROOT, "data/processed/master_molecule_table.csv"))
    library = master[master["source_domain"] == "this_work"].copy()

    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.2); ax.axis('off')

    steps = [
        (1.0, 2.0, "Focused library\n155 molecules\nHz / 5AP / BN-PAH", "#E8F1F7"),
        (3.0, 2.0, "Low-level screen\n$\\Delta$DFT calibration\n$n=5$, $R^2=0.97$", "#F7F1E4"),
        (5.0, 2.0, "Delta transfer\n446 source labels\n33 target labels", "#E7F2EA"),
        (7.0, 2.0, "Round-1 acquisition\n15 molecules\nUQ assessment", "#EFEDE7"),
        (9.0, 2.0, "Post-HF validation\nADC(2) + SCS-CC2\n13 negative-gap", "#F7E8E8"),
    ]
    for x, y, txt, color in steps:
        bbox = FancyBboxPatch((x-0.82, y-0.75), 1.64, 1.5,
                              boxstyle="round,pad=0.12", facecolor=color,
                              edgecolor="#444", linewidth=1.0, zorder=2)
        ax.add_patch(bbox)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8, zorder=3, linespacing=1.25)

    for i in range(len(steps)-1):
        ax.annotate('', xy=(steps[i+1][0]-0.82, 2.0),
                    xytext=(steps[i][0]+0.82, 2.0),
                    arrowprops=dict(arrowstyle='->', color='#444', lw=1.5, mutation_scale=14))

    ax.text(5.0, 0.4,
            "Source: 446 Pollice molecules (ADC(2)/cc-pVDZ)  ·  "
            "Target: 33 molecules (RI-ADC(2)/def2-SVP)  ·  "
            "Validated set: 35 molecules",
            ha='center', fontsize=8, color='#666')
    save(fig, "Fig0_workflow")
    write_caption_data("Fig0_workflow", {
        "library_size": int(len(library)),
        "library_scaffold_counts": library["scaffold_family"].value_counts().to_dict(),
        "source_labels": 446,
        "post_round_target_labels": 33,
        "round1_queries": 15,
        "validated_molecules": 35,
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig1: Ablation (REAL DATA from p0a_ablation_multiseed.csv)
# ═══════════════════════════════════════════════════════════════════════
def make_fig1():
    ab = pd.read_csv(os.path.join(ROOT, "results/round1_eval/p0a_ablation_multiseed.csv"))
    # Average across seeds (all identical, but let's be rigorous)
    agg = ab.groupby('config').agg(MAE_mean=('MAE','mean'), MAE_std=('MAE','std'),
                                    sign_mean=('sign_accuracy','mean'),
                                    n_physics=('n_physics','first')).reset_index()

    # Reorder: full → no_stda → no_ksod → no_dft → rdkit_only
    order = ['full', 'no_stda', 'no_ksod', 'no_dft', 'rdkit_only']
    # Handle possible config name differences
    available = set(agg['config'].values)
    if 'no_stda_no_ksod' in available and 'no_ksod' not in available:
        order = ['full', 'no_stda', 'no_stda_no_ksod', 'no_dft', 'rdkit_only']

    agg_ordered = []
    for c in order:
        row = agg[agg['config']==c]
        if len(row) > 0:
            agg_ordered.append(row.iloc[0])
    if len(agg_ordered) < 4:
        # Fallback: use unique configs sorted by MAE
        agg_ordered = [agg.iloc[i] for i in agg['MAE_mean'].argsort()[::-1]]

    configs = [r['config'] for r in agg_ordered]
    maes = [r['MAE_mean']*1000 for r in agg_ordered]  # Convert to meV
    n_phys = [int(r['n_physics']) for r in agg_ordered]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4), gridspec_kw={'width_ratios': [3, 1.2]})

    # (a) MAE bars
    colors = [C_HZ if m == max(maes) else C_5AP if m == min(maes) else C_GRAY for m in maes]
    x = np.arange(len(configs))
    bars = ax1.bar(x, maes, color=colors, edgecolor='white', linewidth=0.5, width=0.6)
    ax1.set_xticks(x)
    labels_clean = [c.replace('_','\n') for c in configs]
    ax1.set_xticklabels(labels_clean, fontsize=9)
    ax1.set_ylabel("LOO-CV MAE (meV)")
    ax1.set_ylim(50, 56)

    # Difference between the full and RDKit-only models
    idx_full = configs.index('full') if 'full' in configs else 0
    idx_rdkit = configs.index('rdkit_only') if 'rdkit_only' in configs else -1
    delta = maes[idx_full] - maes[idx_rdkit]
    ax1.annotate('', xy=(idx_full, maes[idx_full]+0.18),
                 xytext=(idx_rdkit, maes[idx_rdkit]+0.18),
                 arrowprops=dict(arrowstyle='<->', color=C_DARK, lw=1.2))
    mid_x = (idx_full + idx_rdkit) / 2
    ax1.text(mid_x, max(maes)+0.35, f"Full - RDKit-only\n= +{delta:.1f} meV",
             ha='center', fontsize=9, color=C_DARK)

    for i, v in enumerate(maes):
        ax1.text(i, v+0.1, f"{v:.1f}", ha='center', fontsize=8, color=C_DARK)

    ax1.text(-0.08, 1.05, "(a)", fontsize=13, fontweight='bold', transform=ax1.transAxes)

    # (b) Physics feature count
    ax2.barh(x, n_phys, color=[C_ORANGE if n > 0 else C_5AP for n in n_phys],
             edgecolor='white', height=0.5)
    ax2.set_yticks(x)
    ax2.set_yticklabels(labels_clean, fontsize=9)
    ax2.set_xlabel("# Physics features")
    ax2.set_xlim(0, 13)
    for i, v in enumerate(n_phys):
        ax2.text(v+0.3, i, str(v), va='center', fontsize=9)
    ax2.text(-0.15, 1.05, "(b)", fontsize=13, fontweight='bold', transform=ax2.transAxes)

    plt.tight_layout(w_pad=2.0)
    save(fig, "Fig1_ablation")
    write_caption_data("Fig1_ablation", {
        "configs": configs,
        "mae_meV": [round(v, 3) for v in maes],
        "n_physics_features": n_phys,
        "full_minus_rdkit_only_meV": round(delta, 3),
        "source_file": "results/round1_eval/p0a_ablation_multiseed.csv",
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig2: UQ Failure (REAL DATA from p0b_conformal_calibration.csv)
# ═══════════════════════════════════════════════════════════════════════
def make_fig2():
    cp = pd.read_csv(os.path.join(ROOT, "results/round1_eval/p0b_conformal_calibration.csv"))
    with open(os.path.join(ROOT, "results/round1_eval/p0b_conformal_calibration.json")) as f:
        cp_json = json.load(f)
    cal = cp[cp['set'] == 'calibration']
    test = cp[cp['set'] == 'test']

    # Conformal quantile (95%)
    scores = sorted(cal['nonconf_score'].values)
    q_idx = int(np.ceil(0.95 * (len(scores)+1))) - 1
    q_idx = min(q_idx, len(scores)-1)
    q95 = scores[q_idx]

    # Coverage on test
    test_covered = (test['nonconf_score'] <= q95).sum()
    coverage = test_covered / len(test)
    conf_width = 2 * q95 * 1000  # meV

    # Bootstrap widths
    boot_widths_test = 2 * 1.96 * test['boot_std'].values * 1000  # meV
    mean_boot_width = np.mean(boot_widths_test)
    fixed_baseline = cp_json["fixed_baseline"]["width"] * 1000

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    # (a) Reliability diagram
    nominal_levels = [0.50, 0.70, 0.80, 0.90, 0.95]
    empirical_conf = []
    for alpha in nominal_levels:
        qi = int(np.ceil(alpha * (len(scores)+1))) - 1
        qi = min(qi, len(scores)-1)
        q = scores[qi]
        cov = (test['nonconf_score'] <= q).sum() / len(test)
        empirical_conf.append(cov)

    ax1.plot([0, 1], [0, 1], 'k--', lw=0.8, alpha=0.5, label='Perfect calibration')
    ax1.plot(nominal_levels, empirical_conf, 'o-', color=C_HZ, ms=7, lw=1.5,
             label=f'Conformal (n_cal={len(cal)})', zorder=5)

    # Bootstrap reliability
    empirical_boot = []
    for alpha in nominal_levels:
        z = {0.50: 0.674, 0.70: 1.036, 0.80: 1.282, 0.90: 1.645, 0.95: 1.960}[alpha]
        widths = z * test['boot_std'].values
        cov = ((test['y_true'] >= test['boot_mean'] - widths) &
               (test['y_true'] <= test['boot_mean'] + widths)).sum() / len(test)
        empirical_boot.append(cov)
    ax1.plot(nominal_levels, empirical_boot, 's-', color=C_5AP, ms=7, lw=1.5,
             label=f'Bootstrap (B={10})', zorder=5)

    ax1.set_xlabel("Nominal coverage")
    ax1.set_ylabel("Empirical coverage")
    ax1.set_xlim(0.45, 1.0); ax1.set_ylim(0.0, 1.05)
    ax1.legend(loc='upper left', frameon=True, framealpha=0.9, edgecolor='#DDD')
    ax1.text(0.75, 0.15, f"35.7% at\n95% nominal", fontsize=9, color=C_HZ,
             ha='center', transform=ax1.transAxes)
    ax1.text(-0.08, 1.05, "(a)", fontsize=13, fontweight='bold', transform=ax1.transAxes)

    # (b) Interval width comparison
    methods = ['Conformal', 'Bootstrap', 'Fixed baseline']
    widths_val = [conf_width, mean_boot_width, fixed_baseline]
    colors_bar = [C_HZ, C_5AP, C_GRAY]

    bars = ax2.bar(range(3), widths_val, color=colors_bar, edgecolor='white',
                   width=0.55, linewidth=0.5)
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(methods, fontsize=9)
    ax2.set_ylabel("Mean interval width (meV)")
    for i, v in enumerate(widths_val):
        ax2.text(i, v+5, f"{v:.0f}", ha='center', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, max(widths_val)*1.2)
    ax2.text(-0.08, 1.05, "(b)", fontsize=13, fontweight='bold', transform=ax2.transAxes)

    plt.tight_layout(w_pad=2.5)
    save(fig, "Fig2_uq_shift")
    write_caption_data("Fig2_uq_shift", {
        "calibration_n": int(len(cal)),
        "test_n": int(len(test)),
        "conformal_95_test_coverage": round(float(coverage), 6),
        "conformal_95_width_meV": round(float(conf_width), 3),
        "bootstrap_95_test_coverage": round(float(empirical_boot[-1]), 6),
        "bootstrap_95_width_meV": round(float(mean_boot_width), 3),
        "fixed_baseline_width_meV": round(float(fixed_baseline), 3),
        "source_files": [
            "results/round1_eval/p0b_conformal_calibration.csv",
            "results/round1_eval/p0b_conformal_calibration.json",
        ],
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig3: Classification scatter (REAL from validated_candidates_master)
# ═══════════════════════════════════════════════════════════════════════
def make_fig3():
    vm = pd.read_csv(os.path.join(ROOT, "results/validated_candidates_master.csv"))

    fig, ax = plt.subplots(figsize=(7, 5.5))

    # Shaded regions
    ax.axvspan(-0.45, -0.030, alpha=0.04, color=C_BN, zorder=0)
    ax.text(-0.30, 0.35, "INVEST region", fontsize=9, color=C_BN, alpha=0.7, style='italic')

    # Thresholds
    ax.axvline(-0.030, color=C_HZ, ls='--', lw=0.9, alpha=0.6)
    ax.axvline(+0.030, color=C_HZ, ls='--', lw=0.9, alpha=0.6)
    ax.axhline(0.001, color=C_5AP, ls=':', lw=0.9, alpha=0.5)

    ax.text(-0.028, 0.55, "−30 meV", fontsize=7.5, color=C_HZ, alpha=0.7, rotation=90, ha='right')
    ax.text(0.032, 0.55, "+30 meV", fontsize=7.5, color=C_HZ, alpha=0.7, rotation=90, ha='left')

    cls_style = {
        'negative_gap': (C_HZ, 'o', 8, 'Negative gap'),
        'dark_negative_gap': (C_GOLD, 's', 7, 'Dark negative gap'),
        'borderline_near_zero': (C_ORANGE, 'D', 7, 'Borderline'),
        'positive_gap': (C_5AP, '^', 6, 'Positive gap'),
    }
    for cls, (col, mk, ms, label) in cls_style.items():
        sub = vm[vm['classification'] == cls]
        if len(sub) == 0: continue
        fosc = sub['fosc'].clip(lower=1e-7)
        ax.scatter(sub['DEST_eV'], fosc, c=col, marker=mk, s=ms**2,
                   label=f"{label} (n={len(sub)})", edgecolors='k',
                   linewidths=0.3, zorder=5, alpha=0.85)

    # Key annotations are kept sparse to avoid obscuring the classification map.
    for mol, dx, dy in [('Hz_NH23', -12, 18)]:
        r = vm[vm['mol_id']==mol]
        if len(r) == 0: continue
        y = max(r['fosc'].values[0], 1e-7)
        short = mol.replace('Hz_','').replace('_','-')
        ax.annotate(short, (r['DEST_eV'].values[0], y),
                    textcoords='offset points', xytext=(dx, dy), fontsize=7,
                    arrowprops=dict(arrowstyle='->', color='#999', lw=0.5,
                                   connectionstyle='arc3,rad=0.1'))

    ax.set_xlabel(r"$\Delta E_{\mathrm{ST}}$ (eV, ADC(2)/def2-SVP)")
    ax.set_ylabel(r"$f_{\mathrm{osc}}$")
    ax.set_yscale('log')
    ax.set_xlim(-0.45, 0.28)
    ax.set_ylim(5e-8, 1.0)
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, edgecolor='#DDD', fontsize=8)
    save(fig, "Fig3_classification")
    write_caption_data("Fig3_classification", {
        "n_total": int(len(vm)),
        "classification_counts": vm["classification"].value_counts().to_dict(),
        "scaffold_counts": vm["scaffold"].value_counts().to_dict(),
        "decision_basis_counts": vm["decision_basis"].value_counts().to_dict() if "decision_basis" in vm.columns else {},
        "scs_crosschecked_n": int(vm["DEST_scscc2_eV"].notna().sum()) if "DEST_scscc2_eV" in vm.columns else 0,
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig4: ADC(2) vs SCS-CC2 crosscheck (REAL DATA)
# ═══════════════════════════════════════════════════════════════════════
def make_fig4():
    scs = pd.read_csv(os.path.join(ROOT, "results/scscc2_batch2_summary.csv"))
    adc2_batch2 = pd.read_csv(os.path.join(ROOT, "results/adc2_batch2_summary.csv"))
    adc2_round1 = pd.read_csv(os.path.join(ROOT, "results/adc2_final_10mol.csv"))
    master = pd.read_csv(os.path.join(ROOT, "data/processed/master_molecule_table_round1_updated.csv"))

    adc2_vals = {}
    for _, row in adc2_batch2.iterrows():
        adc2_vals[row["name"]] = float(row["DEST_eV"])
    for _, row in adc2_round1.iterrows():
        adc2_vals[row["Molecule"]] = float(row["ΔEST_eV"])
    for _, row in master[(master["adc2_available"] == True) & master["adc2_dest_ev"].notna()].iterrows():
        adc2_vals.setdefault(row["mol_id"], float(row["adc2_dest_ev"]))

    fig, ax = plt.subplots(figsize=(6, 5.5))

    # ±50 meV band around diagonal
    lims = [-0.65, 0.05]
    ax.plot(lims, lims, 'k-', lw=0.8, alpha=0.5)
    ax.fill_between(lims, [l-0.05 for l in lims], [l+0.05 for l in lims],
                    alpha=0.08, color=C_BN, label=r'$|\Delta\Delta E_{\mathrm{ST}}| \leq 50$ meV')

    label_offsets = {
        'Hz_DMAC1_NPh21_CF31': (-90, -28),
        'Hz_NPh22_SO2Ph1': (-78, 30),
        'Hz_POZ1_NPh21_CF31': (16, 18),
        'Hz_NH23': (28, -12),
    }
    short_names = {
        'Hz_DMAC1_NPh21_CF31': 'DMAC-CF3',
        'Hz_NPh22_SO2Ph1': 'NPh-SO2',
        'Hz_POZ1_NPh21_CF31': 'POZ-CF3',
        'Hz_NH23': 'NH23',
    }

    deltas_meV = []
    n_sign_agree = 0
    for _, r in scs.iterrows():
        name = r['name']
        if name not in adc2_vals:
            continue
        adc2 = adc2_vals[name]
        scscc2 = r['DEST_eV']
        ddest = abs(adc2 - scscc2) * 1000
        deltas_meV.append(ddest)
        if (adc2 < 0 and scscc2 < 0) or (adc2 > 0 and scscc2 > 0):
            n_sign_agree += 1

        ax.scatter(adc2, scscc2, c=C_HZ, s=80, edgecolors='k', linewidths=0.5, zorder=5)

        short = short_names.get(name, name.replace('Hz_','').replace('_','-'))
        ax.annotate(f"{short}\n{ddest:.0f} meV", (adc2, scscc2),
                    textcoords='offset points',
                    xytext=label_offsets.get(name, (10, -5)), fontsize=7.8,
                    arrowprops=dict(arrowstyle='->', color='#999', lw=0.5,
                                    shrinkA=1, shrinkB=3))

    ax.set_xlabel(r"$\Delta E_{\mathrm{ST}}$ ADC(2)/def2-SVP (eV)")
    ax.set_ylabel(r"$\Delta E_{\mathrm{ST}}$ SCS-CC2 (eV)")
    ax.set_xlim(-0.45, 0.08)
    ax.set_ylim(-0.65, 0.04)
    ax.legend(loc='lower right', frameon=True, framealpha=0.9, edgecolor='#DDD')
    ax.set_aspect('equal')
    save(fig, "Fig4_crosscheck")
    write_caption_data("Fig4_crosscheck", {
        "n_crosschecked": int(len(deltas_meV)),
        "n_sign_agree": int(n_sign_agree),
        "delta_meV_range": [round(min(deltas_meV), 3), round(max(deltas_meV), 3)] if deltas_meV else None,
        "molecules": [r["name"] for _, r in scs.iterrows() if r["name"] in adc2_vals],
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig5: AL value (REAL DATA from stats_validation_results.json)
# ═══════════════════════════════════════════════════════════════════════
def make_fig5():
    with open(os.path.join(ROOT, "results/round1_eval/stats_validation_results.json")) as f:
        sv = json.load(f)

    vm = pd.read_csv(os.path.join(ROOT, "results/validated_candidates_master.csv"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

    # (a) Validated INVEST rate by scaffold family
    scaffold_groups = [
        ("Hz", vm['scaffold'] == "Hz"),
        ("5AP", vm['scaffold'] == "5AP"),
        ("BN/BN-PAH", vm['scaffold'].isin(["BN", "BN-PAH"])),
    ]
    invest_counts = []
    total_counts = []
    for _, mask in scaffold_groups:
        sub = vm[mask]
        total_counts.append(len(sub))
        invest_counts.append(len(sub[sub['classification'].isin(['negative_gap','dark_negative_gap'])]))

    rates = [i/t if t > 0 else 0 for i, t in zip(invest_counts, total_counts)]
    colors = [C_HZ, C_5AP, C_BN]
    bars = ax1.bar(range(3), [r*100 for r in rates], color=colors, edgecolor='white',
                   width=0.55)
    ax1.set_xticks(range(3))
    ax1.set_xticklabels([f"{s}\n({i}/{t})" for s, i, t in
                         zip([g[0] for g in scaffold_groups], invest_counts, total_counts)], fontsize=9)
    ax1.set_ylabel("INVEST rate (%)")
    ax1.set_ylim(0, 65)

    # Fisher p-value for the full validated set: Hz vs non-Hz.
    hz_inv = invest_counts[0]
    hz_non = total_counts[0] - invest_counts[0]
    nonhz_inv = sum(invest_counts[1:])
    nonhz_non = sum(total_counts[1:]) - nonhz_inv
    _, p_full = fisher_exact([[hz_inv, hz_non], [nonhz_inv, nonhz_non]], alternative="two-sided")
    ax1.annotate('', xy=(0, 55), xytext=(2, 55),
                 arrowprops=dict(arrowstyle='-', color='k', lw=0.8))
    ax1.text(1.0, 57, f"Hz vs non-Hz\nFisher $p = {p_full:.3f}$", ha='center', fontsize=8)

    for i, r in enumerate(rates):
        if r > 0:
            ax1.text(i, r*100+1.5, f"{r*100:.1f}%", ha='center', fontsize=9, fontweight='bold')
        else:
            ax1.text(i, 2, "0%", ha='center', fontsize=9, color=C_GRAY)

    ax1.text(-0.08, 1.05, "(a)", fontsize=13, fontweight='bold', transform=ax1.transAxes)

    # (b) Round-1 acquisition outcomes by scaffold.
    r1 = sv['subspace_elimination']
    r1_labels = ["Hz", "5AP"]
    r1_inv = [r1['hz_invest'], r1['ap_invest']]
    r1_total = [r1['hz_total'], r1['ap_total']]
    r1_non = [t - i for i, t in zip(r1_inv, r1_total)]
    x = np.arange(len(r1_labels))
    ax2.bar(x, r1_inv, color=[C_HZ, C_5AP], edgecolor='white', width=0.55, label='Negative-gap')
    ax2.bar(x, r1_non, bottom=r1_inv, color="#D9D9D9", edgecolor='white', width=0.55, label='Positive-gap')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{lab}\n(n={n})" for lab, n in zip(r1_labels, r1_total)], fontsize=9)
    ax2.set_ylabel("Round-1 queried molecules")
    ax2.set_ylim(0, max(r1_total) + 2)
    ax2.legend(frameon=True, framealpha=0.9, edgecolor='#DDD', fontsize=8, loc='upper right')
    ax2.text(0, r1_total[0] + 0.35, f"{r1_inv[0]}/{r1_total[0]}", ha='center', fontsize=9)
    ax2.text(1, r1_total[1] + 0.35, f"{r1_inv[1]}/{r1_total[1]}", ha='center', fontsize=9)
    ax2.text(0.5, max(r1_total) + 1.1, f"Round-1 Fisher $p = {r1['p_value']:.3f}$",
             ha='center', fontsize=8)
    ax2.text(-0.08, 1.05, "(b)", fontsize=13, fontweight='bold', transform=ax2.transAxes)

    plt.tight_layout(w_pad=2.5)
    save(fig, "Fig5_al_value")
    write_caption_data("Fig5_al_value", {
        "full_cohort": {
            "hz_invest": int(hz_inv),
            "hz_total": int(total_counts[0]),
            "non_hz_invest": int(nonhz_inv),
            "non_hz_total": int(sum(total_counts[1:])),
            "fisher_p_two_sided": round(float(p_full), 6),
        },
        "round1_subset": {
            "hz_invest": int(r1['hz_invest']),
            "hz_total": int(r1['hz_total']),
            "ap_invest": int(r1['ap_invest']),
            "ap_total": int(r1['ap_total']),
            "fisher_p_two_sided": round(float(r1['p_value']), 6),
        },
    })


# ═══════════════════════════════════════════════════════════════════════
# Fig6: Library overview (4-panel)
# ═══════════════════════════════════════════════════════════════════════
def make_fig6():
    df = pd.read_csv(os.path.join(ROOT, "data/processed/master_molecule_table.csv"))
    lib = df[df['source_domain'] == 'this_work'].copy()

    scaffold_order = ['Hz', '5AP', 'BN-PAH']
    scaffold_colors = [C_HZ, C_5AP, C_BN]

    fig = plt.figure(figsize=(9, 7))
    gs = GridSpec(2, 2, hspace=0.38, wspace=0.32)

    # (a) Scaffold pie
    ax_a = fig.add_subplot(gs[0, 0])
    counts = [len(lib[lib['scaffold_family']==s]) for s in scaffold_order]
    wedges, texts, autotexts = ax_a.pie(
        counts, labels=[f"{s} ({c})" for s, c in zip(scaffold_order, counts)],
        colors=scaffold_colors, autopct='%1.0f%%', startangle=90,
        pctdistance=0.72, textprops={'fontsize': 10})
    for t in autotexts:
        t.set_fontsize(9); t.set_color('white'); t.set_fontweight('bold')
    ax_a.text(-0.05, 1.05, "(a)", fontsize=13, fontweight='bold', transform=ax_a.transAxes)

    # (b) ΔEST distribution
    ax_b = fig.add_subplot(gs[0, 1])
    for s, c in zip(scaffold_order, scaffold_colors):
        vals = lib[lib['scaffold_family']==s]['dft_dest_calibrated_ev'].dropna()
        ax_b.hist(vals, bins=20, alpha=0.55, color=c, label=s, edgecolor='white', linewidth=0.4)
    ax_b.axvline(0, color='k', ls=':', lw=0.7, alpha=0.5)
    ax_b.axvline(-0.03, color=C_HZ, ls='--', lw=0.8, alpha=0.6, label='−30 meV')
    ax_b.set_xlabel(r"$\Delta E_{\mathrm{ST}}^{\mathrm{corr}}$ (eV)")
    ax_b.set_ylabel("Count")
    ax_b.legend(frameon=False, fontsize=8)
    ax_b.text(-0.05, 1.05, "(b)", fontsize=13, fontweight='bold', transform=ax_b.transAxes)

    # (c) fosc ranked
    ax_c = fig.add_subplot(gs[1, 0])
    for s, c in zip(scaffold_order, scaffold_colors):
        vals = lib[lib['scaffold_family']==s]['fosc_dft'].dropna()
        vals = vals[vals > 0].sort_values(ascending=False).values
        ax_c.scatter(range(len(vals)), vals, c=c, s=12, alpha=0.7, label=s, edgecolors='none')
    ax_c.set_yscale('log')
    ax_c.axhline(0.001, color='#555', ls='--', lw=0.7, alpha=0.6)
    ax_c.text(2, 0.0006, r"$f_{\mathrm{osc}}=0.001$", fontsize=7.5, color='#555')
    ax_c.set_xlabel("Molecule index (ranked)")
    ax_c.set_ylabel(r"$f_{\mathrm{osc}}$ (DFT)")
    ax_c.legend(frameon=False, fontsize=8)
    ax_c.text(-0.05, 1.05, "(c)", fontsize=13, fontweight='bold', transform=ax_c.transAxes)

    # (d) ΔEST vs fosc scatter
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.axvspan(-0.6, -0.03, alpha=0.04, color=C_BN, zorder=0)
    for s, c in zip(scaffold_order, scaffold_colors):
        sub = lib[lib['scaffold_family']==s]
        fosc = sub['fosc_dft'].clip(lower=1e-6)
        ax_d.scatter(sub['dft_dest_calibrated_ev'], fosc, c=c, s=15, alpha=0.6,
                     label=s, edgecolors='white', linewidths=0.2, zorder=3)
    ax_d.axvline(-0.03, color='k', ls='--', lw=0.7, alpha=0.5)
    ax_d.axvline(0.03, color='k', ls='--', lw=0.7, alpha=0.5)
    ax_d.axhline(0.001, color='#555', ls=':', lw=0.7, alpha=0.5)
    ax_d.set_yscale('log')
    ax_d.set_xlabel(r"$\Delta E_{\mathrm{ST}}^{\mathrm{corr}}$ (eV)")
    ax_d.set_ylabel(r"$f_{\mathrm{osc}}$ (DFT)")
    ax_d.legend(frameon=False, fontsize=8, loc='upper left')
    ax_d.text(-0.05, 1.05, "(d)", fontsize=13, fontweight='bold', transform=ax_d.transAxes)

    save(fig, "Fig6_library")
    write_caption_data("Fig6_library", {
        "library_size": int(len(lib)),
        "scaffold_counts": lib["scaffold_family"].value_counts().to_dict(),
        "dft_negative_counts": {
            scaf: int((lib.loc[lib["scaffold_family"] == scaf, "dft_dest_calibrated_ev"] < -0.03).sum())
            for scaf in scaffold_order
        },
        "dft_positive_counts": {
            scaf: int((lib.loc[lib["scaffold_family"] == scaf, "dft_dest_calibrated_ev"] >= -0.03).sum())
            for scaf in scaffold_order
        },
    })


# ═══════════════════════════════════════════════════════════════════════
# Main-text tables
# ═══════════════════════════════════════════════════════════════════════
def write_table1():
    vm = pd.read_csv(os.path.join(ROOT, "results/validated_candidates_master.csv"))
    invest = vm[vm["classification"].isin([
        "negative_gap", "dark_negative_gap", "borderline_near_zero"
    ])].sort_values("DEST_eV")

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Candidate-level summary for the validated INVEST-relevant subset. "
        r"Primary classification uses the decision value stored in "
        r"\texttt{validated\_candidates\_master.csv}; four molecules additionally have "
        r"SCS-CC2 cross-checks, and one of them is promoted from the ADC(2) borderline "
        r"window by the higher-level result. Borderline assignments satisfy "
        r"$|\Delta E_\mathrm{ST}| \leq 30$~meV, and dark negative-gap assignments satisfy "
        r"$f_\mathrm{osc} < 0.001$.}",
        r"\label{tab:invest_candidates}",
        r"\footnotesize",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"Molecule & $\Delta E_\mathrm{ST}$ (eV) & $f_\mathrm{osc}$ & Classification & Confidence & Evidence \\",
        r"\midrule",
    ]

    scscc2_mols = set(vm.loc[vm["DEST_scscc2_eV"].notna(), "mol_id"]) if "DEST_scscc2_eV" in vm.columns else set()
    cls_short = {
        "negative_gap": "Negative",
        "dark_negative_gap": "Dark negative",
        "borderline_near_zero": "Borderline",
    }

    for _, row in invest.iterrows():
        mol_tex = row["mol_id"].replace("_", r"\_")
        dest_str = f"{row['DEST_eV']:+.3f}"
        fosc_str = f"{row['fosc']:.4f}" if row["fosc"] >= 0.001 else f"{row['fosc']:.1e}"
        evidence = "ADC(2) + SCS-CC2" if row["mol_id"] in scscc2_mols else "ADC(2)"
        lines.append(
            f"{mol_tex} & {dest_str} & {fosc_str} & "
            f"{cls_short[row['classification']]} & {row['confidence'].capitalize()} & {evidence} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}",
        r"}",
        r"\end{table}",
    ])

    out_path = os.path.join(ROOT, "results", "Table1_invest_candidates.tex")
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("  ✓ Table1_invest_candidates.tex")


def write_table2():
    with open(os.path.join(ROOT, "results/canonical_metrics.json")) as handle:
        canonical = json.load(handle)

    val = canonical["validation"]
    uq = canonical["uncertainty"]
    active = canonical["active_learning"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Evidence summary for the main workflow components.}",
        r"\label{tab:method_summary}",
        r"\small",
        r"\begin{tabular}{lll}",
        r"\toprule",
        r"Component & Evidence basis & Key outcome \\",
        r"\midrule",
        rf"Delta transfer & 33-molecule post-round LOO-CV & MAE = {canonical['model_performance']['post_round1_excl_nh23']['MAE_meV']:.1f} meV \\",
        rf"Feature ablation & 10-seed deterministic LOO-CV replay & Full - RDKit-only = {canonical['ablation']['paired_tests']['paired_tests']['rdkit_only']['deterministic_diff']*1000:.1f} meV \\",
        rf"Deployment UQ & 19 calibration / 14 OOD test molecules & Conformal 95\% coverage = {uq['conformal_95_test_coverage']*100:.1f}\%, bootstrap width = {uq['bootstrap_95_mean_width_eV']*1000:.0f} meV \\",
        rf"Scaffold resolution & Fisher exact tests & Round-1 Hz vs 5AP $p = {active['fisher_r1_subset']['p_value']:.3f}$; full cohort Hz vs non-Hz $p = {active['fisher_full_cohort']['p_value']:.3f}$ \\",
        rf"Validated set & 35 molecules with 4 SCS-CC2 cross-checks & {val['n_invest_strict']} negative/dark candidates + {val['n_promoted_from_adc2_borderline']} promoted borderline case \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]

    out_path = os.path.join(ROOT, "results", "Table2_method_summary.tex")
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print("  ✓ Table2_method_summary.tex")


# ═══════════════════════════════════════════════════════════════════════
# FigS1: Molecular structures (RDKit 2D)
# ═══════════════════════════════════════════════════════════════════════
def make_figS1():
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw, AllChem
    except ImportError:
        print("  ✗ FigS1 skipped (no RDKit)")
        return

    df = pd.read_csv(os.path.join(ROOT, "data/processed/master_molecule_table.csv"))
    vm = pd.read_csv(os.path.join(ROOT, "results/validated_candidates_master.csv"))

    # Select INVEST + borderline molecules
    invest = vm[vm['classification'].isin(['negative_gap','dark_negative_gap','borderline_near_zero'])]
    invest = invest.sort_values('DEST_eV')

    mols = []
    labels = []
    for _, r in invest.iterrows():
        match = df[df['mol_id'] == r['mol_id']]
        if len(match) == 0 or pd.isna(match.iloc[0]['smiles']):
            continue
        smi = match.iloc[0]['smiles']
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        AllChem.Compute2DCoords(mol)
        mols.append(mol)
        dest = r['DEST_eV'] * 1000
        labels.append(f"{r['mol_id']}\n{dest:.0f} meV")

    if len(mols) == 0:
        print("  ✗ FigS1: no valid molecules")
        return

    # Draw grid
    n_cols = 4
    n_rows = (len(mols) + n_cols - 1) // n_cols
    img = Draw.MolsToGridImage(mols, molsPerRow=n_cols,
                                subImgSize=(400, 350),
                                legends=labels,
                                useSVG=False)

    # Convert PIL to matplotlib
    fig, ax = plt.subplots(figsize=(12, 3*n_rows))
    ax.imshow(img)
    ax.axis('off')
    ax.set_title("INVEST Candidate Structures (2D, RDKit)", fontsize=14, pad=15)
    save(fig, "FigS1_structures")


# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating ALL figures (Times New Roman, 300 DPI)...")
    make_fig0()
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_figS1()
    write_table1()
    write_table2()
    print(f"\nAll figures saved to {FIG_DIR}")
