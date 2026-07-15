#!/usr/bin/env python3
"""P0-a (fixed): Multi-seed ablation with correct feature handling.

Root cause of original ablation failure:
  Physics features (sTDA, KS-OD, DFT) have 0% coverage in Pollice source domain,
  so they were NaN-filtered out → all 6 configs used identical 54 RDKit features.

Fix: Source model always uses shared features (RDKit FP + PCA).
     Delta correction model uses target-domain features INCLUDING physics descriptors.
     Ablation removes physics features from the DELTA model only.

Output: results/round1_eval/p0a_ablation_multiseed.csv  (overwrite)
        results/round1_eval/p0a_ablation_paired_tests.json  (overwrite)
"""

import os, json, warnings
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "results", "round1_eval")
os.makedirs(OUT, exist_ok=True)

N_SEEDS = 10
BASE_SEEDS = [42, 123, 7, 2024, 314, 999, 55, 8080, 1337, 65535]

FEATURE_EXCLUDE = [
    "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
    "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
    "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
    "is_invest", "is_near_zero", "is_high_fosc", "canonical_smiles",
]

STDA_FEATURES = ["stda_s1_ev", "stda_t1_ev", "stda_dest_ev", "stda_fosc"]
KSOD_FEATURES = ["homo_spacing", "lumo_spacing", "od_index"]
DFT_FEATURES = ["dft_dest_raw_ev", "dft_dest_calibrated_ev", "fosc_dft",
                 "homo_ev", "lumo_ev", "hl_gap_ev", "homo_m1_ev", "lumo_p1_ev"]


def run_loo_delta_split(source_df, target_df, shared_feats, delta_feats, seed):
    """LOO delta transfer with SEPARATE feature sets for source and delta models.

    source model: trained on shared_feats (available in both domains)
    delta model:  trained on delta_feats (may include target-only features)
    """
    # XGBoost handles NaN natively — no fillna(-999) which would create spurious splits
    X_src = source_df[shared_feats].values.astype(np.float32)
    y_src = source_df["adc2_dest_ev"].values

    model_src = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        random_state=seed, n_jobs=-1, verbosity=0,
    )
    model_src.fit(X_src, y_src)

    X_tgt_shared = target_df[shared_feats].values.astype(np.float32)
    src_pred = model_src.predict(X_tgt_shared)

    X_tgt_delta = target_df[delta_feats].values.astype(np.float32)
    y_target = target_df["adc2_dest_ev"].values

    n = len(target_df)
    preds = np.zeros(n)
    for i in range(n):
        train_idx = list(range(n))
        train_idx.remove(i)
        residuals = y_target[train_idx] - src_pred[train_idx]

        # Delta features = target features + source prediction
        X_d_tr = np.column_stack([X_tgt_delta[train_idx], src_pred[train_idx].reshape(-1, 1)])
        X_d_te = np.column_stack([X_tgt_delta[[i]], src_pred[[i]].reshape(-1, 1)])

        m = XGBRegressor(n_estimators=50, max_depth=2, learning_rate=0.1,
                         random_state=seed, n_jobs=-1, verbosity=0)
        m.fit(X_d_tr, residuals)
        preds[i] = src_pred[i] + m.predict(X_d_te)[0]

    return preds


# ── Load data ──
model_input = pd.read_csv(os.path.join(ROOT, "data", "processed", "model_input_table.csv"))
master_updated = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

all_feat_cols = [c for c in model_input.columns if c not in FEATURE_EXCLUDE]
feats = model_input[["mol_id"] + all_feat_cols]
df = master_updated.merge(feats, on="mol_id", how="left", suffixes=("", "_feat"))
df = df.drop(columns=[c for c in df.columns if c.endswith("_feat")])

labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
source = labeled[labeled["source_domain"] == "pollice"]

r1_mols = ["Hz_NEt21_NPh22", "Hz_NH22_SO2Ph1", "5AP_NEt2_Ph", "Hz_NEt22_CN1",
            "5AP_NPh2_Me", "5AP_NPh22", "Hz_DMAC1_NPh21_SO2Ph1", "Hz_POZ1_NPh21_SO2Ph1",
            "5AP_NPh2_OMe", "5AP_NMe2_NPh2", "Hz_NEt22_CF31", "Hz_NPh22_CN1",
            "Hz_NMe22_CN1", "Hz_Cz1_NPh21_CF31"]

pre_ids = model_input[(model_input["adc2_available"] == True) &
                       (model_input["source_domain"] != "pollice")].dropna(
    subset=["adc2_dest_ev"])["mol_id"].tolist()
post_ids = list(set(pre_ids + r1_mols))
target = labeled[labeled["mol_id"].isin(post_ids)]
y_tgt = target["adc2_dest_ev"].values

# ── Feature sets ──
# Shared features: available in BOTH source and target (≥10% non-NaN in both)
shared_feats = [c for c in all_feat_cols
                if source[c].notna().mean() >= 0.1
                and target[c].notna().mean() >= 0.1]

