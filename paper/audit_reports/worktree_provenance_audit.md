# Worktree Provenance Audit

Date: 2026-04-27

## Scope

This audit compares the current repository at `/home/nudt_cleng/2026/github_upload` against the related historical worktrees and result directories under `/home/nudt_cleng/2026`, with emphasis on code provenance, processed data, and manuscript-facing result files.

## Primary conclusion

The current authoritative worktree for the manuscript is:

- `/home/nudt_cleng/2026/github_upload`

This is the worktree that should be treated as the manuscript authority for scripts, processed data, regenerated figures/tables, and audit reports.

## Relationship to `/home/nudt_cleng/2026/project`

`/home/nudt_cleng/2026/project` is the closest historical predecessor to `github_upload`.

The main provenance findings are:

- The shared processed data files in `project/data` and `github_upload/data` are consistent for the common files that were compared.
- The shared `round1_eval` results are effectively the same evidence base.
- The common files under `project/results/round1_eval` and `github_upload/results/round1_eval` matched for the manuscript-relevant round-1 outputs that were compared.
- Several common scripts differ only by path handling and repository-root normalization, not by substantive algorithm changes.

Accordingly, `project` can be treated as a historically consistent predecessor worktree, but not as the current manuscript authority.

## Status of `/home/nudt_cleng/2026/github_repo` and `/home/nudt_cleng/2026/src`

The directories:

- `/home/nudt_cleng/2026/github_repo`
- `/home/nudt_cleng/2026/src`

represent earlier exploratory development lines.

They contain:

- older manuscript drafts,
- alternate figure-generation pipelines,
- exploratory model-development scripts,
- partially divergent repository layouts.

They should **not** be treated as the authoritative source for the current manuscript. Any figures, tables, scripts, or textual claims drawn from those directories require explicit re-validation inside `github_upload` before use.

## Deprecated Task-3 ablation chain

The following legacy Task-3 ablation chain is incorrect and should not be used for the current manuscript:

- `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py`
- `/home/nudt_cleng/2026/project/results/round1_eval/task3_ablation_results.csv`
- `/home/nudt_cleng/2026/project/results/round1_eval/task3_bootstrap_ci.csv`

### Root cause

The legacy script defines nominal ablation configurations that include physics-feature blocks, but then applies a shared coverage filter requiring each feature to have usable coverage in both source and target domains.

In the current processed data:

- physics features have `0%` coverage on the source-side Pollice rows,
- therefore the shared coverage filter removes them before model fitting,
- as a result, `full`, `no_stda`, `no_ksod`, and `no_dft` all collapse to the same effective 54-feature RDKit shared subset.

This is why the legacy outputs report different nominal feature counts while producing identical Task-3 performance metrics across all configurations.

This failure mode has been independently reconstructed and documented in:

- `results/round1_eval/task3_ablation_root_cause.md`
- `results/round1_eval/task3_ablation_root_cause.json`

## Current authoritative ablation and validation files

The current manuscript should use the following files instead:

- `scripts/p0a_ablation_fixed.py`
- `results/round1_eval/p0a_ablation_multiseed.csv`
- `results/validated_candidates_master.csv`

These files reflect the corrected ablation design in which:

- the source model remains on shared RDKit features,
- the delta model can use target-domain physics features directly,
- the resulting ablation differences are no longer artifacts of source-side missingness.

## Validated candidate table provenance

The current `results/validated_candidates_master.csv` differs from the older `/home/nudt_cleng/2026/results/validated_candidates_master.csv` in interpretation metadata, not in the underlying classification outcome.

Specifically:

- the changes are more conservative in `confidence`,
- the current table adds explicit `decision_basis`,
- the current table also preserves `DEST_adc2_eV` and `DEST_scscc2_eV` for traceability.

The following manuscript-relevant fields were not changed by this update:

- `DEST_eV`
- `classification`

Therefore, the update should be understood as a tightening of evidence labeling and decision traceability, not as a change to the underlying validated chemical classifications.

## Operational guidance

For any future manuscript edits, figure regeneration, or reviewer-response work:

- use `github_upload` as the sole authority,
- treat `project` as a historical predecessor for provenance checks only,
- do not cite or revive the legacy Task-3 ablation outputs,
- do not treat `github_repo` or top-level `src` as current evidence sources without re-importing and re-auditing the relevant material.

## DO NOT USE

- `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py`
  Reason: legacy shared-coverage filtering removes all source-missing physics features and collapses the ablation configs to the same 54-feature RDKit subset.
- `/home/nudt_cleng/2026/project/results/round1_eval/task3_ablation_results.csv`
  Reason: stale output from the deprecated Task-3 ablation chain.
- `/home/nudt_cleng/2026/project/results/round1_eval/task3_bootstrap_ci.csv`
  Reason: derived from the same deprecated Task-3 chain.
- `/home/nudt_cleng/2026/github_repo`
  Reason: earlier exploratory branch, not the current manuscript authority.
- `/home/nudt_cleng/2026/src`
  Reason: earlier exploratory script line with divergent figure/manuscript tooling.

## AUTHORITATIVE USE

- `/home/nudt_cleng/2026/github_upload`
  Purpose: current authoritative manuscript worktree.
- `/home/nudt_cleng/2026/github_upload/scripts/p0a_ablation_fixed.py`
  Purpose: corrected ablation workflow for manuscript use.
- `/home/nudt_cleng/2026/github_upload/results/round1_eval/p0a_ablation_multiseed.csv`
  Purpose: authoritative ablation result table.
- `/home/nudt_cleng/2026/github_upload/results/validated_candidates_master.csv`
  Purpose: authoritative validated candidate decision table.
- `/home/nudt_cleng/2026/github_upload/results/canonical_metrics.json`
  Purpose: script-generated manuscript metrics anchor.
