#!/usr/bin/env python3
"""Source → Target transfer experiment.

Compares:
  1. Source-only: train on Pollice, test on this-work
  2. Target-only: train/test within this-work (LOO-CV due to small n)
  3. Source + target fine-tune: pretrain on Pollice, fine-tune on this-work (LOO-CV)
  4. Delta transfer: train residual model on target after source prediction

Usage:
    python scripts/train_source_target_transfer.py [--project-root PROJECT_ROOT]
"""
import argparse
import logging
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import spearmanr
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
]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    return p.parse_args()


def get_feature_cols(df):
    return [c for c in df.columns if c not in FEATURE_PREFIX_EXCLUDE]


def prepare_xy(df, feat_cols):
    usable = [c for c in feat_cols if df[c].notna().mean() >= 0.1]
    X = df[usable].fillna(-999).values
    y = df["adc2_dest_ev"].values
    valid = ~np.isnan(y)
    return X[valid], y[valid], usable


def eval_metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    rho = spearmanr(y_true, y_pred)[0] if len(y_true) > 2 else np.nan
    sign_acc = np.mean(np.sign(y_true) == np.sign(y_pred))
    n_invest_true = (y_true < 0).sum()
    n_invest_pred = (y_pred < 0).sum()
    invest_recall = np.nan
    invest_precision = np.nan
    if n_invest_true > 0:
        invest_recall = ((y_true < 0) & (y_pred < 0)).sum() / n_invest_true
    if n_invest_pred > 0:
        invest_precision = ((y_true < 0) & (y_pred < 0)).sum() / n_invest_pred
    return {
        "MAE": mae, "RMSE": rmse, "Spearman_rho": rho,
        "sign_accuracy": sign_acc,
        "INVEST_recall": invest_recall, "INVEST_precision": invest_precision,
    }


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    df = pd.read_csv(os.path.join(proj, "data/processed/model_input_table.csv"))

    feat_cols = get_feature_cols(df)
    labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])

    source = labeled[labeled["source_domain"] == "pollice"].copy()
    target = labeled[labeled["source_domain"] != "pollice"].copy()
    log.info("Source (Pollice): %d, Target (this-work): %d", len(source), len(target))

    results = []

    # ---- Experiment 1: Source-only ----
    log.info("\n=== Exp 1: Source-only → Target ===")
    X_src, y_src, used = prepare_xy(source, feat_cols)
    X_tgt, y_tgt, _ = prepare_xy(target, [c for c in used if c in target.columns])

    # Align columns
    X_tgt_aligned = target[used].fillna(-999).values[:len(y_tgt)]

    model_src = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        random_state=SEED, n_jobs=-1, verbosity=0,
    )
    model_src.fit(X_src, y_src)
    y_pred_src = model_src.predict(X_tgt_aligned)
    m1 = eval_metrics(y_tgt, y_pred_src)
    m1["experiment"] = "source_only"
    results.append(m1)
    log.info("MAE=%.4f, RMSE=%.4f, ρ=%.3f, sign_acc=%.3f, INVEST_rec=%.3f",
             m1["MAE"], m1["RMSE"], m1["Spearman_rho"], m1["sign_accuracy"],
             m1.get("INVEST_recall", 0))

    # ---- Experiment 2: Target-only LOO-CV ----
    log.info("\n=== Exp 2: Target-only (LOO-CV) ===")
    loo_preds = []
    for i in range(len(target)):
        train_idx = list(range(len(target)))
        train_idx.remove(i)
        train_df = target.iloc[train_idx]
        test_df = target.iloc[[i]]
        X_tr = train_df[used].fillna(-999).values
        y_tr = train_df["adc2_dest_ev"].values
        X_te = test_df[used].fillna(-999).values
        model_loo = XGBRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.1,
            random_state=SEED, n_jobs=-1, verbosity=0,
        )
        model_loo.fit(X_tr, y_tr)
        loo_preds.append(model_loo.predict(X_te)[0])
    loo_preds = np.array(loo_preds)
    m2 = eval_metrics(y_tgt, loo_preds)
    m2["experiment"] = "target_only_loo"
    results.append(m2)
    log.info("MAE=%.4f, RMSE=%.4f, ρ=%.3f, sign_acc=%.3f",
             m2["MAE"], m2["RMSE"], m2["Spearman_rho"], m2["sign_accuracy"])

    # ---- Experiment 3: Source + Target fine-tune (LOO-CV) ----
    log.info("\n=== Exp 3: Source pretrain + Target fine-tune (LOO-CV) ===")
    ft_preds = []
    for i in range(len(target)):
        train_idx = list(range(len(target)))
        train_idx.remove(i)
        train_df = target.iloc[train_idx]
        test_df = target.iloc[[i]]

        # Pretrain on source
        model_ft = XGBRegressor(
            n_estimators=200, max_depth=4, learning_rate=0.1,
            random_state=SEED, n_jobs=-1, verbosity=0,
        )
        model_ft.fit(X_src, y_src)

        # Fine-tune on target (continue training)
        X_ft = train_df[used].fillna(-999).values
        y_ft = train_df["adc2_dest_ev"].values
        model_ft.fit(X_ft, y_ft, xgb_model=model_ft.get_booster())

        X_te = test_df[used].fillna(-999).values
        ft_preds.append(model_ft.predict(X_te)[0])

    ft_preds = np.array(ft_preds)
    m3 = eval_metrics(y_tgt, ft_preds)
    m3["experiment"] = "source_finetune_loo"
    results.append(m3)
    log.info("MAE=%.4f, RMSE=%.4f, ρ=%.3f, sign_acc=%.3f, INVEST_rec=%.3f",
             m3["MAE"], m3["RMSE"], m3["Spearman_rho"], m3["sign_accuracy"],
             m3.get("INVEST_recall", 0))

    # ---- Experiment 4: Delta transfer (LOO-CV) ----
    log.info("\n=== Exp 4: Delta transfer (LOO-CV) ===")
    # Use source model predictions as a feature, train residual on target
    source_pred_on_target = y_pred_src  # from Exp 1
    delta_preds = []
    for i in range(len(target)):
        train_idx = list(range(len(target)))
        train_idx.remove(i)

        # Residual = true - source_pred
        residuals_train = y_tgt[train_idx] - source_pred_on_target[train_idx]

        # Features: original features + source prediction
        X_delta_tr = np.column_stack([
            target.iloc[train_idx][used].fillna(-999).values,
            source_pred_on_target[train_idx].reshape(-1, 1),
        ])
        X_delta_te = np.column_stack([
            target.iloc[[i]][used].fillna(-999).values,
            source_pred_on_target[[i]].reshape(-1, 1),
        ])

        model_delta = XGBRegressor(
            n_estimators=50, max_depth=2, learning_rate=0.1,
            random_state=SEED, n_jobs=-1, verbosity=0,
        )
        model_delta.fit(X_delta_tr, residuals_train)
        delta_pred = model_delta.predict(X_delta_te)[0]
        delta_preds.append(source_pred_on_target[i] + delta_pred)

    delta_preds = np.array(delta_preds)
    m4 = eval_metrics(y_tgt, delta_preds)
    m4["experiment"] = "delta_transfer_loo"
    results.append(m4)
    log.info("MAE=%.4f, RMSE=%.4f, ρ=%.3f, sign_acc=%.3f, INVEST_rec=%.3f",
             m4["MAE"], m4["RMSE"], m4["Spearman_rho"], m4["sign_accuracy"],
             m4.get("INVEST_recall", 0))

    # ---- Summary ----
    results_df = pd.DataFrame(results)
    out_path = os.path.join(proj, "results/tables/source_target_transfer_results.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    results_df.to_csv(out_path, index=False)
    log.info("\n=== TRANSFER RESULTS SUMMARY ===")
    log.info("\n%s", results_df.to_string(index=False))
    log.info("\nSaved to: %s", out_path)

    # Per-molecule predictions
    pred_df = pd.DataFrame({
        "mol_id": target["mol_id"].values[:len(y_tgt)],
        "y_true": y_tgt,
        "source_only": y_pred_src,
        "target_loo": loo_preds,
        "source_finetune_loo": ft_preds,
        "delta_transfer_loo": delta_preds,
    })
    pred_path = os.path.join(proj, "results/tables/transfer_per_molecule_predictions.csv")
    pred_df.to_csv(pred_path, index=False)
    log.info("Per-molecule predictions saved to: %s", pred_path)


if __name__ == "__main__":
    main()
