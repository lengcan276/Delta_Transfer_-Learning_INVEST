# Phase 2 — `canonical_metrics.json` processed-level audit

Audit phase: Phase 2
Repository HEAD: `3a72bc9` (from `audit/AUDIT_COMMIT.txt`)
Date: 2026-05-20

---

## Phase 2 Status

**PASS_WITH_WARNINGS**

Reasoning (full detail below):
- ✓ Zero `SUSPECT_HARDCODED_RESULT` in `scripts/99_emit_canonical.py`
- ✓ `99_emit_canonical.py` runs cleanly inside git-archive isolated copy
  (exitcode 0)
- ✓ Regeneration is **byte-identical** for every block that the script
  claims to produce
- ⚠ **One block (`scs_cc2_extended_n13`) does NOT regenerate** because it
  is written by a separate Phase 3 pipeline
  (`scripts/scscc2_extension/build_cross_check_n13.py` + a manual JSON
  patch), not by `99_emit_canonical.py`. This is an honest scope gap, not
  a hardcode or numeric drift.
- ✓ All 9 paper claim domains are covered in the file
- ✓ Fisher p-value inconsistency (0.015 vs 0.031) is properly marked as
  `intentional_analysis_set_distinction` with full resolution metadata
- ✓ No repository contamination

---

## Repository contamination check

Step 1 result: see `audit/phase2_repo_contamination_check.md`.
- `git status --short` shows only `?? audit/` and `?? scripts/audit/`
- No modification to any file under `paper/`, `results/`, `data/`,
  `figures/`, or pre-existing `scripts/` files
- **No repo contamination — phase 2 allowed to proceed.**

---

## Hardcoded-number audit

See `audit/canonical_hardcoded_findings.md`.

| Metric | Value |
|---|---|
| Generic 3+dp number scan hits | 0 |
| Targeted paper-number scan hits | 23 |
| → of which `SUSPECT_HARDCODED_RESULT` | **0** |
| → of which `NEEDS_MANUAL_REVIEW` | **0** |
| → of which `OK_DOCSTRING` / `OK_DERIVED_FROM_FILE` | 23 |
| `scripts/99_emit_canonical.py` imports | `json`, `pathlib`, `numpy`, `pandas`, `scipy.stats` (5 stdlib + 3rd-party) |
| Project-internal module imports | **0** |
| Imported-module number scan | N/A (no internal modules to scan) |

All 23 targeted hits are docstring text, comment text, or string-literal
`description`/`resolution` fields embedded into the output JSON to
explain values that are themselves computed from `pd.read_csv(...)` of
project-local processed CSVs.

The most numerically suggestive hits (`0.015245`, `0.030969`) appear in
the `resolution` string of the `active_learning.fisher_p_value` known
inconsistency. Spot-check: the script independently calls
`scipy.stats.fisher_exact(table, alternative='two-sided')` on the live
contingency table built from `validated_candidates_master.csv` (lines
~510 of the script), and the regenerated `fisher_full_cohort.p_value`
equals `0.015245` byte-for-byte in the diff — i.e. these are computed,
not hardcoded.

---

## Dependency trace

### File-IO reads (from `audit/canonical_dependency_scan.txt`)
`99_emit_canonical.py` reads from:
- `data/processed/master_molecule_table.csv`
- `data/processed/master_molecule_table_round1_updated.csv`
- `data/processed/model_input_table.csv`
- `data/source/invest_master_dataset.csv`
- `results/round1_eval/p0a_ablation_multiseed.csv`
- `results/round1_eval/p0a_ablation_paired_tests.json`
- `results/round1_eval/p0b_conformal_calibration.json`
- `results/round1_eval/task1_cv_matrix.csv`
- `results/round1_eval/task1_deployment_detail.csv`
- `results/round1_eval/task1_learning_curve.csv`
- `results/round1_eval/task2_baseline_significance.csv`
- `results/round1_eval/task3_ablation_results.csv`
- `results/round1_eval/stats_validation_results.json`
- `results/tables/round1_candidates_frozen.csv`
- `results/round2_eval/round2_acquisition_summary.json`
- `results/round2_eval/round2_final_candidates.csv`
- `results/validated_candidates_master.csv`
- `results/method_consistency_table.csv`
- `results/scscc2_batch2_summary.csv`
- `results/adc2_batch2_summary.csv`
- `results/adc2_final_10mol.csv`
- `results/diagnostics/distance_*.json` (4 files)
- `results/diagnostics/local_conformal.json`
- `results/diagnostics/mondrian_*.json`

