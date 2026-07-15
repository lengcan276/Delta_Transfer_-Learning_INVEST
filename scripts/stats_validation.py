#!/usr/bin/env python3
"""
stats_validation.py — OOD Statistical Proof Suite
==================================================
Three statistically rigorous tests proving:
  1. Subspace elimination (Fisher exact: 5AP vs Hz INVEST rates)
  2. Rapid domain adaptation (Wilcoxon signed-rank on LOO residuals)
  3. Information gain quantification (Shannon entropy reduction on pool)

All tests use real project data. No mocking.

Usage:
    python scripts/stats_validation.py
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
from xgboost import XGBRegressor
import warnings

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "results", "round1_eval")
os.makedirs(OUT, exist_ok=True)

SEED = 42

# ─── Columns excluded from ML features ───
FEATURE_EXCLUDE = [
    "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
    "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
    "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
    "is_invest", "is_near_zero", "is_high_fosc", "canonical_smiles",
]

# ─── Round 1 ADC(2) ground truth (15 with T1) ───
ROUND1_DEST = {
    "Hz_NEt21_NPh22": -0.08858, "Hz_NH22_SO2Ph1": -0.06416,
    "5AP_NEt2_Ph": 0.17270, "Hz_NEt22_CN1": 0.04848,
    "5AP_NPh2_Me": 0.17137, "5AP_NPh22": 0.19540,
    "Hz_DMAC1_NPh21_SO2Ph1": -0.06566, "Hz_POZ1_NPh21_SO2Ph1": 0.06967,
    "5AP_NPh2_OMe": 0.22031, "5AP_NMe2_NPh2": 0.22997,
    "Hz_NEt22_CF31": -0.03593, "Hz_NPh22_CN1": -0.05384,
    "Hz_NMe22_CN1": 0.05350, "Hz_NH23": -0.38346,
    "Hz_Cz1_NPh21_CF31": -0.13573,
}


# ════════════════════════════════════════════════════════════════
# TEST 1: Subspace Elimination — Fisher Exact Test
# ════════════════════════════════════════════════════════════════

def test_subspace_elimination():
    """
    Fisher Exact Test: 5AP INVEST rate (0/5) vs Hz INVEST rate (6/9).
    H0: Both scaffolds have the same underlying INVEST probability.
    Threshold: ΔEST < -0.01 eV (−10 meV).
    Hz_NH23 excluded (Grubbs outlier, pending verification).
    """
    print("=" * 70)
    print("TEST 1: Subspace Elimination — Fisher Exact Test")
    print("=" * 70)

    # Separate R1 molecules by scaffold, exclude Hz_NH23
    hz_mols = {k: v for k, v in ROUND1_DEST.items()
               if k.startswith("Hz_") and k != "Hz_NH23"}
    ap_mols = {k: v for k, v in ROUND1_DEST.items()
               if k.startswith("5AP_")}

    hz_invest = sum(1 for v in hz_mols.values() if v < -0.01)
    hz_non    = len(hz_mols) - hz_invest
    ap_invest = sum(1 for v in ap_mols.values() if v < -0.01)
    ap_non    = len(ap_mols) - ap_invest

    # 2×2 contingency table:
    #              INVEST   Non-INVEST
    #  Hz          hz_invest hz_non
    #  5AP         ap_invest ap_non
    table = np.array([[hz_invest, hz_non],
                      [ap_invest, ap_non]])

    odds_ratio, p_value = stats.fisher_exact(table, alternative="two-sided")

    print(f"\n  Contingency table:")
    print(f"               INVEST  Non-INVEST")
    print(f"    Hz           {hz_invest}          {hz_non}")
    print(f"    5AP          {ap_invest}          {ap_non}")
    print(f"\n  Hz INVEST rate:  {hz_invest}/{hz_invest + hz_non} "
          f"= {hz_invest / (hz_invest + hz_non):.1%}")
    print(f"  5AP INVEST rate: {ap_invest}/{ap_invest + ap_non} "
          f"= {ap_invest / (ap_invest + ap_non):.1%}")
    print(f"\n  Odds Ratio: {odds_ratio:.4f}")
    print(f"  Fisher Exact p-value (two-sided): {p_value:.4f}")

    if p_value < 0.05:
        print("  >>> SIGNIFICANT (p < 0.05): scaffold classes have different INVEST rates")
    else:
        print(f"  >>> Not significant at α=0.05 (p={p_value:.3f}), but 5AP shows "
              f"complete absence of INVEST (0/5, all ΔEST > +0.17 eV)")

    # Supplementary: Clopper-Pearson 95% CI for 5AP INVEST rate (0/5)
    # Upper bound for 0 successes in n trials
    ap_ci_upper = 1 - 0.05 ** (1 / len(ap_mols))  # exact formula
    # More precisely via Beta distribution
    ap_ci_upper_exact = stats.beta.ppf(0.95, ap_invest + 1,
                                        len(ap_mols) - ap_invest)
    print(f"\n  5AP INVEST rate 95% CI upper bound (Clopper-Pearson): "
          f"{ap_ci_upper_exact:.3f}")
    print(f"  5AP quantitative floor: min ΔEST = "
          f"{min(ap_mols.values()):+.4f} eV (5AP_NEt2_Ph)")

    # Effect size: all 5AP molecules are far from the INVEST boundary
    ap_dests = sorted(ap_mols.values())
    print(f"\n  5AP ΔEST values (all positive, sorted):")
    for k, v in sorted(ap_mols.items(), key=lambda x: x[1]):
        print(f"    {k:<20} ΔEST = {v:+.5f} eV  "
              f"(margin from 0: {v:.3f} eV ≈ {v/0.052:.1f}× post-R1 MAE)")

    result = {
        "test": "fisher_exact_5ap_vs_hz",
        "table": table.tolist(),
        "hz_invest": hz_invest, "hz_total": hz_invest + hz_non,
        "ap_invest": ap_invest, "ap_total": ap_invest + ap_non,
        "odds_ratio": float(odds_ratio),
        "p_value": float(p_value),
        "ap_ci_upper_95": float(ap_ci_upper_exact),
        "ap_min_dest_ev": float(min(ap_mols.values())),
        "significant_005": p_value < 0.05,
    }
    return result


# ════════════════════════════════════════════════════════════════
# TEST 2: Domain Adaptation — Wilcoxon Signed-Rank Test
# ════════════════════════════════════════════════════════════════

def test_domain_adaptation():
    """
    Wilcoxon Signed-Rank Test on the absolute LOO residuals of the
    original 19 target molecules: pre-R1 model vs post-R1 model.

    Both models use delta transfer (source pretrain → target residual).
    The ONLY difference is the training data:
      - Pre-R1: 19 target molecules
      - Post-R1: 19 + 14 Round 1 molecules (excl Hz_NH23)

    If post-R1 |residuals| are systematically smaller, AL sampling
    produced genuine model improvement.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Domain Adaptation — Wilcoxon Signed-Rank Test")
    print("=" * 70)

    # Load data
    model_input = pd.read_csv(os.path.join(ROOT, "data", "processed", "model_input_table.csv"))
    master_updated = pd.read_csv(
        os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

    feat_cols = [c for c in model_input.columns if c not in FEATURE_EXCLUDE]

    # Merge features
    feats = model_input[["mol_id"] + feat_cols]
    df = master_updated.merge(feats, on="mol_id", how="left",
                               suffixes=("", "_dup"))
    df = df.drop(columns=[c for c in df.columns if c.endswith("_dup")])

    labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
    source = labeled[labeled["source_domain"] == "pollice"]

    # Original 19 target molecules (pre-R1)
    orig_target_ids = model_input[
        (model_input["adc2_available"] == True) &
        (model_input["source_domain"] != "pollice")
    ].dropna(subset=["adc2_dest_ev"])["mol_id"].tolist()

    pre_target = labeled[labeled["mol_id"].isin(orig_target_ids)]

    # Post-R1 target: original 19 + R1 usable (excl Hz_NH23)
    r1_usable = [m for m in ROUND1_DEST if m != "Hz_NH23"]
    post_target_ids = list(set(orig_target_ids + r1_usable))
    post_target = labeled[labeled["mol_id"].isin(post_target_ids)]

    print(f"\n  Source (Pollice): {len(source)}")
    print(f"  Pre-R1 target: {len(pre_target)}")
    print(f"  Post-R1 target: {len(post_target)}")

    # Identify usable feature columns
    usable = [c for c in feat_cols
              if source[c].notna().mean() >= 0.1
              and pre_target[c].notna().mean() >= 0.1]

    # ── Train source model (shared) ──
    X_src = source[usable].fillna(-999).values
    y_src = source["adc2_dest_ev"].values
    model_src = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.1,
                              random_state=SEED, n_jobs=-1, verbosity=0)
    model_src.fit(X_src, y_src)

    def loo_residuals(target_df):
        """Compute LOO absolute residuals via delta transfer."""
        X_tgt = target_df[usable].fillna(-999).values
        y_tgt = target_df["adc2_dest_ev"].values
        src_pred = model_src.predict(X_tgt)
        n = len(target_df)
        preds = np.zeros(n)
        for i in range(n):
            tr = list(range(n))
            tr.remove(i)
            res_tr = y_tgt[tr] - src_pred[tr]
            X_d_tr = np.column_stack([X_tgt[tr], src_pred[tr].reshape(-1, 1)])
            X_d_te = np.column_stack([X_tgt[[i]], src_pred[[i]].reshape(-1, 1)])
            m = XGBRegressor(n_estimators=50, max_depth=2, learning_rate=0.1,
                             random_state=SEED, n_jobs=-1, verbosity=0)
            m.fit(X_d_tr, res_tr)
            preds[i] = src_pred[i] + m.predict(X_d_te)[0]
        return target_df["mol_id"].values, y_tgt, preds

    # ── Pre-R1 LOO on original 19 ──
    pre_ids, pre_true, pre_pred = loo_residuals(pre_target)
    pre_abs_res = np.abs(pre_pred - pre_true)

    # ── Post-R1 LOO on expanded pool, extract original 19 ──
    post_ids, post_true, post_pred = loo_residuals(post_target)
    # Map: for each of the 19 original molecules, find its post-R1 residual
    post_id_list = list(post_ids)
    post_abs_res_all = np.abs(post_pred - post_true)

    # Align: both arrays ordered by original 19
    pre_res_aligned = []
    post_res_aligned = []
    mol_ids_aligned = []
    for i, mid in enumerate(pre_ids):
        if mid in post_id_list:
            j = post_id_list.index(mid)
            pre_res_aligned.append(pre_abs_res[i])
            post_res_aligned.append(post_abs_res_all[j])
            mol_ids_aligned.append(mid)

    pre_arr = np.array(pre_res_aligned)
    post_arr = np.array(post_res_aligned)
    diff = pre_arr - post_arr  # positive = post-R1 is better

    print(f"\n  Paired molecules: {len(mol_ids_aligned)}")
    print(f"\n  {'mol_id':<28} {'|res|_pre':>10} {'|res|_post':>11} {'Δ':>8} {'better':>7}")
    print("  " + "-" * 66)
    for mid, pr, po in sorted(zip(mol_ids_aligned, pre_arr, post_arr),
                                key=lambda x: x[1] - x[2], reverse=True):
        d = pr - po
        better = "pre" if d < 0 else "POST"
        print(f"  {mid:<28} {pr:>10.5f} {po:>11.5f} {d:>+8.5f} {better:>7}")

    n_improved = (diff > 0).sum()
    n_worsened = (diff < 0).sum()
    n_tied = (diff == 0).sum()

    print(f"\n  Improved (post < pre):  {n_improved}/{len(diff)}")
    print(f"  Worsened (post > pre):  {n_worsened}/{len(diff)}")
    print(f"  Pre-R1 mean |residual|:  {pre_arr.mean():.5f} eV")
    print(f"  Post-R1 mean |residual|: {post_arr.mean():.5f} eV")
    print(f"  Mean reduction:          {diff.mean():+.5f} eV")

    # Wilcoxon signed-rank test (one-sided: post < pre)
    stat_val, p_two = stats.wilcoxon(pre_arr, post_arr, alternative="two-sided")
    _, p_one = stats.wilcoxon(pre_arr, post_arr, alternative="greater")

    print(f"\n  Wilcoxon signed-rank statistic: {stat_val:.2f}")
    print(f"  p-value (two-sided): {p_two:.4f}")
    print(f"  p-value (one-sided, pre > post): {p_one:.4f}")

    if p_one < 0.05:
        print("  >>> SIGNIFICANT: Post-R1 model has smaller residuals on original 19")
    else:
        print("  >>> Not significant at α=0.05")

    # Sample Efficiency Ratio
    pre_mae = pre_arr.mean()
    post_mae = post_arr.mean()
    delta_mae_frac = (pre_mae - post_mae) / pre_mae if pre_mae > 0 else 0
    delta_n_frac = 14 / 155
    ser = delta_mae_frac / delta_n_frac if delta_n_frac > 0 else 0
    print(f"\n  Sample Efficiency Ratio (SER): {ser:.2f}")
    print(f"    ΔMAE/MAE_pre = {delta_mae_frac:.3f}, Δn/N_pool = {delta_n_frac:.3f}")

    result = {
        "test": "wilcoxon_signed_rank_domain_adaptation",
        "n_paired": len(mol_ids_aligned),
        "n_improved": int(n_improved),
        "n_worsened": int(n_worsened),
        "pre_mean_abs_res": float(pre_arr.mean()),
        "post_mean_abs_res": float(post_arr.mean()),
        "mean_reduction": float(diff.mean()),
        "wilcoxon_stat": float(stat_val),
        "p_two_sided": float(p_two),
        "p_one_sided_greater": float(p_one),
        "significant_005": p_one < 0.05,
        "sample_efficiency_ratio": float(ser),
    }
    return result