# Target-only physics features (available in target but NOT source)
physics_in_target = [c for c in STDA_FEATURES + KSOD_FEATURES + DFT_FEATURES
                     if c in target.columns and target[c].notna().mean() >= 0.1]

print("=" * 70)
print("P0-a (FIXED): Multi-seed Ablation with Split Feature Sets")
print("=" * 70)
print(f"Source: {len(source)}, Target: {len(target)}")
print(f"Shared features (source+target): {len(shared_feats)}")
print(f"Physics features available in target: {physics_in_target}")
print(f"Physics features with ≥10% coverage in target:")
for f in physics_in_target:
    print(f"  {f}: {target[f].notna().mean():.1%}")

# ── Ablation configs (delta model features) ──
# Delta model can use: shared_feats + physics features from target
all_delta_feats = shared_feats + [f for f in physics_in_target if f not in shared_feats]

stda_in_tgt = [f for f in STDA_FEATURES if f in physics_in_target]
ksod_in_tgt = [f for f in KSOD_FEATURES if f in physics_in_target]
dft_in_tgt = [f for f in DFT_FEATURES if f in physics_in_target]

configs = {
    "full": all_delta_feats,
    "no_stda": [c for c in all_delta_feats if c not in STDA_FEATURES],
    "no_ksod": [c for c in all_delta_feats if c not in KSOD_FEATURES],
    "no_stda_no_ksod": [c for c in all_delta_feats if c not in STDA_FEATURES + KSOD_FEATURES],
    "no_dft": [c for c in all_delta_feats if c not in DFT_FEATURES],
    "rdkit_only": shared_feats,  # only features shared with source (= RDKit)
}

for name, feats_list in configs.items():
    n_physics = len([f for f in feats_list if f in STDA_FEATURES + KSOD_FEATURES + DFT_FEATURES])
    print(f"  {name:20s}: {len(feats_list)} features ({n_physics} physics)")

# ── Run all seeds × configs ──
rows = []
config_mae_vectors = {name: [] for name in configs}

for si, seed in enumerate(BASE_SEEDS):
    print(f"\n--- Seed {si+1}/{N_SEEDS}: {seed} ---")
    for name, delta_feats_list in configs.items():
        preds = run_loo_delta_split(source, target, shared_feats, delta_feats_list, seed)
        mae = mean_absolute_error(y_tgt, preds)
        sign_acc = np.mean(np.sign(y_tgt) == np.sign(preds))
        n_inv = (y_tgt < 0).sum()
        inv_rec = ((y_tgt < 0) & (preds < 0)).sum() / max(n_inv, 1)

        rows.append({
            "seed": seed, "config": name,
            "n_delta_features": len(delta_feats_list),
            "n_physics": len([f for f in delta_feats_list if f in STDA_FEATURES + KSOD_FEATURES + DFT_FEATURES]),
            "MAE": mae, "sign_accuracy": sign_acc, "INVEST_recall": inv_rec,
        })
        config_mae_vectors[name].append(mae)
        print(f"  {name:20s}: MAE={mae:.5f}  sign_acc={sign_acc:.1%}  inv_rec={inv_rec:.1%}")

results_df = pd.DataFrame(rows)

# ── Summary ──
print("\n" + "=" * 70)
print("Summary: mean ± std across 10 seeds")
print("=" * 70)

summary = results_df.groupby("config").agg(
    MAE_mean=("MAE", "mean"), MAE_std=("MAE", "std"),
    sign_acc_mean=("sign_accuracy", "mean"), sign_acc_std=("sign_accuracy", "std"),
    INVEST_rec_mean=("INVEST_recall", "mean"), INVEST_rec_std=("INVEST_recall", "std"),
    n_delta_features=("n_delta_features", "first"),
    n_physics=("n_physics", "first"),
).reset_index()

for _, r in summary.iterrows():
    print(f"  {r['config']:20s}: MAE={r['MAE_mean']:.5f}±{r['MAE_std']:.5f}  "
          f"sign_acc={r['sign_acc_mean']:.1%}±{r['sign_acc_std']:.1%}  "
          f"n_feat={int(r['n_delta_features'])} ({int(r['n_physics'])} physics)")

# ── Paired Wilcoxon tests ──
print("\n" + "=" * 70)
print("Paired Wilcoxon signed-rank tests (full vs ablation)")
print("=" * 70)