Writes to:
- `results/canonical_metrics.json`

### Imports (project-internal)
**None.** Only `json`, `pathlib`, `numpy`, `pandas`, `scipy.stats`.

→ no need to recursively scan internal helper modules; there are none.

---

## Regeneration test

See `audit/canonical_regeneration_analysis.md` for full detail.

| Check | Result |
|---|---|
| Tmp repro repo created by `git archive HEAD` | `audit/_tmp_repro_repo/` |
| `python3 scripts/99_emit_canonical.py` exitcode | **0** |
| `missing_metrics` in regen output | **0** |
| `known_inconsistencies` in regen output | 5 (same as live) |
| Diff `before` vs `regen` total lines | 168 |
| Substantive numeric drift in any block written by 99_emit_canonical.py | **0** |
| Untracked-input FileNotFoundError | None |
| Block missing from regen | **`scs_cc2_extended_n13`** (159 of the 168 diff lines) |

### Diagnosis of the scs_cc2_extended_n13 gap

This block is not written by `99_emit_canonical.py`. It is added to
`canonical_metrics.json` by Phase 3 tooling:
- `scripts/scscc2_extension/build_cross_check_n13.py` (which writes
  `results/scscc2_extension_n13/{cross_check_n13.csv, stats_n13.json}`)
- followed by a manual JSON-patch step (logged in `session.md` around
  Phase 3) that copies that stats / per-molecule data into
  `canonical_metrics.json` under the `scs_cc2_extended_n13` key.

This is not an untracked input file (Step 4 not triggered). It is a
**second writer** to the same JSON, outside the scope of
`99_emit_canonical.py`.

