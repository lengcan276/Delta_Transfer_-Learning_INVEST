#!/usr/bin/env python3
"""emit_figure_caption_data.py

Generate figures/caption_data/*.json for every paper figure from the
single source of truth (results/canonical_metrics.json) plus the few
raw files that hold per-molecule detail.

Output schema (every figure):
    figure_id
    source_data_files
    sample_size
    key_numbers
    exclusions_or_filters
    visualization_caveats
    manuscript_claims_allowed
    manuscript_claims_not_allowed

Mandatory enforcement rules (encoded as caveats / not-allowed claims):
    1. Fig0_workflow:        SCS-CC2 cross-checks = 4 selected molecules,
                             not all 13 candidates.
    2. Fig1_ablation:        2.8 meV difference is NOT statistically
                             significant.
    3. Fig2_uq_shift:        n_test = 14, conformal-90 coverage = 5/14
                             = 35.7%, with small-sample Wilson CI caveat.
    4. Fig3_classification:  state how fosc = 0 is rendered on log-scale.
    5. Fig4_crosscheck:      keep candidate_scscc2_crosschecks separate
                             from method_consistency_benchmark.
    6. Fig5_al_value:        cite the 7/15 vs 6/14 reconciliation rule
                             and defer to fig5_reconciliation.md.
    7. Fig6_library:         state whether all 155 target molecules are
                             included or filtered.

This script DOES NOT modify paper/main.tex.

Run from project root:
    python3 scripts/emit_figure_caption_data.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ROUND1 = RESULTS / "round1_eval"
DATA = ROOT / "data" / "processed"
CAPTIONS = ROOT / "figures" / "caption_data"

CANONICAL = RESULTS / "canonical_metrics.json"
VALIDATED = RESULTS / "validated_candidates_master.csv"
MASTER = DATA / "master_molecule_table.csv"

FIG5_RECON_REPORT = "paper/audit_reports/fig5_reconciliation.md"


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required input missing: {path}")
    return path


def round_meV(x: float | None, digits: int = 3) -> float | None:
    if x is None:
        return None
    return round(float(x) * 1000.0, digits)


def write_json(obj: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# ── builders ─────────────────────────────────────────────────────────────

def build_fig0_workflow(canon: dict) -> dict:
    lib = canon["library"]
    val = canon["validation"]
    ds = canon["datasets"]
    mc_cand = canon["method_crosscheck"]["candidate_scscc2_crosschecks"]

    n_invest_strict = int(val["n_invest_strict"])
    n_borderline = int(val["n_borderline"])
    n_table1 = int(val["n_table1_candidates"])
    n_scs = int(mc_cand["n"])

    return {
        "figure_id": "Fig0_workflow",
        "source_data_files": [
            "results/canonical_metrics.json",
            "data/processed/master_molecule_table.csv",
            "results/validated_candidates_master.csv",
            "results/scscc2_batch2_summary.csv",
        ],
        "sample_size": {
            "n_source_dataset": int(lib["n_source_dataset"]),
            "n_target_library": int(lib["n_target_domain"]),
            "n_invest_labeled_source": int(lib["n_invest_labeled_pollice_source"]),
            "round1_deployment": int(ds["round1_deployment_n"]),
            "post_round1_excl_nh23": int(ds["post_round1_excl_nh23_n"]),
            "validated_total": int(val["n_total"]),
            "table1_candidates": n_table1,
            "scs_cc2_crosschecks": n_scs,
        },
        "key_numbers": {
            "target_scaffold_counts": lib["target_scaffold_counts"],
            "validated_invest_strict": n_invest_strict,
            "validated_borderline_near_zero": n_borderline,
            "n_table1_candidates": n_table1,
            "round1_deployment_n": int(ds["round1_deployment_n"]),
            "round2_selected_n": int(ds["round2_selected_n"]),
            "scscc2_crosscheck_molecule_names": mc_cand["molecule_names"],
            "scscc2_crosscheck_abs_delta_meV_range":
                mc_cand["abs_delta_meV_range"],
        },
        "exclusions_or_filters": [
            "Workflow boxes are schematic summaries, not one-to-one molecule "
            "inventories.",
            "Post-round1 LOO-CV uses the 33-molecule set excluding Hz_NH23.",
            f"SCS-CC2 verification is restricted to {n_scs} selected lead "
            "candidates (Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, "
            "Hz_POZ1_NPh21_CF31, Hz_NH23). It is NOT a population-scale "
            "method audit.",
        ],
        "visualization_caveats": [
            f"SCS-CC2 cross-checks are n = {n_scs} selected molecules, NOT "
            f"all {n_table1} Table-1 candidates and NOT all "
            f"{val['n_total']} validated molecules.",
            "The validation box aggregates ADC(2)-level validation with a "
            "much smaller SCS-CC2 subset; the two should be visually "
            "distinguished in the diagram.",
        ],
        "manuscript_claims_allowed": [
            f"The workflow spans an {lib['n_source_dataset']}-row source "
            f"dataset, a {lib['n_target_domain']}-molecule target library, "
            f"{ds['round1_deployment_n']} Round-1 queries, and "
            f"{val['n_total']} ADC(2)-validated molecules.",
            f"Higher-level SCS-CC2 evidence is available only for the "
            f"selected {n_scs}-molecule subset.",
            "The workflow describes a closed-loop progression from "
            "screening to validation without claiming universal "
            "higher-level confirmation.",
        ],
        "manuscript_claims_not_allowed": [
            f"Do not state or imply that all {n_table1} Table-1 candidates "
            "(or all 13 INVEST-strict candidates) were SCS-CC2 "
            f"cross-checked. Only {n_scs} were.",
            "Do not treat the workflow schematic as a quantitative "
            "substitute for the underlying tables.",
            "Do not equate SCS-CC2 cross-check coverage with method "
            "consistency across the full library.",
        ],
    }


def build_fig1_ablation(canon: dict) -> dict:
    abl = canon["ablation"]
    summary = abl["multiseed_summary"]
    paired = abl["paired_tests"]["paired_tests"]
    n_target = int(abl["paired_tests"].get("n_target", 33))
    n_seeds = int(abl["n_seeds"])

    full_mae_meV = round_meV(summary["full"]["MAE_mean_eV"])
    rdkit_mae_meV = round_meV(summary["rdkit_only"]["MAE_mean_eV"])
    full_minus_rdkit_meV = round(full_mae_meV - rdkit_mae_meV, 3)

    configs = []
    for cfg, v in summary.items():
        configs.append({
            "config": cfg,
            "MAE_meV": round_meV(v["MAE_mean_eV"]),
            "MAE_std_meV": round_meV(v["MAE_std_eV"]),
            "sign_accuracy": v["sign_acc_mean"],
            "invest_recall": v["INVEST_rec_mean"],
            "n_physics_features": v["n_physics_features"],
            "n_delta_features": v["n_delta_features"],
        })

    paired_summary = {}
    for cfg, t in paired.items():
        paired_summary[cfg] = {
            "comparison": t.get("comparison"),
            "p_value": t.get("p_value"),
            "significant_005": t.get("significant_005"),
            "deterministic_diff_eV": t.get("deterministic_diff"),
            "interpretation": t.get("interpretation"),
        }

    return {
        "figure_id": "Fig1_ablation",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/round1_eval/p0a_ablation_multiseed.csv",
            "results/round1_eval/p0a_ablation_paired_tests.json",
            "scripts/p0a_ablation_fixed.py",
        ],
        "sample_size": {
            "n_seeds": n_seeds,
            "n_target_molecules": n_target,
            "n_configs": len(configs),
            "evaluation": "LOO-CV on post-Round-1 target set "
                          "(excludes Hz_NH23)",
        },
        "key_numbers": {
            "configs": configs,
            "full_minus_rdkit_only_meV": full_minus_rdkit_meV,
            "shared_rdkit_features": int(
                abl["paired_tests"]["shared_features_n"]),
            "paired_tests": paired_summary,
        },
        "exclusions_or_filters": [
            "Authoritative ablation source is scripts/p0a_ablation_fixed.py "
            "with results/round1_eval/p0a_ablation_multiseed.csv.",
            "results/round1_eval/task3_ablation_results.csv is DEPRECATED "
            "(its source-target shared-coverage filter collapsed all "
            "configs to the same 54 RDKit features).",
            "Physics-feature ablation removes features only from the "
            "target-domain delta-correction model; the source model "
            "always uses the shared RDKit feature set.",
        ],
        "visualization_caveats": [
            f"LOO-CV is deterministic for this dataset: across all "
            f"{n_seeds} seeds the per-config MAE is identical "
            "(MAE_std = 0). Seed count therefore does NOT imply "
            "independent stochastic variation.",
            "Wilcoxon paired tests are reported for `no_stda` (p = 1.0, "
            "identical across seeds); the other comparisons collapse to "
            "n_eff = 1 deterministic differences and Wilcoxon is not "
            "applicable.",
            f"The full vs RDKit-only difference is "
            f"{full_minus_rdkit_meV:+.3f} meV; this is within numerical "
            "noise and NOT statistically significant.",
        ],
        "manuscript_claims_allowed": [
            "RDKit-only and physics-augmented configurations differ by a "
            f"few meV on the {n_target}-molecule LOO-CV set; the "
            "differences are within numerical noise.",
            "The ablation supports a conservative statement that the "
            "current physics descriptors did not produce a clear "
            "deployment-scale gain in this benchmark.",
            "Report MAE values together with `n_target = "
            f"{n_target}, excl. Hz_NH23` and `n_seeds = {n_seeds}, "
            "deterministic LOO-CV (std = 0)`.",
        ],
        "manuscript_claims_not_allowed": [
            "Do not describe the 2.8 meV (or any sub-5 meV) full-vs-"
            "RDKit-only gap as statistically significant.",
            "Do not report a Wilcoxon p-value for any comparison labeled "
            "`p_value: null` in paired_tests (those are deterministic, "
            "n_eff = 1).",
            "Do not cite results from results/round1_eval/"
            "task3_ablation_results.csv or its derivatives.",
            "Do not claim that adding the current physics features "
            "unequivocally improves accuracy.",
        ],
    }


def build_fig2_uq_shift(canon: dict) -> dict:
    uq = canon["uncertainty"]
    n_calib = int(uq["calibration_n"])
    n_test = int(uq["test_n"])
    cov90 = uq["coverage_by_nominal_level"]["0.9"]
    cov95 = uq["coverage_by_nominal_level"]["0.95"]
    p90 = float(cov90["conformal_test_coverage"])
    k90 = round(p90 * n_test)
    wilson = uq["conformal_90_coverage_wilson_ci_95"]

    return {
        "figure_id": "Fig2_uq_shift",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/round1_eval/p0b_conformal_calibration.json",
            "results/round1_eval/p0b_conformal_calibration.csv",
        ],
        "sample_size": {
            "calibration_n": n_calib,
            "test_n": n_test,
            "calibration_set":
                "pre-Round-1 split-conformal calibration (19 mols)",
            "test_set":
                "Round-1 deployment EXCLUDING Hz_NH23 (14 mols)",
        },
        "key_numbers": {
            "calibration_MAE_eV": uq["calibration_MAE_eV"],
            "test_MAE_eV": uq["test_MAE_eV"],
            "conformal_90_test_coverage": p90,
            "conformal_90_test_hits_over_n": f"{int(k90)}/{n_test}",
            "conformal_90_test_coverage_pct": round(p90 * 100, 1),
            "conformal_90_wilson_95_ci": wilson,
            "conformal_90_width_eV": cov90["conformal_width_eV"],
            "conformal_95_test_coverage":
                cov95["conformal_test_coverage"],
            "conformal_95_width_eV": cov95["conformal_width_eV"],
            "bootstrap_95_test_coverage":
                cov95["bootstrap_test_coverage"],
            "bootstrap_95_mean_width_eV":
                cov95["bootstrap_test_mean_width_eV"],
            "fixed_baseline_width_eV": uq["fixed_baseline_width_eV"],
            "coverage_by_nominal_level":
                uq["coverage_by_nominal_level"],
        },
        "exclusions_or_filters": [
            f"Test set is the Round-1 deployment EXCLUDING Hz_NH23 "
            f"(n = {n_test}). The 15-molecule deployment yield is "
            "reported separately and must NOT be used as the conformal "
            "test denominator.",
            f"Calibration set is the pre-Round-1 labeled target subset "
            f"(n = {n_calib}); it is the split-conformal calibration "
            "set, NOT the DFT 5-anchor TDDFT calibration.",
        ],
        "visualization_caveats": [
            f"Conformal-90 test coverage is {int(k90)}/{n_test} = "
            f"{p90*100:.1f}%. With n_test = {n_test} (< 30) this point "
            f"estimate has a wide Wilson 95% CI of "
            f"[{wilson[0]:.3f}, {wilson[1]:.3f}].",
            "Coverage bars at every nominal level must carry the small-"
            f"sample caveat: n_test = {n_test} only; CI overlap with "
            "nominal does NOT prove calibration.",
            "Bootstrap intervals achieve nominal coverage but at much "
            "wider intervals (see width columns); show both coverage "
            "AND width to avoid misleading the reader.",
        ],
        "manuscript_claims_allowed": [
            f"Split-conformal calibrated on n = {n_calib} pre-Round-1 "
            f"molecules; tested on n = {n_test} Round-1 deployments "
            "(Hz_NH23 excluded by design).",
            f"Conformal-90 test coverage {int(k90)}/{n_test} = "
            f"{p90*100:.1f}% (Wilson 95% CI "
            f"[{wilson[0]:.3f}, {wilson[1]:.3f}]) is well below the "
            "nominal 90% level, indicating distribution shift between "
            "the calibration and deployment subsets.",
            "Bootstrap intervals achieve nominal coverage but at "
            "substantially wider intervals than the conformal "
            "intervals.",
        ],
        "manuscript_claims_not_allowed": [
            f"Do not report conformal coverage without stating "
            f"n_test = {n_test} and the small-sample CI.",
            f"Do not use the 15-molecule deployment denominator for any "
            f"conformal coverage statement (use {n_test}).",
            "Do not claim the conformal predictor is well-calibrated "
            "from a single coverage point estimate; cite the Wilson CI.",
        ],
    }


def build_fig3_classification(canon: dict) -> dict:
    val = canon["validation"]
    df = pd.read_csv(VALIDATED)
    fosc_zero_mols = df.loc[df["fosc"].fillna(0).eq(0), "mol_id"].tolist()
    fosc_min_pos = float(df.loc[df["fosc"].fillna(0) > 0, "fosc"].min())
    fosc_max = float(df["fosc"].max())
    log_floor = 1e-4

    return {
        "figure_id": "Fig3_classification",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/validated_candidates_master.csv",
        ],
        "sample_size": {
            "n_total_validated": int(val["n_total"]),
            "n_invest_strict_negative_gap":
                int(val["n_negative_gap"]),
            "n_dark_negative_gap": int(val["n_dark_negative_gap"]),
            "n_invest_strict": int(val["n_invest_strict"]),
            "n_borderline_near_zero": int(val["n_borderline"]),
            "n_positive_gap":
                int(val["classification_counts"].get("positive_gap", 0)),
        },
        "key_numbers": {
            "classification_counts": val["classification_counts"],
            "scaffold_counts": val["scaffold_counts"],
            "min_DEST_eV": val["min_DEST_eV"],
            "max_DEST_eV": val["max_DEST_eV"],
            "median_DEST_eV": val["median_DEST_eV"],
            "fosc_zero_molecule_ids": fosc_zero_mols,
            "fosc_min_positive": fosc_min_pos,
            "fosc_max": fosc_max,
            "log_floor_for_zero_fosc": log_floor,
        },
        "exclusions_or_filters": [
            f"Panel uses the full {val['n_total']}-molecule validated "
            "cohort. No molecules are filtered out.",
            f"`dark_negative_gap` molecules ({val['n_dark_negative_gap']}) "
            "have ADC(2) ΔEST < 0 but fosc(S1) ≤ 1e-3 and are NOT "
            "OLED-emitter candidates by the M3 rule.",
        ],
        "visualization_caveats": [
            f"fosc = 0 molecules ({len(fosc_zero_mols)}: "
            f"{', '.join(fosc_zero_mols) or 'none'}) are plotted at the "
            f"explicit log-scale floor fosc = {log_floor:g}; the floor "
            "value MUST be stated in the figure caption.",
            "Zero-fosc points must be visually distinguished (e.g., open "
            "marker or '×' glyph) to avoid implying a measured non-zero "
            "fosc on log axes.",
            "Color alone (red/green) must not encode INVEST vs non-"
            "INVEST; pair with shape encoding for colorblind readers.",
        ],
        "manuscript_claims_allowed": [
            f"{val['n_invest_strict']} of {val['n_total']} validated "
            f"molecules satisfy ΔEST < 0 (negative-gap or dark-negative-"
            f"gap), and {val['n_borderline']} additional molecule(s) "
            "fall in the borderline near-zero region.",
            f"Dark INVEST molecules (fosc = 0) are plotted at the "
            f"log-scale floor fosc = {log_floor:g} for visibility.",
            "Cite per-class counts directly from "
            "canonical_metrics.validation.classification_counts.",
        ],
        "manuscript_claims_not_allowed": [
            "Do not silently drop fosc = 0 points from a log-scale "
            "scatter; either show them at the stated floor or move to "
            "a separate panel.",
            "Do not call dark_negative_gap molecules \"OLED emitter "
            "candidates\" — they fail the fosc > 1e-3 requirement (M3).",
            "Do not aggregate negative_gap and dark_negative_gap counts "
            "without naming them separately in the caption.",
        ],
    }


def build_fig4_crosscheck(canon: dict) -> dict:
    mc = canon["method_crosscheck"]
    cand = mc["candidate_scscc2_crosschecks"]
    bench = mc["method_consistency_benchmark"]

    return {
        "figure_id": "Fig4_crosscheck",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/scscc2_batch2_summary.csv",
            "results/method_consistency_table.csv",
        ],
        "sample_size": {
            "candidate_scscc2_crosschecks_n": int(cand["n"]),
            "method_consistency_benchmark_n":
                int(bench["n_rows"]) if bench else None,
        },
        "key_numbers": {
            "candidate_scscc2_crosschecks": {
                "n": int(cand["n"]),
                "n_all_signs_agree": int(cand["n_all_signs_agree"]),
                "n_sign_conflict": int(cand["n_sign_conflict"]),
                "abs_delta_meV_range": cand["abs_delta_meV_range"],
                "molecule_names": cand["molecule_names"],
                "molecule_details": cand["molecule_details"],
            },
            "method_consistency_benchmark": ({
                "n_rows": bench.get("n_rows"),
                "n_sign_conflict_molecules":
                    bench.get("n_sign_conflict_molecules"),
                "sign_conflict_molecule_list":
                    bench.get("sign_conflict_molecule_list"),
                "basis_set_coverage": bench.get("basis_set_coverage"),
            } if bench else None),
            "scope_separation_note": mc["scope_separation_note"],
        },
        "exclusions_or_filters": [
            f"candidate_scscc2_crosschecks contains exactly {cand['n']} "
            "lead INVEST candidates promoted to SCS-CC2 verification. "
            "It is NOT a population-scale benchmark.",
            "method_consistency_benchmark draws from "
            "results/method_consistency_table.csv and reports cross-"
            "method sign-conflict statistics for a different set of "
            "molecules.",
        ],
        "visualization_caveats": [
            f"Panels showing the {cand['n']}-molecule SCS-CC2 cross-check "
            "and panels showing the multi-method consistency benchmark "
            "must be visually separated and individually labeled with "
            "their respective n.",
            f"Absolute ADC(2)-vs-SCS-CC2 differences in the candidate "
            f"set span "
            f"{cand['abs_delta_meV_range'][0]:.1f}–"
            f"{cand['abs_delta_meV_range'][1]:.1f} meV; signs agree in "
            f"{cand['n_all_signs_agree']}/{cand['n']} molecules.",
            "Per M2, do NOT label SCS-CC2 as a 'gold standard' relative "
            "to ADC(2). Use phrases like 'higher-level correlated "
            "wavefunction reference' or 'independent SCS-CC2 "
            "verification'.",
        ],
        "manuscript_claims_allowed": [
            f"On the {cand['n']}-molecule candidate cross-check set, "
            f"ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for "
            f"{cand['n_all_signs_agree']}/{cand['n']} molecules with "
            f"absolute differences spanning "
            f"{cand['abs_delta_meV_range'][0]:.0f}–"
            f"{cand['abs_delta_meV_range'][1]:.0f} meV.",
            "The wider method_consistency_benchmark may be cited "
            "separately for cross-method sign-conflict statistics, "
            "with its own n and basis-set coverage.",
            "Higher-level SCS-CC2 evidence is described as 'independent "
            "verification' rather than 'gold standard'.",
        ],
        "manuscript_claims_not_allowed": [
            f"Do not report a single sign-agreement rate that mixes the "
            f"{cand['n']}-molecule candidate cross-check with the "
            "method_consistency_benchmark.",
            "Do not use 'gold standard' for ADC(2), SCS-CC2, or any "
            "non-CCSD(T) reference (M2).",
            "Do not extrapolate the candidate cross-check sign agreement "
            "to a population-scale claim about method transferability.",
        ],
    }


def build_fig5_al_value(canon: dict) -> dict:
    al = canon["active_learning"]
    ds = canon["datasets"]
    fisher_full = al["fisher_full_cohort"]
    fisher_r1 = al["fisher_r1_subset"]
    deploy_n = int(ds["round1_deployment_n"])
    fisher_n = int(ds["round1_conformal_test_n"])
    deploy_neg = int(canon["deployment"]["n_invest_actual"])
    fisher_neg = int(fisher_r1["hz_invest"]) + int(fisher_r1["ap_invest"])

    return {
        "figure_id": "Fig5_al_value",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/tables/round1_candidates_frozen.csv",
            "results/round1_eval/task1_deployment_detail.csv",
            "results/round1_eval/task1_learning_curve.csv",
            "results/round1_eval/task2_baseline_significance.csv",
            "results/round1_eval/stats_validation_results.json",
            "results/validated_candidates_master.csv",
            "results/audit/round1_reconciliation.csv",
            FIG5_RECON_REPORT,
        ],
        "sample_size": {
            "full_validated_cohort": int(canon["validation"]["n_total"]),
            "round1_frozen_candidates":
                int(ds["round1_frozen_candidates_n"]),
            "round1_deployment": deploy_n,
            "fisher_conformal_subset": fisher_n,
        },
        "key_numbers": {
            "deployment_total_queries": deploy_n,
            "deployment_negative_hits": deploy_neg,
            "fisher_subset_total": fisher_n,
            "fisher_subset_negative_hits": fisher_neg,
            "deployment_yield_string": f"{deploy_neg}/{deploy_n}",
            "fisher_subset_string": f"{fisher_neg}/{fisher_n}",
            "full_cohort_Hz_vs_nonHz": {
                "table": fisher_full["contingency_table"],
                "hz_invest": fisher_full["hz_invest"],
                "hz_total": fisher_full["hz_total"],
                "non_hz_invest": fisher_full["non_hz_invest"],
                "non_hz_total": fisher_full["non_hz_total"],
                "fisher_p_two_sided": fisher_full["p_value_two_sided"],
            },
            "round1_subset_Hz_vs_5AP": {
                "hz_invest": fisher_r1["hz_invest"],
                "hz_total": fisher_r1["hz_total"],
                "ap_invest": fisher_r1["ap_invest"],
                "ap_total": fisher_r1["ap_total"],
                "fisher_p_two_sided": fisher_r1["p_value"],
            },
            "baseline_p_values": al["baseline_comparisons"],
            "reconciliation_report": FIG5_RECON_REPORT,
        },
        "exclusions_or_filters": [
            f"Round-1 deployment yield uses n = {deploy_n} (includes "
            "Hz_NH23). Fisher / split-conformal subset uses n = "
            f"{fisher_n} (excludes Hz_NH23 — dark, fosc = 0, extreme "
            "residual that would dominate quantile-based UQ).",
            "Frozen candidate ranking lists "
            f"{ds['round1_frozen_candidates_n']} molecules; "
            f"{ds['round1_frozen_candidates_n'] - deploy_n} were not "
            "deployed in Round 1 (deferred to a later batch).",
            "Per the reconciliation report "
            f"({FIG5_RECON_REPORT}), the 7/15 and 6/14 numbers describe "
            "different analysis sets and must each be cited only in "
            "their own scope.",
        ],
        "visualization_caveats": [
            f"Deployment yield = {deploy_neg}/{deploy_n}. Fisher / "
            f"conformal subset = {fisher_neg}/{fisher_n}. Both must "
            "appear in the caption with their distinct n.",
            "Fisher tests are descriptive: the queried set is policy-"
            "selected, not random. p-values describe contrast within "
            "the queried set, not unbiased prevalence in the library.",
            "Active learning vs random / scaffold-stratified / Hz-"
            "greedy baselines are not significant (all p ≥ 0.97 in "
            "task2_baseline_significance.csv); do not claim AL beat "
            "random at p < 0.05.",
        ],
        "manuscript_claims_allowed": [
            f"Round-1 deployment outcome: {deploy_neg} INVEST hits "
            f"among {deploy_n} queried molecules.",
            f"Fisher subset (Hz vs 5AP, excluding Hz_NH23): "
            f"{fisher_neg} INVEST hits in {fisher_n}, two-sided Fisher "
            f"exact p = {fisher_r1['p_value']:.3f} (descriptive).",
            f"Full validated cohort (Hz vs non-Hz): two-sided Fisher "
            f"exact p = {fisher_full['p_value_two_sided']:.3f} "
            "(descriptive).",
            "Cite the reconciliation rule in "
            f"{FIG5_RECON_REPORT} whenever 7/15 or 6/14 appears.",
        ],
        "manuscript_claims_not_allowed": [
            f"Do not write \"{fisher_neg}/{deploy_n}\" or any 6-from-15 "
            "wording for the deployment yield.",
            f"Do not write \"{deploy_neg}/{fisher_n}\" or any 7-from-14 "
            "wording for the Fisher subset.",
            "Do not combine the 35-molecule full cohort denominator "
            f"with the {fisher_n}-molecule Fisher numerator (or vice "
            "versa).",
            "Do not claim Fisher significance establishes library-wide "
            "INVEST prevalence — the queried set is policy-selected.",
            "Do not claim active learning beat random sampling at "
            "p < 0.05 (it does not in any of the four task2 baselines).",
        ],
    }


def build_fig6_library(canon: dict) -> dict:
    lib = canon["library"]
    val = canon["validation"]
    n_target = int(lib["n_target_domain"])
    target_scaf = lib["target_scaffold_counts"]

    # Verify the target library is exactly the n_target rows of the master
    # (defensive sanity check; raises if upstream changes the master).
    if MASTER.exists():
        m = pd.read_csv(MASTER, usecols=["source_domain", "scaffold_family"])
        n_this_work = int((m["source_domain"] == "this_work").sum())
        if n_this_work != n_target:
            raise AssertionError(
                f"master_molecule_table.csv has {n_this_work} rows with "
                f"source_domain==this_work; canonical reports "
                f"n_target_domain={n_target}. These must agree."
            )

    return {
        "figure_id": "Fig6_library",
        "source_data_files": [
            "results/canonical_metrics.json",
            "data/processed/master_molecule_table.csv",
            "results/validated_candidates_master.csv",
        ],
        "sample_size": {
            "n_source_dataset": int(lib["n_source_dataset"]),
            "n_master_library": int(lib["n_molecules_master"]),
            "n_target_domain": n_target,
            "n_invest_labeled_source": int(lib["n_invest_labeled_pollice_source"]),
            "n_validated": int(val["n_total"]),
            "n_table1_candidates": int(val["n_table1_candidates"]),
        },
        "key_numbers": {
            "scaffold_family_counts": lib["scaffold_family_counts"],
            "target_scaffold_counts": target_scaf,
            "n_scaffold_families": int(lib["n_scaffold_families"]),
            "n_model_input_rows": int(lib["n_model_input_rows"]),
            "n_model_features_total": int(lib["n_model_features_total"]),
            "target_inclusion_rule":
                "All rows with source_domain == 'this_work' in "
                "master_molecule_table.csv are included.",
        },
        "exclusions_or_filters": [
            f"The figure shows ALL {n_target} target-domain molecules "
            "(Hz, 5AP, BN-PAH); no fosc / energy / scaffold filter is "
            "applied at the target-library level.",
            f"Background scaffold families "
            f"(pollice_heptazine_deriv: "
            f"{lib['scaffold_family_counts'].get('pollice_heptazine_deriv', 0)}, "
            f"literature: "
            f"{lib['scaffold_family_counts'].get('literature', 0)}, "
            f"reference: "
            f"{lib['scaffold_family_counts'].get('reference', 0)}) are "
            "shown for context but are NOT part of the target-domain "
            "screening pool.",
            f"Validated subset (n = {val['n_total']}) is a strict "
            "subset of the target library; molecules without ADC(2) "
            "validation are not annotated as validated.",
        ],
        "visualization_caveats": [
            f"State explicitly in the caption: \"All {n_target} target-"
            "domain molecules are included; no fosc / energy / scaffold "
            "filter is applied to this panel.\"",
            f"Counts per scaffold family must match canonical_metrics."
            f"library.target_scaffold_counts: {target_scaf}.",
            f"The {lib['n_molecules_master']}-molecule master library "
            f"is larger than the {n_target}-molecule target library; "
            "do not conflate the two denominators.",
        ],
        "manuscript_claims_allowed": [
            f"The target screening library comprises {n_target} "
            f"molecules across {len(target_scaf)} scaffold families "
            f"({target_scaf}).",
            f"The full master library has {lib['n_molecules_master']} "
            f"rows; the source dataset has {lib['n_source_dataset']} "
            f"rows with {lib['n_invest_labeled_pollice_source']} Pollice "
            "ADC(2)-labeled source-domain molecules "
            f"(plus {lib['n_invest_labeled_thiswork_target_preR1']} "
            "pre-Round-1 labelled target molecules).",
            f"All {n_target} target molecules are visualised in this "
            "figure without additional filtering.",
        ],
        "manuscript_claims_not_allowed": [
            f"Do not state \"{n_target} target molecules were "
            "filtered/screened\" — Fig 6 shows the full target library.",
            f"Do not use the {lib['n_molecules_master']}-row master "
            f"library or {lib['n_source_dataset']}-row source dataset "
            "as the denominator for target-library percentages.",
            f"Do not equate \"validated\" (n = {val['n_total']}) with "
            f"\"target-domain\" (n = {n_target}); the former is a "
            "sub-selection of the latter.",
        ],
    }


def build_figS1_structures(canon: dict) -> dict:
    val = canon["validation"]
    df = pd.read_csv(VALIDATED)
    table1_classes = ["negative_gap", "dark_negative_gap",
                      "borderline_near_zero"]
    t1 = df[df["classification"].isin(table1_classes)].copy()
    t1_ids = t1["mol_id"].tolist()
    n_table1 = int(val["n_table1_candidates"])
    n_dark = int(val["n_dark_negative_gap"])
    dark_ids = df.loc[df["classification"] == "dark_negative_gap",
                      "mol_id"].tolist()

    return {
        "figure_id": "FigS1_structures",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/validated_candidates_master.csv",
            "data/processed/master_molecule_table.csv",
        ],
        "sample_size": {
            "n_table1_candidates": n_table1,
            "n_negative_gap": int(val["n_negative_gap"]),
            "n_dark_negative_gap": n_dark,
            "n_borderline_near_zero": int(val["n_borderline"]),
        },
        "key_numbers": {
            "table1_molecule_ids": t1_ids,
            "dark_negative_gap_molecule_ids": dark_ids,
            "scaffold_breakdown_in_table1":
                t1["scaffold"].value_counts().to_dict(),
            "method_breakdown_in_table1":
                t1["method"].value_counts().to_dict()
                if "method" in t1.columns else None,
        },
        "exclusions_or_filters": [
            f"Figure includes the {n_table1} Table-1 candidates "
            "(negative_gap + dark_negative_gap + borderline_near_zero).",
            f"Positive-gap validated molecules "
            f"({val['classification_counts'].get('positive_gap', 0)}) "
            "are NOT shown; they are documented in the validated master "
            "table.",
        ],
        "visualization_caveats": [
            f"Molecule IDs in the figure must match `mol_id` in "
            f"results/validated_candidates_master.csv exactly: "
            f"{t1_ids}.",
            f"The {n_dark} dark_negative_gap molecule(s) "
            f"({dark_ids}) must be visually distinguished from the "
            "bright negative-gap molecules (e.g., shaded background or "
            "'dark' badge).",
            "If a structure is rotated/redrawn, preserve atom indices "
            "consistent with the SMILES recorded in the candidates "
            "table.",
        ],
        "manuscript_claims_allowed": [
            f"FigS1 shows all {n_table1} Table-1 candidates with their "
            "scaffold family, ADC(2) ΔEST, and classification.",
            f"Dark INVEST molecules ({n_dark}) are flagged as not "
            "viable OLED emitters (M3) but are retained in the figure "
            "for chemical-space context.",
        ],
        "manuscript_claims_not_allowed": [
            "Do not present FigS1 as a complete inventory of all "
            f"{val['n_total']} validated molecules; it is restricted to "
            f"the {n_table1} Table-1 candidates.",
            "Do not call dark_negative_gap molecules 'OLED emitter "
            "candidates' (M3 fails: fosc = 0).",
            "Do not introduce molecule abbreviations in this figure "
            "that are not defined in Table 1.",
        ],
    }


# ── orchestration ────────────────────────────────────────────────────────

BUILDERS = {
    "Fig0_workflow":       build_fig0_workflow,
    "Fig1_ablation":       build_fig1_ablation,
    "Fig2_uq_shift":       build_fig2_uq_shift,
    "Fig3_classification": build_fig3_classification,
    "Fig4_crosscheck":     build_fig4_crosscheck,
    "Fig5_al_value":       build_fig5_al_value,
    "Fig6_library":        build_fig6_library,
    "FigS1_structures":    build_figS1_structures,
}

REQUIRED_KEYS = {
    "figure_id",
    "source_data_files",
    "sample_size",
    "key_numbers",
    "exclusions_or_filters",
    "visualization_caveats",
    "manuscript_claims_allowed",
    "manuscript_claims_not_allowed",
}


def validate_payload(name: str, payload: dict) -> None:
    missing = REQUIRED_KEYS - payload.keys()
    if missing:
        raise ValueError(
            f"{name} is missing required keys: {sorted(missing)}"
        )


def enforce_rules(payloads: dict[str, dict]) -> None:
    """Hard checks for the 7 mandatory enforcement rules."""

    def assert_substring(name: str, field: str, needle: str) -> None:
        text = " ".join(str(x) for x in payloads[name].get(field, []))
        if needle.lower() not in text.lower():
            raise AssertionError(
                f"{name}.{field} must contain text mentioning {needle!r}; "
                f"got: {text[:240]}"
            )

    # Rule 1 — Fig0_workflow: SCS-CC2 = 4 selected molecules, not 13
    f0 = payloads["Fig0_workflow"]
    assert f0["sample_size"]["scs_cc2_crosschecks"] == 4, \
        "Fig0 scs_cc2_crosschecks must be 4"
    assert_substring("Fig0_workflow", "manuscript_claims_not_allowed",
                     "Only 4 were")

    # Rule 2 — Fig1_ablation: 2.8 meV NOT statistically significant
    assert_substring("Fig1_ablation", "manuscript_claims_not_allowed",
                     "2.8 meV")
    assert_substring("Fig1_ablation", "manuscript_claims_not_allowed",
                     "statistically significant")

    # Rule 3 — Fig2_uq_shift: n_test=14, 5/14 = 35.7%, Wilson caveat
    f2 = payloads["Fig2_uq_shift"]
    assert f2["sample_size"]["test_n"] == 14, \
        f"Fig2 test_n must be 14, got {f2['sample_size']['test_n']}"
    assert f2["key_numbers"]["conformal_90_test_hits_over_n"] == "5/14"
    assert abs(f2["key_numbers"]["conformal_90_test_coverage_pct"]
               - 35.7) < 0.1
    assert_substring("Fig2_uq_shift", "visualization_caveats", "Wilson")

    # Rule 4 — Fig3_classification: log-floor for fosc=0 declared
    f3 = payloads["Fig3_classification"]
    assert "log_floor_for_zero_fosc" in f3["key_numbers"]
    assert_substring("Fig3_classification", "visualization_caveats",
                     "log-scale floor")

    # Rule 5 — Fig4_crosscheck: candidate vs benchmark separation
    f4 = payloads["Fig4_crosscheck"]
    assert "candidate_scscc2_crosschecks" in f4["key_numbers"]
    assert "method_consistency_benchmark" in f4["key_numbers"]
    assert_substring("Fig4_crosscheck", "manuscript_claims_not_allowed",
                     "mixes")

    # Rule 6 — Fig5_al_value: 7/15 and 6/14 + reconciliation report
    f5 = payloads["Fig5_al_value"]
    assert f5["key_numbers"]["deployment_yield_string"] == "7/15"
    assert f5["key_numbers"]["fisher_subset_string"] == "6/14"
    assert_substring("Fig5_al_value", "exclusions_or_filters",
                     "fig5_reconciliation")

    # Rule 7 — Fig6_library: state whether all 155 included or filtered
    f6 = payloads["Fig6_library"]
    assert f6["sample_size"]["n_target_domain"] == 155, \
        f"Fig6 n_target_domain must be 155, got " \
        f"{f6['sample_size']['n_target_domain']}"
    assert_substring("Fig6_library", "visualization_caveats",
                     "no fosc / energy / scaffold filter")


def main() -> None:
    canon = json.loads(_require(CANONICAL).read_text())
    _require(VALIDATED)

    payloads = {name: build(canon) for name, build in BUILDERS.items()}
    for name, payload in payloads.items():
        validate_payload(name, payload)
    enforce_rules(payloads)

    for name, payload in payloads.items():
        path = CAPTIONS / f"{name}.json"
        write_json(payload, path)
        print(f"[OK] {path.relative_to(ROOT)}")

    print(f"\nWrote {len(payloads)} caption JSON files to "
          f"{CAPTIONS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
