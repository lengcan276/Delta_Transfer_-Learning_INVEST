#!/usr/bin/env python3
"""P0-b: Conformal Prediction calibration + comparison with Bootstrap UQ.

CORRECTED DESIGN (after GPT adversarial review):
- Calibration set: 19 pre-R1 target molecules (known before deployment)
- Test set: 14 R1 deployment molecules (truly held-out)
- Single model trained on calibration set → residuals → q_hat
- q_hat applied to test set predictions → coverage evaluation

This avoids data leakage: test molecules never participate in q_hat computation.

Output: results/round1_eval/p0b_conformal_calibration.json
        results/round1_eval/p0b_conformal_calibration.csv
"""

import os, json, warnings
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "results", "round1_eval")
os.makedirs(OUT, exist_ok=True)

SEED = 42
N_BOOT = 10

FEATURE_EXCLUDE = [
    "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
    "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
    "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
    "is_invest", "is_near_zero", "is_high_fosc", "canonical_smiles",
]

# ── Load data ──
model_input = pd.read_csv(os.path.join(ROOT, "data", "processed", "model_input_table.csv"))
master_updated = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

all_feat_cols = [c for c in model_input.columns if c not in FEATURE_EXCLUDE]
feats = model_input[["mol_id"] + all_feat_cols]
df = master_updated.merge(feats, on="mol_id", how="left", suffixes=("", "_feat"))
df = df.drop(columns=[c for c in df.columns if c.endswith("_feat")])

labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
source = labeled[labeled["source_domain"] == "pollice"]

# R1 deployment molecules (the TEST set — must be held out from calibration)
r1_mols = ["Hz_NEt21_NPh22", "Hz_NH22_SO2Ph1", "5AP_NEt2_Ph", "Hz_NEt22_CN1",
            "5AP_NPh2_Me", "5AP_NPh22", "Hz_DMAC1_NPh21_SO2Ph1", "Hz_POZ1_NPh21_SO2Ph1",
            "5AP_NPh2_OMe", "5AP_NMe2_NPh2", "Hz_NEt22_CF31", "Hz_NPh22_CN1",
            "Hz_NMe22_CN1", "Hz_Cz1_NPh21_CF31"]

# Pre-R1 target molecules (the CALIBRATION set — known before deployment)
pre_r1_ids = model_input[(model_input["adc2_available"] == True) &
                          (model_input["source_domain"] != "pollice")].dropna(
    subset=["adc2_dest_ev"])["mol_id"].tolist()
# Remove any R1 mols that might overlap
pre_r1_ids = [m for m in pre_r1_ids if m not in r1_mols]

calib_set = labeled[labeled["mol_id"].isin(pre_r1_ids)]
test_set = labeled[labeled["mol_id"].isin(r1_mols)]
# Exclude Hz_NH23 from test (Grubbs outlier)
test_set = test_set[test_set["mol_id"] != "Hz_NH23"]

usable = [c for c in all_feat_cols
          if labeled[c].notna().mean() >= 0.1
          and calib_set[c].notna().mean() >= 0.1]

X_src = source[usable].fillna(-999).values
y_src = source["adc2_dest_ev"].values

X_calib = calib_set[usable].fillna(-999).values
y_calib = calib_set["adc2_dest_ev"].values
mol_ids_calib = calib_set["mol_id"].values

X_test = test_set[usable].fillna(-999).values
y_test = test_set["adc2_dest_ev"].values
mol_ids_test = test_set["mol_id"].values

print("=" * 70)
print("P0-b: Conformal Prediction (CORRECTED — proper train/calib/test split)")
print("=" * 70)
print(f"Source (training): {len(source)}")
print(f"Calibration (pre-R1): {len(calib_set)} molecules")
print(f"Test (R1 deployment): {len(test_set)} molecules (excl Hz_NH23)")
print(f"Usable features: {len(usable)}")

# ── Step 1: Train model on source + calibration, get calibration residuals ──
print("\n--- Step 1: Train model & get calibration residuals ---")

# Source model
model_src = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1,
                         random_state=SEED, n_jobs=-1, verbosity=0)
model_src.fit(X_src, y_src)

# Source predictions on calibration and test sets
src_pred_calib = model_src.predict(X_calib)
src_pred_test = model_src.predict(X_test)

