#!/usr/bin/env python3
"""Active learning round 1: select 16 molecules for ADC(2) computation.

Selection strategy (16 molecules):
  - 5 highest uncertainty
  - 5 predicted near-zero ΔEST
  - 4 predicted high fosc + small |ΔEST|
  - 2 structural outliers

Usage:
    python scripts/run_active_learning_round1.py [--project-root PROJECT_ROOT] [--n-select N]
"""
import argparse
import logging
import os
import warnings

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.ensemble import RandomForestRegressor
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
    p.add_argument("--n-select", type=int, default=16)
    return p.parse_args()


def get_feature_cols(df):
    return [c for c in df.columns if c not in FEATURE_PREFIX_EXCLUDE]


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    df = pd.read_csv(os.path.join(proj, "data/processed/model_input_table.csv"))

    feat_cols = get_feature_cols(df)
    labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
    unlabeled = df[
        (df["adc2_available"] == False) &
        (df["source_domain"] == "this_work")
    ].copy()

    log.info("Labeled: %d, Unlabeled pool (this-work): %d", len(labeled), len(unlabeled))

    if len(unlabeled) == 0:
        log.warning("No unlabeled this-work molecules. Exiting.")
        return

    # Use features available for all molecules (RDKit-based)
    usable = [c for c in feat_cols if labeled[c].notna().mean() >= 0.5
              and unlabeled[c].notna().mean() >= 0.5]
    log.info("Usable features: %d / %d", len(usable), len(feat_cols))

    X_labeled = labeled[usable].fillna(-999).values
    y_labeled = labeled["adc2_dest_ev"].values
    X_unlabeled = unlabeled[usable].fillna(-999).values

    # --- Train ensemble for predictions and uncertainty ---
    n_models = 10
    predictions = np.zeros((n_models, len(X_unlabeled)))

    for i in range(n_models):
        # Bootstrap ensemble
        rng = np.random.RandomState(SEED + i)
        idx = rng.choice(len(X_labeled), size=len(X_labeled), replace=True)
        model = XGBRegressor(
            n_estimators=150, max_depth=4, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            random_state=SEED + i, n_jobs=-1, verbosity=0,
        )
        model.fit(X_labeled[idx], y_labeled[idx])
        predictions[i] = model.predict(X_unlabeled)

    pred_mean = predictions.mean(axis=0)
    pred_std = predictions.std(axis=0)

    unlabeled = unlabeled.copy()
    unlabeled["predicted_dest_ev"] = pred_mean
    unlabeled["uncertainty_score"] = pred_std

    # Predicted probabilities (from sign of prediction + uncertainty)
    # P(INVEST) ≈ P(ΔEST < 0) using Gaussian approximation
    from scipy.stats import norm
    unlabeled["predicted_invest_prob"] = norm.cdf(0, loc=pred_mean, scale=np.maximum(pred_std, 1e-6))
    unlabeled["predicted_near_zero_prob"] = (
        norm.cdf(0.10, loc=np.abs(pred_mean), scale=np.maximum(pred_std, 1e-6)) -
        norm.cdf(0, loc=np.abs(pred_mean), scale=np.maximum(pred_std, 1e-6))
    )

    # --- Diversity score (distance to labeled set in feature space) ---
    dists = cdist(X_unlabeled, X_labeled, metric="euclidean")
    unlabeled["diversity_score"] = dists.min(axis=1)  # distance to nearest labeled

    # --- fosc proxy (use DFT fosc if available) ---
    if "fosc_dft" in unlabeled.columns:
        unlabeled["fosc_proxy"] = unlabeled["fosc_dft"].fillna(0)
    else:
        unlabeled["fosc_proxy"] = 0

    # --- Selection ---
    n_select = min(args.n_select, len(unlabeled))
    n_uncertainty = 5
    n_near_zero = 5
    n_high_fosc = 4
    n_outlier = 2

    # Adjust if total exceeds pool
    total_want = n_uncertainty + n_near_zero + n_high_fosc + n_outlier
    if total_want > n_select:
        scale = n_select / total_want
        n_uncertainty = max(1, int(n_uncertainty * scale))
        n_near_zero = max(1, int(n_near_zero * scale))
        n_high_fosc = max(1, int(n_high_fosc * scale))
        n_outlier = max(1, n_select - n_uncertainty - n_near_zero - n_high_fosc)

    selected_ids = set()

    # Bucket 1: Highest uncertainty
    candidates = unlabeled.sort_values("uncertainty_score", ascending=False)
    for _, row in candidates.iterrows():
        if len(selected_ids) >= n_uncertainty:
            break
        if row["mol_id"] not in selected_ids:
            selected_ids.add(row["mol_id"])

    # Bucket 2: Predicted near-zero (|pred_ΔEST| closest to 0)
    candidates = unlabeled.copy()
    candidates["abs_pred"] = np.abs(candidates["predicted_dest_ev"])
    candidates = candidates.sort_values("abs_pred")
    for _, row in candidates.iterrows():
        if len(selected_ids) >= n_uncertainty + n_near_zero:
            break
        if row["mol_id"] not in selected_ids:
            selected_ids.add(row["mol_id"])

    # Bucket 3: High fosc + small gap
    candidates = unlabeled.copy()
    candidates["fosc_gap_score"] = candidates["fosc_proxy"] / (np.abs(candidates["predicted_dest_ev"]) + 0.01)
    candidates = candidates.sort_values("fosc_gap_score", ascending=False)
    for _, row in candidates.iterrows():
        if len(selected_ids) >= n_uncertainty + n_near_zero + n_high_fosc:
            break
        if row["mol_id"] not in selected_ids:
            selected_ids.add(row["mol_id"])

    # Bucket 4: Structural outliers (farthest from labeled)
    candidates = unlabeled.sort_values("diversity_score", ascending=False)
    for _, row in candidates.iterrows():
        if len(selected_ids) >= n_select:
            break
        if row["mol_id"] not in selected_ids:
            selected_ids.add(row["mol_id"])

    # Build output with bucket assignment
    def get_bucket(mol_id):
        # Re-derive bucket membership
        order_unc = unlabeled.sort_values("uncertainty_score", ascending=False)["mol_id"].tolist()
        order_nz = unlabeled.assign(abs_pred=np.abs(unlabeled["predicted_dest_ev"])).sort_values("abs_pred")["mol_id"].tolist()
        fosc_gap = unlabeled["fosc_proxy"] / (np.abs(unlabeled["predicted_dest_ev"]) + 0.01)
        order_fosc = unlabeled.assign(fgs=fosc_gap).sort_values("fgs", ascending=False)["mol_id"].tolist()
        order_div = unlabeled.sort_values("diversity_score", ascending=False)["mol_id"].tolist()

        seen = set()
        for mid in order_unc[:n_uncertainty]:
            if mid == mol_id and mid not in seen:
                return "uncertainty"
            seen.add(mid)
        for mid in order_nz:
            if len(seen) >= n_uncertainty + n_near_zero:
                break
            if mid not in seen:
                if mid == mol_id:
                    return "near_zero"
                seen.add(mid)
        for mid in order_fosc:
            if len(seen) >= n_uncertainty + n_near_zero + n_high_fosc:
                break
            if mid not in seen:
                if mid == mol_id:
                    return "high_fosc"
                seen.add(mid)
        return "outlier"

    selected_df = unlabeled[unlabeled["mol_id"].isin(selected_ids)].copy()
    selected_df["selection_bucket"] = selected_df["mol_id"].apply(get_bucket)

    # Acquisition score (composite)
    selected_df["acquisition_score"] = (
        0.3 * (selected_df["uncertainty_score"] / selected_df["uncertainty_score"].max()) +
        0.3 * selected_df["predicted_near_zero_prob"] +
        0.2 * (selected_df["fosc_proxy"] / max(selected_df["fosc_proxy"].max(), 1e-6)) +
        0.2 * (selected_df["diversity_score"] / selected_df["diversity_score"].max())
    )

    # Output columns
    out_cols = [
        "mol_id", "smiles", "scaffold_family",
        "predicted_dest_ev", "predicted_invest_prob", "predicted_near_zero_prob",
        "uncertainty_score", "diversity_score", "fosc_proxy",
        "acquisition_score", "selection_bucket",
    ]
    out_cols = [c for c in out_cols if c in selected_df.columns]
    result = selected_df[out_cols].sort_values("acquisition_score", ascending=False)

    out_path = os.path.join(proj, "results/tables/ranked_candidates_round1.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.to_csv(out_path, index=False)

    log.info("\n=== ACTIVE LEARNING ROUND 1 ===")
    log.info("Selected %d molecules from %d unlabeled pool", len(result), len(unlabeled))
    log.info("\nBucket distribution:")
    log.info("%s", result["selection_bucket"].value_counts().to_string())
    log.info("\nTop candidates:")
    log.info("\n%s", result[["mol_id", "predicted_dest_ev", "uncertainty_score",
                             "selection_bucket", "acquisition_score"]].to_string(index=False))
    log.info("\nSaved to: %s", out_path)


if __name__ == "__main__":
    main()
