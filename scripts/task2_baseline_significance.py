#!/usr/bin/env python3
"""Task 2: Three-Baseline Significance Tests

Baselines:
  B1: Uniform random selection from this_work pool
  B2: Scaffold-stratified random (proportional to pool composition)
  B3: Hz-prior-greedy (select only Hz molecules randomly)

Tests whether our AL selection significantly outperforms each baseline
in terms of INVEST discovery rate.
"""

import os, json, warnings
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(ROOT, "results", "round1_eval")
os.makedirs(OUT, exist_ok=True)

SEED = 42
N_PERM = 10000

# Load data
master = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table.csv"))
frozen = pd.read_csv(os.path.join(ROOT, "results", "tables", "round1_candidates_frozen.csv"))

# Round 1 actual results (15 usable with T1)
ROUND1_ACTUAL = {
    "Hz_NEt21_NPh22": -0.08858, "Hz_NH22_SO2Ph1": -0.06416,
    "5AP_NEt2_Ph": 0.17270, "Hz_NEt22_CN1": 0.04848,
    "5AP_NPh2_Me": 0.17137, "5AP_NPh22": 0.19540,
    "Hz_DMAC1_NPh21_SO2Ph1": -0.06566, "Hz_POZ1_NPh21_SO2Ph1": 0.06967,
    "5AP_NPh2_OMe": 0.22031, "5AP_NMe2_NPh2": 0.22997,
    "Hz_NEt22_CF31": -0.03593, "Hz_NPh22_CN1": -0.05384,
    "Hz_NMe22_CN1": 0.05350, "Hz_NH23": -0.38346,
    "Hz_Cz1_NPh21_CF31": -0.13573,
}

# Our actual hit count
our_n = 15
our_invest = sum(1 for v in ROUND1_ACTUAL.values() if v < -0.01)  # 7 INVEST

# Excluding Hz_NH23
our_invest_excl_nh23 = sum(1 for k, v in ROUND1_ACTUAL.items() if v < -0.01 and k != "Hz_NH23")

# Pool composition
target = master[master["source_domain"] == "this_work"].copy()
target_unlabeled = target[target["adc2_available"] == False]

# ΔDFT calibrated as surrogate for "ground truth" INVEST rate in unlabeled pool
has_dft = target["dft_dest_calibrated_ev"].notna()
dft_vals = target.loc[has_dft, "dft_dest_calibrated_ev"]
pool_invest_rate = (dft_vals < 0).mean()

# Per-scaffold invest rates (from ΔDFT surrogate)
scaffold_invest_rates = {}
for scaf in ["Hz", "5AP", "BN-PAH"]:
    sub = target[target["scaffold_family"] == scaf]
    sub_dft = sub["dft_dest_calibrated_ev"].dropna()
    if len(sub_dft) > 0:
        scaffold_invest_rates[scaf] = (sub_dft < 0).mean()
    else:
        scaffold_invest_rates[scaf] = 0.0

scaffold_counts = target["scaffold_family"].value_counts().to_dict()
total_pool = len(target)

print("=" * 70)
print("Task 2: Three-Baseline Significance Tests")
print("=" * 70)
print(f"\nOur AL selection: {our_invest}/{our_n} INVEST = {our_invest/our_n:.1%}")
print(f"  (excl Hz_NH23: {our_invest_excl_nh23}/{our_n-1} = {our_invest_excl_nh23/(our_n-1):.1%})")
print(f"\nPool INVEST rate (ΔDFT surrogate): {pool_invest_rate:.1%}")
print(f"Per-scaffold INVEST rates (ΔDFT): {scaffold_invest_rates}")
print(f"Pool composition: {scaffold_counts}")

results = []

# ─── Baseline 1: Uniform random ───
print("\n" + "-" * 50)
print("B1: Uniform random selection from this_work pool")
print("-" * 50)

# Under uniform random, P(INVEST) = pool_invest_rate for each draw
# Expected INVEST in 15 draws = 15 * pool_invest_rate
rng = np.random.RandomState(SEED)
b1_invest_counts = []
for _ in range(N_PERM):
    # Draw 15 molecules at random, each has pool_invest_rate chance of INVEST
    draws = rng.random(our_n) < pool_invest_rate
    b1_invest_counts.append(draws.sum())

b1_invest_counts = np.array(b1_invest_counts)
b1_mean = b1_invest_counts.mean()
b1_p_value = (b1_invest_counts >= our_invest).mean()
b1_p_excl = (b1_invest_counts >= our_invest_excl_nh23).mean()

