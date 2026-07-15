#!/usr/bin/env python3
"""reconcile_active_learning_figure.py

Resolve the active-learning counting rule for Fig5_al_value.

Produces three artefacts that establish the single source of truth for the
"15 vs 14" and "7 vs 6" reconciliation:

  1. results/audit/round1_reconciliation.csv
  2. figures/caption_data/Fig5_al_value.json
  3. paper/audit_reports/fig5_reconciliation.md

This script DOES NOT modify paper/main.tex.

Inputs:
  results/canonical_metrics.json
  results/tables/round1_candidates_frozen.csv
  results/round1_eval/task2_baseline_significance.csv
  results/round1_eval/stats_validation_results.json
  results/validated_candidates_master.csv
  results/round1_eval/task1_deployment_detail.csv
  results/round1_eval/task1_learning_curve.csv

Run from project root:
    python3 scripts/reconcile_active_learning_figure.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ROUND1 = RESULTS / "round1_eval"

INPUTS = {
    "canonical": RESULTS / "canonical_metrics.json",
    "frozen":    RESULTS / "tables" / "round1_candidates_frozen.csv",
    "task2":     ROUND1 / "task2_baseline_significance.csv",
    "stats":     ROUND1 / "stats_validation_results.json",
    "validated": RESULTS / "validated_candidates_master.csv",
    "deploy":    ROUND1 / "task1_deployment_detail.csv",
    "learncurve": ROUND1 / "task1_learning_curve.csv",
}

OUTPUTS = {
    "csv":     RESULTS / "audit" / "round1_reconciliation.csv",
    "caption": ROOT / "figures" / "caption_data" / "Fig5_al_value.json",
    "report":  ROOT / "paper" / "audit_reports" / "fig5_reconciliation.md",
}

NEG_GAP_THRESHOLD_EV = 0.0
HZ_NH23 = "Hz_NH23"


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required input missing: {path}")
    return path


def load_inputs():
    canonical  = json.loads(_require(INPUTS["canonical"]).read_text())
    frozen     = pd.read_csv(_require(INPUTS["frozen"]))
    task2      = pd.read_csv(_require(INPUTS["task2"]))
    stats_json = json.loads(_require(INPUTS["stats"]).read_text())
    validated  = pd.read_csv(_require(INPUTS["validated"]))
    deploy     = pd.read_csv(_require(INPUTS["deploy"]))
    learn      = pd.read_csv(_require(INPUTS["learncurve"]))
    return canonical, frozen, task2, stats_json, validated, deploy, learn


def build_reconciliation(frozen: pd.DataFrame,
                         deploy: pd.DataFrame,
                         validated: pd.DataFrame) -> pd.DataFrame:
    """One row per molecule that participates in any Round-1 analysis set.

    Columns required by the spec:
        molecule_id, molecule_name, scaffold,
        selected_in_round1, included_in_deployment_yield,
        included_in_fisher_subset, included_in_conformal_test,
        adc2_gap_eV, classification, is_negative_gap,
        exclusion_reason_if_any
    """
    frozen_ids = set(frozen["mol_id"].tolist())
    deploy_ids = set(deploy["mol_id"].tolist())
    universe = sorted(frozen_ids | deploy_ids)

    val_lookup = validated.set_index("mol_id").to_dict(orient="index")
    frozen_lookup = frozen.set_index("mol_id").to_dict(orient="index")
    deploy_lookup = deploy.set_index("mol_id").to_dict(orient="index")

    rows = []
    for mol in universe:
        f = frozen_lookup.get(mol, {})
        d = deploy_lookup.get(mol, {})
        v = val_lookup.get(mol, {})

        scaffold = (
            f.get("scaffold_family")
            or d.get("scaffold")
            or v.get("scaffold")
        )

        adc2 = v.get("DEST_adc2_eV")
        if pd.isna(adc2):
            adc2 = None
        classification = v.get("classification")
        is_neg = (adc2 is not None) and (float(adc2) < NEG_GAP_THRESHOLD_EV)

        selected_r1 = mol in frozen_ids
        in_deploy = mol in deploy_ids

        # Fisher subset (panel-b in stats_validation_results.json):
        # Hz vs 5AP, Round-1 deployment, EXCLUDING Hz_NH23.
        in_fisher = (
            in_deploy
            and mol != HZ_NH23
            and scaffold in {"Hz", "5AP"}
        )
        # Conformal test set: 14 R1 deployment molecules, EXCLUDING Hz_NH23.
        in_conformal = in_deploy and mol != HZ_NH23

        reasons = []
        if selected_r1 and not in_deploy:
            reasons.append(
                "selected in Round-1 frozen list but not in the 15-molecule "
                "R1 deployment yield (deferred to a later batch)"
            )
        if in_deploy and mol == HZ_NH23:
            reasons.append(
                "Hz_NH23 is the dark / fosc=0 outlier; it is in the "
                "15-molecule deployment but excluded from the 14-molecule "
                "Fisher and conformal subsets by design (extreme residual "
                "would dominate quantile-based UQ)"
            )

        rows.append({
            "molecule_id": mol,
            "molecule_name": mol,
            "scaffold": scaffold,
            "selected_in_round1": bool(selected_r1),
            "included_in_deployment_yield": bool(in_deploy),
            "included_in_fisher_subset": bool(in_fisher),
            "included_in_conformal_test": bool(in_conformal),
            "adc2_gap_eV": (round(float(adc2), 6)
                            if adc2 is not None else None),
            "classification": classification,
            "is_negative_gap": bool(is_neg),
            "exclusion_reason_if_any": "; ".join(reasons),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(
        by=["included_in_deployment_yield", "scaffold", "adc2_gap_eV"],
        ascending=[False, True, True],
        kind="stable",
    ).reset_index(drop=True)
    return df


def fisher_two_sided(table) -> float:
    _, p = stats.fisher_exact(table, alternative="two-sided")
    return float(p)


def assemble_caption_json(recon: pd.DataFrame,
                          canonical: dict,
                          stats_json: dict,
                          task2: pd.DataFrame) -> dict:
    al = canonical.get("active_learning", {})
    fisher_full = al.get("fisher_full_cohort", {})
    fisher_r1   = al.get("fisher_r1_subset", {})
    subspace = stats_json.get("subspace_elimination", {})

    deploy_rows   = recon[recon["included_in_deployment_yield"]]
    fisher_rows   = recon[recon["included_in_fisher_subset"]]
    conformal_rows = recon[recon["included_in_conformal_test"]]

    deployment_total_queries    = int(len(deploy_rows))
    deployment_negative_hits    = int(deploy_rows["is_negative_gap"].sum())
    fisher_subset_total         = int(len(fisher_rows))
    fisher_subset_negative_hits = int(fisher_rows["is_negative_gap"].sum())
    conformal_test_total        = int(len(conformal_rows))

    # Hz vs 5AP table (R1 subset)
    hz_invest = int(((fisher_rows.scaffold == "Hz") &
                     fisher_rows.is_negative_gap).sum())
    hz_total  = int((fisher_rows.scaffold == "Hz").sum())
    ap_invest = int(((fisher_rows.scaffold == "5AP") &
                     fisher_rows.is_negative_gap).sum())
    ap_total  = int((fisher_rows.scaffold == "5AP").sum())
    hz_vs_5ap_table = [
        [hz_invest, hz_total - hz_invest],
        [ap_invest, ap_total - ap_invest],
    ]
    p_hz_vs_5ap = fisher_two_sided(hz_vs_5ap_table)

    # Full cohort table from canonical_metrics
    full_table = fisher_full.get("contingency_table")
    full_p     = fisher_full.get("p_value_two_sided")

    # Cross-check stats_validation_results.json
    src_consistent = (
        subspace.get("hz_invest") == hz_invest
        and subspace.get("hz_total") == hz_total
        and subspace.get("ap_invest") == ap_invest
        and subspace.get("ap_total") == ap_total
    )

    # Cross-check task2_baseline_significance.csv
    task2_invest_incl = int(task2["our_invest"].iloc[0])
    task2_invest_excl = int(task2["our_invest_excl_nh23"].iloc[0])

    deploy_neg_mols = deploy_rows.loc[
        deploy_rows.is_negative_gap, "molecule_id"
    ].tolist()
    fisher_neg_mols = fisher_rows.loc[
        fisher_rows.is_negative_gap, "molecule_id"
    ].tolist()
    frozen_only = sorted(recon.loc[
        recon.selected_in_round1 & ~recon.included_in_deployment_yield,
        "molecule_id",
    ].tolist())

    baseline_p = al.get("baseline_comparisons", {})

    return {
        "figure_id": "Fig5_al_value",
        "source_data_files": [
            "results/canonical_metrics.json",
            "results/tables/round1_candidates_frozen.csv",
            "results/round1_eval/task2_baseline_significance.csv",
            "results/round1_eval/stats_validation_results.json",
            "results/validated_candidates_master.csv",
            "results/round1_eval/task1_deployment_detail.csv",
            "results/round1_eval/task1_learning_curve.csv",
            "results/audit/round1_reconciliation.csv",
        ],

        "deployment_total_queries":    deployment_total_queries,
        "deployment_negative_hits":    deployment_negative_hits,
        "fisher_subset_total":         fisher_subset_total,
        "fisher_subset_negative_hits": fisher_subset_negative_hits,
        "conformal_test_total":        conformal_test_total,

        "reason_for_15_vs_14": (
            "15 = full Round-1 deployment yield "
            "(task1_deployment_detail.csv, includes Hz_NH23). "
            "14 = the Fisher / conformal subset that excludes Hz_NH23. "
            "Hz_NH23 is a dark (fosc = 0) outlier with ADC(2) gap "
            "-0.383 eV, far outside the deployment residual distribution; "
            "stats_validation and split-conformal pipelines remove it by "
            "design. Different analysis sets — not a contradiction."
        ),
        "reason_for_7_vs_6": (
            "7 = negative-gap (INVEST) hits in the 15-molecule deployment "
            "(includes Hz_NH23, classified as dark_negative_gap with "
            "DEST = -0.383 eV). "
            "6 = INVEST hits in the 14-molecule Fisher subset that "
            "excludes Hz_NH23. The single-molecule difference is the same "
            "Hz_NH23 inclusion/exclusion rule. "
            f"task2_baseline_significance.csv records both: "
            f"our_invest = {task2_invest_incl}, "
            f"our_invest_excl_nh23 = {task2_invest_excl}. "
            "Not a contradiction."
        ),

        "Hz_vs_5AP_table": {
            "description": (
                "Round-1 Fisher subset, Hz vs 5AP, EXCLUDES Hz_NH23. "
                "Rows: [Hz, 5AP]; columns: [INVEST (DEST<0), non-INVEST]."
            ),
            "rows_labels":    ["Hz", "5AP"],
            "columns_labels": ["INVEST", "non_INVEST"],
            "table":          hz_vs_5ap_table,
            "hz_invest":      hz_invest,
            "hz_total":       hz_total,
            "ap_invest":      ap_invest,
            "ap_total":       ap_total,
            "fisher_p_two_sided": p_hz_vs_5ap,
            "matches_stats_validation_json": bool(src_consistent),
        },
        "full_cohort_Hz_vs_nonHz_table": {
            "description": (
                "Full validated cohort (n=35), Hz vs ALL non-Hz scaffolds. "
                "This is the paper-cited Fisher comparison."
            ),
            "rows_labels":    ["Hz", "non_Hz"],
            "columns_labels": ["INVEST", "non_INVEST"],
            "table":          full_table,
            "hz_invest":      fisher_full.get("hz_invest"),
            "hz_total":       fisher_full.get("hz_total"),
            "non_hz_invest":  fisher_full.get("non_hz_invest"),
            "non_hz_total":   fisher_full.get("non_hz_total"),
            "fisher_p_two_sided": full_p,
        },

        "p_values": {
            "hz_vs_5ap_round1_subset_two_sided":     p_hz_vs_5ap,
            "hz_vs_5ap_round1_subset_canonical":     fisher_r1.get("p_value"),
            "hz_vs_nonhz_full_cohort_two_sided":     full_p,
            "hz_vs_nonhz_full_cohort_one_sided_greater":
                fisher_full.get("p_value_one_sided_greater"),
            "task2_vs_uniform_random_incl_nh23":
                baseline_p.get("B1_uniform_random", {}).get("p_value_incl_nh23"),
            "task2_vs_uniform_random_excl_nh23":
                baseline_p.get("B1_uniform_random", {}).get("p_value_excl_nh23"),
            "task2_vs_scaffold_stratified_incl_nh23":
                baseline_p.get("B2_scaffold_stratified", {}).get("p_value_incl_nh23"),
            "task2_vs_hz_greedy_dft_incl_nh23":
                baseline_p.get("B3_hz_greedy_dft", {}).get("p_value_incl_nh23"),
            "task2_vs_hz_greedy_empirical_incl_nh23":
                baseline_p.get("B3_hz_greedy_empirical", {}).get("p_value_incl_nh23"),
        },

        "molecule_lists": {
            "deployment_negative_hits":           deploy_neg_mols,
            "fisher_subset_negative_hits":        fisher_neg_mols,
            "deployment_only_excluded_from_fisher": [HZ_NH23],
            "frozen_only_not_deployed":           frozen_only,
        },

        "caveat": (
            "Fisher tests are descriptive because the validation set is "
            "selected by the active-learning acquisition policy, not drawn "
            "at random. p-values quantify the observed Hz vs non-Hz "
            "contrast inside the queried set; they do NOT establish "
            "unbiased prevalence estimates for the broader chemical "
            "library."
        ),
    }


def write_markdown(recon: pd.DataFrame,
                   caption: dict,
                   canonical: dict) -> str:
    al = canonical.get("active_learning", {})
    full = caption["full_cohort_Hz_vs_nonHz_table"]
    r1   = caption["Hz_vs_5AP_table"]

    deploy_neg  = caption["molecule_lists"]["deployment_negative_hits"]
    fisher_neg  = caption["molecule_lists"]["fisher_subset_negative_hits"]
    frozen_only = caption["molecule_lists"]["frozen_only_not_deployed"]

    L: list[str] = []

    L += [
        "# Fig5 active-learning reconciliation",
        "",
        "Generated by `scripts/reconcile_active_learning_figure.py`. ",
        "Audit artefact only — `paper/main.tex` is not modified by this "
        "script.",
        "",
    ]

    L += [
        "## Q1. Is 15 vs 14 a real contradiction or different analysis sets?",
        "",
        "**Different analysis sets — not a contradiction.**",
        "",
        f"- 15 = Round-1 deployment yield, from "
        f"`task1_deployment_detail.csv`. Equals "
        f"`canonical_metrics.datasets.round1_deployment_n` = "
        f"{canonical['datasets']['round1_deployment_n']}.",
        f"- 14 = Fisher / conformal subset, from "
        f"`stats_validation_results.json` and `p0b_conformal_*`. Equals "
        f"`canonical_metrics.datasets.round1_conformal_test_n` = "
        f"{canonical['datasets']['round1_conformal_test_n']}.",
        f"- The single difference is `{HZ_NH23}` — dark (fosc = 0), "
        "ADC(2) gap = -0.383 eV. The conformal pipeline excludes it by "
        "design (its residual would dominate the empirical quantile). "
        "Both numbers are valid for their respective scopes and must "
        "not be interchanged.",
        "",
    ]

    L += [
        "## Q2. Is 7 vs 6 a real contradiction or NH23 inclusion/exclusion?",
        "",
        "**Same Hz_NH23 inclusion/exclusion rule — not a contradiction.**",
        "",
        "- 7 = negative-gap hits in the 15-molecule deployment "
        "(`task2_baseline_significance.csv :: our_invest = 7`).",
        "- 6 = negative-gap hits in the 14-molecule Fisher subset "
        "(`task2_baseline_significance.csv :: our_invest_excl_nh23 = 6`; "
        "matches `stats_validation_results.json :: hz_invest = 6`).",
        f"- The molecule that flips between the two: `{HZ_NH23}` "
        "(`dark_negative_gap`, ADC(2) = -0.383 eV).",
        "",
        "Negative-hit lists:",
        "",
        f"- Deployment (7/15): {', '.join(deploy_neg)}.",
        f"- Fisher subset (6/14): {', '.join(fisher_neg)}.",
        "",
        "Frozen-only molecules NOT in deployment "
        "(explains 16 → 15 attrition): "
        f"{', '.join(frozen_only) if frozen_only else 'none'}.",
        "",
    ]

    L += [
        "## Q3. How should the Figure 5 caption be written?",
        "",
        "Suggested caption (NOT injected into main.tex):",
        "",
        "> **Figure 5.** Active-learning value. **(a)** Full validated "
        f"cohort (n = 35): Hz vs non-Hz contingency table = "
        f"{full['table']}, two-sided Fisher exact "
        f"p = {full['fisher_p_two_sided']:.3f} (descriptive). "
        "**(b)** Round-1 Fisher subset (n = 14, Hz_NH23 excluded as the "
        "fosc = 0 / extreme-residual outlier): Hz vs 5AP contingency "
        f"table = {r1['table']}, two-sided Fisher exact "
        f"p = {r1['fisher_p_two_sided']:.3f}. The Round-1 deployment "
        "yield (7 INVEST hits in 15 queried molecules, including "
        "Hz_NH23) is reported separately in the text. p-values are "
        "descriptive: the queried set is policy-selected, not random.",
        "",
    ]

    L += [
        "## Q4. How should the active-learning results be written in body?",
        "",
        "Suggested wording (NOT injected into main.tex):",
        "",
        "> Round-1 active learning queried 15 molecules and recovered 7 "
        "negative-gap candidates. Restricting to the Fisher / "
        "conformal-evaluation subset of 14 molecules — which excludes "
        "the dark fosc = 0 outlier Hz_NH23 by design — leaves 6 "
        "negative-gap hits in 14. Within that subset, Hz scaffolds "
        "account for 6/9 hits while 5AP scaffolds account for 0/5 "
        f"(Fisher exact two-sided p = "
        f"{r1['fisher_p_two_sided']:.3f}, descriptive). Across the full "
        f"validated cohort (n = 35), the Hz vs non-Hz contrast is "
        f"{full['hz_invest']}/{full['hz_total']} vs "
        f"{full['non_hz_invest']}/{full['non_hz_total']} "
        f"(p = {full['fisher_p_two_sided']:.3f}, descriptive). Because "
        "molecules were chosen by the acquisition policy rather than at "
        "random, these p-values describe the contrast inside the "
        "queried set and should not be interpreted as unbiased "
        "estimates of library-wide INVEST prevalence.",
        "",
    ]

    L += [
        "## Q5. Forbidden phrasing",
        "",
        "Do **not** write any of the following in main.tex or "
        "supplementary:",
        "",
        "- \"6 of 15\" / \"6/15\" for the deployment yield. The 6/14 "
        "number applies only to the Fisher / conformal subset.",
        "- \"7 of 14\" / \"7/14\" for the Fisher subset. The 7/15 "
        "number applies only to the full deployment.",
        "- Any wording that combines the 35-molecule full-cohort "
        "denominator with the 14-molecule Fisher subset numerator (or "
        "vice versa).",
        "- \"Statistically significant enrichment of Hz INVESTs in the "
        "library at p < 0.05\". The Fisher test is descriptive — the "
        "validation set was selected by active learning, not sampled at "
        "random, so the p-value does not generalise to the library.",
        "- \"Active learning beat random sampling at p < 0.05\". "
        "`task2_baseline_significance.csv` shows p ≥ 0.97 against all "
        "four baselines (B1, B2, B3-DFT, B3-empirical) using both 7/15 "
        "and 6/14 — none are significant.",
        "- \"Round-1 yielded 7 INVEST candidates from 14 deployments\" "
        "or any other 7-from-14 wording. Hz_NH23 is required to reach "
        "7.",
        "",
    ]

    L += [
        "## File-by-file evidence",
        "",
        f"- `results/tables/round1_candidates_frozen.csv` → 16 frozen "
        f"candidates; the row not deployed in Round 1 is "
        f"`{frozen_only[0] if frozen_only else 'n/a'}`.",
        "- `results/round1_eval/task1_deployment_detail.csv` → 15 "
        "deployed molecules.",
        "- `results/round1_eval/task2_baseline_significance.csv` → "
        "`our_invest = 7`, `our_invest_excl_nh23 = 6`.",
        "- `results/round1_eval/stats_validation_results.json` → "
        "Hz vs 5AP subset: hz_invest = 6, hz_total = 9, ap_invest = 0, "
        "ap_total = 5, p = 0.030969.",
        "- `results/canonical_metrics.json` → "
        "`active_learning.fisher_full_cohort.p_value` = "
        f"{al.get('fisher_full_cohort', {}).get('p_value')}; "
        "`datasets.round1_deployment_n` = "
        f"{canonical['datasets']['round1_deployment_n']}; "
        "`datasets.round1_conformal_test_n` = "
        f"{canonical['datasets']['round1_conformal_test_n']}.",
        "",
    ]

    L += [
        "## Caveat (must accompany every Fisher citation)",
        "",
        "> Fisher tests in this work are descriptive: the queried set "
        "was selected by the active-learning acquisition policy, not "
        "drawn at random. p-values describe the observed contrast "
        "within the queried set and do not establish unbiased "
        "prevalence estimates for the broader chemical library.",
        "",
    ]

    return "\n".join(L)


def main() -> None:
    canonical, frozen, task2, stats_json, validated, deploy, _learn = load_inputs()

    recon = build_reconciliation(frozen, deploy, validated)
    OUTPUTS["csv"].parent.mkdir(parents=True, exist_ok=True)
    recon.to_csv(OUTPUTS["csv"], index=False)

    caption = assemble_caption_json(recon, canonical, stats_json, task2)
    OUTPUTS["caption"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["caption"].write_text(json.dumps(caption, indent=2) + "\n")

    md = write_markdown(recon, caption, canonical)
    OUTPUTS["report"].parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS["report"].write_text(md)

    # Hard-coded sanity assertions per spec.
    assert caption["deployment_total_queries"] == 15, (
        f"Expected 15 deployment queries, got "
        f"{caption['deployment_total_queries']}"
    )
    assert caption["deployment_negative_hits"] == 7, (
        f"Expected 7 deployment INVEST hits, got "
        f"{caption['deployment_negative_hits']}"
    )
    assert caption["fisher_subset_total"] == 14, (
        f"Expected 14 in Fisher subset, got "
        f"{caption['fisher_subset_total']}"
    )
    assert caption["fisher_subset_negative_hits"] == 6, (
        f"Expected 6 Fisher subset INVEST hits, got "
        f"{caption['fisher_subset_negative_hits']}"
    )
    assert caption["Hz_vs_5AP_table"]["matches_stats_validation_json"], (
        "Recomputed Hz vs 5AP table disagrees with "
        "stats_validation_results.json"
    )

    print(f"[OK] {OUTPUTS['csv'].relative_to(ROOT)} ({len(recon)} rows)")
    print(f"[OK] {OUTPUTS['caption'].relative_to(ROOT)}")
    print(f"[OK] {OUTPUTS['report'].relative_to(ROOT)}")
    print(f"     deployment_total_queries     = "
          f"{caption['deployment_total_queries']}")
    print(f"     deployment_negative_hits     = "
          f"{caption['deployment_negative_hits']}")
    print(f"     fisher_subset_total          = "
          f"{caption['fisher_subset_total']}")
    print(f"     fisher_subset_negative_hits  = "
          f"{caption['fisher_subset_negative_hits']}")


if __name__ == "__main__":
    main()
