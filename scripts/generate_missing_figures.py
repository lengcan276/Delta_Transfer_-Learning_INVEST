#!/usr/bin/env python3
"""Generate missing figures for INVEST paper, referencing v6 style.

New figures:
  Fig0_workflow.pdf  — Computational pipeline overview
  Fig6_library.pdf   — Library composition (4-panel, v6 fig2_library style)

Also regenerate Fig3 with v6-style green shading region.
"""

import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIG_DIR = os.path.join(ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Font setup (match v6) ──
_tnr = any('Times New Roman' in f.name for f in fm.fontManager.ttflist)
if _tnr:
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Times New Roman'
    plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
    plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'
    print("Font: Times New Roman")
else:
    _tgt = any('TeX Gyre Termes' in f.name for f in fm.fontManager.ttflist)
    if _tgt:
        plt.rcParams['font.family'] = 'TeX Gyre Termes'
        print("Font: TeX Gyre Termes")
    else:
        plt.rcParams['font.family'] = 'DejaVu Serif'
        plt.rcParams['mathtext.fontset'] = 'dejavuserif'
        print("Font: DejaVu Serif (fallback)")

plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "mathtext.fontset": "stix" if not _tnr else plt.rcParams.get("mathtext.fontset", "stix"),
})

# Colors (v6 consistent)
C_HZ = "#C62828"       # dark red for heptazine
C_5AP = "#1565C0"      # blue for 5AP
C_BN = "#2E7D32"       # green for BN-PAH
C_GRAY = "#757575"
C_LIGHT_GREEN = "#E8F5E9"
C_LIGHT_RED = "#FFEBEE"
C_GOLD = "#F57F17"


def save(fig, name):
    for ext in ['pdf', 'png']:
        fig.savefig(os.path.join(FIG_DIR, f"{name}.{ext}"), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> {name}.pdf/png")


# ═══════════════════════════════════════════════════════════════════════════
# Fig0: Workflow / Framework overview
# ═══════════════════════════════════════════════════════════════════════════
def make_workflow():
    print("Fig0: Workflow diagram...")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Box style
    box_kw = dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#333", linewidth=1.2)

    steps = [
        (0.8, 2.5, "Library\nConstruction\n155 molecules\n(Hz/5AP/BN-PAH)", "#E3F2FD"),
        (2.8, 2.5, "L1: $\\Delta$DFT\nScreen\n$n = 5$ anchors\n$R^2 = 0.97$", "#FFF3E0"),
        (4.8, 2.5, "Delta Transfer\nLearning\n446 $\\to$ 33 mol\nMAE = 52 meV", "#E8F5E9"),
        (6.8, 2.5, "Active Learning\n+ UQ\n15 molecules\nselected", "#F3E5F5"),
        (8.8, 2.5, "Multi-Level\nVerification\nADC(2) + SCS-CC2\n13 INVEST", "#FFEBEE"),
    ]

    for x, y, txt, color in steps:
        bbox = FancyBboxPatch((x-0.75, y-0.85), 1.5, 1.7,
                              boxstyle="round,pad=0.15",
                              facecolor=color, edgecolor="#333",
                              linewidth=1.2, zorder=2)
        ax.add_patch(bbox)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5,
                fontweight='normal', zorder=3, linespacing=1.3)

    # Arrows between boxes
    arrow_kw = dict(arrowstyle='->', color='#333', lw=1.5,
                    connectionstyle='arc3,rad=0', mutation_scale=15)
    for i in range(len(steps)-1):
        x1 = steps[i][0] + 0.75
        x2 = steps[i+1][0] - 0.75
        ax.annotate('', xy=(x2, 2.5), xytext=(x1, 2.5),
                    arrowprops=arrow_kw)

    # Top annotations (innovations)
    innov = [
        (0.8, 4.3, ""),
        (2.8, 4.3, ""),
        (4.8, 4.3, "Innovation 1-2:\nNeg. transfer\nfrom physics desc."),
        (6.8, 4.3, "Innovation 3-4:\nUQ failure modes\nAL reframing"),
        (8.8, 4.3, "Innovation 5:\nConfidence\ngrading"),
    ]
    for x, y, txt in innov:
        if txt:
            ax.text(x, y, txt, ha='center', va='center', fontsize=7.5,
                    color='#555', style='italic', linespacing=1.2)
            ax.annotate('', xy=(x, 2.5+0.85), xytext=(x, y-0.35),
                        arrowprops=dict(arrowstyle='->', color='#AAA',
                                        lw=0.8, ls='--'))

    # Bottom: data flow
    ax.text(5.0, 0.5, "Source: 446 Pollice mol. (ADC(2)/cc-pVDZ)  →  "
            "Target: 33 mol. (RI-ADC(2)/def2-SVP)  →  "
            "Validation: 35 mol. verified",
            ha='center', va='center', fontsize=8, color='#666',
            style='italic')

    ax.text(0.1, 4.8, "(a)", fontsize=13, fontweight='bold', transform=ax.transAxes,
            va='top', ha='left')

    save(fig, "Fig0_workflow")