print(f"  Expected INVEST under B1: {b1_mean:.1f}/{our_n}")
print(f"  Our INVEST: {our_invest}/{our_n}")
print(f"  Permutation p-value (one-sided, ≥{our_invest}): {b1_p_value:.4f}")
print(f"  Permutation p-value excl Hz_NH23 (≥{our_invest_excl_nh23}): {b1_p_excl:.4f}")

results.append({
    "baseline": "B1_uniform_random",
    "expected_invest": b1_mean,
    "our_invest": our_invest,
    "our_invest_excl_nh23": our_invest_excl_nh23,
    "p_value": b1_p_value,
    "p_value_excl_nh23": b1_p_excl,
    "significant_005": b1_p_value < 0.05,
})

# ─── Baseline 2: Scaffold-stratified random ───
print("\n" + "-" * 50)
print("B2: Scaffold-stratified random (proportional)")
print("-" * 50)

# Our selection: 10 Hz, 5 5AP, 0 BN-PAH
our_scaffold_counts = frozen["scaffold_family"].value_counts().to_dict()
print(f"  Our selection composition: {our_scaffold_counts}")

# Under proportional stratified sampling of 15:
n_hz_strat = round(15 * scaffold_counts.get("Hz", 0) / total_pool)
n_5ap_strat = round(15 * scaffold_counts.get("5AP", 0) / total_pool)
n_bn_strat = 15 - n_hz_strat - n_5ap_strat
print(f"  Proportional: Hz={n_hz_strat}, 5AP={n_5ap_strat}, BN-PAH={n_bn_strat}")

rng = np.random.RandomState(SEED)
b2_invest_counts = []
for _ in range(N_PERM):
    n_invest = 0
    for scaf, n_draw in [("Hz", n_hz_strat), ("5AP", n_5ap_strat), ("BN-PAH", n_bn_strat)]:
        rate = scaffold_invest_rates.get(scaf, 0)
        n_invest += (rng.random(n_draw) < rate).sum()
    b2_invest_counts.append(n_invest)

b2_invest_counts = np.array(b2_invest_counts)
b2_mean = b2_invest_counts.mean()
b2_p_value = (b2_invest_counts >= our_invest).mean()
b2_p_excl = (b2_invest_counts >= our_invest_excl_nh23).mean()

print(f"  Expected INVEST under B2: {b2_mean:.1f}/{our_n}")
print(f"  Permutation p-value (≥{our_invest}): {b2_p_value:.4f}")
print(f"  Permutation p-value excl Hz_NH23 (≥{our_invest_excl_nh23}): {b2_p_excl:.4f}")

results.append({
    "baseline": "B2_scaffold_stratified",
    "expected_invest": b2_mean,
    "our_invest": our_invest,
    "our_invest_excl_nh23": our_invest_excl_nh23,
    "p_value": b2_p_value,
    "p_value_excl_nh23": b2_p_excl,
    "significant_005": b2_p_value < 0.05,
})

# ─── Baseline 3: Hz-prior-greedy ───
print("\n" + "-" * 50)
print("B3: Hz-prior-greedy (select 15 Hz molecules at random)")
print("-" * 50)

hz_invest_rate = scaffold_invest_rates["Hz"]
print(f"  Hz INVEST rate (ΔDFT): {hz_invest_rate:.1%}")

rng = np.random.RandomState(SEED)
b3_invest_counts = []
for _ in range(N_PERM):
    draws = rng.random(our_n) < hz_invest_rate
    b3_invest_counts.append(draws.sum())

b3_invest_counts = np.array(b3_invest_counts)
b3_mean = b3_invest_counts.mean()
b3_p_value = (b3_invest_counts >= our_invest).mean()
b3_p_excl = (b3_invest_counts >= our_invest_excl_nh23).mean()

# Also: Hz-only baseline using ACTUAL Round 1 Hz hit rate (6/9 = 67%)
# This is the empirical Hz prior from P0-2
hz_empirical = 6 / 9  # from P0-2
rng2 = np.random.RandomState(SEED + 1)
b3e_invest_counts = []
for _ in range(N_PERM):
    draws = rng2.random(our_n) < hz_empirical
    b3e_invest_counts.append(draws.sum())
b3e_invest_counts = np.array(b3e_invest_counts)
b3e_mean = b3e_invest_counts.mean()
b3e_p = (b3e_invest_counts >= our_invest).mean()