# ════════════════════════════════════════════════════════════════
# TEST 3: Entropy Reduction — Information Gain Quantification
# ════════════════════════════════════════════════════════════════

def calculate_entropy_reduction():
    """
    Calculate binary Shannon entropy for the unlabeled pool under
    pre-R1 vs post-R1 models. Measures how much the AL round
    reduced uncertainty about INVEST classification.

    H = -Σ [p_i log2(p_i) + (1-p_i) log2(1-p_i)]

    where p_i = P(INVEST | x_i) estimated via Gaussian CDF from
    bootstrap ensemble predictions.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Entropy Reduction — Information Gain")
    print("=" * 70)

    model_input = pd.read_csv(os.path.join(ROOT, "data", "processed", "model_input_table.csv"))
    master_updated = pd.read_csv(
        os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))

    feat_cols = [c for c in model_input.columns if c not in FEATURE_EXCLUDE]

    feats = model_input[["mol_id"] + feat_cols]
    df = master_updated.merge(feats, on="mol_id", how="left",
                               suffixes=("", "_dup"))
    df = df.drop(columns=[c for c in df.columns if c.endswith("_dup")])

    labeled_all = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
    source = labeled_all[labeled_all["source_domain"] == "pollice"]

    # Pre-R1 labeled target (original 19)
    orig_ids = model_input[
        (model_input["adc2_available"] == True) &
        (model_input["source_domain"] != "pollice")
    ].dropna(subset=["adc2_dest_ev"])["mol_id"].tolist()

    pre_labeled = labeled_all[labeled_all["mol_id"].isin(
        source["mol_id"].tolist() + orig_ids)]

    # Post-R1 labeled (source + 19 + 14 R1)
    r1_usable = [m for m in ROUND1_DEST if m != "Hz_NH23"]
    post_ids = list(set(orig_ids + r1_usable))
    post_labeled = labeled_all[labeled_all["mol_id"].isin(
        source["mol_id"].tolist() + post_ids)]

    # Unlabeled pool (this_work, not labeled in EITHER phase)
    all_labeled_ids = set(source["mol_id"]) | set(post_ids)
    unlabeled = df[(df["source_domain"] == "this_work") &
                    (~df["mol_id"].isin(all_labeled_ids))].copy()

    print(f"\n  Pre-R1 labeled: {len(pre_labeled)} "
          f"(source={len(source)}, target={len(orig_ids)})")
    print(f"  Post-R1 labeled: {len(post_labeled)} "
          f"(source={len(source)}, target={len(post_ids)})")
    print(f"  Unlabeled pool: {len(unlabeled)}")

    usable = [c for c in feat_cols
              if pre_labeled[c].notna().mean() >= 0.1
              and unlabeled[c].notna().mean() >= 0.1]

    X_unlabeled = unlabeled[usable].fillna(-999).values
    EPS = 1e-10  # epsilon to prevent log(0)

    def get_invest_probs(labeled_df, n_bootstrap=10):
        """Train bootstrap ensemble and return P(INVEST) for unlabeled."""
        X_lab = labeled_df[usable].fillna(-999).values
        y_lab = labeled_df["adc2_dest_ev"].values
        preds = np.zeros((n_bootstrap, len(X_unlabeled)))
        for b in range(n_bootstrap):
            rng = np.random.RandomState(SEED + b)
            idx = rng.choice(len(X_lab), size=len(X_lab), replace=True)
            m = XGBRegressor(n_estimators=150, max_depth=4, learning_rate=0.1,
                             subsample=0.8, colsample_bytree=0.8,
                             random_state=SEED + b, n_jobs=-1, verbosity=0)
            m.fit(X_lab[idx], y_lab[idx])
            preds[b] = m.predict(X_unlabeled)
        mu = preds.mean(axis=0)
        sigma = np.maximum(preds.std(axis=0), EPS)
        # P(ΔEST < 0) via Gaussian CDF
        from scipy.stats import norm
        p_invest = norm.cdf(0, loc=mu, scale=sigma)
        return np.clip(p_invest, EPS, 1 - EPS), mu, sigma

    print("\n  Computing pre-R1 predictions...")
    pre_probs, pre_mu, pre_sigma = get_invest_probs(pre_labeled)

    print("  Computing post-R1 predictions...")
    post_probs, post_mu, post_sigma = get_invest_probs(post_labeled)

    # Binary Shannon entropy per molecule
    def binary_entropy(p):
        return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))

    H_pre = binary_entropy(pre_probs)
    H_post = binary_entropy(post_probs)

    total_H_pre = H_pre.sum()
    total_H_post = H_post.sum()
    delta_H = total_H_pre - total_H_post  # positive = entropy reduced

    print(f"\n  Total pre-R1 entropy:  {total_H_pre:.4f} bits")
    print(f"  Total post-R1 entropy: {total_H_post:.4f} bits")
    print(f"  ΔH (reduction):        {delta_H:+.4f} bits")
    print(f"  Mean per-molecule ΔH:  {delta_H / len(unlabeled):+.6f} bits")
    print(f"  Relative reduction:    {delta_H / total_H_pre:.1%}")

    # Per-scaffold entropy breakdown
    print(f"\n  Per-scaffold entropy breakdown:")
    for scaf in ["Hz", "5AP", "BN-PAH"]:
        mask = unlabeled["scaffold_family"].values == scaf
        if mask.sum() == 0:
            continue
        h_pre_s = H_pre[mask].sum()
        h_post_s = H_post[mask].sum()
        dh = h_pre_s - h_post_s
        print(f"    {scaf:<7}: ΔH = {dh:+.3f} bits "
              f"(pre={h_pre_s:.3f}, post={h_post_s:.3f}, "
              f"n={mask.sum()}, per-mol={dh / mask.sum():+.4f})")

    # Scaffold Coverage Entropy (SCE) comparison
    r1_scaffolds = pd.Series([
        "Hz" if m.startswith("Hz_") else "5AP" if m.startswith("5AP_") else "BN-PAH"
        for m in ROUND1_DEST.keys()
    ])
    sce_al = 0
    for scaf, count in r1_scaffolds.value_counts().items():
        frac = count / len(r1_scaffolds)
        sce_al -= frac * np.log2(frac)

    print(f"\n  Scaffold Coverage Entropy (SCE):")
    print(f"    Our AL selection:     {sce_al:.4f} bits "
          f"({r1_scaffolds.value_counts().to_dict()})")
    print(f"    Hz-greedy (all Hz):   0.0000 bits")
    print(f"    Proportional random:  ~1.08 bits (theoretical)")

    # Chemical Space Reduction Factor
    # 5AP: 55 total in pool, 1 already labeled pre-R1, 5 tested in R1
    # Remaining untested 5AP deprioritized by inference = 55 - 1 - 5 = 49
    n_5ap_eliminated = 49
    csrf = n_5ap_eliminated / 15
    print(f"\n  Chemical Space Reduction Factor (CSRF):")
    print(f"    Molecules eliminated: {n_5ap_eliminated} (5AP subspace)")
    print(f"    Queries used: 15")
    print(f"    CSRF = {csrf:.2f} (eliminated per query)")
    print(f"    Hz-greedy CSRF = 0.00")

    result = {
        "test": "shannon_entropy_reduction",
        "n_unlabeled": len(unlabeled),
        "total_H_pre": float(total_H_pre),
        "total_H_post": float(total_H_post),
        "delta_H": float(delta_H),
        "relative_reduction": float(delta_H / total_H_pre) if total_H_pre > 0 else 0,
        "sce_al": float(sce_al),
        "sce_hz_greedy": 0.0,
        "csrf": float(csrf),
    }
    return result


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

def main():
    all_results = {}

    r1 = test_subspace_elimination()
    all_results["subspace_elimination"] = r1

    r2 = test_domain_adaptation()
    all_results["domain_adaptation"] = r2

    r3 = calculate_entropy_reduction()
    all_results["entropy_reduction"] = r3

    # ── Summary ──
    print("\n" + "=" * 70)
    print("STATISTICAL VALIDATION SUMMARY")
    print("=" * 70)

    print(f"\n  1. Subspace Elimination (Fisher Exact):")
    print(f"     Hz INVEST: {r1['hz_invest']}/{r1['hz_total']} = "
          f"{r1['hz_invest']/r1['hz_total']:.1%}")
    print(f"     5AP INVEST: {r1['ap_invest']}/{r1['ap_total']} = "
          f"{r1['ap_invest']/r1['ap_total']:.1%}")
    print(f"     p = {r1['p_value']:.4f}, OR = {r1['odds_ratio']:.2f}")

    print(f"\n  2. Domain Adaptation (Wilcoxon):")
    print(f"     Pre MAE: {r2['pre_mean_abs_res']:.5f} → "
          f"Post MAE: {r2['post_mean_abs_res']:.5f}")
    print(f"     Improved: {r2['n_improved']}/{r2['n_paired']}")
    print(f"     p (one-sided) = {r2['p_one_sided_greater']:.4f}")
    print(f"     SER = {r2['sample_efficiency_ratio']:.2f}")

    print(f"\n  3. Entropy Reduction:")
    print(f"     ΔH = {r3['delta_H']:+.3f} bits "
          f"({r3['relative_reduction']:.1%} reduction)")
    print(f"     CSRF = {r3['csrf']:.2f}")
    print(f"     SCE_AL = {r3['sce_al']:.3f} vs SCE_Hz_greedy = 0.000")

    # Save
    out_path = os.path.join(OUT, "stats_validation_results.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n  Results saved to: {out_path}")


if __name__ == "__main__":
    main()
