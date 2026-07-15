#!/usr/bin/env python3
"""diag_distance_nonconformity.py

Phase 2A — Test whether the conformal nonconformity score on the Round-1
deployment set is correlated with chemical distance to the calibration set.

Hypothesis:
    Conformal under-coverage (35.7% empirical vs 95% nominal) is driven by
    deployment-shift; a per-molecule distance-to-calibration metric should
    correlate with per-molecule nonconformity score on the test set.

Data sources (all read-only paths under ~/2026/github_upload/):
    - results/round1_eval/p0b_conformal_calibration.csv
        (mol_id, set, y_true, pred, nonconf_score, boot_mean, boot_std)
    - data/processed/master_molecule_table.csv
        (mol_id ↔ smiles)

Outputs (all written under ~/2026/github_upload/):
    - results/diagnostics/distance_nonconformity.json
    - results/diagnostics/distance_nonconformity.csv
    - figures/diag_distance_nonconformity.pdf
    - figures/caption_data/diag_distance_nonconformity.json

Idempotent: re-running on the same inputs reproduces the same outputs
(deterministic Morgan fingerprint, deterministic Spearman correlation).

Run:
    python3 scripts/diag_distance_nonconformity.py
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
OUT_JSON = ROOT / "results/diagnostics/distance_nonconformity.json"
OUT_CSV = ROOT / "results/diagnostics/distance_nonconformity.csv"
OUT_PDF = ROOT / "figures/diag_distance_nonconformity.pdf"
OUT_CAP = ROOT / "figures/caption_data/diag_distance_nonconformity.json"

FP_RADIUS = 2
FP_NBITS = 2048


def morgan_fp(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit failed to parse: {smiles}")
    return AllChem.GetMorganFingerprintAsBitVect(mol, FP_RADIUS, nBits=FP_NBITS)


def tanimoto(a, b) -> float:
    return DataStructs.TanimotoSimilarity(a, b)


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_CAP.parent.mkdir(parents=True, exist_ok=True)

    cp = pd.read_csv(CONF_CSV)
    mas = pd.read_csv(MASTER, usecols=["mol_id", "smiles", "scaffold_family"])
    df = cp.merge(mas, on="mol_id", how="left")
    if df["smiles"].isna().any():
        missing = df.loc[df["smiles"].isna(), "mol_id"].tolist()
        raise RuntimeError(f"SMILES missing for: {missing}")

    df["fp"] = df["smiles"].map(morgan_fp)

    calib = df[df["set"] == "calibration"].reset_index(drop=True)
    test = df[df["set"] == "test"].reset_index(drop=True)

    # For each test mol: nearest-neighbour Tanimoto sim to calib set,
    # and corresponding 1 - sim distance.
    nn_sim, nn_dist, nn_calib_id = [], [], []
    for _, t in test.iterrows():
        sims = np.array([tanimoto(t["fp"], c) for c in calib["fp"].tolist()])
        i = int(np.argmax(sims))
        nn_sim.append(float(sims[i]))
        nn_dist.append(1.0 - float(sims[i]))
        nn_calib_id.append(calib["mol_id"].iloc[i])

    test_out = test[["mol_id", "scaffold_family", "y_true", "pred",
                     "nonconf_score", "boot_std"]].copy()
    test_out["nearest_calib_id"] = nn_calib_id
    test_out["nearest_calib_tanimoto"] = nn_sim
    test_out["nearest_calib_distance"] = nn_dist
    test_out["abs_residual"] = (test_out["y_true"] - test_out["pred"]).abs()
    test_out.to_csv(OUT_CSV, index=False)

    # Spearman ρ between distance and nonconformity / |residual|
    r_nonconf, p_nonconf = stats.spearmanr(test_out["nearest_calib_distance"],
                                           test_out["nonconf_score"])
    r_absres, p_absres = stats.spearmanr(test_out["nearest_calib_distance"],
                                         test_out["abs_residual"])

    # Side stat: same on calibration set for sanity (LOO-style: each calib
    # mol's nearest *other* calib mol).
    calib_dists, calib_nonconf = [], []
    calib_fps = calib["fp"].tolist()
    for i in range(len(calib)):
        sims = np.array([tanimoto(calib_fps[i], calib_fps[j])
                         for j in range(len(calib)) if j != i])
        calib_dists.append(1.0 - float(sims.max()))
        calib_nonconf.append(float(calib["nonconf_score"].iloc[i]))
    r_calib, p_calib = stats.spearmanr(calib_dists, calib_nonconf)

    # Distribution comparison: test distances vs calib LOO distances
    mw_u, mw_p = stats.mannwhitneyu(
        test_out["nearest_calib_distance"].values,
        np.array(calib_dists),
        alternative="greater",
    )

    payload = {
        "experiment_id": "diag_A_distance_nonconformity",
        "hypothesis": (
            "Conformal nonconformity score on the test set is correlated with "
            "the molecule's Tanimoto distance to its nearest calibration "
            "neighbour."
        ),
        "fp_settings": {"type": "Morgan", "radius": FP_RADIUS, "nBits": FP_NBITS},
        "n_calibration": int(len(calib)),
        "n_test": int(len(test)),
        "test_distance_summary": {
            "min": float(test_out["nearest_calib_distance"].min()),
            "median": float(test_out["nearest_calib_distance"].median()),
            "mean": float(test_out["nearest_calib_distance"].mean()),
            "max": float(test_out["nearest_calib_distance"].max()),
        },
        "calib_loo_distance_summary": {
            "min": float(np.min(calib_dists)),
            "median": float(np.median(calib_dists)),
            "mean": float(np.mean(calib_dists)),
            "max": float(np.max(calib_dists)),
        },
        "spearman_test_distance_vs_nonconf": {
            "rho": float(r_nonconf),
            "p_two_sided": float(p_nonconf),
            "n": int(len(test_out)),
        },
        "spearman_test_distance_vs_abs_residual": {
            "rho": float(r_absres),
            "p_two_sided": float(p_absres),
            "n": int(len(test_out)),
        },
        "spearman_calib_loo_distance_vs_nonconf": {
            "rho": float(r_calib),
            "p_two_sided": float(p_calib),
            "n": int(len(calib)),
        },
        "mannwhitney_test_dist_gt_calib_loo_dist": {
            "U": float(mw_u),
            "p_one_sided_greater": float(mw_p),
            "interpretation": (
                "Tests whether deployment (test) molecules are systematically "
                "further from the calibration set than calibration molecules "
                "are from each other (LOO-style)."
            ),
        },
        "interpretation": (
            "If r_test_distance_vs_nonconf > 0 with p < 0.1, the conformal "
            "under-coverage is at least partially driven by chemical-space "
            "shift between calibration and deployment subsets — i.e., the "
            "exchangeability assumption is empirically violated, and a "
            "distance-aware (Mondrian or locally-weighted) recalibration "
            "is warranted."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    # Figure: scatter of distance vs nonconformity, with regression line
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
    })
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6))

    ax = axes[0]
    is_5ap = test_out["scaffold_family"] == "5AP"
    ax.scatter(test_out.loc[~is_5ap, "nearest_calib_distance"],
               test_out.loc[~is_5ap, "nonconf_score"] * 1000,
               s=42, c="#1f77b4", marker="o", label="Hz", edgecolor="black",
               linewidth=0.5)
    ax.scatter(test_out.loc[is_5ap, "nearest_calib_distance"],
               test_out.loc[is_5ap, "nonconf_score"] * 1000,
               s=42, c="#ff7f0e", marker="^", label="5AP", edgecolor="black",
               linewidth=0.5)
    ax.set_xlabel("Distance to nearest calibration neighbour (1 − Tanimoto)")
    ax.set_ylabel("Conformal nonconformity score (meV)")
    ax.set_title(
        f"(a) test set (n={len(test_out)}): "
        f"Spearman ρ = {r_nonconf:+.2f} (p = {p_nonconf:.3f})")
    ax.legend(loc="upper left", frameon=False)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    bp_data = [
        np.array(calib_dists),
        test_out["nearest_calib_distance"].values,
    ]
    ax.boxplot(bp_data, labels=["calib LOO\n(n=19)", "test\n(n=14)"],
               patch_artist=True,
               boxprops=dict(facecolor="lightgray"))
    ax.set_ylabel("Distance to nearest calibration neighbour")
    ax.set_title(
        f"(b) Mann-Whitney U (test > calib): p = {mw_p:.3f}")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(OUT_PDF, format="pdf", bbox_inches="tight")
    plt.close(fig)

    cap = {
        "figure_id": "diag_distance_nonconformity",
        "source_data_files": [
            "results/round1_eval/p0b_conformal_calibration.csv",
            "data/processed/master_molecule_table.csv",
            "results/diagnostics/distance_nonconformity.csv",
            "results/diagnostics/distance_nonconformity.json",
        ],
        "sample_size": {
            "n_calibration": int(len(calib)),
            "n_test": int(len(test)),
        },
        "key_numbers": {
            "spearman_distance_vs_nonconformity_test": {
                "rho": round(float(r_nonconf), 4),
                "p_two_sided": round(float(p_nonconf), 4),
                "n": int(len(test_out)),
            },
            "spearman_distance_vs_abs_residual_test": {
                "rho": round(float(r_absres), 4),
                "p_two_sided": round(float(p_absres), 4),
            },
            "mannwhitney_test_gt_calib_loo": {
                "U": round(float(mw_u), 2),
                "p_one_sided": round(float(mw_p), 4),
            },
            "test_distance_median": round(
                float(test_out["nearest_calib_distance"].median()), 4),
            "calib_loo_distance_median": round(
                float(np.median(calib_dists)), 4),
        },
        "exclusions_or_filters": [
            "Distances computed on Morgan fingerprints (radius=2, 2048 bits) "
            "from canonical SMILES in master_molecule_table.csv.",
            "Hz_NH23 is excluded by design from the conformal test set "
            "(n_test = 14, not 15).",
        ],
        "visualization_caveats": [
            "Spearman ρ on n = 14 has a wide CI; interpret as directional "
            "evidence rather than a calibrated effect size.",
            "Panel (b) compares test distances to calibration LOO-style "
            "distances; both distributions have small n.",
        ],
        "manuscript_claims_allowed": [
            f"Test-set conformal nonconformity correlates with "
            f"distance to calibration (Spearman ρ = {r_nonconf:+.2f}, "
            f"two-sided p = {p_nonconf:.3f}, n = {len(test_out)}).",
            f"Test molecules are systematically farther from the "
            f"calibration set than calibration molecules are from each "
            f"other (Mann–Whitney U one-sided p = {mw_p:.3f}).",
        ],
        "manuscript_claims_not_allowed": [
            "Do not call the correlation 'statistically significant' "
            "without disclosing n = 14.",
            "Do not generalise the diagnostic to molecule libraries "
            "outside the Hz / 5AP scope tested here.",
        ],
    }
    OUT_CAP.write_text(json.dumps(cap, indent=2) + "\n")

    print(f"[OK] {OUT_JSON.relative_to(ROOT)}")
    print(f"[OK] {OUT_CSV.relative_to(ROOT)}")
    print(f"[OK] {OUT_PDF.relative_to(ROOT)}")
    print(f"[OK] {OUT_CAP.relative_to(ROOT)}")
    print(f"     Spearman ρ(distance, nonconf, test) = "
          f"{r_nonconf:+.3f}  p = {p_nonconf:.3f}")
    print(f"     Mann-Whitney U test_dist > calib_loo_dist: "
          f"U = {mw_u:.1f}, p = {mw_p:.3f}")


if __name__ == "__main__":
    main()
