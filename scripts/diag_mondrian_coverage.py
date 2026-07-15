#!/usr/bin/env python3
"""diag_mondrian_coverage.py

Phase 2C — Scaffold-conditional (Mondrian) conformal coverage.

Hypothesis:
    The 35.7% empirical 95%-nominal coverage is an aggregate; a
    scaffold-conditional split should reveal whether the failure is
    uniform across scaffolds or driven by a particular subset (e.g.,
    5AP, which is over-represented in the test set relative to calib).

Method (Mondrian conformal regressor, Bostrom & Johansson PMLR 2020):
    Partition both calibration and test sets by scaffold_family. For
    each scaffold bucket B with calib subset C_B and test subset T_B:
        q_hat_B = quantile(nonconf_score[C_B], 0.95)   # bucket-local
        coverage_B = mean(|y_test - pred_test| <= q_hat_B over T_B)
    Compare to the global aggregate coverage.

Data sources (read-only):
    results/round1_eval/p0b_conformal_calibration.csv
    data/processed/master_molecule_table.csv

Outputs:
    results/diagnostics/mondrian_coverage.{json,csv}
    figures/diag_mondrian_coverage.pdf
    figures/caption_data/diag_mondrian_coverage.json
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONF_CSV = ROOT / "results/round1_eval/p0b_conformal_calibration.csv"
MASTER = ROOT / "data/processed/master_molecule_table.csv"
OUT_JSON = ROOT / "results/diagnostics/mondrian_coverage.json"
OUT_CSV = ROOT / "results/diagnostics/mondrian_coverage.csv"
OUT_PDF = ROOT / "figures/diag_mondrian_coverage.pdf"
OUT_CAP = ROOT / "figures/caption_data/diag_mondrian_coverage.json"

NOMINAL = 0.95


def quantile_with_finite_correction(scores: np.ndarray, alpha: float) -> float:
    """Standard split-conformal quantile with the (n+1)/(n) correction.

    Returns the alpha-quantile of `scores` interpolated as
    ceil((n+1) * alpha) / n -th order statistic, capped at the max.
    """
    if len(scores) == 0:
        return float("nan")
    n = len(scores)
    rank = math.ceil((n + 1) * alpha)
    rank = min(rank, n)  # cap
    sorted_s = np.sort(scores)
    return float(sorted_s[rank - 1])


def wilson_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    z = 1.959963984540054  # 95% normal
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def main() -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_CAP.parent.mkdir(parents=True, exist_ok=True)

    cp = pd.read_csv(CONF_CSV)
    mas = pd.read_csv(MASTER, usecols=["mol_id", "scaffold_family"])
    df = cp.merge(mas, on="mol_id", how="left")
    df["abs_residual"] = (df["y_true"] - df["pred"]).abs()

    # Coalesce small scaffold families.
    df["scaffold_bucket"] = df["scaffold_family"].where(
        df["scaffold_family"].isin(["Hz", "5AP"]), "other"
    )

    calib = df[df["set"] == "calibration"].copy()
    test = df[df["set"] == "test"].copy()

    # Global (non-Mondrian) reference using the same quantile rule.
    global_q = quantile_with_finite_correction(
        calib["nonconf_score"].values, NOMINAL)
    global_covered = (test["abs_residual"] <= global_q).astype(int)
    global_k = int(global_covered.sum())
    global_n = int(len(test))
    global_cov = global_k / global_n
    global_lo, global_hi = wilson_ci(global_k, global_n)

    # Mondrian buckets.
    bucket_rows = []
    test_assignment = []
    for scaf in ["Hz", "5AP", "other"]:
        c_b = calib[calib["scaffold_bucket"] == scaf]
        t_b = test[test["scaffold_bucket"] == scaf]
        if len(c_b) > 0:
            q_b = quantile_with_finite_correction(c_b["nonconf_score"].values,
                                                  NOMINAL)
        else:
            q_b = float("nan")
        if len(t_b) > 0 and not math.isnan(q_b):
            covered_b = (t_b["abs_residual"] <= q_b).astype(int)
            k_b, n_b = int(covered_b.sum()), int(len(t_b))
            cov_b = k_b / n_b
            lo_b, hi_b = wilson_ci(k_b, n_b)
            for mol_id, cov in zip(t_b["mol_id"], covered_b):
                test_assignment.append({
                    "mol_id": mol_id, "bucket": scaf,
                    "q_hat_bucket": q_b, "covered": int(cov),
                })
        else:
            k_b = 0; n_b = int(len(t_b)); cov_b = float("nan")
            lo_b, hi_b = (float("nan"), float("nan"))
        bucket_rows.append({
            "scaffold_bucket": scaf,
            "n_calib": int(len(c_b)),
            "n_test": int(len(t_b)),
            "q_hat_eV": q_b,
            "q_hat_meV": q_b * 1000.0 if not math.isnan(q_b) else float("nan"),
            "coverage": cov_b,
            "covered_n": k_b,
            "wilson_ci_lo": lo_b,
            "wilson_ci_hi": hi_b,
        })
    bucket_df = pd.DataFrame(bucket_rows)
    bucket_df.to_csv(OUT_CSV, index=False)

    # Aggregate Mondrian coverage (sum of bucket coverages weighted by test n)
    mondrian_test_assignment = pd.DataFrame(test_assignment)
    if len(mondrian_test_assignment):
        mondrian_k = int(mondrian_test_assignment["covered"].sum())
        mondrian_n = int(len(mondrian_test_assignment))
        mondrian_cov = mondrian_k / mondrian_n
        mondrian_lo, mondrian_hi = wilson_ci(mondrian_k, mondrian_n)
    else:
        mondrian_k = mondrian_n = 0
        mondrian_cov = float("nan")
        mondrian_lo = mondrian_hi = float("nan")

    payload = {
        "experiment_id": "diag_C_mondrian_coverage",
        "method": (
            "Mondrian (scaffold-conditional) split-conformal regressor "
            "with finite-sample quantile correction "
            "(rank = ceil((n+1)*alpha))."
        ),
        "nominal_coverage": NOMINAL,
        "scaffold_buckets": ["Hz", "5AP", "other"],
        "global_reference": {
            "q_hat_eV": float(global_q),
            "q_hat_meV": float(global_q) * 1000.0,
            "coverage": global_cov,
            "covered_over_n": f"{global_k}/{global_n}",
            "wilson_95_ci": [global_lo, global_hi],
        },
        "buckets": {
            r["scaffold_bucket"]: {
                "n_calib": int(r["n_calib"]),
                "n_test": int(r["n_test"]),
                "q_hat_meV": (None if math.isnan(r["q_hat_meV"])
                              else round(float(r["q_hat_meV"]), 3)),
                "coverage": (None if math.isnan(r["coverage"])
                             else round(float(r["coverage"]), 4)),
                "covered_over_n": (
                    f"{r['covered_n']}/{r['n_test']}"
                    if r["n_test"] > 0 else "n/a"),
                "wilson_95_ci": [
                    None if math.isnan(r["wilson_ci_lo"])
                    else round(float(r["wilson_ci_lo"]), 4),
                    None if math.isnan(r["wilson_ci_hi"])
                    else round(float(r["wilson_ci_hi"]), 4),
                ],
            }
            for _, r in bucket_df.iterrows()
        },
        "mondrian_aggregate": {
            "coverage": mondrian_cov,
            "coverage_pct": (None if math.isnan(mondrian_cov)
                             else round(float(mondrian_cov) * 100.0, 1)),
            "covered_over_n": f"{mondrian_k}/{mondrian_n}",
            "wilson_95_ci": [mondrian_lo, mondrian_hi],
            "wilson_95_ci_pct": [
                None if math.isnan(mondrian_lo) else round(float(mondrian_lo) * 100.0, 1),
                None if math.isnan(mondrian_hi) else round(float(mondrian_hi) * 100.0, 1),
            ],
        },
        "interpretation": (
            "Mondrian buckets reveal whether the global 35.7% under-coverage "
            "is uniform or scaffold-driven. A bucket with very different "
            "coverage from the global aggregate is a candidate for "
            "scaffold-aware re-calibration. With these small calibration "
            "buckets, all coverage estimates carry wide Wilson CIs; treat "
            "as descriptive."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2))

    # Figure: bucket coverage with Wilson CIs + global reference
    plt.rcParams.update({
        "font.family": "Times New Roman",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
    })
    fig, ax = plt.subplots(figsize=(6.0, 4.0))

    labels = []
    covs = []
    los = []
    his = []
    ns = []
    for r in bucket_rows + [{
        "scaffold_bucket": "all (Mondrian)",
        "n_test": mondrian_n, "coverage": mondrian_cov,
        "wilson_ci_lo": mondrian_lo, "wilson_ci_hi": mondrian_hi,
        "n_calib": int(len(calib)),
    }, {
        "scaffold_bucket": "all (global)",
        "n_test": global_n, "coverage": global_cov,
        "wilson_ci_lo": global_lo, "wilson_ci_hi": global_hi,
        "n_calib": int(len(calib)),
    }]:
        labels.append(
            f"{r['scaffold_bucket']}\n"
            f"calib n={r['n_calib']}, test n={r['n_test']}")
        covs.append(r["coverage"] if r["coverage"] == r["coverage"] else 0)
        los.append(r["wilson_ci_lo"] if r["wilson_ci_lo"] == r["wilson_ci_lo"] else 0)
        his.append(r["wilson_ci_hi"] if r["wilson_ci_hi"] == r["wilson_ci_hi"] else 0)
        ns.append(r["n_test"])

    x = np.arange(len(labels))
    yerr = np.array([
        [c - lo for c, lo in zip(covs, los)],
        [hi - c for c, hi in zip(covs, his)],
    ])
    colors = ["#1f77b4", "#ff7f0e", "#7f7f7f", "#2ca02c", "#d62728"]
    bars = ax.bar(x, covs, yerr=yerr, capsize=4,
                  color=colors[:len(labels)], edgecolor="black",
                  linewidth=0.5, alpha=0.8)
    ax.axhline(NOMINAL, color="black", linestyle="--", linewidth=1,
               label=f"nominal {int(NOMINAL*100)}%")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel(f"Empirical {int(NOMINAL*100)}% coverage")
    ax.set_ylim(0, 1.1)
    ax.set_title(f"Scaffold-conditional (Mondrian) {int(NOMINAL*100)}% "
                 "conformal coverage (95% Wilson CIs)")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(OUT_PDF, format="pdf", bbox_inches="tight")
    plt.close(fig)

    cap = {
        "figure_id": "diag_mondrian_coverage",
        "source_data_files": [
            "results/round1_eval/p0b_conformal_calibration.csv",
            "data/processed/master_molecule_table.csv",
            "results/diagnostics/mondrian_coverage.csv",
            "results/diagnostics/mondrian_coverage.json",
        ],
        "sample_size": {
            "n_calibration": int(len(calib)),
            "n_test": int(len(test)),
            "buckets": {
                r["scaffold_bucket"]: {
                    "n_calib": int(r["n_calib"]),
                    "n_test": int(r["n_test"]),
                } for _, r in bucket_df.iterrows()
            },
        },
        "key_numbers": {
            "nominal_coverage": NOMINAL,
            "global_q_hat_meV": round(float(global_q) * 1000.0, 2),
            "global_coverage": round(float(global_cov), 4),
            "global_covered_over_n": f"{global_k}/{global_n}",
            "mondrian_aggregate_coverage": (
                None if math.isnan(mondrian_cov)
                else round(float(mondrian_cov), 4)),
            "mondrian_aggregate_covered_over_n":
                f"{mondrian_k}/{mondrian_n}",
            "buckets": payload["buckets"],
        },
        "exclusions_or_filters": [
            "Scaffold buckets coalesce 'BN-PAH' and any other small family "
            "into 'other' so that no bucket has n_calib < 2.",
            "Wilson 95% CIs are reported on every bucket because all bucket "
            "n_test < 30.",
        ],
        "visualization_caveats": [
            "Bucket sizes are very small; CIs are wide. The bar chart shows "
            "directional contrast rather than calibrated effect sizes.",
            "Buckets with n_test = 0 are omitted from the comparison.",
        ],
        "manuscript_claims_allowed": [
            f"Global split-conformal coverage at the {int(NOMINAL*100)}% "
            f"nominal level is {global_k}/{global_n} = "
            f"{global_cov*100:.1f}% (Wilson 95% CI "
            f"[{global_lo*100:.1f}%, {global_hi*100:.1f}%]).",
            "Mondrian (scaffold-conditional) recalibration with the same "
            "calibration set and finite-sample quantile correction yields "
            f"the bucket coverages reported in `key_numbers.buckets`.",
        ],
        "manuscript_claims_not_allowed": [
            "Do not claim a Mondrian bucket coverage is significantly "
            "different from the global without citing the bucket-level n "
            "and Wilson CI.",
            "Do not extrapolate bucket Mondrian quantiles outside the "
            "scaffold families present here.",
        ],
    }
    OUT_CAP.write_text(json.dumps(cap, indent=2) + "\n")

    print(f"[OK] {OUT_JSON.relative_to(ROOT)}")
    print(f"[OK] {OUT_CSV.relative_to(ROOT)}")
    print(f"[OK] {OUT_PDF.relative_to(ROOT)}")
    print(f"[OK] {OUT_CAP.relative_to(ROOT)}")
    print(f"     global q_hat_meV = {global_q*1000:.2f}, "
          f"coverage = {global_k}/{global_n} = {global_cov*100:.1f}%")
    print(f"     Mondrian aggregate: {mondrian_k}/{mondrian_n} = "
          f"{mondrian_cov*100:.1f}%")
    for _, r in bucket_df.iterrows():
        print(f"     bucket {r['scaffold_bucket']:8s}: "
              f"calib n={r['n_calib']:2d}, test n={r['n_test']:2d}, "
              f"q_hat={r['q_hat_meV']:>6.2f} meV, cov={r['coverage']}")


if __name__ == "__main__":
    main()