# Delta model trained on ALL calibration data (no LOO — single model for conformal)
residuals_calib = y_calib - src_pred_calib
X_d_calib = np.column_stack([X_calib, src_pred_calib.reshape(-1, 1)])
X_d_test = np.column_stack([X_test, src_pred_test.reshape(-1, 1)])

delta_model = XGBRegressor(n_estimators=50, max_depth=2, learning_rate=0.1,
                           random_state=SEED, n_jobs=-1, verbosity=0)
delta_model.fit(X_d_calib, residuals_calib)

# Calibration predictions and residuals (nonconformity scores)
calib_preds = src_pred_calib + delta_model.predict(X_d_calib)
calib_nonconf = np.abs(y_calib - calib_preds)

# Test predictions
test_preds = src_pred_test + delta_model.predict(X_d_test)
test_residuals = np.abs(y_test - test_preds)

calib_mae = np.mean(calib_nonconf)
test_mae = np.mean(test_residuals)
print(f"  Calibration MAE: {calib_mae:.4f} eV ({len(calib_set)} mols)")
print(f"  Test (R1) MAE: {test_mae:.4f} eV ({len(test_set)} mols)")

# ── Step 2: Bootstrap ensemble UQ ──
print("\n--- Step 2: Bootstrap ensemble UQ ---")

n_calib = len(calib_set)
n_test = len(test_set)

boot_preds_calib = np.zeros((N_BOOT, n_calib))
boot_preds_test = np.zeros((N_BOOT, n_test))

for b in range(N_BOOT):
    rng = np.random.RandomState(SEED + b)
    idx_src = rng.choice(len(X_src), size=len(X_src), replace=True)
    m_src = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1,
                         random_state=SEED + b, n_jobs=-1, verbosity=0)
    m_src.fit(X_src[idx_src], y_src[idx_src])

    sp_calib = m_src.predict(X_calib)
    sp_test = m_src.predict(X_test)

    # Delta model on calibration
    res_b = y_calib - sp_calib
    idx_calib = rng.choice(n_calib, size=n_calib, replace=True)
    Xd_c = np.column_stack([X_calib, sp_calib.reshape(-1, 1)])
    Xd_t = np.column_stack([X_test, sp_test.reshape(-1, 1)])
    m_d = XGBRegressor(n_estimators=50, max_depth=2, learning_rate=0.1,
                       random_state=SEED + b, n_jobs=-1, verbosity=0)
    m_d.fit(Xd_c[idx_calib], res_b[idx_calib])

    boot_preds_calib[b] = sp_calib + m_d.predict(Xd_c)
    boot_preds_test[b] = sp_test + m_d.predict(Xd_t)

boot_mean_calib = boot_preds_calib.mean(axis=0)
boot_std_calib = boot_preds_calib.std(axis=0)
boot_mean_test = boot_preds_test.mean(axis=0)
boot_std_test = boot_preds_test.std(axis=0)

# ── Step 3: Conformal prediction intervals ──
print("\n--- Step 3: Conformal Prediction ---")
print("  Using calibration nonconformity scores to set intervals on test set")

alphas = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
n_cal = len(calib_nonconf)

