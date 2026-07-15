#!/usr/bin/env python3
"""Retrain the delta transfer model after Round 1 ADC(2) data is ingested.

Compares pre-round1 (frozen) performance vs post-round1 performance.
Generates learning curve showing benefit of additional labeled data.

Usage:
    python scripts/retrain_after_round1.py [--project-root PROJECT_ROOT]
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
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SEED = 42
FEATURE_PREFIX_EXCLUDE = [
    "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
    "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
    "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
    "is_invest", "is_near_zero", "is_high_fosc",
    "canonical_smiles",
]

plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "font.size": 11,
    "figure.dpi": 300,
})


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    return p.parse_args()


def get_feature_cols(df):
    return [c for c in df.columns if c not in FEATURE_PREFIX_EXCLUDE]


def compute_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    rho = spearmanr(y_true, y_pred)[0] if len(y_true) > 2 else np.nan
    sign_acc = np.mean(np.sign(y_true) == np.sign(y_pred))
    n_invest_true = (y_true < 0).sum()
    n_invest_pred = (y_pred < 0).sum()
    invest_recall = ((y_true < 0) & (y_pred < 0)).sum() / max(n_invest_true, 1) if n_invest_true > 0 else np.nan
    invest_precision = ((y_true < 0) & (y_pred < 0)).sum() / max(n_invest_pred, 1) if n_invest_pred > 0 else np.nan
    nz_mask = np.abs(y_true) <= 0.10
    nz_f1 = np.nan
    if nz_mask.sum() > 0:
        pred_nz = np.abs(y_pred) <= 0.10
        tp = (nz_mask & pred_nz).sum()
        prec = tp / max(pred_nz.sum(), 1)
        rec = tp / max(nz_mask.sum(), 1)
        nz_f1 = 2 * prec * rec / max(prec + rec, 1e-10)
    return {
        "MAE": mae, "RMSE": rmse, "Spearman_rho": rho,
        "sign_accuracy": sign_acc,
        "INVEST_recall": invest_recall, "INVEST_precision": invest_precision,
        "near_zero_F1": nz_f1,
    }


def run_delta_transfer_loo(source_df, target_df, feat_cols):
    """Run delta transfer with LOO-CV on target."""
    usable = [c for c in feat_cols if source_df[c].notna().mean() >= 0.1
              and target_df[c].notna().mean() >= 0.1]

    X_src = source_df[usable].fillna(-999).values
    y_src = source_df["adc2_dest_ev"].values

    # Train source model
    model_src = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        random_state=SEED, n_jobs=-1, verbosity=0,
    )
    model_src.fit(X_src, y_src)

    # Source predictions on all target
    X_tgt_all = target_df[usable].fillna(-999).values
    y_tgt_all = target_df["adc2_dest_ev"].values
    src_pred_all = model_src.predict(X_tgt_all)

    # LOO delta transfer
    n = len(target_df)
    delta_preds = np.zeros(n)
    for i in range(n):
        train_idx = list(range(n))
        train_idx.remove(i)

        residuals_train = y_tgt_all[train_idx] - src_pred_all[train_idx]
        X_delta_tr = np.column_stack([
            X_tgt_all[train_idx],
            src_pred_all[train_idx].reshape(-1, 1),
        ])
        X_delta_te = np.column_stack([
            X_tgt_all[[i]],
            src_pred_all[[i]].reshape(-1, 1),
        ])

        model_delta = XGBRegressor(
            n_estimators=50, max_depth=2, learning_rate=0.1,
            random_state=SEED, n_jobs=-1, verbosity=0,
        )
        model_delta.fit(X_delta_tr, residuals_train)
        delta_preds[i] = src_pred_all[i] + model_delta.predict(X_delta_te)[0]

    return y_tgt_all, delta_preds


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)

    os.makedirs(os.path.join(proj, "results/tables"), exist_ok=True)
    os.makedirs(os.path.join(proj, "results/figures"), exist_ok=True)
    os.makedirs(os.path.join(proj, "results/reports"), exist_ok=True)

    # Load ORIGINAL model_input_table (pre-round1, for feature columns)
    original_input = pd.read_csv(os.path.join(proj, "data/processed/model_input_table.csv"))
    feat_cols = get_feature_cols(original_input)

    # Load UPDATED master table
    updated_path = os.path.join(proj, "data/processed/master_molecule_table_round1_updated.csv")
    if not os.path.exists(updated_path):
        log.error("Updated master table not found: %s", updated_path)
        log.error("Run ingest_round1_adc2_results.py first.")
        return

    master_updated = pd.read_csv(updated_path)

    # Merge features from original input table
    feats_only = original_input[["mol_id"] + feat_cols]
    df_updated = master_updated.merge(feats_only, on="mol_id", how="left", suffixes=("", "_feat"))
    # Drop duplicates from merge
    dup_cols = [c for c in df_updated.columns if c.endswith("_feat")]
    df_updated = df_updated.drop(columns=dup_cols)

    labeled = df_updated[df_updated["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
    source = labeled[labeled["source_domain"] == "pollice"]
    target = labeled[labeled["source_domain"] != "pollice"]

    log.info("Source: %d, Target (post-round1): %d", len(source), len(target))

    # Load pre-round1 frozen results for comparison
    frozen_results = pd.read_csv(os.path.join(proj, "results/tables/source_target_transfer_results.csv"))
    pre_delta = frozen_results[frozen_results["experiment"] == "delta_transfer_loo"].iloc[0].to_dict()

    log.info("Pre-round1 delta transfer: MAE=%.4f, sign_acc=%.3f",
             pre_delta["MAE"], pre_delta["sign_accuracy"])

    # --- Run post-round1 delta transfer ---
    log.info("\n=== Post-Round1 Delta Transfer (LOO on expanded target) ===")
    y_true, y_pred = run_delta_transfer_loo(source, target, feat_cols)
    post_metrics = compute_metrics(y_true, y_pred)
    post_metrics["stage"] = "post_round1"
    post_metrics["n_target"] = len(target)

    pre_metrics = {k: pre_delta.get(k, np.nan) for k in post_metrics if k not in ["stage", "n_target"]}
    pre_metrics["stage"] = "pre_round1"
    pre_metrics["n_target"] = 19  # frozen

    results = pd.DataFrame([pre_metrics, post_metrics])
    results.to_csv(os.path.join(proj, "results/tables/post_round1_model_update_summary.csv"), index=False)

    log.info("\n=== Comparison ===")
    log.info("\n%s", results.to_string(index=False))

    # --- Learning curve: incrementally add target data ---
    log.info("\n=== Learning Curve ===")
    # Sort target by original order
    target_sorted = target.copy().reset_index(drop=True)
    lc_points = []

    # Start from the original 19 target molecules
    original_target_ids = pd.read_csv(
        os.path.join(proj, "results/tables/transfer_per_molecule_predictions.csv"))["mol_id"].tolist()
    original_target = target_sorted[target_sorted["mol_id"].isin(original_target_ids)]
    new_target = target_sorted[~target_sorted["mol_id"].isin(original_target_ids)]

    for n_add in range(0, len(new_target) + 1):
        if n_add == 0:
            subset = original_target
        else:
            subset = pd.concat([original_target, new_target.iloc[:n_add]], ignore_index=True)

        if len(subset) < 3:
            continue

        y_t, y_p = run_delta_transfer_loo(source, subset, feat_cols)
        m = compute_metrics(y_t, y_p)
        m["n_target"] = len(subset)
        m["n_added"] = n_add
        lc_points.append(m)

    lc_df = pd.DataFrame(lc_points)
    lc_df.to_csv(os.path.join(proj, "results/tables/learning_curve_round1.csv"), index=False)

    # --- Learning curve figure ---
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    for ax, metric, ylabel in zip(axes,
                                   ["MAE", "sign_accuracy", "Spearman_rho"],
                                   ["MAE (eV)", "Sign Accuracy", "Spearman ρ"]):
        ax.plot(lc_df["n_target"], lc_df[metric], "o-", color="C2", markersize=5)
        ax.axhline(pre_delta.get(metric, np.nan), color="C3", ls="--", lw=1,
                   label=f"Pre-round1 (n=19): {pre_delta.get(metric, 0):.3f}")
        ax.set_xlabel("Target pool size")
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
        ax.legend(fontsize=8)

    plt.suptitle("Learning Curve: Delta Transfer with Incremental Target Data", fontsize=12)
    plt.tight_layout()
    fig.savefig(os.path.join(proj, "results/figures/learning_curve_round1.png"), bbox_inches="tight")
    plt.close()

    # --- Report ---
    report = f"""# Post-Round1 模型更新报告

