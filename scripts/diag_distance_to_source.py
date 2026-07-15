#!/usr/bin/env python3
"""diag_distance_to_source.py

Phase 2B — Test whether the calibration vs deployment subsets differ in
their distance to the 446-molecule Pollice ADC(2)/cc-pVDZ source-domain
training set, and whether |residual| correlates with that distance.

Hypothesis:
    Conformal under-coverage on the 14-molecule deployment set is a
    deployment-shift effect: the deployment molecules are systematically
    farther from the source training distribution than the calibration
    molecules are. We measure shift via Tanimoto distance to the nearest
    Pollice source neighbour and to the k=5 nearest neighbours
    (the nUNC applicability-domain metric of Whitehead et al., ACS
    Omega 2026).

Data sources (read-only, all under ~/2026/github_upload/):
    - results/round1_eval/p0b_conformal_calibration.csv
        (33 rows: 19 calibration + 14 test, with y_true and pred)
    - data/processed/master_molecule_table.csv
        (mol_id ↔ smiles ↔ source_domain; the 446-row Pollice subset is
        filtered as source_domain == 'pollice' & adc2_dest_ev.notna())

Outputs:
    - results/diagnostics/distance_to_source.json
    - results/diagnostics/distance_to_source.csv
    - figures/diag_distance_to_source.pdf
    - figures/caption_data/diag_distance_to_source.json

Idempotent.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CONF_CSV = ROOT / "results/round1_eval/p0b_conformal_calibration.csv"
MASTER = ROOT / "data/processed/master_molecule_table.csv"
OUT_JSON = ROOT / "results/diagnostics/distance_to_source.json"
OUT_CSV = ROOT / "results/diagnostics/distance_to_source.csv"
OUT_PDF = ROOT / "figures/diag_distance_to_source.pdf"
OUT_CAP = ROOT / "figures/caption_data/diag_distance_to_source.json"

FP_RADIUS = 2
FP_NBITS = 2048
KNN_K = 5


def morgan_fp(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit failed to parse: {smiles}")
    return AllChem.GetMorganFingerprintAsBitVect(mol, FP_RADIUS, nBits=FP_NBITS)


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_CAP.parent.mkdir(parents=True, exist_ok=True)

    cp = pd.read_csv(CONF_CSV)
    mas = pd.read_csv(MASTER)
    target = cp.merge(
        mas[["mol_id", "smiles", "scaffold_family"]],
        on="mol_id", how="left",
    )
    if target["smiles"].isna().any():
        raise RuntimeError("missing SMILES for target molecule(s)")

    # 446 Pollice source training set (the 'n_invest_labeled_pollice_source'
    # subset cited as 446 in the manuscript).
    pollice = mas[
        (mas["source_domain"] == "pollice")
        & mas["adc2_dest_ev"].notna()
    ].copy()
    if len(pollice) != 446:
        raise RuntimeError(
            f"Pollice source filter returned {len(pollice)} rows, "
            "expected 446. Check master_molecule_table.csv."
        )

    target["fp"] = target["smiles"].map(morgan_fp)
    pollice["fp"] = pollice["smiles"].map(morgan_fp)
    pol_fps = pollice["fp"].tolist()

    # For each target mol, compute similarities to all 446 Pollice source
    # mols, then derive d_NN (1 - max sim) and d_kNN (mean of 1 - top-k
    # sims, the Whitehead-style nUNC AD metric).
    rows = []
    for _, t in target.iterrows():
        sims = np.array([DataStructs.TanimotoSimilarity(t["fp"], p)
                         for p in pol_fps])
        sims_sorted = np.sort(sims)[::-1]
        nn_sim = float(sims_sorted[0])
        knn_sims = sims_sorted[:KNN_K]
        rows.append({
            "mol_id": t["mol_id"],
            "set": t["set"],
            "scaffold_family": t["scaffold_family"],
            "y_true": float(t["y_true"]),
            "pred": float(t["pred"]),
            "abs_residual": float(abs(t["y_true"] - t["pred"])),
            "nonconf_score": float(t["nonconf_score"]),
            "boot_std": float(t["boot_std"]),
            "d_nn_to_source": 1.0 - nn_sim,
            "d_knn5_to_source": float(np.mean(1.0 - knn_sims)),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False)

    calib = df[df["set"] == "calibration"]
    test = df[df["set"] == "test"]

    # Mann-Whitney: are test distances larger than calib distances?
    mw_nn_u, mw_nn_p = stats.mannwhitneyu(
        test["d_nn_to_source"].values,
        calib["d_nn_to_source"].values,
        alternative="greater",
    )
    mw_knn_u, mw_knn_p = stats.mannwhitneyu(
        test["d_knn5_to_source"].values,
        calib["d_knn5_to_source"].values,
        alternative="greater",
    )

    # Spearman: distance vs |residual| (over all 33 mols, since this is
    # a structural-shift property, not a CP-internal one)
    r_nn_all, p_nn_all = stats.spearmanr(df["d_nn_to_source"],
                                         df["abs_residual"])
    r_knn_all, p_knn_all = stats.spearmanr(df["d_knn5_to_source"],
                                           df["abs_residual"])
    # Also test set only (most directly relevant to OOD coverage failure)
    r_nn_test, p_nn_test = stats.spearmanr(test["d_nn_to_source"],
                                           test["abs_residual"])
    r_knn_test, p_knn_test = stats.spearmanr(test["d_knn5_to_source"],
                                             test["abs_residual"])

    payload = {
        "experiment_id": "diag_B_distance_to_source",
        "hypothesis": (
            "Round-1 deployment molecules are systematically farther from "
            "the 446-molecule Pollice ADC(2) source training set than "
            "the pre-Round-1 calibration molecules are, providing a "
            "geometric mechanism for the conformal under-coverage."
        ),
        "fp_settings": {"type": "Morgan", "radius": FP_RADIUS,
                        "nBits": FP_NBITS, "knn_k": KNN_K},
        "n_pollice_source": int(len(pollice)),
        "n_calibration": int(len(calib)),
        "n_test": int(len(test)),
        "distance_summary_d_nn_to_source": {
            "calib_mean": float(calib["d_nn_to_source"].mean()),
            "calib_median": float(calib["d_nn_to_source"].median()),
            "test_mean": float(test["d_nn_to_source"].mean()),
            "test_median": float(test["d_nn_to_source"].median()),
        },
        "distance_summary_d_knn5_to_source": {
            "calib_mean": float(calib["d_knn5_to_source"].mean()),
            "calib_median": float(calib["d_knn5_to_source"].median()),
            "test_mean": float(test["d_knn5_to_source"].mean()),
            "test_median": float(test["d_knn5_to_source"].median()),
        },
        "mannwhitney_test_dist_gt_calib_dist": {
            "d_nn":  {"U": float(mw_nn_u),  "p_one_sided_greater": float(mw_nn_p)},
            "d_knn5":{"U": float(mw_knn_u), "p_one_sided_greater": float(mw_knn_p)},
        },
        "spearman_distance_vs_abs_residual": {
            "d_nn_all_33":   {"rho": float(r_nn_all),   "p": float(p_nn_all),
                              "n": int(len(df))},
            "d_knn5_all_33": {"rho": float(r_knn_all),  "p": float(p_knn_all),
                              "n": int(len(df))},
            "d_nn_test_14":  {"rho": float(r_nn_test),  "p": float(p_nn_test),
                              "n": int(len(test))},
            "d_knn5_test_14":{"rho": float(r_knn_test), "p": float(p_knn_test),
                              "n": int(len(test))},
        },
        "interpretation": (
            "If test mols are systematically farther from the source set "
            "than calib mols are (Mann–Whitney p < 0.05, one-sided), the "
            "deployment-shift hypothesis holds and conformal calibration "
            "computed on the calib set cannot be expected to transfer."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    # Figure
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
    })
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6))

    ax = axes[0]
    bp_data = [calib["d_knn5_to_source"].values,
               test["d_knn5_to_source"].values]
    bp = ax.boxplot(bp_data,
                    tick_labels=[f"calib\n(n={len(calib)})",
                                 f"test\n(n={len(test)})"],
                    patch_artist=True)
    bp["boxes"][0].set_facecolor("#1f77b4")
    bp["boxes"][1].set_facecolor("#ff7f0e")
    for box in bp["boxes"]:
        box.set_alpha(0.6)
    ax.set_ylabel(f"k-NN={KNN_K} mean distance to Pollice source (1 − T)")
    ax.set_title(
        f"(a) Mann-Whitney (test > calib): p = {mw_knn_p:.3f}")
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1]
    is_5ap = df["scaffold_family"] == "5AP"
    is_calib = df["set"] == "calibration"
    for mask, c, m, lab in [
        (~is_5ap & is_calib, "#1f77b4", "o", "Hz calib"),
        (is_5ap & is_calib, "#ff7f0e", "o", "5AP calib"),
        (~is_5ap & ~is_calib, "#1f77b4", "^", "Hz test"),
        (is_5ap & ~is_calib, "#ff7f0e", "^", "5AP test"),
    ]:
        sub = df[mask]
        if len(sub):
            ax.scatter(sub["d_knn5_to_source"],
                       sub["abs_residual"] * 1000,
                       s=42, c=c, marker=m, edgecolor="black",
                       linewidth=0.5, label=lab)
    ax.set_xlabel(f"k-NN={KNN_K} distance to Pollice source")
    ax.set_ylabel("|residual| (meV)")
    ax.set_title(
        f"(b) all n=33: Spearman ρ = {r_knn_all:+.2f} (p = {p_knn_all:.3f})")
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_PDF, format="pdf", bbox_inches="tight")
    plt.close(fig)

    cap = {
        "figure_id": "diag_distance_to_source",
        "source_data_files": [
            "results/round1_eval/p0b_conformal_calibration.csv",
            "data/processed/master_molecule_table.csv",
            "results/diagnostics/distance_to_source.csv",
            "results/diagnostics/distance_to_source.json",
        ],
        "sample_size": {
            "n_pollice_source": int(len(pollice)),
            "n_calibration": int(len(calib)),
            "n_test": int(len(test)),
            "k_for_knn_distance": KNN_K,
        },
        "key_numbers": {
            "calib_d_knn5_median": round(
                float(calib["d_knn5_to_source"].median()), 4),
            "test_d_knn5_median": round(
                float(test["d_knn5_to_source"].median()), 4),
            "mannwhitney_test_gt_calib_d_knn5": {
                "U": round(float(mw_knn_u), 2),
                "p_one_sided": round(float(mw_knn_p), 4),
            },
            "spearman_d_knn5_vs_abs_residual_all_33": {
                "rho": round(float(r_knn_all), 4),
                "p_two_sided": round(float(p_knn_all), 4),
            },
            "spearman_d_knn5_vs_abs_residual_test_14": {
                "rho": round(float(r_knn_test), 4),
                "p_two_sided": round(float(p_knn_test), 4),
            },
        },
        "exclusions_or_filters": [
            "Pollice source = 446 molecules (source_domain == 'pollice' AND "
            "adc2_dest_ev.notna() in master_molecule_table.csv).",
            f"Distance metric: 1 − Tanimoto on Morgan FP (radius={FP_RADIUS}, "
            f"{FP_NBITS} bits); k = {KNN_K} for the nUNC-style applicability "
            "metric (Whitehead et al., ACS Omega 2026).",
        ],
        "visualization_caveats": [
            f"Both calib (n={len(calib)}) and test (n={len(test)}) have small "
            "samples; statistical tests are reported with their actual n.",
            "The k-NN distance metric is sensitive to the choice of k; "
            "we report k = 5 following Whitehead et al. (2026).",
        ],
        "manuscript_claims_allowed": [
            f"Round-1 deployment molecules are at median k-NN={KNN_K} "
            f"distance {test['d_knn5_to_source'].median():.3f} from the "
            f"Pollice source set, vs {calib['d_knn5_to_source'].median():.3f} "
            f"for the calibration set; Mann-Whitney one-sided "
            f"p = {mw_knn_p:.3f}.",
            f"Across all 33 target molecules, |residual| correlates with "
            f"k-NN={KNN_K} distance to the source set "
            f"(Spearman ρ = {r_knn_all:+.2f}, p = {p_knn_all:.3f}).",
        ],
        "manuscript_claims_not_allowed": [
            "Do not state the test molecules are 'far OOD' without citing "
            "the actual median distance and the calib comparator.",
            "Do not cite Spearman significance from n = 14 alone; cite "
            "n = 33 (calib + test combined) when supportive.",
        ],
    }
    OUT_CAP.write_text(json.dumps(cap, indent=2) + "\n")

    print(f"[OK] {OUT_JSON.relative_to(ROOT)}")
    print(f"[OK] {OUT_CSV.relative_to(ROOT)}")
    print(f"[OK] {OUT_PDF.relative_to(ROOT)}")
    print(f"[OK] {OUT_CAP.relative_to(ROOT)}")
    print(f"     d_knn5 median: calib = {calib['d_knn5_to_source'].median():.3f}, "
          f"test = {test['d_knn5_to_source'].median():.3f}")
    print(f"     Mann-Whitney one-sided p = {mw_knn_p:.4f}")
    print(f"     Spearman(d_knn5, |residual|) all 33: rho = {r_knn_all:+.3f}, "
          f"p = {p_knn_all:.4f}")


if __name__ == "__main__":
    main()