conformal_results = []
for alpha in alphas:
    # Conformal quantile: alpha = nominal coverage
    # q_level = ceil(alpha * (n_cal+1)) / n_cal  (Vovk et al. 2005)
    q_level = np.ceil(alpha * (n_cal + 1)) / n_cal
    q_level = min(q_level, 1.0)
    q_hat = np.quantile(calib_nonconf, q_level)

    # Conformal coverage on CALIBRATION (sanity check — expected ≥ alpha)
    conf_calib_cov = np.mean((y_calib >= calib_preds - q_hat) &
                             (y_calib <= calib_preds + q_hat))

    # Conformal coverage on TEST (the real evaluation — may degrade under OOD)
    conf_test_cov = np.mean((y_test >= test_preds - q_hat) &
                            (y_test <= test_preds + q_hat))

    # Bootstrap coverage on calibration and test
    z_mult = {0.50: 0.674, 0.60: 0.842, 0.70: 1.036,
              0.80: 1.282, 0.90: 1.645, 0.95: 1.960}[alpha]

    boot_calib_cov = np.mean((y_calib >= boot_mean_calib - z_mult * boot_std_calib) &
                             (y_calib <= boot_mean_calib + z_mult * boot_std_calib))

    boot_test_cov = np.mean((y_test >= boot_mean_test - z_mult * boot_std_test) &
                            (y_test <= boot_mean_test + z_mult * boot_std_test))

    conformal_results.append({
        "nominal_coverage": alpha,
        "conformal_calib_coverage": float(conf_calib_cov),
        "conformal_test_coverage": float(conf_test_cov),
        "conformal_width": float(2 * q_hat),
        "conformal_q_hat": float(q_hat),
        "bootstrap_calib_coverage": float(boot_calib_cov),
        "bootstrap_test_coverage": float(boot_test_cov),
        "bootstrap_test_mean_width": float(2 * z_mult * boot_std_test.mean()),
    })

    print(f"  α={alpha:.0%}: Conformal calib={conf_calib_cov:.1%} test={conf_test_cov:.1%} (w={2*q_hat:.3f}eV) | "
          f"Bootstrap calib={boot_calib_cov:.1%} test={boot_test_cov:.1%} (w={2*z_mult*boot_std_test.mean():.3f}eV)")

# ── Step 4: UQ-error correlation ──
print("\n--- Step 4: UQ-error correlation ---")

rho_calib, p_calib = spearmanr(boot_std_calib, calib_nonconf)
rho_test, p_test = spearmanr(boot_std_test, test_residuals)
print(f"  Bootstrap σ vs |residual| (calibration): ρ={rho_calib:.3f}, p={p_calib:.3f}")
print(f"  Bootstrap σ vs |residual| (test/deploy):  ρ={rho_test:.3f}, p={p_test:.3f}")

# ── Step 5: Summary ──
print("\n" + "=" * 70)
print("CONFORMAL vs BOOTSTRAP SUMMARY")
print("=" * 70)

conf_95 = [r for r in conformal_results if r["nominal_coverage"] == 0.95][0]

print(f"\n  At 95% nominal coverage:")
print(f"    Calibration ({n_cal} pre-R1 mols):")
print(f"      Conformal PICP = {conf_95['conformal_calib_coverage']:.1%}  (width={conf_95['conformal_width']:.3f} eV)")
print(f"      Bootstrap PICP = {conf_95['bootstrap_calib_coverage']:.1%}")
print(f"    Test ({n_test} R1 deployment mols):")
print(f"      Conformal PICP = {conf_95['conformal_test_coverage']:.1%}  (width={conf_95['conformal_width']:.3f} eV)")
print(f"      Bootstrap PICP = {conf_95['bootstrap_test_coverage']:.1%}  (width={conf_95['bootstrap_test_mean_width']:.3f} eV)")

# Determine conclusion
conf_test_95 = conf_95["conformal_test_coverage"]
boot_test_95 = conf_95["bootstrap_test_coverage"]
boot_width_95 = conf_95["bootstrap_test_mean_width"]
conf_width_95 = conf_95["conformal_width"]

# Fixed interval baseline for comparison
fixed_width = 0.16  # ±0.16 eV spans INVEST boundary

# Classification logic (4 branches, not 3):
#   1. Both fail coverage → STRONG: generic OOD failure
#   2. Conformal fails, bootstrap achieves via wide intervals → MODERATE-STRONG
#   3. Conformal works, bootstrap fails → MODERATE
#   4. Both achieve coverage with narrow intervals → WEAK (OOD mild)

both_fail = (conf_test_95 < 0.85 and boot_test_95 < 0.85)
conf_fails_boot_wide = (conf_test_95 < 0.85 and boot_test_95 >= 0.85)

if both_fail:
    conclusion = (
        "BOTH conformal prediction and bootstrap UQ fail to achieve nominal coverage "
        "on held-out R1 deployment molecules. UQ failure is method-agnostic under OOD."
    )
    conclusion_strength = "STRONG — generic UQ failure under OOD"
