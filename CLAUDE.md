# Claude Code project instructions for INVEST manuscript

Use the global skills in ~/.claude/skills.

## Mandatory skills

- manuscript-consistency for any manuscript text or numerical claim
- stats-rigor-reviewer for ML/statistical claims
- figure-auditor for figures and captions
- comp-chem-method-reviewer for electronic-structure and INVEST/OLED claims
- adversarial-reviewer for cold peer review

## Hard rules

1. Never invent numbers.
2. Never copy numbers from prose into new prose.
3. Verify numbers against results/canonical_metrics.json or figures/caption_data/*.json.
4. Do not edit paper/main.tex before canonical metrics and figure caption data are generated.
5. When fixing review comments, write responses to reviews/author_response.md.

## Current top priority

First fix the evidence chain:
1. Generate results/canonical_metrics.json.
2. Reconcile the active-learning figure inconsistency.
3. Generate figures/caption_data/*.json.
4. Audit paper/main.tex.
5. Only then rewrite text.

## Deprecated sources / Authoritative sources

Deprecated:
- results/round1_eval/task3_ablation_results.csv
- results/round1_eval/task3_bootstrap_ci.csv
- any result derived from /home/nudt_cleng/2026/project/scripts/task3_ablation_study.py

Reason:
The old task3 ablation pipeline filtered features by source-target shared coverage, so all target-domain physics features had 0% source coverage and the nominal full/no_stda/no_ksod/no_dft configurations collapsed to the same 54 RDKit shared features.

Authoritative:
- scripts/p0a_ablation_fixed.py
- results/round1_eval/p0a_ablation_multiseed.csv
- results/round1_eval/p0a_ablation_paired_tests.json
- results/validated_candidates_master.csv

Rule:
- Any manuscript claim about ablation must use p0a_ablation_fixed.py and p0a_ablation_multiseed.csv, not task3_ablation_results.csv.
- Any manuscript claim about final validation confidence must use current results/validated_candidates_master.csv.
