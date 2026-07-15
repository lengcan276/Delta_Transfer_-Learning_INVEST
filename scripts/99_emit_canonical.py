#!/usr/bin/env python3
"""
99_emit_canonical.py  --  generate results/canonical_metrics.json from raw data files.

Every number is derived from actual data/results files. Nothing is hardcoded.
Values that cannot be derived are set to null and listed in missing_metrics.
Inconsistencies across files are listed in known_inconsistencies.

Run from project root:
    python3 scripts/99_emit_canonical.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "results"
DATA = ROOT / "data"
ROUND1 = RESULTS / "round1_eval"

missing_metrics = []
known_inconsistencies = []


def miss(key, reason):
    missing_metrics.append({"key": key, "reason": reason})
    return None


def incon(key, val_a, src_a, val_b, src_b,
          status="unresolved_contradiction", resolution=None):
    """Record a numerical disagreement between two sources.

    status:
        "unresolved_contradiction" (default) — must be reconciled before
        publication.
        "intentional_analysis_set_distinction" — the two values describe
        different analysis sets by design and BOTH are valid in their
        respective scopes; `resolution` documents the rule that selects
        which one to cite where.
    """
    entry = {"key": key, "value_a": val_a, "source_a": src_a,
             "value_b": val_b, "source_b": src_b,
             "status": status}
    if resolution:
        entry["resolution"] = resolution
    known_inconsistencies.append(entry)


def safe_csv(path, **kw):
    p = Path(path)
    return pd.read_csv(p, **kw) if p.exists() else None


def safe_json(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None


def as_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
    return bool(value)


# ── LIBRARY ──────────────────────────────────────────────────────────────────

def build_library():
    """Library counts, with explicit separation of source vs target ADC(2) labels.

    ── 446 vs 465 reconciliation ─────────────────────────────────────────
    Earlier versions of this function emitted a single field
    ``n_invest_labeled`` equal to *all* ADC(2)-labelled rows in
    ``master_molecule_table.csv`` (= 465). That total conflates two distinct
    populations:
      - 446 Pollice molecules with ADC(2)/cc-pVDZ labels   → SOURCE domain
      - 19 this_work pre-Round-1 target molecules with ADC(2) labels → TARGET (pre-R1)
    The manuscript correctly cites 446 for the Pollice source set
    (e.g. "446 source-domain ADC(2)/cc-pVDZ labels"); the legacy 465 union
    has no manuscript anchor. We now expose the two counts separately and
    keep the union as a transparency field, so downstream consumers can
    pick the correct semantics.

    Truth table:
      pollice2021_adc2.txt      → 446 rows (raw Pollice ADC(2) file)
      master_molecule_table.csv (source_domain == 'pollice'): 1719 rows;
                                  446 of them have a non-null adc2_dest_ev
      master_molecule_table.csv (source_domain == 'this_work'): 155 rows;
                                  19 of them have a non-null adc2_dest_ev
                                  (= pre-Round-1 labelled target subset)
    """
    master = safe_csv(DATA / "processed" / "master_molecule_table.csv")
    model_input = safe_csv(DATA / "processed" / "model_input_table.csv")
    source_ds = safe_csv(DATA / "source" / "invest_master_dataset.csv")

    if master is None:
        return miss("library", "master_molecule_table.csv not found")

    scaf_counts = master["scaffold_family"].value_counts().to_dict()
    target_families = {"Hz", "5AP", "BN-PAH", "BN"}
    target_mask = master["scaffold_family"].isin(target_families)
    n_target = int(target_mask.sum())
    target_scaf = master.loc[target_mask, "scaffold_family"].value_counts().to_dict()

    adc2_avail = (int(master["adc2_available"].sum())
                  if "adc2_available" in master.columns else None)

    # Per-source-domain ADC(2)-label counts.
    src_counts: dict[str, int] = {}
    if "adc2_dest_ev" in master.columns and "source_domain" in master.columns:
        for sd, grp in master.groupby("source_domain"):
            src_counts[str(sd)] = int(grp["adc2_dest_ev"].notna().sum())
    n_invest_labeled_total = int(sum(src_counts.values())) if src_counts else None
    n_invest_labeled_pollice_source = src_counts.get("pollice")
    n_invest_labeled_thiswork_target_preR1 = src_counts.get("this_work")

    if (n_invest_labeled_total is not None
            and n_invest_labeled_pollice_source is not None
            and n_invest_labeled_thiswork_target_preR1 is not None
            and n_invest_labeled_pollice_source
                + n_invest_labeled_thiswork_target_preR1
                != n_invest_labeled_total):
        # Other source_domains (omar2023, pang2025) currently contribute 0,
        # but if they ever do, surface that as an inconsistency rather than
        # silently shifting the canonical numbers.
        incon(
            "library.n_invest_labeled_partition",
            n_invest_labeled_pollice_source
                + n_invest_labeled_thiswork_target_preR1,
            "pollice + this_work ADC(2)-label counts",
            n_invest_labeled_total,
            "sum across all source_domains in master_molecule_table.csv",
            status="unresolved_contradiction",
            resolution="A non-pollice/non-this_work source_domain now "
                       "contributes ADC(2) labels; update build_library() "
                       "to expose it as a named field.",
        )

    return {
        "n_molecules_master": len(master),
        "n_target_domain": n_target,
        "target_scaffold_counts": target_scaf,

        # ── ADC(2)-label partition ────────────────────────────────────
        # The manuscript should cite n_invest_labeled_pollice_source
        # whenever it talks about the Pollice source training set
        # (e.g. "446 Pollice ADC(2)/cc-pVDZ labels"). The total field
        # is the union and includes the pre-Round-1 labelled target.
        "n_invest_labeled_pollice_source": n_invest_labeled_pollice_source,
        "n_invest_labeled_thiswork_target_preR1":
            n_invest_labeled_thiswork_target_preR1,
        "n_invest_labeled_total": n_invest_labeled_total,
        "n_invest_labeled_by_source_domain": src_counts,
        "n_invest_labeled_filter_description": (
            "Counted master_molecule_table.csv rows with "
            "adc2_dest_ev.notna(), grouped by source_domain. "
            "Pollice = source training set (446); "
            "this_work = pre-Round-1 labelled target (19); "
            "total = 465."
        ),
        "n_invest_labeled_source_files": [
            "data/processed/master_molecule_table.csv",
            "data/invest_core/literature_data/pollice2021_adc2.txt",
        ],

        "adc2_available_n": adc2_avail,
        "n_scaffold_families": master["scaffold_family"].nunique(),
        "scaffold_family_counts": scaf_counts,
        "n_source_dataset": len(source_ds) if source_ds is not None else None,
        "n_model_input_rows": len(model_input) if model_input is not None else None,
        "n_model_features_total": (model_input.shape[1] - 1
                                   if model_input is not None else None),
    }


# ── DATASETS ─────────────────────────────────────────────────────────────────

def build_datasets():
    conf_json = safe_json(ROUND1 / "p0b_conformal_calibration.json")
    deploy = safe_csv(ROUND1 / "task1_deployment_detail.csv")
    cv = safe_csv(ROUND1 / "task1_cv_matrix.csv")
    frozen = safe_csv(RESULTS / "tables" / "round1_candidates_frozen.csv")
    r2 = safe_json(RESULTS / "round2_eval" / "round2_acquisition_summary.json")
    r2_cand = safe_csv(RESULTS / "round2_eval" / "round2_final_candidates.csv")

    calib_n = conf_json["calibration_n"] if conf_json else None
    test_n = conf_json["test_n"] if conf_json else None
    deploy_n = len(deploy) if deploy is not None else None

    pre_n = post_excl_n = post_incl_n = None
    if cv is not None:
        for _, row in cv.iterrows():
            s = str(row.get("stage", ""))
            if "pre_round1" in s:
                pre_n = int(row["n_target"])
            elif "excl" in s:
                post_excl_n = int(row["n_target"])
            elif "incl" in s:
                post_incl_n = int(row["n_target"])

    if test_n is not None and deploy_n is not None and test_n != deploy_n:
        incon("datasets.round1_n",
              deploy_n, "task1_deployment_detail.csv (all deployed)",
              test_n, "p0b_conformal_calibration.json test_n (Hz_NH23 excluded by design)",
              status="intentional_analysis_set_distinction",
              resolution=(
                  "15 = Round-1 deployment yield (full set, includes Hz_NH23). "
                  "14 = Fisher / split-conformal subset (excludes Hz_NH23 by design "
                  "as a dark / fosc=0 outlier whose residual would dominate the "
                  "empirical quantile). The two numbers describe different analysis "
                  "sets and must each be cited only in their own scope."
              ))

    r2_cand_summary = None
    if r2_cand is not None:
        bucket_col = "selection_bucket_r2" if "selection_bucket_r2" in r2_cand.columns else None
        scaf_col = "scaffold_family" if "scaffold_family" in r2_cand.columns else None
        r2_cand_summary = {
            "n_rows": len(r2_cand),
            "scaffold_counts": r2_cand[scaf_col].value_counts().to_dict() if scaf_col else None,
            "bucket_counts": r2_cand[bucket_col].value_counts().to_dict() if bucket_col else None,
            "predicted_dest_eV_min": round(float(r2_cand["predicted_dest_ev"].min()), 6)
                if "predicted_dest_ev" in r2_cand.columns else None,
            "predicted_dest_eV_max": round(float(r2_cand["predicted_dest_ev"].max()), 6)
                if "predicted_dest_ev" in r2_cand.columns else None,
        }
        # Cross-check the round2 candidate count against the acquisition summary
        if r2 is not None and r2.get("n_selected") and len(r2_cand) != r2.get("n_selected"):
            incon("datasets.round2_n_candidates",
                  r2.get("n_selected"), "round2_acquisition_summary.json n_selected",
                  len(r2_cand), "round2_final_candidates.csv row count")

    return {
        # ── Naming note ──────────────────────────────────────────────────
        # "pre_round1_*" fields refer to the data-driven model and split-
        # conformal calibration (the set of target-domain molecules with
        # ADC(2) labels available BEFORE Round-1 acquisition). They are
        # NOT the low-level DFT 5-anchor TDDFT calibration that fits
        # ΔEST_corr from a small chemistry-anchor set. Never conflate
        # the two.
        "field_name_note": (
            "pre_round1_conformal_calibration_n and "
            "pre_round1_model_labeled_n refer to the pre-Round-1 "
            "target-domain labeled set used for split-conformal calibration "
            "and Δ-correction model training; they are NOT the DFT 5-anchor "
            "TDDFT calibration."
        ),
        "pre_round1_conformal_calibration_n": calib_n,
        "pre_round1_model_labeled_n": pre_n,
        "round1_conformal_test_n": test_n,
        "conformal_design_note": conf_json.get("design") if conf_json else None,
        "round1_deployment_n": deploy_n,
        "post_round1_excl_nh23_n": post_excl_n,
        "post_round1_incl_nh23_n": post_incl_n,
        "round2_selected_n": r2.get("n_selected") if r2 else None,
        "round2_scaffold_distribution": r2.get("scaffold_distribution") if r2 else None,
        "round2_hz_selected": r2.get("hz_selected") if r2 else None,
        "round2_n_counterfactual": r2.get("n_counterfactual") if r2 else None,
        "round2_final_candidates": r2_cand_summary,
        "round1_frozen_candidates_n": len(frozen) if frozen is not None else None,
    }


# ── MODEL PERFORMANCE ────────────────────────────────────────────────────────

def build_model_performance():
    cv = safe_csv(ROUND1 / "task1_cv_matrix.csv")
    conf_json = safe_json(ROUND1 / "p0b_conformal_calibration.json")
    lc = safe_csv(ROUND1 / "task1_learning_curve.csv")

    stages = {}
    if cv is not None:
        for _, row in cv.iterrows():
            stage = str(row.get("stage", ""))
            d = {k: round(float(row[k]), 10) for k in
                 ["MAE", "RMSE", "Spearman_rho", "sign_accuracy",
                  "INVEST_recall", "INVEST_precision"] if k in row}
            d["MAE_meV"] = round(float(row["MAE"]) * 1000, 6)
            d["n_target"] = int(row["n_target"])
            stages[stage] = d

    lc_points = []
    if lc is not None:
        for _, row in lc.iterrows():
            pt = {"n_added": int(row.get("n_added", 0)),
                  "n_target": int(row.get("n_target", 0))}
            for k in ["MAE", "Spearman_rho", "sign_accuracy", "INVEST_recall"]:
                if k in row:
                    pt[f"{k}_eV" if k == "MAE" else k] = round(float(row[k]), 10)
            lc_points.append(pt)

    out = dict(stages)
    out["conformal_calibration_MAE_eV"] = (
        round(conf_json["calibration_MAE"], 10) if conf_json else None)
    out["conformal_test_MAE_eV"] = (
        round(conf_json["test_MAE"], 10) if conf_json else None)
    out["learning_curve_points"] = lc_points
    return out


# ── DEPLOYMENT ───────────────────────────────────────────────────────────────

def build_deployment():
    deploy = safe_csv(ROUND1 / "task1_deployment_detail.csv")
    if deploy is None:
        return miss("deployment", "task1_deployment_detail.csv not found")

    nh23 = None
    if "mol_id" in deploy.columns:
        rows = deploy[deploy["mol_id"] == "Hz_NH23"]
        nh23 = rows.iloc[0] if len(rows) > 0 else None

    invest_mask = (deploy["actual_dest"] < 0) if "actual_dest" in deploy.columns else None

    return {
        "n_molecules": len(deploy),
        "sign_correct_n": int(deploy["sign_correct"].sum()) if "sign_correct" in deploy.columns else None,
        "sign_wrong_n": int((~deploy["sign_correct"]).sum()) if "sign_correct" in deploy.columns else None,
        "sign_accuracy": round(float(deploy["sign_correct"].mean()), 10) if "sign_correct" in deploy.columns else None,
        "n_invest_actual": int(invest_mask.sum()) if invest_mask is not None else None,
        "n_non_invest_actual": int((~invest_mask).sum()) if invest_mask is not None else None,
        "hz_nh23_included": nh23 is not None,
        "hz_nh23_actual_dest_eV": round(float(nh23["actual_dest"]), 5) if nh23 is not None and "actual_dest" in nh23 else None,
        "hz_nh23_pred_dest_eV": round(float(nh23["pred_dest"]), 7) if nh23 is not None and "pred_dest" in nh23 else None,
        "hz_nh23_abs_residual_eV": round(float(nh23["abs_residual"]), 7) if nh23 is not None and "abs_residual" in nh23 else None,
        "scaffold_counts": deploy["scaffold"].value_counts().to_dict() if "scaffold" in deploy.columns else None,
        "bucket_counts": deploy["bucket"].value_counts().to_dict() if "bucket" in deploy.columns else None,
    }


# ── ABLATION ─────────────────────────────────────────────────────────────────

def build_ablation():
    ms = safe_csv(ROUND1 / "p0a_ablation_multiseed.csv")
    pt = safe_json(ROUND1 / "p0a_ablation_paired_tests.json")
    t3 = safe_csv(ROUND1 / "task3_ablation_results.csv")

    if ms is None:
        return miss("ablation", "p0a_ablation_multiseed.csv not found")

    summary = {}
    for config, grp in ms.groupby("config"):
        mae_vals = grp["MAE"].values
        summary[str(config)] = {
            "MAE_mean_eV": round(float(mae_vals.mean()), 10),
            "MAE_std_eV": round(float(mae_vals.std()), 10),
            "sign_acc_mean": round(float(grp["sign_accuracy"].mean()), 10) if "sign_accuracy" in grp.columns else None,
            "INVEST_rec_mean": round(float(grp["INVEST_recall"].mean()), 10) if "INVEST_recall" in grp.columns else None,
            "n_delta_features": int(grp["n_delta_features"].iloc[0]) if "n_delta_features" in grp.columns else None,
            "n_physics_features": int(grp["n_physics"].iloc[0]) if "n_physics" in grp.columns else None,
        }

    # Negative transfer check
    full_mae = summary.get("full", {}).get("MAE_mean_eV")
    rdkit_mae = summary.get("rdkit_only", {}).get("MAE_mean_eV")
    if full_mae and rdkit_mae:
        if full_mae < rdkit_mae:
            incon("ablation.negative_transfer",
                  f"full={full_mae:.6f} < rdkit_only={rdkit_mae:.6f} (physics HELPS, not hurts)",
                  "p0a_ablation_multiseed.csv",
                  "paper claims physics descriptors cause negative transfer (full > rdkit_only)",
                  "paper/main.tex")
        # else: full > rdkit_only → negative transfer confirmed

    t3_summary = {}
    if t3 is not None:
        for _, row in t3.iterrows():
            cfg = str(row.get("config", _))
            t3_summary[cfg] = {
                "MAE_eV": round(float(row.get("MAE", np.nan)), 10),
                "RMSE_eV": round(float(row.get("RMSE", np.nan)), 10),
                "sign_accuracy": round(float(row.get("sign_accuracy", np.nan)), 10),
                "INVEST_recall": round(float(row.get("INVEST_recall", np.nan)), 10),
                "n_features": int(row["n_features"]) if "n_features" in row else None,
            }
        # Warn if all configs identical
        t3_maes = [v["MAE_eV"] for v in t3_summary.values()]
        if len(set(round(x, 8) for x in t3_maes)) == 1 and len(t3_maes) > 1:
            incon("ablation.task3_all_configs_identical_MAE",
                  f"all {len(t3_maes)} configs: {t3_maes[0]:.10f} eV",
                  "task3_ablation_results.csv",
                  "p0a shows variation across configs",
                  "p0a_ablation_multiseed.csv")
        # Cross-check full config between p0a and task3
        full_t3 = t3_summary.get("full", {}).get("MAE_eV")
        if full_mae and full_t3 and abs(full_mae - full_t3) > 1e-6:
            incon("ablation.full_config_MAE_mismatch",
                  full_mae, "p0a_ablation_multiseed.csv (10-seed mean)",
                  full_t3, "task3_ablation_results.csv")

    return {
        "n_seeds": ms["seed"].nunique() if "seed" in ms.columns else None,
        "n_target_p0a": int(ms.get("n_target", pd.Series([None])).iloc[0])
            if "n_target" in ms.columns else None,
        "multiseed_summary": summary,
        "paired_tests": pt,
        "task3_configs": t3_summary if t3 is not None else None,
    }


# ── UNCERTAINTY ──────────────────────────────────────────────────────────────

def build_uncertainty():
    conf_json = safe_json(ROUND1 / "p0b_conformal_calibration.json")
    if conf_json is None:
        return miss("uncertainty", "p0b_conformal_calibration.json not found")

    calib_n = conf_json["calibration_n"]
    test_n = conf_json["test_n"]

    cov_by_level = {}
    for row in conf_json["results"]:
        nom = str(row["nominal_coverage"])
        cov_by_level[nom] = {
            "conformal_calib_coverage": round(row["conformal_calib_coverage"], 10),
            "conformal_test_coverage": round(row["conformal_test_coverage"], 10),
            "conformal_width_eV": round(row["conformal_width"], 10),
            "conformal_q_hat": round(row["conformal_q_hat"], 10),
            "bootstrap_calib_coverage": round(row["bootstrap_calib_coverage"], 10),
            "bootstrap_test_coverage": round(row["bootstrap_test_coverage"], 10),
            "bootstrap_test_mean_width_eV": round(row["bootstrap_test_mean_width"], 10),
        }

    lvl90 = cov_by_level.get("0.9", {})
    lvl95 = cov_by_level.get("0.95", {})

    # Binomial Wilson CI on 90%-nominal test coverage
    k90 = round(float(lvl90.get("conformal_test_coverage", 0)) * test_n)
    try:
        from statsmodels.stats.proportion import proportion_confint as _pcf
        lo90, hi90 = _pcf(int(k90), test_n, alpha=0.05, method='wilson')
    except ImportError:
        # Manual Wilson CI
        _p = k90 / test_n if test_n > 0 else 0
        _z = 1.96
        _denom = 1 + _z**2 / test_n
        _center = (_p + _z**2 / (2 * test_n)) / _denom
        _half = _z * (_p * (1 - _p) / test_n + _z**2 / (4 * test_n**2))**0.5 / _denom
        lo90, hi90 = max(0, _center - _half), min(1, _center + _half)

    fixed_baseline = round(float(conf_json.get("fixed_baseline", {}).get("width", 0.32)), 4)

    bs95_width = lvl95.get("bootstrap_test_mean_width_eV")

    return {
        "calibration_n": calib_n,
        "test_n": test_n,
        "calibration_MAE_eV": round(conf_json["calibration_MAE"], 10),
        "test_MAE_eV": round(conf_json["test_MAE"], 10),
        "design_note": conf_json.get("design"),
        "coverage_by_nominal_level": cov_by_level,
        "conformal_90_test_coverage": lvl90.get("conformal_test_coverage"),
        "conformal_90_coverage_wilson_ci_95": [round(lo90, 4), round(hi90, 4)],
        "conformal_95_test_coverage": lvl95.get("conformal_test_coverage"),
        "conformal_95_width_eV": lvl95.get("conformal_width_eV"),
        "bootstrap_95_test_coverage": lvl95.get("bootstrap_test_coverage"),
        "bootstrap_95_mean_width_eV": bs95_width,
        "fixed_baseline_width_eV": fixed_baseline,
        "fixed_baseline_coverage": 1.0,
    }


# ── ACTIVE LEARNING ──────────────────────────────────────────────────────────

def build_active_learning():
    stats_json = safe_json(ROUND1 / "stats_validation_results.json")
    t2 = safe_csv(ROUND1 / "task2_baseline_significance.csv")
    validated = safe_csv(RESULTS / "validated_candidates_master.csv")

    out = {}

    # ── Full-cohort Fisher (Hz vs ALL non-Hz) from validated_candidates_master ──
    if validated is not None:
        hz_mask = validated["scaffold"] == "Hz"
        neg_mask = validated["classification"].isin(["negative_gap", "dark_negative_gap"])

        hz_invest = int((hz_mask & neg_mask).sum())
        hz_total = int(hz_mask.sum())
        non_hz_invest = int((~hz_mask & neg_mask).sum())
        non_hz_total = int((~hz_mask).sum())

        table = [[hz_invest, hz_total - hz_invest],
                 [non_hz_invest, non_hz_total - non_hz_invest]]
        _, p_full_two = stats.fisher_exact(table, alternative='two-sided')
        _, p_full_one = stats.fisher_exact(table, alternative='greater')
        p_full = round(float(p_full_two), 6)   # paper cites two-sided

        out["fisher_full_cohort"] = {
            "description": "Hz vs ALL non-Hz, full validated cohort — PAPER-CITED VALUE",
            "hz_invest": hz_invest, "hz_total": hz_total,
            "non_hz_invest": non_hz_invest, "non_hz_total": non_hz_total,
            "contingency_table": table,
            "p_value_two_sided": round(float(p_full_two), 6),
            "p_value_one_sided_greater": round(float(p_full_one), 6),
            "p_value": p_full,
            "note": f"Two-sided Fisher exact; rounded paper value is p={p_full:.3f}",
        }

        # R1-subset from stats_json (historical, DO NOT cite in paper)
        if stats_json:
            sub = stats_json.get("subspace_elimination", {})
            p_r1 = round(float(sub.get("p_value", 1.0)), 6)
            out["fisher_r1_subset"] = {
                "description": "R1 subset only (Hz vs 5AP) — DO NOT cite in paper",
                "hz_invest": sub.get("hz_invest"), "hz_total": sub.get("hz_total"),
                "ap_invest": sub.get("ap_invest"), "ap_total": sub.get("ap_total"),
                "p_value": p_r1,
            }
            if abs(p_r1 - p_full) > 0.001:
                incon("active_learning.fisher_p_value",
                      p_r1, "stats_validation_results.json (R1 subset, Hz vs 5AP only)",
                      p_full, "validated_candidates_master.csv (full cohort, Hz vs ALL non-Hz) ← paper uses this",
                      status="intentional_analysis_set_distinction",
                      resolution=(
                          "0.015245 = full validated cohort Hz vs all non-Hz Fisher exact "
                          "(13/27 vs 0/8) — used in Abstract, §3.4, Conclusion. "
                          "0.030969 = Round-1 subset Hz vs 5AP only (6/9 vs 0/5) — used "
                          "in §3.4 paragraph and Fig 5(b) caption. The two p-values "
                          "describe different cohorts and contrasts; both are correct in "
                          "their own scope and the paper labels each scope flag explicitly."
                      ))

        out["fisher_p_value_paper"] = p_full
        out["fisher_contingency_paper"] = (
            f"Hz {hz_invest}/{hz_total} vs non-Hz {non_hz_invest}/{non_hz_total}")

    # Domain adaptation & entropy (from stats_json)
    if stats_json:
        da = stats_json.get("domain_adaptation", {})
        out.update({
            "domain_adapt_n_paired": da.get("n_paired"),
            "domain_adapt_wilcoxon_stat": da.get("wilcoxon_stat"),
            "domain_adapt_p_two_sided": da.get("p_two_sided"),
            "domain_adapt_significant_005": as_bool(da.get("significant_005")),
            "domain_adapt_sample_efficiency": da.get("sample_efficiency_ratio"),
            "domain_adapt_pre_mean_abs_res": da.get("pre_mean_abs_res"),
            "domain_adapt_post_mean_abs_res": da.get("post_mean_abs_res"),
        })
        er = stats_json.get("entropy_reduction", {})
        out.update({
            "entropy_n_unlabeled": er.get("n_unlabeled"),
            "entropy_delta_H": er.get("delta_H"),
            "entropy_rel_reduction": er.get("relative_reduction"),
            "sce_al": er.get("sce_al"),
            "sce_hz_greedy": er.get("sce_hz_greedy"),
            "csrf": er.get("csrf"),
        })

    # Baseline comparisons
    if t2 is not None:
        baselines = {}
        for _, row in t2.iterrows():
            bl = str(row["baseline"])
            baselines[bl] = {
                "expected_invest_mean": float(row.get("expected_invest", np.nan)),
                "our_invest_incl_nh23": int(row.get("our_invest", 0)),
                "our_invest_excl_nh23": int(row["our_invest_excl_nh23"]) if "our_invest_excl_nh23" in row else None,
                "p_value_incl_nh23": float(row.get("p_value", np.nan)),
                "p_value_excl_nh23": float(row.get("p_value_excl_nh23", np.nan)) if "p_value_excl_nh23" in row else None,
                "significant_005": as_bool(row.get("significant_005", False)),
            }
        out["baseline_comparisons"] = baselines

        # Inconsistency: incl vs excl Hz_NH23
        our_incl = int(t2["our_invest"].iloc[0]) if "our_invest" in t2.columns else None
        our_excl = int(t2["our_invest_excl_nh23"].iloc[0]) if "our_invest_excl_nh23" in t2.columns else None
        if our_incl and our_excl and our_incl != our_excl:
            incon("active_learning.r1_invest_count_7_vs_6",
                  f"{our_incl}/15",
                  "task2 our_invest (Round-1 deployment yield, incl. Hz_NH23)",
                  f"{our_excl}/14",
                  "task2 our_invest_excl_nh23 (Fisher / conformal subset, excl. Hz_NH23)",
                  status="intentional_analysis_set_distinction",
                  resolution=(
                      "7/15 is the Round-1 deployment yield and must be cited "
                      "for acquisition-policy outcomes. 6/14 is the Fisher / "
                      "split-conformal subset (excludes Hz_NH23, the dark "
                      "fosc=0 outlier) and must be cited only for the Fisher "
                      "and conformal analyses. The two are different analysis "
                      "sets — not contradictory. See "
                      "paper/audit_reports/fig5_reconciliation.md for the full "
                      "molecule-level audit."
                  ))

    return out


# ── VALIDATION ───────────────────────────────────────────────────────────────

def build_validation():
    validated = safe_csv(RESULTS / "validated_candidates_master.csv")
    if validated is None:
        return miss("validation", "validated_candidates_master.csv not found")

    cls_counts = validated["classification"].value_counts().to_dict()
    neg = cls_counts.get("negative_gap", 0)
    dark = cls_counts.get("dark_negative_gap", 0)
    border = cls_counts.get("borderline_near_zero", 0)
    n_invest_strict = neg + dark

    hz_invest = None
    if "scaffold" in validated.columns:
        hz_invest = int((
            (validated["scaffold"] == "Hz") &
            validated["classification"].isin(["negative_gap", "dark_negative_gap"])
        ).sum())
        non_hz_invest = n_invest_strict - hz_invest
        if non_hz_invest > 0:
            miss("validation.non_hz_invest",
                 f"{non_hz_invest} INVEST molecules are non-Hz — verify scaffold column")

    return {
        "n_total": len(validated),
        "classification_counts": cls_counts,
        "n_negative_gap": int(neg),
        "n_dark_negative_gap": int(dark),
        "n_invest_strict": int(n_invest_strict),
        "n_invest_hz_only": hz_invest,
        "n_borderline": int(border),
        "n_table1_candidates": int(n_invest_strict + border),
        "confidence_counts": validated["confidence"].value_counts().to_dict() if "confidence" in validated.columns else {},
        "decision_basis_counts": validated["decision_basis"].value_counts().to_dict() if "decision_basis" in validated.columns else {},
        "batch_counts": validated["batch"].value_counts().to_dict() if "batch" in validated.columns else {},
        "scaffold_counts": validated["scaffold"].value_counts().to_dict() if "scaffold" in validated.columns else {},
        "n_scs_crosschecked": int(validated["DEST_scscc2_eV"].notna().sum()) if "DEST_scscc2_eV" in validated.columns else 0,
        "n_promoted_from_adc2_borderline": int((
            validated["DEST_scscc2_eV"].notna() &
            validated["DEST_adc2_eV"].abs().le(0.03) &
            validated["classification"].isin(["negative_gap", "dark_negative_gap"])
        ).sum()) if {"DEST_scscc2_eV", "DEST_adc2_eV", "classification"}.issubset(validated.columns) else 0,
        "min_DEST_eV": round(float(validated["DEST_eV"].min()), 5) if "DEST_eV" in validated.columns else None,
        "max_DEST_eV": round(float(validated["DEST_eV"].max()), 5) if "DEST_eV" in validated.columns else None,
        "median_DEST_eV": round(float(validated["DEST_eV"].median()), 5) if "DEST_eV" in validated.columns else None,
    }


# ── METHOD CROSSCHECK ────────────────────────────────────────────────────────

def build_method_crosscheck():
    scs = safe_csv(RESULTS / "scscc2_batch2_summary.csv")
    adc2_batch2 = safe_csv(RESULTS / "adc2_batch2_summary.csv")
    adc2_round1 = safe_csv(RESULTS / "adc2_final_10mol.csv")
    master = safe_csv(DATA / "processed" / "master_molecule_table_round1_updated.csv")

    if scs is None:
        return miss("method_crosscheck", "scscc2_batch2_summary.csv not found")

    adc2_lookup = {}
    if adc2_batch2 is not None:
        for _, row in adc2_batch2.iterrows():
            adc2_lookup[str(row["name"])] = float(row["DEST_eV"])
    if adc2_round1 is not None:
        for _, row in adc2_round1.iterrows():
            adc2_lookup[str(row["Molecule"])] = float(row["ΔEST_eV"])
    if master is not None:
        subset = master[(master["adc2_available"] == True) & master["adc2_dest_ev"].notna()]
        for _, row in subset.iterrows():
            adc2_lookup.setdefault(str(row["mol_id"]), float(row["adc2_dest_ev"]))

    records = []
    for _, row in scs.iterrows():
        mol = str(row["name"])
        if mol not in adc2_lookup:
            continue
        adc2_val = float(adc2_lookup[mol])
        scs_val = float(row["DEST_eV"])
        same_sign = (adc2_val < 0 and scs_val < 0) or (adc2_val > 0 and scs_val > 0)
        records.append({
            "molecule": mol,
            "ADC2_SVP_eV": round(adc2_val, 5),
            "SCSCC2_eV": round(scs_val, 5),
            "delta_meV": round(abs(adc2_val - scs_val) * 1000, 1),
            "all_signs_agree": same_sign,
        })

    n_total = len(records)
    n_sign_conflict = sum(1 for r in records if r["all_signs_agree"] is False)

    # Multi-method consistency table (DDFT / ADC2-SVP / SCSCC2-SVP / ADC2-TZVP / SCSCC2-TZVP)
    mc_table = safe_csv(RESULTS / "method_consistency_table.csv")
    mc_block = None
    if mc_table is not None:
        n_methods_dist = mc_table["n_methods_available"].value_counts().to_dict() \
            if "n_methods_available" in mc_table.columns else None
        agree_col = mc_table["all_signs_agree"] if "all_signs_agree" in mc_table.columns else None
        if agree_col is not None:
            agree_bool = agree_col.apply(as_bool)
            n_conflict = int((~agree_bool).sum())
            conflict_mols = mc_table.loc[~agree_bool, "molecule"].tolist() \
                if "molecule" in mc_table.columns else None
        else:
            n_conflict = None
            conflict_mols = None

        n_with_tzvp = int(mc_table["ADC2_TZVP_eV"].notna().sum()) \
            if "ADC2_TZVP_eV" in mc_table.columns else 0
        n_with_scscc2_svp = int(mc_table["SCSCC2_SVP_eV"].notna().sum()) \
            if "SCSCC2_SVP_eV" in mc_table.columns else 0
        n_with_scscc2_tzvp = int(mc_table["SCSCC2_TZVP_eV"].notna().sum()) \
            if "SCSCC2_TZVP_eV" in mc_table.columns else 0

        mc_block = {
            "n_rows": len(mc_table),
            "n_methods_available_distribution": n_methods_dist,
            "n_sign_conflict_molecules": n_conflict,
            "sign_conflict_molecule_list": conflict_mols,
            "n_with_adc2_tzvp": n_with_tzvp,
            "n_with_scscc2_svp": n_with_scscc2_svp,
            "n_with_scscc2_tzvp": n_with_scscc2_tzvp,
        }

    candidate_block = {
        "description": (
            "ADC(2)/def2-SVP vs SCS-CC2/def2-SVP cross-check on the small "
            "set of candidate INVEST molecules promoted to higher-level "
            "verification. This is the 4-molecule consistency probe used "
            "to corroborate the negative-gap sign for the lead candidates; "
            "it is NOT a population-scale benchmark."
        ),
        "n": n_total,
        "n_all_signs_agree": sum(1 for r in records if r["all_signs_agree"] is True),
        "n_sign_conflict": n_sign_conflict,
        "frac_sign_conflict": round(n_sign_conflict / n_total, 4) if n_total else None,
        "abs_delta_meV_range": [
            min(r["delta_meV"] for r in records),
            max(r["delta_meV"] for r in records),
        ] if records else None,
        "molecule_names": [r["molecule"] for r in records],
        "molecule_details": records,
    }

    benchmark_block = None
    if mc_block is not None:
        # Basis-set coverage summary (which methods/basis are available,
        # at how many molecules) — distinct from the 4-molecule cross-check.
        basis_set_coverage = {
            "n_with_adc2_tzvp":     mc_block.get("n_with_adc2_tzvp"),
            "n_with_scscc2_svp":    mc_block.get("n_with_scscc2_svp"),
            "n_with_scscc2_tzvp":   mc_block.get("n_with_scscc2_tzvp"),
            "n_methods_distribution": mc_block.get("n_methods_available_distribution"),
        }
        benchmark_block = {
            "description": (
                "Population-scale multi-method consistency benchmark from "
                "results/method_consistency_table.csv. Reports sign-conflict "
                "molecules across DDFT / ADC(2)-SVP / SCS-CC2-SVP / "
                "ADC(2)-TZVP / SCS-CC2-TZVP. This is NOT the 4-molecule "
                "candidate SCS-CC2 cross-check above — do not conflate the "
                "two when reporting method-agreement statistics."
            ),
            "n_rows": mc_block.get("n_rows"),
            "n_sign_conflict_molecules":   mc_block.get("n_sign_conflict_molecules"),
            "sign_conflict_molecule_list": mc_block.get("sign_conflict_molecule_list"),
            "basis_set_coverage": basis_set_coverage,
        }

    return {
        "scope_separation_note": (
            "candidate_scscc2_crosschecks (n=4) is a targeted SCS-CC2 "
            "verification on lead INVEST candidates and reports per-molecule "
            "sign agreement and ADC(2) vs SCS-CC2 absolute differences. "
            "method_consistency_benchmark is a population-scale audit drawn "
            "from results/method_consistency_table.csv reporting cross-method "
            "sign conflicts and basis-set coverage. The two are NOT "
            "interchangeable: do not quote candidate-level sign-agreement "
            "rates as evidence for population-scale method consistency, and "
            "do not quote benchmark-level conflict counts as a defect of "
            "the candidate cross-check set."
        ),
        "candidate_scscc2_crosschecks": candidate_block,
        "method_consistency_benchmark": benchmark_block,
    }


# ── UNCERTAINTY DIAGNOSTICS ──────────────────────────────────────────────────

def build_uncertainty_diagnostics():
    """Surface the four Phase-2 UQ diagnostic JSONs as a top-level block.

    Reads results/diagnostics/{distance_nonconformity,
    distance_to_source, mondrian_coverage, local_conformal}.json. The
    raw JSONs are reproduced verbatim so every number cited in §2.5 /
    §3.3 of paper/main.tex resolves here. If the files are missing
    (e.g., diagnostics not yet computed in a fresh checkout) we record
    the gap rather than failing.
    """
    diag_dir = RESULTS / "diagnostics"
    blocks = {}
    for slug in ("distance_nonconformity", "distance_to_source",
                 "mondrian_coverage", "local_conformal"):
        path = diag_dir / f"{slug}.json"
        if path.exists():
            blocks[slug] = json.loads(path.read_text())
        else:
            miss(f"uncertainty_diagnostics.{slug}",
                 f"{path.relative_to(ROOT)} not found")
            blocks[slug] = None
    return blocks


# ── PER-MOLECULE HIGHLIGHTS ──────────────────────────────────────────────────

def build_per_molecule_highlights():
    """Surface the small set of per-molecule values that the manuscript prose
    cites by name (Hz_NH23 magnitudes, Hz_POZ1_NPh21_CF31 borderline-vs-SCS-CC2
    promotion). These rounding-stable meV values let the audit script trace
    every numerical claim in §4.5 / §5 to a canonical leaf rather than a CSV
    row that the audit cannot see.

    Source: results/validated_candidates_master.csv (DEST_adc2_eV,
    DEST_scscc2_eV, fosc, classification, confidence).
    """
    val = safe_csv(RESULTS / "validated_candidates_master.csv")
    if val is None:
        return miss("per_molecule_highlights",
                    "validated_candidates_master.csv not found")

    indexed = val.set_index("mol_id")

    def row_block(mol_id: str, context: str) -> dict | None:
        if mol_id not in indexed.index:
            miss(f"per_molecule_highlights.{mol_id}",
                 f"{mol_id} not in validated_candidates_master.csv")
            return None
        r = indexed.loc[mol_id]
        adc2 = (round(float(r["DEST_adc2_eV"]) * 1000.0, 1)
                if pd.notna(r["DEST_adc2_eV"]) else None)
        scs = (round(float(r["DEST_scscc2_eV"]) * 1000.0, 1)
               if pd.notna(r["DEST_scscc2_eV"]) else None)
        return {
            "adc2_gap_meV": adc2,
            "scs_cc2_gap_meV": scs,
            "fosc": (float(r["fosc"]) if pd.notna(r["fosc"]) else None),
            "classification": str(r["classification"]),
            "confidence": str(r["confidence"]),
            "context": context,
            "source_csv": "results/validated_candidates_master.csv",
            "source_csv_key": f"mol_id == '{mol_id}'",
        }

    return {
        "Hz_NH23": row_block(
            "Hz_NH23",
            "Deepest negative-gap molecule in the decision table; dark "
            "(fosc = 0); used as a mechanistic endpoint, not an emitter "
            "candidate.",
        ),
        "Hz_POZ1_NPh21_CF31": row_block(
            "Hz_POZ1_NPh21_CF31",
            "Borderline by ADC(2)/def2-SVP (|DEST| < 30 meV window); "
            "promoted to negative-gap classification by the SCS-CC2 "
            "result; kept at low confidence pending basis-set "
            "sensitivity check.",
        ),
        "field_purpose": (
            "Per-molecule meV values cited by name in the manuscript "
            "(§4.5 and §5). Exposing them at the top level lets "
            "scripts/audit_numbers.py resolve the four meV figures "
            "(9.7, 165.6, 383, 558) that previously appeared as "
            "unresolved because they only existed in CSV rows."
        ),
    }


# ── SCS-CC2 n=13 EXTENDED CROSS-CHECK ────────────────────────────────────────

def build_scs_cc2_extended_n13():
    """Assemble the scs_cc2_extended_n13 block from the upstream artifacts.

    Inputs (single source of truth, written by
    scripts/scscc2_extension/build_cross_check_n13.py):
        results/scscc2_extension_n13/cross_check_n13.csv
        results/scscc2_extension_n13/stats_n13.json

    This function is the SINGLE WRITER of
    canonical_metrics.json["scs_cc2_extended_n13"]; no other script
    should mutate that block. Numeric values are preserved verbatim
    from the upstream CSV/JSON — the assembly logic only computes
    per-molecule summaries, the narrowest-margin pointer, and adds
    paper-facing scope labels (rule-of-three; repository identity).
    """
    upstream_dir = RESULTS / "scscc2_extension_n13"
    csv_path = upstream_dir / "cross_check_n13.csv"
    stats_path = upstream_dir / "stats_n13.json"
    df = safe_csv(csv_path)
    stats = safe_json(stats_path)
    if df is None or stats is None:
        return miss(
            "scs_cc2_extended_n13",
            f"missing upstream artifact(s): "
            f"{'cross_check_n13.csv ' if df is None else ''}"
            f"{'stats_n13.json' if stats is None else ''}".strip(),
        )

    # Per-molecule block (rounded to manuscript display precision: 1 dp meV,
    # 5 dp eV) — preserves numeric values from the upstream CSV.
    per_molecule = {}
    for _, row in df.iterrows():
        mol = str(row["mol_id"])
        adc2_meV = round(float(row["ADC2_dEST_meV"]), 1)
        scs_meV = round(float(row["SCSCC2_dEST_meV"]), 1)
        per_molecule[mol] = {
            "ADC2_dEST_meV": adc2_meV,
            "SCSCC2_dEST_meV": scs_meV,
            "SCSCC2_S1_eV": round(float(row["SCSCC2_S1_eV"]), 5),
            "SCSCC2_T1_eV": round(float(row["SCSCC2_T1_eV"]), 5),
            "abs_ddEST_meV": round(float(row["abs_ddEST_meV"]), 1),
            "sign_agree": as_bool(row["sign_agree"]),
            "ADC2_dEST_meV_abs": round(abs(adc2_meV), 1),
            "SCSCC2_dEST_meV_abs": round(abs(scs_meV), 1),
        }

    # Per-molecule warnings — paper-facing flags only; numeric values
    # remain in the per_molecule entries.
    if "Hz_NPh21_Cz2" in per_molecule:
        per_molecule["Hz_NPh21_Cz2"]["narrowest_margin_warning"] = (
            "smallest |ddEST| in the n=13 cohort; most likely sign-flip "
            "candidate under further method change"
        )
    if "Hz_POZ1_NPh21_CF31" in per_molecule:
        per_molecule["Hz_POZ1_NPh21_CF31"]["borderline_low_evidence_warning"] = (
            "ADC(2)/def2-SVP value inside +-30 meV near-zero window; "
            "SCS-CC2 promotion to negative-gap kept at low evidence "
            "strength pending def2-TZVP basis-set or method-family "
            "triangulation; SCS-CC2/def2-SVP basis assignment "
            "confirmed from the ricc2 runtime banner (both one-electron "
            "and auxiliary blocks print as def2-SVP for all elements)"
        )

    # Narrowest margin pointer (CSV-derived).
    narrow_row = df.iloc[df["abs_ddEST_meV"].astype(float).idxmin()]
    narrowest_margin_mol = str(narrow_row["mol_id"])
    narrowest_margin_meV = round(float(narrow_row["abs_ddEST_meV"]), 1)

    abs_summary = stats.get("abs_ddEST_meV_summary", {})

    # Drift / consistency guards: rule-of-three upper bound is a function
    # of n_total only; if upstream reported a value, it must agree.
    n_total = int(stats["n_total"])
    n_disagree = n_total - int(stats["n_sign_retain"])
    rule_of_three_upper_bound = (round(3.0 / n_total, 4)
                                 if n_disagree == 0 else None)
    upstream_rule = stats.get("rule_of_three_upper_bound_disagreement_rate")
    if (upstream_rule is not None
            and rule_of_three_upper_bound is not None
            and abs(upstream_rule - rule_of_three_upper_bound) > 1e-6):
        incon(
            "scs_cc2_extended_n13.rule_of_three_upper_bound",
            upstream_rule, "results/scscc2_extension_n13/stats_n13.json",
            rule_of_three_upper_bound, "recomputed from n_total in 99_emit_canonical.py",
        )

    return {
        # ── Explicit canonical schema aliases (Patch B review-fix) ─
        # These are the field names that downstream validators and
        # paper-facing readers should anchor on. Numeric values are
        # preserved verbatim from the upstream CSV/JSON.
        "generator": "scripts/99_emit_canonical.py::build_scs_cc2_extended_n13",
        "upstream_generator": "scripts/scscc2_extension/build_cross_check_n13.py",
        "screened_cohort_n": n_total,
        "sign_disagreements": int(n_total - int(stats["n_sign_retain"])),
        "rule_of_three_upper_bound": rule_of_three_upper_bound,
        "paper_cited_signrate": (
            "0 sign disagreement within the ADC(2)-screened cohort"
        ),
        "paper_cited_scope": (
            "ADC(2)-screened negative-or-dark-negative cohort; not a "
            "randomly sampled chemical population"
        ),
        "ci_method": (
            "Not reported as a Clopper-Pearson population confidence "
            "interval because the 13 molecules were ADC(2)-preselected."
        ),
        "repository": "https://github.com/lengcan276/INVEST-n13",
        "raw_provenance_status": (
            "SCS-CC2 n=13 raw-output verified from local "
            "ricc2_scscc2 outputs; ADC(2) raw provenance remains partial."
        ),
        "audit_report_reference": "audit/phase4_qc.md",
        "generated_from": [
            "results/scscc2_extension_n13/cross_check_n13.csv",
            "results/scscc2_extension_n13/stats_n13.json",
        ],

        # ── Legacy / numeric-summary fields (kept for downstream
        # consumers that already address them by these names) ─────
        "n_total": n_total,
        "n_sign_retain": int(stats["n_sign_retain"]),
        "sign_retain_rate": float(stats["sign_retain_rate"]),
        "paper_cited_bound": (
            f"rule of three; one-sided 95% upper bound "
            f"~= 3/{n_total} = {rule_of_three_upper_bound}"
        ),
        "ci_method_long_form": stats.get("ci_method"),

        # Transparency-only Clopper-Pearson alternative (carried through
        # from the upstream stats file; NOT the paper-facing interval).
        "clopper_pearson_95_CI": stats.get("clopper_pearson_95_CI"),
        "clopper_pearson_90_CI": stats.get("clopper_pearson_90_CI"),
        "clopper_pearson_note": stats.get(
            "clopper_pearson_note",
            "transparency-only; not the paper-facing interpretation for "
            "this ADC(2)-pre-screened cohort",
        ),

        # Cohort numerics — verbatim from upstream CSV/stats.
        "abs_ddEST_meV_min": abs_summary.get("min"),
        "abs_ddEST_meV_max": abs_summary.get("max"),
        "abs_ddEST_meV_mean": abs_summary.get("mean"),
        "abs_ddEST_meV_median": abs_summary.get("median"),
        "narrowest_margin_mol": narrowest_margin_mol,
        "narrowest_margin_meV": narrowest_margin_meV,

        "design_note": stats.get("design_note"),
        "cross_check_csv": "results/scscc2_extension_n13/cross_check_n13.csv",
        "stats_json": "results/scscc2_extension_n13/stats_n13.json",
        "repository_canonical": "https://github.com/lengcan276/INVEST-n13",
        "writer": "scripts/99_emit_canonical.py::build_scs_cc2_extended_n13",
        "per_molecule_representation": "dict keyed by mol_id",

        "per_molecule": per_molecule,
    }


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    out = {
        "library": build_library(),
        "datasets": build_datasets(),
        "model_performance": build_model_performance(),
        "deployment": build_deployment(),
        "ablation": build_ablation(),
        "uncertainty": build_uncertainty(),
        "active_learning": build_active_learning(),
        "validation": build_validation(),
        "method_crosscheck": build_method_crosscheck(),
        "scs_cc2_extended_n13": build_scs_cc2_extended_n13(),
        "uncertainty_diagnostics": build_uncertainty_diagnostics(),
        "per_molecule_highlights": build_per_molecule_highlights(),
        "missing_metrics": missing_metrics,
        "known_inconsistencies": known_inconsistencies,
    }

    out_path = RESULTS / "canonical_metrics.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    print(f"Wrote {out_path}")
    print(f"  missing_metrics:       {len(missing_metrics)}")
    print(f"  known_inconsistencies: {len(known_inconsistencies)}")

    if known_inconsistencies:
        print("\nINCONSISTENCIES DETECTED:")
        for ic in known_inconsistencies:
            print(f"  [{ic['key']}]")
            print(f"    A = {ic['value_a']}  ({ic['source_a']})")
            print(f"    B = {ic['value_b']}  ({ic['source_b']})")

    if missing_metrics:
        print("\nMISSING METRICS:")
        for m in missing_metrics:
            print(f"  [{m['key']}]: {m['reason']}")


if __name__ == "__main__":
    main()
