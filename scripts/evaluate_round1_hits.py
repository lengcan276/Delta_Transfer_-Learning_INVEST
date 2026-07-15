#!/usr/bin/env python3
"""Evaluate Round 1 active learning hit rates and bucket performance.

Requires round1 ADC(2) results to have been ingested first.

Usage:
    python scripts/evaluate_round1_hits.py [--project-root PROJECT_ROOT]
"""
import argparse
import logging
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 11,
    "figure.dpi": 300,
})


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    return p.parse_args()


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)

    os.makedirs(os.path.join(proj, "results/tables"), exist_ok=True)
    os.makedirs(os.path.join(proj, "results/figures"), exist_ok=True)
    os.makedirs(os.path.join(proj, "results/reports"), exist_ok=True)

    # Load frozen candidates with predictions
    frozen = pd.read_csv(os.path.join(proj, "results/tables/round1_candidates_frozen.csv"))

    # Load updated master table
    updated_path = os.path.join(proj, "data/processed/master_molecule_table_round1_updated.csv")
    if not os.path.exists(updated_path):
        log.error("Updated master table not found: %s", updated_path)
        log.error("Run ingest_round1_adc2_results.py first.")
        return

    master = pd.read_csv(updated_path)

    # Merge true ADC(2) values onto frozen candidates
    true_vals = master[master["mol_id"].isin(frozen["mol_id"])][
        ["mol_id", "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available"]
    ]

    merged = frozen.merge(true_vals, on="mol_id", how="left")
    has_result = merged["adc2_available"] == True
    n_returned = has_result.sum()

    log.info("Candidates: %d, with ADC(2) results: %d", len(merged), n_returned)

    if n_returned == 0:
        log.warning("No ADC(2) results available yet. Cannot evaluate.")
        return

    evaluated = merged[has_result].copy()

    # --- Hit definitions ---
    evaluated["true_invest"] = evaluated["adc2_dest_ev"] < 0
    evaluated["true_near_zero"] = evaluated["adc2_dest_ev"].abs() <= 0.10
    evaluated["true_high_fosc"] = evaluated["adc2_fosc"] >= 0.10
    evaluated["pred_invest"] = evaluated["predicted_dest_ev"] < 0
    evaluated["pred_near_zero"] = evaluated["predicted_dest_ev"].abs() <= 0.10

    # --- Overall hit summary ---
    n_invest = evaluated["true_invest"].sum()
    n_nz = evaluated["true_near_zero"].sum()
    n_high_fosc = evaluated["true_high_fosc"].sum()

    pred_error = (evaluated["predicted_dest_ev"] - evaluated["adc2_dest_ev"])
    mae = pred_error.abs().mean()
    rmse = np.sqrt((pred_error ** 2).mean())
    sign_acc = (np.sign(evaluated["predicted_dest_ev"]) == np.sign(evaluated["adc2_dest_ev"])).mean()
    rho = spearmanr(evaluated["adc2_dest_ev"], evaluated["predicted_dest_ev"])[0] if len(evaluated) > 2 else np.nan

    hit_summary = {
        "n_candidates": len(evaluated),
        "n_invest": int(n_invest),
        "n_near_zero": int(n_nz),
        "n_high_fosc": int(n_high_fosc),
        "invest_rate": n_invest / len(evaluated),
        "near_zero_rate": n_nz / len(evaluated),
        "prediction_MAE": mae,
        "prediction_RMSE": rmse,
        "prediction_sign_accuracy": sign_acc,
        "prediction_spearman_rho": rho,
    }

    log.info("\n=== Hit Summary ===")
    for k, v in hit_summary.items():
        log.info("  %-30s %s", k, f"{v:.4f}" if isinstance(v, float) else v)

    pd.DataFrame([hit_summary]).to_csv(
        os.path.join(proj, "results/tables/round1_hit_summary.csv"), index=False)

    # --- Bucket performance ---
    bucket_stats = []
    for bucket in ["uncertainty", "near_zero", "high_fosc", "outlier"]:
        bdata = evaluated[evaluated["selection_bucket"] == bucket]
        if len(bdata) == 0:
            continue
        bucket_stats.append({
            "bucket": bucket,
            "n": len(bdata),
            "n_invest": int(bdata["true_invest"].sum()),
            "invest_rate": bdata["true_invest"].mean(),
            "n_near_zero": int(bdata["true_near_zero"].sum()),
            "near_zero_rate": bdata["true_near_zero"].mean(),
            "n_high_fosc": int(bdata["true_high_fosc"].sum()),
            "mean_abs_error": (bdata["predicted_dest_ev"] - bdata["adc2_dest_ev"]).abs().mean(),
            "mean_true_dest": bdata["adc2_dest_ev"].mean(),
        })

    bucket_df = pd.DataFrame(bucket_stats)
    bucket_df.to_csv(os.path.join(proj, "results/tables/round1_bucket_performance.csv"), index=False)

    log.info("\n=== Bucket Performance ===")
    log.info("\n%s", bucket_df.to_string(index=False))

    # --- Figure 1: Predicted vs True scatter ---
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.axhline(0, color="gray", ls="--", lw=0.7)
    ax.axvline(0, color="gray", ls="--", lw=0.7)
    ax.axhspan(-0.10, 0.10, alpha=0.07, color="orange")
    ax.axvspan(-0.10, 0.10, alpha=0.07, color="orange")

    bucket_colors = {"uncertainty": "C0", "near_zero": "orange", "high_fosc": "C2", "outlier": "C3"}
    bucket_markers = {"uncertainty": "o", "near_zero": "D", "high_fosc": "^", "outlier": "s"}

    for bucket in ["uncertainty", "near_zero", "high_fosc", "outlier"]:
        bdata = evaluated[evaluated["selection_bucket"] == bucket]
        if len(bdata) == 0:
            continue
        ax.scatter(bdata["adc2_dest_ev"], bdata["predicted_dest_ev"],
                   c=bucket_colors[bucket], marker=bucket_markers[bucket],
                   s=60, alpha=0.9, edgecolors="k", lw=0.5,
                   label=f"{bucket} (n={len(bdata)})")

    lims = [min(evaluated["adc2_dest_ev"].min(), evaluated["predicted_dest_ev"].min()) - 0.05,
            max(evaluated["adc2_dest_ev"].max(), evaluated["predicted_dest_ev"].max()) + 0.05]
    ax.plot(lims, lims, "k--", lw=0.8, alpha=0.4)
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    ax.set_xlabel("True ADC(2) ΔEST (eV)")
    ax.set_ylabel("Predicted ΔEST (eV)")
    ax.set_title(f"Round 1: Predicted vs True (MAE={mae:.4f} eV)")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(proj, "results/figures/round1_pred_vs_true_scatter.png"), bbox_inches="tight")
    plt.close()

    # --- Figure 2: Bucket hit bar chart ---
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    buckets = bucket_df["bucket"].tolist()
    x = np.arange(len(buckets))
    colors = [bucket_colors.get(b, "gray") for b in buckets]

    for ax, metric, title in zip(axes,
                                  ["invest_rate", "near_zero_rate", "mean_abs_error"],
                                  ["INVEST Hit Rate", "Near-Zero Hit Rate", "Mean |Error| (eV)"]):
        vals = bucket_df[metric].values
        bars = ax.bar(x, vals, color=colors, edgecolor="k", lw=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(buckets, fontsize=9, rotation=20)
        ax.set_title(title, fontsize=10)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    fig.savefig(os.path.join(proj, "results/figures/round1_bucket_hit_bar.png"), bbox_inches="tight")
    plt.close()

    # --- Figure 3: Acquisition score vs true ΔEST ---
    fig, ax = plt.subplots(figsize=(6, 5))
    for bucket in ["uncertainty", "near_zero", "high_fosc", "outlier"]:
        bdata = evaluated[evaluated["selection_bucket"] == bucket]
        if len(bdata) == 0:
            continue
        ax.scatter(bdata["acquisition_score"], bdata["adc2_dest_ev"],
                   c=bucket_colors[bucket], marker=bucket_markers[bucket],
                   s=60, alpha=0.9, edgecolors="k", lw=0.5,
                   label=f"{bucket}")
    ax.axhline(0, color="gray", ls="--", lw=0.7)
    ax.axhspan(-0.10, 0.10, alpha=0.07, color="orange")
    ax.set_xlabel("Acquisition Score")
    ax.set_ylabel("True ADC(2) ΔEST (eV)")
    ax.set_title("Acquisition Score vs True ΔEST")
    ax.legend(fontsize=8)
    fig.savefig(os.path.join(proj, "results/figures/round1_acquisition_vs_true_dest.png"), bbox_inches="tight")
    plt.close()

    # --- Report ---
    report = f"""# Round 1 命中率评估报告

**日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}
**候选总数**: {len(frozen)}
**已返回 ADC(2)**: {n_returned}

## 总体命中率

| 指标 | 值 |
|------|-----|
| INVEST 命中 (ΔEST < 0) | {n_invest} / {n_returned} ({100*n_invest/n_returned:.1f}%) |
| Near-zero 命中 (|ΔEST| ≤ 0.10) | {n_nz} / {n_returned} ({100*n_nz/n_returned:.1f}%) |
| 高 fosc 命中 (fosc ≥ 0.10) | {n_high_fosc} / {n_returned} ({100*n_high_fosc/n_returned:.1f}%) |

## 预测精度

| 指标 | 值 |
|------|-----|
| MAE | {mae:.4f} eV |
| RMSE | {rmse:.4f} eV |
| Sign accuracy | {sign_acc:.3f} |
| Spearman ρ | {rho:.3f} |

## 各 Bucket 表现

| Bucket | n | INVEST | Near-zero | MAE (eV) |
|--------|---|--------|-----------|----------|
"""
    for _, row in bucket_df.iterrows():
        report += f"| {row['bucket']} | {int(row['n'])} | {int(row['n_invest'])}/{int(row['n'])} ({100*row['invest_rate']:.0f}%) | {int(row['n_near_zero'])}/{int(row['n'])} ({100*row['near_zero_rate']:.0f}%) | {row['mean_abs_error']:.4f} |\n"

    report += f"""
## 逐分子结果

| Rank | mol_id | Bucket | Pred ΔEST | True ΔEST | Error | INVEST? |
|------|--------|--------|-----------|-----------|-------|---------|
"""
    for _, row in evaluated.sort_values("rank").iterrows():
        err = row["predicted_dest_ev"] - row["adc2_dest_ev"]
        inv = "Yes" if row["true_invest"] else "No"
        report += f"| {int(row['rank'])} | {row['mol_id']} | {row['selection_bucket']} | {row['predicted_dest_ev']:.4f} | {row['adc2_dest_ev']:.4f} | {err:+.4f} | {inv} |\n"

    report += """
## 图

- `round1_pred_vs_true_scatter.png`: 预测 vs 真实 ΔEST
- `round1_bucket_hit_bar.png`: 各 bucket 命中率
- `round1_acquisition_vs_true_dest.png`: acquisition score vs 真实 ΔEST
"""

    with open(os.path.join(proj, "results/reports/round1_hit_report.md"), "w") as f:
        f.write(report)
    log.info("\nAll evaluation outputs saved.")


if __name__ == "__main__":
    main()
