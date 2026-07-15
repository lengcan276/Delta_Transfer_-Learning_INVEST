# Phase 2 Step 5 — Canonical regeneration diff analysis

## Test setup
- Method: `git archive --format=tar HEAD | tar -xf - -C audit/_tmp_repro_repo`
- Then: `cd audit/_tmp_repro_repo && python3 scripts/99_emit_canonical.py`
- Compared: live `results/canonical_metrics.json` (saved as `audit/canonical_metrics.before.json`) vs regenerated `audit/_tmp_repro_repo/results/canonical_metrics.json`

## Exit code
```
$ cat audit/emit_canonical.exitcode
exitcode: 0
```

## Regeneration log key lines
```
Wrote /home/nudt_cleng/2026/release_n13/audit/_tmp_repro_repo/results/canonical_metrics.json
  missing_metrics:       0
  known_inconsistencies: 5
```
The script ran cleanly. 0 missing metrics inside its own scope. 5
known inconsistencies recorded (per design).

## Diff summary
- Total diff lines: **168**
- Lines unique to `before` (live): **159** — every line is part of one
  top-level block: **`scs_cc2_extended_n13`** (per-molecule data + summary
  stats + `narrowest_margin_*` + `rule_of_three_upper_bound` +
  `ci_method_v2`)
- Lines unique to `regen`: **1** — `]` closing the prior section
  (`known_inconsistencies`)
- Other diffs: **0**

## Diff classification

**REGENERATION_PARTIAL — substantive content gap is entirely confined to
one top-level block (`scs_cc2_extended_n13`).**

| Element | Reproduces? | Notes |
|---|---|---|
| `library` | ✓ byte-identical | from master_molecule_table.csv |
| `datasets` | ✓ byte-identical | from CV matrix + conformal JSON |
| `model_performance` | ✓ byte-identical | from task1 outputs |
| `deployment` | ✓ byte-identical | from task1_deployment_detail.csv |
| `ablation` | ✓ byte-identical | from p0a / task3 |
| `uncertainty` | ✓ byte-identical | from p0b_conformal |
| `active_learning` | ✓ byte-identical | includes Fisher full/R1 cohort recomputation |
| `validation` | ✓ byte-identical | from validated_candidates_master.csv |
| `method_crosscheck` | ✓ byte-identical | from method_consistency_table.csv |
| `known_inconsistencies` | ✓ byte-identical | including fisher_p_value resolution string |
| **`scs_cc2_extended_n13`** | ✗ **missing in regen** | Not written by 99_emit_canonical.py — see below |

## Untracked / out-of-scope dependency: scs_cc2_extended_n13

The `scs_cc2_extended_n13` block is produced by a different pipeline:

- **Writer:** `scripts/scscc2_extension/build_cross_check_n13.py` writes
  the upstream `results/scscc2_extension_n13/stats_n13.json` and
  `results/scscc2_extension_n13/cross_check_n13.csv`.
- **Patcher:** a separate manual JSON-patch step (logged in session.md
  around Phase 3) was used to copy `stats_n13.json` contents + per-molecule
  cross_check_n13 rows into `results/canonical_metrics.json` under the
  `scs_cc2_extended_n13` top-level key.

`scripts/99_emit_canonical.py` does **not** import or call
`build_cross_check_n13.py`, and does **not** mention `scs_cc2_extended_n13`
anywhere in its source. Therefore:

- It is **expected** that re-running `99_emit_canonical.py` removes the
  `scs_cc2_extended_n13` block.
- The block is **reproducible** from `scripts/scscc2_extension/build_cross_check_n13.py`
  + raw ricc2 outputs, but that reproduction belongs to Phase 4
  (quantum-chemistry raw-output provenance), not Phase 2.
- The `canonical_metrics.json` file therefore has **two writers**:
  (a) `scripts/99_emit_canonical.py` for everything except
  `scs_cc2_extended_n13`, and
  (b) `scripts/scscc2_extension/build_cross_check_n13.py` (plus the manual
  patch step) for `scs_cc2_extended_n13`.

## Untracked file dependency search (Step 4)
Not triggered — exitcode was 0 and no FileNotFoundError appeared in the
log. The diff is not caused by a missing input; it is caused by a missing
writer.

## Status

**REGENERATION_PARTIAL_BUT_EXPECTED.**

Within the scope of `scripts/99_emit_canonical.py`, the regeneration is
byte-identical. The 159-line content gap is the `scs_cc2_extended_n13`
block, which is produced by a separate Phase 3 extension pipeline whose
authenticity is to be tested in Phase 4 (raw ricc2 outputs).

For Phase 2 disposition: this contributes a **WARNING**, not a FAILURE,
because:
- 99_emit_canonical.py is honest about its scope (zero hidden writers
  inside it).
- The missing block is independently traceable via
  `scripts/scscc2_extension/build_cross_check_n13.py`.
- No numeric value computed by 99_emit_canonical.py has drifted.

What this means concretely for the manuscript audit:
- Any paper number coming from a domain inside 99_emit_canonical.py's
  scope (library, datasets, performance, ablation, UQ, AL, validation,
  method_crosscheck, known_inconsistencies) **is** processed-table
  reproducible from `commit 3a72bc9` via this script alone.
- Any paper number coming from `scs_cc2_extended_n13` (e.g. 13/13 sign
  retention, Clopper-Pearson [0.7529, 1.0000], rule-of-three 0.23,
  per-molecule SCS-CC2 ΔE_ST values) is **NOT** reproducible from
  99_emit_canonical.py alone — it requires
  `scripts/scscc2_extension/build_cross_check_n13.py` plus the manual
  patch logged in session.md, plus (per Phase 4) raw ricc2 outputs.