# ═══════════════════════════════════════════════════════════════════════════
# Fig6: Library overview (4-panel, v6 fig2_library style)
# ═══════════════════════════════════════════════════════════════════════════
def make_library():
    print("Fig6: Library overview...")
    df = pd.read_csv(os.path.join(ROOT, "data/processed/master_molecule_table.csv"))
    lib = df[df['source_domain'] == 'this_work'].copy()

    # Map scaffold colors
    scaffold_map = {'Hz': C_HZ, '5AP': C_5AP, 'BN-PAH': C_BN}
    scaffold_order = ['Hz', '5AP', 'BN-PAH']
    scaffold_counts = [len(lib[lib['scaffold_family']==s]) for s in scaffold_order]

    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 2, hspace=0.35, wspace=0.30)

    # (a) Scaffold distribution - pie chart
    ax_a = fig.add_subplot(gs[0, 0])
    colors = [scaffold_map[s] for s in scaffold_order]
    wedges, texts, autotexts = ax_a.pie(
        scaffold_counts, labels=scaffold_order, colors=colors,
        autopct='%1.0f%%', startangle=90, pctdistance=0.75,
        textprops={'fontsize': 10})
    for t in autotexts:
        t.set_fontsize(9)
        t.set_color('white')
        t.set_fontweight('bold')
    ax_a.set_title("Scaffold Distribution", fontsize=12, pad=10)
    ax_a.text(-0.05, 1.05, "(a)", fontsize=13, fontweight='bold',
              transform=ax_a.transAxes)

    # (b) Calibrated ΔEST distribution by scaffold
    ax_b = fig.add_subplot(gs[0, 1])
    for s, c in zip(scaffold_order, colors):
        vals = lib[lib['scaffold_family']==s]['dft_dest_calibrated_ev'].dropna()
        ax_b.hist(vals, bins=20, alpha=0.6, color=c, label=s, edgecolor='white',
                  linewidth=0.5)
    ax_b.axvline(0, color='k', ls=':', lw=0.8, alpha=0.5)
    ax_b.axvline(-0.03, color=C_HZ, ls='--', lw=0.8, alpha=0.7)
    ax_b.set_xlabel(r"$\Delta E_{\mathrm{ST}}^{\mathrm{corr}}$ (eV)")
    ax_b.set_ylabel("Count")
    ax_b.set_title(r"Calibrated $\Delta E_{\mathrm{ST}}$ Distribution", fontsize=12, pad=10)
    ax_b.legend(frameon=False, fontsize=9)
    ax_b.text(-0.05, 1.05, "(b)", fontsize=13, fontweight='bold',
              transform=ax_b.transAxes)

    # (c) fosc distribution (log scale)
    ax_c = fig.add_subplot(gs[1, 0])
    for s, c in zip(scaffold_order, colors):
        vals = lib[lib['scaffold_family']==s]['fosc_dft'].dropna()
        vals = vals[vals > 0]
        ax_c.scatter(range(len(vals)), sorted(vals, reverse=True),
                     c=c, s=15, alpha=0.7, label=s, edgecolors='none')
    ax_c.set_yscale('log')
    ax_c.axhline(0.001, color='#555', ls='--', lw=0.8, alpha=0.7)
    ax_c.text(2, 0.0007, r"$f_{\mathrm{osc}}$ = 0.001", fontsize=8, color='#555')
    ax_c.set_xlabel("Molecule index (ranked)")
    ax_c.set_ylabel(r"$f_{\mathrm{osc}}$ (DFT)")
    ax_c.set_title("Oscillator Strength Distribution", fontsize=12, pad=10)
    ax_c.legend(frameon=False, fontsize=9)
    ax_c.text(-0.05, 1.05, "(c)", fontsize=13, fontweight='bold',
              transform=ax_c.transAxes)

    # (d) ΔEST_corr vs fosc scatter (library level, DFT)
    ax_d = fig.add_subplot(gs[1, 1])

    # INVEST region shading
    rect = Rectangle((-0.6, 0.001), 0.57, 1.0, alpha=0.06, color=C_HZ,
                      zorder=0, transform=ax_d.transData)
    ax_d.add_patch(rect)

    for s, c in zip(scaffold_order, colors):
        sub = lib[lib['scaffold_family']==s]
        fosc = sub['fosc_dft'].clip(lower=1e-6)
        ax_d.scatter(sub['dft_dest_calibrated_ev'], fosc,
                     c=c, s=20, alpha=0.6, label=s, edgecolors='white',
                     linewidths=0.3, zorder=3)

    ax_d.axvline(-0.03, color='k', ls='--', lw=0.8, alpha=0.5)
    ax_d.axvline(0.03, color='k', ls='--', lw=0.8, alpha=0.5)
    ax_d.axhline(0.001, color='#555', ls=':', lw=0.8, alpha=0.5)
    ax_d.set_yscale('log')
    ax_d.set_xlabel(r"$\Delta E_{\mathrm{ST}}^{\mathrm{corr}}$ (eV)")
    ax_d.set_ylabel(r"$f_{\mathrm{osc}}$ (DFT)")
    ax_d.set_title(r"$\Delta E_{\mathrm{ST}}$ vs $f_{\mathrm{osc}}$ (L1 Screen)",
                   fontsize=12, pad=10)
    ax_d.legend(frameon=False, fontsize=9, loc='upper left')
    ax_d.text(-0.05, 1.05, "(d)", fontsize=13, fontweight='bold',
              transform=ax_d.transAxes)

    save(fig, "Fig6_library")