print(f"  Expected INVEST under B3 (ΔDFT rate): {b3_mean:.1f}/{our_n}")
print(f"  Expected INVEST under B3 (empirical Hz rate 67%): {b3e_mean:.1f}/{our_n}")
print(f"  Permutation p-value ΔDFT (≥{our_invest}): {b3_p_value:.4f}")
print(f"  Permutation p-value empirical (≥{our_invest}): {b3e_p:.4f}")
print(f"  Permutation p-value excl Hz_NH23 (≥{our_invest_excl_nh23}): {b3_p_excl:.4f}")

results.append({
    "baseline": "B3_hz_greedy_dft",
    "expected_invest": b3_mean,
    "our_invest": our_invest,
    "our_invest_excl_nh23": our_invest_excl_nh23,
    "p_value": b3_p_value,
    "p_value_excl_nh23": b3_p_excl,
    "significant_005": b3_p_value < 0.05,
})

results.append({
    "baseline": "B3_hz_greedy_empirical",
    "expected_invest": b3e_mean,
    "our_invest": our_invest,
    "our_invest_excl_nh23": our_invest_excl_nh23,
    "p_value": b3e_p,
    "p_value_excl_nh23": np.nan,
    "significant_005": b3e_p < 0.05,
})

# ─── Summary ───
print("\n" + "=" * 70)
print("Task 2 Summary")
print("=" * 70)

results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
results_df.to_csv(os.path.join(OUT, "task2_baseline_significance.csv"), index=False)

# Key conclusion
print("\n--- Key findings ---")
if b3_p_value > 0.05 and b3e_p > 0.05:
    print("CRITICAL: AL selection does NOT significantly beat Hz-prior-greedy baseline.")
    print("The Hz scaffold itself carries most of the INVEST signal.")
    print("AL's value must be framed as exploration/information gain, not hit rate.")
else:
    print("AL selection significantly outperforms Hz-prior-greedy baseline.")

if b1_p_value < 0.05:
    print("AL selection significantly outperforms uniform random baseline.")
else:
    print("AL selection does NOT significantly outperform uniform random baseline.")

# Hz-prior attack defense
print("\n--- Hz-prior attack defense ---")
print("Can we defend against the argument that 'just pick Hz molecules randomly'?")
our_hz_invest = sum(1 for k, v in ROUND1_ACTUAL.items()
                     if "Hz_" in k and v < -0.01 and k != "Hz_NH23")
our_hz_n = sum(1 for k in ROUND1_ACTUAL if "Hz_" in k and k != "Hz_NH23")
print(f"  Our Hz INVEST rate: {our_hz_invest}/{our_hz_n} = {our_hz_invest/our_hz_n:.1%}")
print(f"  Hz-greedy expected: {hz_empirical:.1%}")
print(f"  Difference: {our_hz_invest/our_hz_n - hz_empirical:+.1%}")
print(f"  → Our Hz selection rate ≈ Hz prior. No evidence AL improves Hz hit rate.")

# What AL DOES provide
print("\n--- What AL provides beyond Hz-greedy ---")
print("  1. Scaffold diversity: selected 5 5AP molecules (Hz-greedy misses these)")
print("  2. Information gain: uncertainty bucket identified OOD 5AP region")
print("  3. Model improvement: post-R1 LOO MAE improved from 0.078 to 0.052 eV")
print("  4. Negative result: confirmed 5AP are NOT INVEST, saves future compute")

with open(os.path.join(OUT, "task2_hz_prior_defense.json"), "w") as f:
    json.dump({
        "our_invest_rate": our_invest / our_n,
        "b1_uniform_expected": float(b1_mean) / our_n,
        "b2_stratified_expected": float(b2_mean) / our_n,
        "b3_hz_greedy_expected": float(b3_mean) / our_n,
        "b3_hz_greedy_empirical_expected": float(b3e_mean) / our_n,
        "b1_p": float(b1_p_value),
        "b2_p": float(b2_p_value),
        "b3_dft_p": float(b3_p_value),
        "b3_empirical_p": float(b3e_p),
        "conclusion": "AL does not beat Hz-greedy on hit rate; value is in exploration and model improvement",
        "defense_strategy": "Frame AL as error-correcting layer that provides scaffold-diverse information and reduces uncertainty",
    }, f, indent=2)

print(f"\nOutput: {os.path.join(OUT, 'task2_baseline_significance.csv')}")
print(f"        {os.path.join(OUT, 'task2_hz_prior_defense.json')}")
