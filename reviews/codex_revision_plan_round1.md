# Codex Revision Plan Round 1

Date: 2026-04-27

This plan is derived directly from [reviews/codex_review_round1.md](/home/nudt_cleng/2026/github_upload/reviews/codex_review_round1.md). It does not modify `paper/main.tex`; it only records the required follow-up actions.

## Major issue 1

- `issue_id`: `major_01_low_level_calibration_traceability`
- `exact sentence or figure affected`:
  - `paper/main.tex:57-61`
  - `paper/main.tex:46` via Fig0 workflow wording
  - `figures/Fig0_workflow.pdf` / `figures/Fig0_workflow.png` as currently rendered
- `evidence source that contradicts or limits the claim`:
  - `results/canonical_metrics.json`
  - `figures/caption_data/Fig0_workflow.json`
  - `results/Table1_invest_candidates.tex`
  - `results/Table2_method_summary.tex`
  - `reviews/codex_review_round1.md`
  - These current canonical sources do not contain the calibration `n=5`, `R^2=0.97`, or the fitted coefficients `0.5501` and `-0.2127`.
- `required action`:
  - Add a script-generated canonical artifact for the low-level calibration containing:
    - anchor identities
    - `n`
    - fit coefficients
    - `R^2`
    - source data files
  - Regenerate the workflow caption-data or figure metadata from that artifact.
  - Only after that, keep or restate the calibration equation and `R^2` in the manuscript/figure text.
- `whether action is wording-only, figure/caption fix, table fix, or new calculation`:
  - `new calculation`
- `proposed replacement wording if wording-only`:
  - `N/A`

## Major issue 2

- `issue_id`: `major_02_fig5_count_reconciliation_not_explicit_enough`
- `exact sentence or figure affected`:
  - `paper/main.tex:74`
  - `paper/main.tex:146`
  - Fig5 caption and any associated cover-letter/reviewer-response summary that cites round-1 counts
- `evidence source that contradicts or limits the claim`:
  - `paper/audit_reports/fig5_reconciliation.md`
  - `figures/caption_data/Fig5_al_value.json`
  - `results/audit/round1_reconciliation.csv`
  - `results/canonical_metrics.json`
  - These sources require the explicit rule:
    - use `7/15` for deployment yield
    - use `6/14` only for the panel-b Fisher/conformal subset excluding `Hz_NH23`
- `required action`:
  - Revise the Fig5 caption so panel (a) is explicitly the full `35`-molecule validated cohort.
  - Revise the Fig5 caption so panel (b) is explicitly the `14`-molecule Fisher/conformal subset excluding `Hz_NH23`.
  - Revise the main-text dataset description so `15` queried molecules and `14` panel-b/conformal molecules are both stated together when relevant.
- `whether action is wording-only, figure/caption fix, table fix, or new calculation`:
  - `figure/caption fix`
- `proposed replacement wording if wording-only`:
  - `Fig5 is interpreted on two denominators: panel (a) uses the full 35-molecule validated cohort, whereas panel (b) uses the 14-molecule Fisher/conformal subset obtained by excluding Hz_NH23; accordingly, round-1 deployment yield is reported as 7/15, while the panel-b scaffold subset is 6/14.`

## Major issue 3

- `issue_id`: `major_03_fisher_p_values_need_descriptive_framing`
- `exact sentence or figure affected`:
  - `paper/main.tex:141`
  - Fig5 caption at `paper/main.tex:146`
  - Any nearby text that uses `p=0.031` or `p=0.015` as if they were general inferential claims
- `evidence source that contradicts or limits the claim`:
  - `figures/caption_data/Fig5_al_value.json`
  - `paper/audit_reports/fig5_reconciliation.md`
  - `results/canonical_metrics.json`
  - `results/round1_eval/stats_validation_results.json`
  - These sources show that:
    - the `p=0.031` result is based on the selected `6/9` vs `0/5` round-1 subset
    - the `p=0.015` result is based on a small `13/27` vs `0/8` validated cohort
    - both are limited-sample scaffold-comparison statistics under the current workflow
- `required action`:
  - Downgrade Fisher-language from inferential to descriptive.
  - Make explicit that the round-1 Fisher test is a subset-level scaffold-resolution statistic.
  - Preserve the baseline result that active learning must not be claimed as a hit-rate improvement.
- `whether action is wording-only, figure/caption fix, table fix, or new calculation`:
  - `wording-only`
- `proposed replacement wording if wording-only`:
  - `In the round-1 subset used for scaffold comparison, the Hz-versus-5AP contingency table is 6/9 versus 0/5 (two-sided Fisher exact p = 0.031); we treat this as a descriptive subset-level statistic rather than a population-level rate estimate. In the full 35-molecule validated cohort, all 13 negative or dark negative-gap classifications occur in Hz molecules (13/27 for Hz versus 0/8 for non-Hz; two-sided Fisher exact p = 0.015), again as evidence within the present computational protocol rather than as a general scaffold-universality claim.`

## Major issue 4

- `issue_id`: `major_04_52mev_model_utility_overstated_relative_to_30mev_threshold`
- `exact sentence or figure affected`:
  - `paper/main.tex:41`
  - `paper/main.tex:107`
  - `paper/main.tex:194`
  - Any title/subsection sentence that treats `52.1 meV` as sufficient candidate-level predictive precision without threshold caveat
- `evidence source that contradicts or limits the claim`:
  - `paper/main.tex:98` defines the `30 meV` borderline window
  - `results/canonical_metrics.json`
    - `model_performance.post_round1_excl_nh23.MAE_meV = 52.08696`
  - `figures/caption_data/Fig1_ablation.json`
  - `figures/caption_data/Fig3_classification.json`
  - These sources jointly limit the claim because the post-round LOO-CV MAE is larger than the classification threshold used for borderline assignment.
- `required action`:
  - Downgrade “quantitatively useful” or equivalent positive headline wording.
  - State explicitly that the model is informative for scaffold-level prioritization or within-domain ranking trends, but is too coarse for confident near-threshold candidate-level classification.
  - Keep the distinction between retrospective within-domain correction and deployment behavior.
- `whether action is wording-only, figure/caption fix, table fix, or new calculation`:
  - `wording-only`
- `proposed replacement wording if wording-only`:
  - `The post-round delta-transfer model improves within-domain LOO-CV error relative to the pre-round target set, but its 52.1 meV MAE remains larger than the 30 meV borderline window used for final classification. We therefore interpret the model as useful for scaffold-level prioritization and coarse within-domain correction, not for confident near-threshold candidate-level assignment.`