paired_tests = {}
for name in ["no_stda", "no_ksod", "no_stda_no_ksod", "no_dft", "rdkit_only"]:
    full_maes = np.array(config_mae_vectors["full"])
    abl_maes = np.array(config_mae_vectors[name])
    diff = abl_maes - full_maes  # positive = ablation worse

    if np.all(diff == 0):
        result = {
            "comparison": f"full vs {name}",
            "n_seeds": len(diff),
            "all_identical": True,
            "mean_diff": 0.0,
            "p_value": 1.0,
            "significant_005": False,
            "interpretation": f"Removing features makes ZERO difference (identical across all {len(diff)} seeds)"
        }
        print(f"\n  full vs {name}: ALL IDENTICAL → p=1.0")
    else:
        n_unique = len(np.unique(diff))
        if n_unique == 1:
            # All seeds produce the same non-zero difference → deterministic result
            # Wilcoxon would be inflated (n=1 repeated K times), so report directly
            result = {
                "comparison": f"full vs {name}",
                "n_seeds": len(diff),
                "all_seeds_same_diff": True,
                "deterministic_diff": float(diff[0]),
                "effect_direction": "ablation_worse" if diff[0] > 0 else "ablation_better",
                "p_value": None,
                "significant_005": None,
                "interpretation": (
                    f"LOO-CV is deterministic for this data: removing features "
                    f"{'increases' if diff[0] > 0 else 'decreases'} MAE by "
                    f"{abs(diff[0]):.5f} eV. Wilcoxon not applicable (n_eff=1)."
                )
            }
            print(f"\n  full vs {name}: DETERMINISTIC Δ={diff[0]:+.5f} eV "
                  f"({'ablation worse' if diff[0] > 0 else 'ablation BETTER'})")
            print(f"    Wilcoxon N/A (all seeds identical → n_eff=1)")
        else:
            nonzero = diff[diff != 0]
            if len(nonzero) < 2:
                stat, p = np.nan, 1.0
            else:
                stat, p = wilcoxon(nonzero, alternative='two-sided')

            result = {
                "comparison": f"full vs {name}",
                "n_seeds": len(diff),
                "all_seeds_same_diff": False,
                "mean_diff": float(diff.mean()),
                "std_diff": float(diff.std()),
                "wilcoxon_stat": float(stat) if not np.isnan(stat) else None,
                "p_value": float(p),
                "significant_005": bool(p < 0.05),
                "effect_direction": "ablation_worse" if diff.mean() > 0 else "ablation_better",
                "interpretation": (
                    f"Removing features "
                    f"{'significantly' if p < 0.05 else 'does NOT significantly'} "
                    f"change MAE (Δ={diff.mean():+.5f}±{diff.std():.5f}, p={p:.4f})"
                )
            }
            print(f"\n  full vs {name}:")
            print(f"    ΔMAE: {diff.mean():+.5f}±{diff.std():.5f}, p={p:.4f}")
            print(f"    Direction: {'ablation worse' if diff.mean() > 0 else 'ablation better or same'}")

    paired_tests[name] = result

# ── Diagnosis ──
print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)

n_physics_full = summary[summary["config"] == "full"]["n_physics"].values[0]
if n_physics_full == 0:
    diagnosis = (
        "CRITICAL: No physics features survived NaN filtering even in the target domain. "
        "sTDA features have 0% coverage in target (not computed for these molecules). "
        "KS-OD and DFT features have partial coverage. "
        "The ablation is vacuous because physics features were never available."
    )
elif all(r.get("all_identical", False) for r in paired_tests.values()):
    diagnosis = (
        "Physics features are available but provide ZERO marginal improvement. "
        "XGBoost's internal feature selection completely ignores physics descriptors "
        "when RDKit fingerprints are present. Confirmed across 10 random seeds."
    )
else:
    has_sig = any(r.get("significant_005", False) for r in paired_tests.values())
    if has_sig:
        diagnosis = (
            "Some physics features provide STATISTICALLY SIGNIFICANT improvement. "
            "The ablation reveals which feature groups contribute to delta model performance."
        )
    else:
        diagnosis = (
            "Physics features produce minor numerical differences but NONE reach "
            "statistical significance (p > 0.05). Their contribution is negligible "
            "relative to RDKit fingerprint features."
        )

print(f"  {diagnosis}")

# ── Save ──
results_df.to_csv(os.path.join(OUT, "p0a_ablation_multiseed.csv"), index=False)

output = {
    "n_seeds": N_SEEDS,
    "seeds": BASE_SEEDS,
    "n_configs": len(configs),
    "n_target": len(target),
    "shared_features_n": len(shared_feats),
    "physics_in_target": physics_in_target,
    "summary": summary.to_dict(orient="records"),
    "paired_tests": paired_tests,
    "diagnosis": diagnosis,
    "design_note": (
        "Source model uses shared features (RDKit FP/PCA, available in both domains). "
        "Delta correction model uses target-domain features which MAY include physics descriptors. "
        "Ablation removes physics features from the DELTA model only."
    ),
}

with open(os.path.join(OUT, "p0a_ablation_paired_tests.json"), "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False, default=str)

print(f"\nOutput: {os.path.join(OUT, 'p0a_ablation_multiseed.csv')}")
print(f"        {os.path.join(OUT, 'p0a_ablation_paired_tests.json')}")
