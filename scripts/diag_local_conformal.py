#!/usr/bin/env python3
"""diag_local_conformal.py

Phase 2D — Tanimoto-weighted locally-adaptive split-conformal regression.

Hypothesis:
    Global split conformal under-covers (5/14 = 35.7% at the 95% nominal
    level) because the calibration nonconformity distribution does not
    transfer uniformly to the deployment subset. A Tanimoto-weighted
    local quantile (Lei & Wasserman 2014; Tibshirani et al. 2019;
    Bostrom 2020) uses all n=19 calibration molecules but weights each
    calibration nonconformity score by the test molecule's similarity to
    that calibration molecule. This avoids the Mondrian small-bucket
    pathology (5AP has only 1 calibration mol).

Method (weighted-quantile split conformal):
    For each test molecule t with Morgan FP f_t:
        s_i  = T(f_t, f_calib[i])                # Tanimoto similarity
        w_i  = (s_i + ε)^β  / Σ_j (s_j + ε)^β     # softmax-style temperature
        q_t  = weighted_quantile({nonconf[i]}, weights=w_i, alpha=0.95)
        covered_t = (|y_true_t - pred_t| <= q_t)
    Aggregate: coverage = mean(covered_t over test set)

We sweep β ∈ {0, 1, 2, 4} so β = 0 reproduces the global quantile and
larger β concentrates weight on near neighbours. β is a hyperparameter,
NOT tuned on the test set; we report all values for transparency.

Data sources (read-only):
    results/round1_eval/p0b_conformal_calibration.csv
    data/processed/master_molecule_table.csv

Outputs:
    results/diagnostics/local_conformal.{json,csv}
    figures/diag_local_conformal.pdf
    figures/caption_data/diag_local_conformal.json
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

ROOT = Path(__file__).resolve().parents[1]
CONF_CSV = ROOT / "results/round1_eval/p0b_conformal_calibration.csv"
MASTER = ROOT / "data/processed/master_molecule_table.csv"
OUT_JSON = ROOT / "results/diagnostics/local_conformal.json"
OUT_CSV = ROOT / "results/diagnostics/local_conformal.csv"
OUT_PDF = ROOT / "figures/diag_local_conformal.pdf"
OUT_CAP = ROOT / "figures/caption_data/diag_local_conformal.json"

FP_RADIUS = 2
FP_NBITS = 2048
EPSILON = 1e-3
BETAS = [0, 1, 2, 4]
# Sweep multiple nominal levels: at alpha = 0.95 with n_calib = 19, the
# finite-sample ceil((n+1)*alpha) rank pins q_hat to the maximum
# calibration nonconformity regardless of weighting; lower alphas leave
# room for local weighting to act.
NOMINAL_LEVELS = [0.80, 0.90, 0.95]


def morgan_fp(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(smiles)
    return AllChem.GetMorganFingerprintAsBitVect(mol, FP_RADIUS, nBits=FP_NBITS)


def weighted_quantile(values: np.ndarray, weights: np.ndarray,
                      alpha: float) -> float:
    """Weighted upper-tail quantile interpolated with the (n+1)/n
    finite-sample correction. Returns the value v such that the
    cumulative weight of {values <= v} reaches alpha * (W + max_w)
    where W = sum(weights). Falls back to max(values) if alpha is too
    large for the available weight mass.
    """
    if len(values) == 0:
        return float("nan")
    order = np.argsort(values)
    v_sorted = values[order]
    w_sorted = weights[order]
    cum = np.cumsum(w_sorted)
    W = cum[-1]
    target = alpha * (W + np.max(w_sorted))
    idx = np.searchsorted(cum, target, side="left")
    if idx >= len(v_sorted):
        return float(v_sorted[-1])
    return float(v_sorted[idx])


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_CAP.parent.mkdir(parents=True, exist_ok=True)

    cp = pd.read_csv(CONF_CSV)
    mas = pd.read_csv(MASTER, usecols=["mol_id", "smiles", "scaffold_family"])
    df = cp.merge(mas, on="mol_id", how="left")
    df["abs_residual"] = (df["y_true"] - df["pred"]).abs()
    df["fp"] = df["smiles"].map(morgan_fp)

    calib = df[df["set"] == "calibration"].reset_index(drop=True)
    test = df[df["set"] == "test"].reset_index(drop=True)

    cal_fps = calib["fp"].tolist()
    cal_nonconf = calib["nonconf_score"].values
    n_cal = len(calib)

    # Precompute test-vs-calib similarity matrix.
    sim = np.zeros((len(test), n_cal))
    for i, t in enumerate(test["fp"].tolist()):
        for j, c in enumerate(cal_fps):
            sim[i, j] = DataStructs.TanimotoSimilarity(t, c)

    # Sweep (alpha, beta) grid.
    results = {}
    per_mol_records = []
    for nominal in NOMINAL_LEVELS:
        for beta in BETAS:
            weights = (sim + EPSILON) ** beta  # (n_test, n_cal)
            wn = weights / weights.sum(axis=1, keepdims=True)
            q_per_mol = []
            covered_per_mol = []
            for i in range(len(test)):
                q_t = weighted_quantile(cal_nonconf, wn[i], nominal)
                q_per_mol.append(q_t)
                covered_per_mol.append(
                    int(test["abs_residual"].iloc[i] <= q_t))
                per_mol_records.append({
                    "alpha": nominal,
                    "beta": beta,
                    "mol_id": test["mol_id"].iloc[i],
                    "scaffold_family": test["scaffold_family"].iloc[i],
                    "abs_residual_meV": float(
                        test["abs_residual"].iloc[i] * 1000),
                    "q_hat_local_meV": float(q_t * 1000),
                    "covered": int(test["abs_residual"].iloc[i] <= q_t),
                    "max_sim_to_calib": float(sim[i].max()),
                    "mean_top5_sim_to_calib": float(
                        np.sort(sim[i])[::-1][:5].mean()),
                })
            k_cov = sum(covered_per_mol)
            n_cov = len(covered_per_mol)
            cov = k_cov / n_cov
            z = 1.959963984540054
            denom = 1 + z * z / n_cov
            centre = (cov + z * z / (2 * n_cov)) / denom
            half = z * math.sqrt(
                cov * (1 - cov) / n_cov + z * z / (4 * n_cov * n_cov)) / denom
            lo = max(0.0, centre - half)
            hi = min(1.0, centre + half)
            results[f"alpha_{nominal}_beta_{beta}"] = {
                "alpha": nominal,
                "beta": beta,
                "covered_over_n": f"{k_cov}/{n_cov}",
                "coverage": cov,
                "wilson_95_ci": [lo, hi],
                "q_hat_local_meV_min": float(min(q_per_mol) * 1000),
                "q_hat_local_meV_median": float(np.median(q_per_mol) * 1000),
                "q_hat_local_meV_max": float(max(q_per_mol) * 1000),
                "q_hat_local_meV_mean": float(np.mean(q_per_mol) * 1000),
            }

    pd.DataFrame(per_mol_records).to_csv(OUT_CSV, index=False)

    payload = {
        "experiment_id": "diag_D_local_conformal",
        "method": (
            "Tanimoto-weighted locally-adaptive split-conformal: per-test-"
            "molecule weighted upper-tail quantile of the calibration "
            "nonconformity scores, with weights w_i ∝ (T(f_t, f_calib[i]) "
            "+ ε)^β. β = 0 recovers the global split-conformal quantile."
        ),
        "fp_settings": {"type": "Morgan", "radius": FP_RADIUS,
                        "nBits": FP_NBITS, "epsilon": EPSILON},
        "nominal_levels_tested": NOMINAL_LEVELS,
        "n_calibration": int(n_cal),
        "n_test": int(len(test)),
        "betas_tested": BETAS,
        "results_by_alpha_beta": results,
        "structural_observation": (
            f"At alpha = 0.95 with n_calib = {n_cal}, the finite-sample "
            f"ceil((n+1)*alpha) = {math.ceil((n_cal+1) * 0.95)} = n rank "
            "pins q_hat to the maximum calibration nonconformity score "
            "regardless of weighting; locally-weighted CP cannot differ "
            "from global CP at this level. At alpha = 0.90 and 0.80 the "
            "rank is < n and local weighting can act."
        ),
        "interpretation": (
            "Sweeping β from 0 (global quantile) upward localises the "
            "calibration weighting around each test molecule. Compare "
            "coverage at α = 0.80, 0.90, 0.95 to disentangle the "
            "structural pinning at α = 0.95 from a real local-weighting "
            "effect at lower α."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    # Figure: coverage vs β + per-molecule q_hat distribution
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
    })
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8))

    ax = axes[0]
    betas_x = list(BETAS)
    colors = {0.80: "#1f77b4", 0.90: "#2ca02c", 0.95: "#d62728"}
    for nominal in NOMINAL_LEVELS:
        covs = [results[f"alpha_{nominal}_beta_{b}"]["coverage"]
                for b in BETAS]
        los = [results[f"alpha_{nominal}_beta_{b}"]["wilson_95_ci"][0]
               for b in BETAS]
        his = [results[f"alpha_{nominal}_beta_{b}"]["wilson_95_ci"][1]
               for b in BETAS]
        yerr = np.array([
            [c - lo for c, lo in zip(covs, los)],
            [hi - c for c, hi in zip(covs, his)],
        ])
        ax.errorbar(betas_x, covs, yerr=yerr, fmt="o-", capsize=3,
                    color=colors[nominal],
                    label=f"α = {nominal:.2f}")
        ax.axhline(nominal, color=colors[nominal], linestyle="--",
                   linewidth=0.7, alpha=0.5)
    ax.set_xticks(betas_x)
    ax.set_xlabel("Tanimoto weight temperature β  (β=0 → global CP)")
    ax.set_ylabel("Empirical coverage")
    ax.set_ylim(0, 1.1)
    ax.set_title(f"(a) coverage vs β at three α  "
                 f"(n_test={len(test)}, n_calib={n_cal})")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    df_per = pd.DataFrame(per_mol_records)
    # Show per-mol q̂ distribution at the most informative α (= 0.90),
    # where local weighting can actually act.
    box_data = []
    box_labels = []
    for b in BETAS:
        sub = df_per[(df_per["beta"] == b) & (df_per["alpha"] == 0.90)
                     ]["q_hat_local_meV"].values
        box_data.append(sub)
        box_labels.append(f"β={b}")
    ax.boxplot(box_data, tick_labels=box_labels, patch_artist=True,
               boxprops=dict(facecolor="lightgray"))
    ax.set_ylabel("Per-test-mol local q̂ at α=0.90 (meV)")
    ax.set_title("(b) interval-width distribution at α=0.90")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(OUT_PDF, format="pdf", bbox_inches="tight")
    plt.close(fig)

    cap = {
        "figure_id": "diag_local_conformal",
        "source_data_files": [
            "results/round1_eval/p0b_conformal_calibration.csv",
            "data/processed/master_molecule_table.csv",
            "results/diagnostics/local_conformal.csv",
            "results/diagnostics/local_conformal.json",
        ],
        "sample_size": {
            "n_calibration": int(n_cal),
            "n_test": int(len(test)),
            "betas_tested": BETAS,
        },
        "key_numbers": {
            "nominal_levels_tested": NOMINAL_LEVELS,
            "betas_tested": BETAS,
            "coverage_grid": {
                f"alpha_{nom}": {
                    f"beta_{b}": {
                        "coverage": round(
                            results[f"alpha_{nom}_beta_{b}"]["coverage"], 4),
                        "covered_over_n": results[
                            f"alpha_{nom}_beta_{b}"]["covered_over_n"],
                        "wilson_95_ci": [
                            round(results[f"alpha_{nom}_beta_{b}"]
                                  ["wilson_95_ci"][0], 4),
                            round(results[f"alpha_{nom}_beta_{b}"]
                                  ["wilson_95_ci"][1], 4),
                        ],
                        "q_hat_local_meV_median": round(
                            results[f"alpha_{nom}_beta_{b}"]
                            ["q_hat_local_meV_median"], 2),
                    } for b in BETAS
                } for nom in NOMINAL_LEVELS
            },
            "structural_pinning_at_alpha_0_95": (
                f"At alpha = 0.95 with n_calib = {n_cal}, the "
                f"finite-sample rank ceil((n+1)*alpha) = "
                f"{math.ceil((n_cal+1)*0.95)} = n, so q_hat is the max "
                "calibration nonconformity score for any β. Local "
                "weighting can act only at lower α."
            ),
        },
        "exclusions_or_filters": [
            "Hz_NH23 is excluded by design from the conformal test set "
            "(n_test = 14, not 15).",
            f"Locally-weighted quantile uses Tanimoto similarity on "
            f"Morgan FP (radius={FP_RADIUS}, {FP_NBITS} bits) with "
            f"epsilon={EPSILON} to avoid zero weights.",
            "β was not tuned on the test set; all four values are "
            "reported for transparency.",
        ],
        "visualization_caveats": [
            f"All coverages are computed on n_test = {len(test)} < 30; "
            "Wilson 95% CIs span > 30 percentage points and overlap.",
            "The β = 0 column reproduces the global split-conformal "
            "result (5/14 = 35.7%); higher β localises calibration around "
            "each test molecule.",
        ],
        "manuscript_claims_allowed": [
            f"Tanimoto-weighted locally-adaptive split conformal yields "
            f"the coverages reported in `key_numbers.coverage_by_beta`; "
            f"intervals become per-test-molecule rather than constant.",
            "On this n_calib = 19 / n_test = 14 setting, the change in "
            "empirical coverage with β must be reported with its Wilson "
            "95% CI rather than as a point claim.",
        ],
        "manuscript_claims_not_allowed": [
            "Do not claim locally-weighted CP 'recovers' nominal "
            "coverage if the post-recalibration Wilson CI does not "
            "include the nominal level.",
            "Do not select β post-hoc on the test set — report all four.",
        ],
    }
    OUT_CAP.write_text(json.dumps(cap, indent=2) + "\n")

    print(f"[OK] {OUT_JSON.relative_to(ROOT)}")
    print(f"[OK] {OUT_CSV.relative_to(ROOT)}")
    print(f"[OK] {OUT_PDF.relative_to(ROOT)}")
    print(f"[OK] {OUT_CAP.relative_to(ROOT)}")
    for nom in NOMINAL_LEVELS:
        for b in BETAS:
            r = results[f"alpha_{nom}_beta_{b}"]
            print(f"     α={nom:.2f} β={b}: cov={r['coverage']*100:5.1f}% "
                  f"[{r['wilson_95_ci'][0]*100:.1f}, "
                  f"{r['wilson_95_ci'][1]*100:.1f}]  "
                  f"({r['covered_over_n']})  median q={r['q_hat_local_meV_median']:.2f} meV")


if __name__ == "__main__":
    main()