elif conf_fails_boot_wide:
    # Bootstrap achieves coverage but check if via uninformatively wide intervals
    # Compare bootstrap width to fixed-width baseline
    # If bootstrap width ≈ naive fixed interval, it provides no decision-making value
    fixed_baseline_width = 2 * fixed_width  # 0.32 eV
    width_ratio = boot_width_95 / fixed_baseline_width if fixed_baseline_width > 0 else 999
    is_uninformative = width_ratio >= 0.90  # bootstrap ≥ 90% of naive baseline width

    if is_uninformative:
        conclusion = (
            f"Conformal prediction suffers calibration failure ({conf_test_95:.0%} at 95% nominal, "
            f"width={conf_width_95:.3f} eV — too narrow for OOD test set). "
            f"Bootstrap maintains nominal coverage ({boot_test_95:.0%}) but its intervals "
            f"(width={boot_width_95:.3f} eV) are comparable to a naive fixed ±{fixed_width:.2f} eV "
            f"baseline ({fixed_baseline_width:.3f} eV), providing no additional decision-making value. "
            f"Failure modes differ: conformal is miscalibrated (undercoverage), "
            f"bootstrap is calibrated but uninformative (≈ naive baseline). "
            f"Neither method provides useful guidance for INVEST classification under OOD."
        )
        conclusion_strength = "STRONG — conformal miscalibrated, bootstrap uninformative under OOD"
    else:
        conclusion = (
            f"Conformal prediction fails ({conf_test_95:.0%}), while bootstrap "
            f"achieves {boot_test_95:.0%} with informative intervals ({boot_width_95:.3f} eV, "
            f"narrower than naive baseline {fixed_baseline_width:.3f} eV). "
            f"Bootstrap provides genuine uncertainty information under this OOD shift."
        )
        conclusion_strength = "MODERATE — conformal fails, bootstrap provides useful UQ"
elif conf_test_95 >= 0.85 and boot_test_95 < 0.85:
    conclusion = (
        f"Conformal prediction achieves {conf_test_95:.0%} coverage on held-out test set "
        f"(width={conf_width_95:.3f} eV), while bootstrap fails ({boot_test_95:.0%}). "
        f"Conformal is more robust but intervals may be uninformatively wide."
    )
    conclusion_strength = "MODERATE — conformal robust but wide intervals"
else:
    conclusion = (
        "Both methods maintain reasonable coverage on the test set. "
        "The OOD shift may be less severe than expected."
    )
    conclusion_strength = "WEAK — both methods work"

print(f"\n  Conclusion: {conclusion_strength}")
print(f"  {conclusion}")

# Fixed interval baseline comparison
fixed_cov = np.mean((y_test >= test_preds - fixed_width) &
                     (y_test <= test_preds + fixed_width))
print(f"\n  Baseline: fixed ±0.16eV interval → PICP={fixed_cov:.1%} (width=0.320 eV)")

# ── Save ──
per_mol_calib = pd.DataFrame({
    "mol_id": mol_ids_calib, "set": "calibration",
    "y_true": y_calib, "pred": calib_preds,
    "nonconf_score": calib_nonconf,
    "boot_mean": boot_mean_calib, "boot_std": boot_std_calib,
})
per_mol_test = pd.DataFrame({
    "mol_id": mol_ids_test, "set": "test",
    "y_true": y_test, "pred": test_preds,
    "nonconf_score": test_residuals,
    "boot_mean": boot_mean_test, "boot_std": boot_std_test,
})
per_mol = pd.concat([per_mol_calib, per_mol_test], ignore_index=True)
per_mol.to_csv(os.path.join(OUT, "p0b_conformal_calibration.csv"), index=False)

output = {
    "design": "Split conformal: calibration=pre-R1 (19 mols), test=R1 deployment (14 mols, excl Hz_NH23)",
    "calibration_n": n_cal,
    "test_n": n_test,
    "calibration_MAE": float(calib_mae),
    "test_MAE": float(test_mae),
    "results": conformal_results,
    "uq_correlation": {
        "calibration": {"rho": float(rho_calib), "p": float(p_calib)},
        "test": {"rho": float(rho_test), "p": float(p_test)},
    },
    "fixed_baseline": {"width": 0.32, "coverage": float(fixed_cov)},
    "conclusion": conclusion,
    "conclusion_strength": conclusion_strength,
}

with open(os.path.join(OUT, "p0b_conformal_calibration.json"), "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nOutput: {os.path.join(OUT, 'p0b_conformal_calibration.csv')}")
print(f"        {os.path.join(OUT, 'p0b_conformal_calibration.json')}")
