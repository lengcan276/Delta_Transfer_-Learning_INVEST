# Phase 2 Step 6 — Canonical domain coverage

## Actual top-level keys in `results/canonical_metrics.json`
```
library
datasets
model_performance
deployment
ablation
uncertainty
active_learning
validation
method_crosscheck
uncertainty_diagnostics
per_molecule_highlights
missing_metrics
known_inconsistencies
scs_cc2_extended_n13
```
14 keys.

## Coverage of paper claim domains

| # | Paper claim domain | Mapped top-level key(s) | Status |
|---|---|---|---|
| 1 | library composition (sizes, scaffold counts, source/target split) | `library` (n_molecules_master=2026, n_target_domain, target_scaffold_counts, n_invest_labeled, …) | COVERED |
| 2 | ML performance (LOO-CV MAE, sign accuracy, deployment MAE) | `model_performance` (pre_round1, post_round1_excl_nh23, post_round1_incl_nh23, round1_deployment) | COVERED |
| 3 | deployment metrics (round-1 deployment set, pre/post distinction) | `deployment` + `model_performance.round1_deployment` | COVERED |
| 4 | ablation (full vs no_* / rdkit_only / descriptor ablation) | `ablation.multiseed_summary` + `ablation.task3_configs` | COVERED |
| 5 | uncertainty (conformal coverage, bootstrap width, CI) | `uncertainty` + `uncertainty_diagnostics` | COVERED |
| 6 | active learning (scaffold elimination, hit rate, Fisher exact p) | `active_learning.fisher_full_cohort` + `fisher_r1_subset` + `fisher_p_value_paper` + `domain_adapt_*` + `entropy_*` + `baseline_comparisons` | COVERED |
| 7 | validation outcomes (validated candidates, negative/dark/borderline counts) | `validation` (classification_counts, n_negative_gap, n_dark_negative_gap, n_borderline, n_table1_candidates) | COVERED |
| 8 | method cross-check (ADC(2) vs SCS-CC2, 13/13, method consistency) | `method_crosscheck` (legacy 9-mol table) + **`scs_cc2_extended_n13`** (new 13-mol cohort, per_molecule, CI, narrowest_margin, rule_of_three_upper_bound) | COVERED |
| 9 | known inconsistencies (0.015 vs 0.031 analysis-set distinction, 15/14, etc.) | `known_inconsistencies` (5 entries, including `active_learning.fisher_p_value`, `active_learning.r1_invest_count_7_vs_6`, `datasets.round1_n`, two `ablation.*` entries) | COVERED |

### Extras present that are not in the rubric (informational, not flagged)

- `uncertainty_diagnostics` — 4 follow-on diagnostics (Tanimoto distance,
  Mondrian, locally-adaptive split, distance-to-source) cited in §3.3
- `per_molecule_highlights` — per-molecule context strings cited in
  Table 1 caption / SI
- `missing_metrics` — explicit empty list as honest "nothing missing here"
  signal

## Coverage tally

| Status | Count |
|---|---|
| COVERED | **9 / 9** |
| PARTIALLY_COVERED | 0 |
| MISSING_FROM_CANONICAL | 0 |
| NOT_APPLICABLE | 0 |

## Conclusion (Step 6 only)

All 9 paper claim domains are covered by at least one top-level key.
No claim domain is missing.

Note that `scs_cc2_extended_n13` (domain 8 — n=13 cross-check) is the
content that fails to regenerate from `99_emit_canonical.py` alone; it
is still **present** in the file, so domain coverage is satisfied. The
*provenance* of that block is the Phase 4 audit's problem.