**日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}
**模型**: Delta transfer (XGBoost, source pretrain + target residual)
**变更**: 仅新增 target 数据，模型定义和超参数不变

## 性能对比

| 指标 | Pre-Round1 (n=19) | Post-Round1 (n={len(target)}) | 变化 |
|------|-------------------|-------------------------------|------|
| MAE (eV) | {pre_delta.get('MAE', 0):.4f} | {post_metrics['MAE']:.4f} | {post_metrics['MAE'] - pre_delta.get('MAE', 0):+.4f} |
| RMSE (eV) | {pre_delta.get('RMSE', 0):.4f} | {post_metrics['RMSE']:.4f} | {post_metrics['RMSE'] - pre_delta.get('RMSE', 0):+.4f} |
| Spearman ρ | {pre_delta.get('Spearman_rho', 0):.3f} | {post_metrics['Spearman_rho']:.3f} | {post_metrics['Spearman_rho'] - pre_delta.get('Spearman_rho', 0):+.3f} |
| Sign accuracy | {pre_delta.get('sign_accuracy', 0):.3f} | {post_metrics['sign_accuracy']:.3f} | {post_metrics['sign_accuracy'] - pre_delta.get('sign_accuracy', 0):+.3f} |
| INVEST recall | {pre_delta.get('INVEST_recall', 0):.3f} | {post_metrics['INVEST_recall']:.3f} | {post_metrics['INVEST_recall'] - pre_delta.get('INVEST_recall', 0):+.3f} |
| INVEST precision | {pre_delta.get('INVEST_precision', 0):.3f} | {post_metrics['INVEST_precision']:.3f} | {post_metrics['INVEST_precision'] - pre_delta.get('INVEST_precision', 0):+.3f} |

## 方法说明

- **模型不变**: XGBoost delta transfer (source→target residual learning)
- **超参数不变**: n_estimators=200/50, max_depth=4/2, lr=0.1
- **评估方式不变**: LOO-CV on target domain
- **唯一变化**: target domain 标签数量从 19 增加到 {len(target)}

## 注意事项

- 与冻结版本(v1.0)相比，模型定义未改变，仅数据池扩大。
- 如果性能下降，可能的原因包括：新数据引入了更难的分布区域、LOO-CV 在更大池中更严格。
- 所有变化都是由于数据新增，而非模型修改。

## 输出文件

- `results/tables/post_round1_model_update_summary.csv`
- `results/tables/learning_curve_round1.csv`
- `results/figures/learning_curve_round1.png`
"""

    with open(os.path.join(proj, "results/reports/post_round1_model_update.md"), "w") as f:
        f.write(report)
    log.info("\nAll outputs saved.")


if __name__ == "__main__":
    main()