# ═══════════════════════════════════════════════════════════════════════════
# Fig3 improved: ΔEST vs fosc with v6-style green shaded INVEST region
# ═══════════════════════════════════════════════════════════════════════════
def make_fig3_improved():
    print("Fig3: Classification scatter (improved)...")
    vm = pd.read_csv(os.path.join(ROOT, "results/validated_candidates_master.csv"))

    fig, ax = plt.subplots(figsize=(8, 6))

    # INVEST region shading (v6 style: green for negative gap + bright fosc)
    rect_invest = Rectangle((-0.45, 0.001), 0.42, 10.0, alpha=0.06,
                            color='#2E7D32', zorder=0)
    ax.add_patch(rect_invest)
    ax.text(-0.36, 0.35, "INVEST\nregion", fontsize=9, color='#2E7D32',
            alpha=0.7, style='italic', va='center')

    # Dark INVEST region
    rect_dark = Rectangle((-0.45, 1e-7), 0.42, 0.001-1e-7, alpha=0.04,
                           color='#F57F17', zorder=0)
    ax.add_patch(rect_dark)
    ax.text(-0.36, 3e-5, "Dark\nINVEST", fontsize=8, color=C_GOLD,
            alpha=0.8, style='italic', va='center')

    # Threshold lines
    ax.axvline(-0.030, color='#C62828', ls='--', lw=1.0, alpha=0.6)
    ax.axvline(+0.030, color='#C62828', ls='--', lw=1.0, alpha=0.6)
    ax.axhline(0.001, color='#1565C0', ls=':', lw=1.0, alpha=0.5)

    # Threshold labels
    ax.text(-0.033, 0.5, r"$-30$ meV", fontsize=8, color='#C62828', alpha=0.7,
            rotation=90, va='center', ha='right')
    ax.text(0.033, 0.5, r"$+30$ meV", fontsize=8, color='#C62828', alpha=0.7,
            rotation=90, va='center', ha='left')

    # Classification colors
    class_style = {
        'negative_gap': {'color': '#C62828', 'marker': 'o', 'ms': 9, 'label': 'Negative gap'},
        'dark_negative_gap': {'color': '#F57F17', 'marker': 's', 'ms': 8, 'label': 'Dark negative gap'},
        'borderline_near_zero': {'color': '#FF8F00', 'marker': 'D', 'ms': 8, 'label': 'Borderline'},
        'positive_gap': {'color': '#1565C0', 'marker': '^', 'ms': 7, 'label': 'Positive gap'},
    }

    for cls, style in class_style.items():
        sub = vm[vm['classification'] == cls]
        if len(sub) == 0:
            continue
        fosc = sub['fosc'].clip(lower=1e-7)
        ax.scatter(sub['DEST_eV'], fosc, c=style['color'],
                   marker=style['marker'], s=style['ms']**2,
                   label=f"{style['label']} ($n$={len(sub)})",
                   edgecolors='k', linewidths=0.4, zorder=5, alpha=0.85)

    # Annotate key molecules
    annotations = {
        'Hz_NH23': (-0.383, 1e-7, 'Hz_NH23\n($-383$ meV)', -15, 20),
        'Hz_POZ1_NPh21_CF31': (-0.166, 0.0383, 'POZ1_NPh21_CF31', 8, 5),
        'Hz_POZ1_DMAC2': (0.027, 0.2263, 'POZ1_DMAC2\n(borderline)', 8, -10),
    }
    for mol, (x, y, txt, dx, dy) in annotations.items():
        row = vm[vm['mol_id'] == mol]
        if len(row) > 0:
            y_val = max(row['fosc'].values[0], 1e-7)
            ax.annotate(txt, (row['DEST_eV'].values[0], y_val),
                        textcoords='offset points', xytext=(dx, dy),
                        fontsize=7.5, color='#333',
                        arrowprops=dict(arrowstyle='->', color='#999',
                                        lw=0.6, connectionstyle='arc3,rad=0.15'))

    ax.set_xlabel(r"$\Delta E_{\mathrm{ST}}$ (eV, ADC(2)/def2-SVP)", fontsize=12)
    ax.set_ylabel(r"$f_{\mathrm{osc}}$", fontsize=12)
    ax.set_yscale('log')
    ax.set_xlim(-0.45, 0.30)
    ax.set_ylim(5e-8, 1.0)
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9,
              edgecolor='#DDD')

    # Panel label
    ax.text(0.02, 0.97, "", fontsize=13, fontweight='bold',
            transform=ax.transAxes, va='top')

    save(fig, "Fig3_classification")


if __name__ == "__main__":
    make_workflow()
    make_library()
    make_fig3_improved()
    print("\nDone! All figures saved to", FIG_DIR)