For the manuscript-audit purpose:
- Numbers inside `scs_cc2_extended_n13` (13/13 sign retain, CI
  [0.7529, 1.0000], rule-of-three 0.23, per-molecule SCS-CC2 ΔE_ST)
  are **still locally reproducible**, but only via
  `scripts/scscc2_extension/build_cross_check_n13.py` + raw ricc2 outputs
  (the latter is Phase 4's responsibility).
- All other paper numbers (MAE 52.1 meV, conformal 35.7%, bootstrap
  324 meV, Fisher 0.015 / 0.031, library sizes, validation counts, etc.)
  are byte-for-byte reproducible from `99_emit_canonical.py` alone on
  commit `3a72bc9`.

---

## Domain coverage

See `audit/canonical_domain_coverage.md` for full detail.

| # | Domain | Status |
|---|---|---|
| 1 | library composition | COVERED |
| 2 | ML performance | COVERED |
| 3 | deployment metrics | COVERED |
| 4 | ablation | COVERED |
| 5 | uncertainty | COVERED |
| 6 | active learning | COVERED |
| 7 | validation outcomes | COVERED |
| 8 | method cross-check | COVERED (legacy 9-mol `method_crosscheck` + new 13-mol `scs_cc2_extended_n13`) |
| 9 | known inconsistencies | COVERED |

All 9 covered, 0 partially covered, 0 missing.

---

## Known inconsistencies check (Fisher p-value)

See `audit/canonical_known_inconsistencies_check.txt`.

Verification per Phase 2 protocol:

| Required check | Result |
|---|---|
| `0.015245` (or ≈) present | ✓ `active_learning.fisher_full_cohort.p_value_two_sided` = 0.015245; also `active_learning.fisher_p_value_paper` = 0.015245 |
| `0.030969` (or ≈) present | ✓ `active_learning.fisher_r1_subset.p_value` = 0.030969 |
| Full-cohort contingency 13/27 vs 0/8 labelled | ✓ `fisher_full_cohort.contingency_table = [[13, 14], [0, 8]]`; description = "Hz vs ALL non-Hz, full validated cohort — PAPER-CITED VALUE" |
| R1-subset contingency 6/9 vs 0/5 labelled | ✓ `fisher_r1_subset` = `hz_invest=6, hz_total=9, ap_invest=0, ap_total=5`; description = "R1 subset only (Hz vs 5AP) — DO NOT cite in paper" |
| Status `intentional_analysis_set_distinction` (or equivalent) | ✓ `known_inconsistencies` entry has `status: "intentional_analysis_set_distinction"` |
| Resolution explains both come from different analysis sets | ✓ resolution string explicitly maps: "0.015245 = full validated cohort Hz vs all non-Hz Fisher exact (13/27 vs 0/8) — used in Abstract, §3.4, Conclusion. 0.030969 = Round-1 subset Hz vs 5AP only (6/9 vs 0/5) — used in §3.4 paragraph and Fig 5(b) caption. The two p-values describe different cohorts and contrasts; both are correct in their own scope and the paper labels each scope flag explicitly." |
| Still `unresolved_contradiction`? | ✗ NO — status is `intentional_analysis_set_distinction` |

**No RED FLAG.** The Fisher p-value inconsistency is documented
correctly.

---

## Allowed conclusion

`results/canonical_metrics.json` can be treated as a **reproducible
processed-table-level source of truth for manuscript-number auditing**,
subject to the following warning:

> The top-level `scs_cc2_extended_n13` block is not produced by
> `scripts/99_emit_canonical.py` and therefore does not regenerate when
> that script is re-run. It is produced by
> `scripts/scscc2_extension/build_cross_check_n13.py` plus a manual JSON
> patch (logged in `session.md`). Manuscript numbers sourced from this
> block (13/13, CI [0.7529, 1.0000], rule-of-three 0.23, narrowest
> margin 10 meV, per-molecule SCS-CC2 ΔE_ST values) remain reproducible
> from local data but **only via that secondary script + the raw ricc2
> outputs to be verified in Phase 4**.

---

## Not allowed conclusion

This audit does **not** verify quantum-chemistry raw-output authenticity.
The fact that `canonical_metrics.json` is internally reproducible from
processed CSVs/JSONs says nothing about whether those processed CSVs
were correctly extracted from the original ADC(2) / SCS-CC2 ricc2 output
files.

**ADC(2)/SCS-CC2 raw-output provenance remains to be tested in Phase 4.**

---

## Deliverables produced this Phase

```
audit/phase2_git_status_before.txt                  2 lines
audit/phase2_repo_contamination_check.md            
audit/canonical_hardcoded_scan.txt                  0 lines
audit/canonical_targeted_number_scan.txt            23 lines
audit/canonical_dependency_scan.txt                 35 lines
audit/canonical_import_scan.txt                     5 lines
audit/canonical_hardcoded_findings.md               
audit/canonical_metrics.before.json                 44.8 KB (live snapshot)
audit/_tmp_repro_repo/                              git-archive copy
audit/emit_canonical.log                            stdout of regen
audit/emit_canonical.exitcode                       0
audit/canonical_regenerate_diff.txt                 168 lines
audit/canonical_regeneration_analysis.md            
audit/canonical_top_level_keys.txt                  14 keys
audit/canonical_domain_coverage.md                  
audit/canonical_known_inconsistencies_check.txt     
audit/phase2_canonical.md                           (this file)
```

---

## Hard-constraint compliance (Phase 2)

| Constraint | Status |
|---|---|
| No file under `paper/`, `results/`, `data/`, `figures/`, `scripts/` (non-`scripts/audit/`) modified | ✓ |
| All new files written under `audit/` and `scripts/audit/` | ✓ |
| `99_emit_canonical.py` run **only** in `audit/_tmp_repro_repo/` (NOT in live repo) | ✓ |
| No `git add` / `commit` / `push` / `rebase` / config | ✓ |
| No network access | ✓ |
| Did not modify `canonical_metrics.json` or any input CSV | ✓ |
| Did not auto-fix or backfill the `scs_cc2_extended_n13` gap | ✓ (reported as honest WARNING) |
| Did not treat `session.md` as evidence | ✓ |

---

## Status & gate

**Phase 2: COMPLETE.**

Final status: **PASS_WITH_WARNINGS**

The single warning is the `scs_cc2_extended_n13` block being written
outside `99_emit_canonical.py`'s scope, by a Phase 3 extension pipeline.
This is honestly disclosed; it does not invalidate the rest of
canonical_metrics.json, and the affected numbers will be independently
verified against raw ricc2 outputs in Phase 4.

**Halting.** Waiting for user instruction "继续 Phase 3" before proceeding
to Phase 3 (audit_numbers + statistical/ML reproduction).
