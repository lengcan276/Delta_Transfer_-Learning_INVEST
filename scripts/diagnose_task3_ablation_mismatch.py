#!/usr/bin/env python3
"""Diagnose the mismatch between task3_ablation_results.csv and p0a_ablation_multiseed.csv.

This script reconstructs the legacy Task-3 ablation logic implemented in
`/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py`:
1. Build nominal ablation configs from RDKit + sTDA + KS-OD + DFT feature names.
2. Re-filter every config by requiring >=10% non-NaN coverage in BOTH source and target.
3. Train the source model and delta model on the surviving shared features only.

That logic reproduces the stale task3 file exactly and shows why all six configs collapse
to the same 54-feature RDKit subset even though the reported nominal feature counts differ.

Outputs:
  results/round1_eval/task3_ablation_root_cause.json
  results/round1_eval/task3_ablation_root_cause.md
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR = os.path.join(ROOT, "results", "round1_eval")
os.makedirs(OUT_DIR, exist_ok=True)

FEATURE_EXCLUDE = [
    "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
    "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
    "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
    "is_invest", "is_near_zero", "is_high_fosc", "canonical_smiles",
]

STDA_FEATURES = ["stda_s1_ev", "stda_t1_ev", "stda_dest_ev", "stda_fosc"]
KSOD_FEATURES = ["homo_spacing", "lumo_spacing", "od_index"]
DFT_FEATURES = [
    "dft_dest_raw_ev", "dft_dest_calibrated_ev", "fosc_dft",
    "homo_ev", "lumo_ev", "hl_gap_ev", "homo_m1_ev", "lumo_p1_ev",
]
PHYSICS_FEATURES = STDA_FEATURES + KSOD_FEATURES + DFT_FEATURES
SEED = 42


def eval_metrics(y_true, y_pred):
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "sign_accuracy": float(np.mean(np.sign(y_true) == np.sign(y_pred))),
        "INVEST_recall": float(((y_true < 0) & (y_pred < 0)).sum() / max((y_true < 0).sum(), 1)),
    }


def legacy_delta_loo(source_df, target_df, usable_feats):
    X_src = source_df[usable_feats].fillna(-999).values
    y_src = source_df["adc2_dest_ev"].values
    X_tgt = target_df[usable_feats].fillna(-999).values
    y_tgt = target_df["adc2_dest_ev"].values

    src_model = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        random_state=SEED, n_jobs=-1, verbosity=0,
    )
    src_model.fit(X_src, y_src)
    src_pred = src_model.predict(X_tgt)

    preds = np.zeros(len(target_df))
    for i in range(len(target_df)):
        train_idx = [j for j in range(len(target_df)) if j != i]
        residuals = y_tgt[train_idx] - src_pred[train_idx]
        X_d_tr = np.column_stack([X_tgt[train_idx], src_pred[train_idx].reshape(-1, 1)])
        X_d_te = np.column_stack([X_tgt[[i]], src_pred[[i]].reshape(-1, 1)])
        delta_model = XGBRegressor(
            n_estimators=50, max_depth=2, learning_rate=0.1,
            random_state=SEED, n_jobs=-1, verbosity=0,
        )
        delta_model.fit(X_d_tr, residuals)
        preds[i] = src_pred[i] + delta_model.predict(X_d_te)[0]
    return preds


def main():
    model_input = pd.read_csv(os.path.join(ROOT, "data", "processed", "model_input_table.csv"))
    master_updated = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

    all_feat_cols = [c for c in model_input.columns if c not in FEATURE_EXCLUDE]
    feats = model_input[["mol_id"] + all_feat_cols]
    df = master_updated.merge(feats, on="mol_id", how="left", suffixes=("", "_dup"))
    df = df.drop(columns=[c for c in df.columns if c.endswith("_dup")])

    labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
    source = labeled[labeled["source_domain"] == "pollice"].copy()

    r1_mols = [
        "Hz_NEt21_NPh22", "Hz_NH22_SO2Ph1", "5AP_NEt2_Ph", "Hz_NEt22_CN1",
        "5AP_NPh2_Me", "5AP_NPh22", "Hz_DMAC1_NPh21_SO2Ph1", "Hz_POZ1_NPh21_SO2Ph1",
        "5AP_NPh2_OMe", "5AP_NMe2_NPh2", "Hz_NEt22_CF31", "Hz_NPh22_CN1",
        "Hz_NMe22_CN1", "Hz_Cz1_NPh21_CF31",
    ]
    pre_ids = model_input[
        (model_input["adc2_available"] == True) &
        (model_input["source_domain"] != "pollice")
    ].dropna(subset=["adc2_dest_ev"])["mol_id"].tolist()
    post_ids = list(set(pre_ids + r1_mols))
    target = labeled[labeled["mol_id"].isin(post_ids)].copy().reset_index(drop=True)

    rdkit_shared = [c for c in all_feat_cols if c not in PHYSICS_FEATURES]
    full_nominal = rdkit_shared + [c for c in PHYSICS_FEATURES if c in df.columns]
    configs = {
        "full": full_nominal,
        "no_stda": [c for c in full_nominal if c not in STDA_FEATURES],
        "no_ksod": [c for c in full_nominal if c not in KSOD_FEATURES],
        "no_stda_no_ksod": [c for c in full_nominal if c not in STDA_FEATURES + KSOD_FEATURES],
        "no_dft": [c for c in full_nominal if c not in DFT_FEATURES],
        "rdkit_only": rdkit_shared,
    }

    task3 = pd.read_csv(os.path.join(OUT_DIR, "task3_ablation_results.csv"))
    p0a = pd.read_csv(os.path.join(OUT_DIR, "p0a_ablation_multiseed.csv"))
    p0a_summary = p0a.groupby("config").agg(
        MAE=("MAE", "mean"),
        sign_accuracy=("sign_accuracy", "mean"),
        INVEST_recall=("INVEST_recall", "mean"),
        n_delta_features=("n_delta_features", "first"),
    ).reset_index()

    source_cov = {
        feat: float(source[feat].notna().mean())
        for feat in PHYSICS_FEATURES if feat in source.columns
    }
    target_cov = {
        feat: float(target[feat].notna().mean())
        for feat in PHYSICS_FEATURES if feat in target.columns
    }

    reconstructed = []
    for name, nominal_feats in configs.items():
        nominal_feats = [c for c in nominal_feats if c in df.columns]
        usable_feats = [
            c for c in nominal_feats
            if source[c].notna().mean() >= 0.1 and target[c].notna().mean() >= 0.1
        ]
        preds = legacy_delta_loo(source, target, usable_feats)
        metrics = eval_metrics(target["adc2_dest_ev"].values, preds)
        reconstructed.append({
            "config": name,
            "nominal_feature_count": len(nominal_feats),
            "usable_feature_count_after_legacy_filter": len(usable_feats),
            "usable_feature_preview": usable_feats[:8],
            **metrics,
        })

    recon_df = pd.DataFrame(reconstructed)
    merged = recon_df.merge(task3, on="config", suffixes=("_reconstructed", "_task3"))
    merged["task3_matches_reconstruction"] = (
        np.isclose(merged["MAE_reconstructed"], merged["MAE_task3"]) &
        np.isclose(merged["RMSE_reconstructed"], merged["RMSE_task3"]) &
        np.isclose(merged["sign_accuracy_reconstructed"], merged["sign_accuracy_task3"]) &
        np.isclose(merged["INVEST_recall_reconstructed"], merged["INVEST_recall_task3"])
    )

    report = {
        "tracked_generator_script_for_task3_exists": True,
        "tracked_generator_script_path": "/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py",
        "git_history_note": (
            "task3_ablation_results.csv appears in the older /home/nudt_cleng/2026/project "
            "workflow and is generated by project/scripts/task3_ablation_study.py, not by the "
            "current github_upload script set."
        ),
        "input_data_files": [
            "data/processed/model_input_table.csv",
            "data/processed/master_molecule_table_round1_updated.csv",
        ],
        "legacy_logic_root_cause": (
            "The legacy task3 workflow counts physics features when naming "
            "ablation configs, but then re-filters features by requiring >=10% coverage in "
            "both source and target. Because all physics descriptors have 0% coverage in the "
            "Pollice source rows, every config collapses to the same 54-feature RDKit subset."
        ),
        "physics_feature_coverage": {
            feat: {"source_non_nan_fraction": source_cov[feat], "target_non_nan_fraction": target_cov[feat]}
            for feat in source_cov
        },
        "reconstructed_task3": reconstructed,
        "task3_exact_match_all_configs": bool(merged["task3_matches_reconstruction"].all()),
        "p0a_summary": p0a_summary.to_dict(orient="records"),
    }

    json_path = os.path.join(OUT_DIR, "task3_ablation_root_cause.json")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    md_lines = [
        "# Task3 Ablation Root Cause",
        "",
        "## Verdict",
        "",
        "- `results/round1_eval/task3_ablation_results.csv` is a stale legacy output.",
        "- Its generator script is the older `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py` workflow, not the current `github_upload` script set.",
        "- The file is exactly reproducible from the current data by a legacy logic that re-filters every ablation config against source-domain coverage, which removes all physics descriptors and leaves the same 54 RDKit features for all six configs.",
        "",
        "## Source Code Origin",
        "",
        "- Tracked current script: `scripts/p0a_ablation_fixed.py`",
        "- Legacy generator script: `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py`",
        "- Exact legacy code pattern: `run_loo_delta()` inside `task3_ablation_study.py` applies a shared `usable_features` filter of the form `source[c].notna().mean() >= 0.1 and target[c].notna().mean() >= 0.1` before both the source and delta models are built.",
        "",
        "## Data Files Driving the Bug",
        "",
        "- `data/processed/model_input_table.csv`",
        "- `data/processed/master_molecule_table_round1_updated.csv`",
        "",
        "## Coverage Pattern That Triggers the Collapse",
        "",
    ]
    for feat in PHYSICS_FEATURES:
        if feat in source_cov:
            md_lines.append(
                f"- `{feat}`: source coverage = {source_cov[feat]:.1%}, target coverage = {target_cov[feat]:.1%}"
            )
    md_lines.extend([
        "",
        "## Reconstruction",
        "",
        "| Config | Nominal count | Usable after legacy filter | Reconstructed MAE | task3 MAE | Match |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for _, row in merged.iterrows():
        md_lines.append(
            f"| `{row['config']}` | {int(row['nominal_feature_count'])} | "
            f"{int(row['usable_feature_count_after_legacy_filter'])} | "
            f"{row['MAE_reconstructed']:.12f} | {row['MAE_task3']:.12f} | "
            f"{'Yes' if row['task3_matches_reconstruction'] else 'No'} |"
        )
    md_lines.extend([
        "",
        "## Why p0a Differs",
        "",
        "- `scripts/p0a_ablation_fixed.py` keeps the source model on shared RDKit features but lets the delta model use target-domain physics features directly.",
        "- Therefore `p0a` does not discard KS-OD and DFT features just because source rows lack them.",
        "- That is why `p0a_ablation_multiseed.csv` shows real differences across configs while `task3_ablation_results.csv` does not.",
    ])

    md_path = os.path.join(OUT_DIR, "task3_ablation_root_cause.md")
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(md_lines) + "\n")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Exact reconstruction match: {report['task3_exact_match_all_configs']}")


if __name__ == "__main__":
    main()
