# Patch B (post review-fix) — Single-writer validation

## Verdict: **PASS_SINGLE_WRITER_CANONICAL**

15/15 checks PASS. Validator:
`scripts/audit/15_validate_patchB_single_writer.py` (read-only;
performs a delete-and-regenerate chain test via a tempfile-backup
+ restore pattern so the live `canonical_metrics.json` is never lost).

## Validator output (raw)

```
[PASS] build_cross_check_n13.py does not write canonical_metrics.json
[PASS] 99_emit_canonical.py is the single canonical writer
[PASS] delete-and-regenerate chain test
[PASS] scs_cc2_extended_n13 contains all required aliases
[PASS] scs_cc2_extended_n13.generator value:
       got: 'scripts/99_emit_canonical.py::build_scs_cc2_extended_n13'
[PASS] scs_cc2_extended_n13.upstream_generator value:
       got: 'scripts/scscc2_extension/build_cross_check_n13.py'
[PASS] scs_cc2_extended_n13.screened_cohort_n == 13:  got: 13
[PASS] scs_cc2_extended_n13.sign_disagreements == 0:  got: 0
[PASS] scs_cc2_extended_n13.paper_cited_signrate is screened-cohort form:
       got: '0 sign disagreement within the ADC(2)-screened cohort'
[PASS] scs_cc2_extended_n13.repository == INVEST-n13:
       got: 'https://github.com/lengcan276/INVEST-n13'
[PASS] scs_cc2_extended_n13.raw_provenance_status present (non-empty)
[PASS] per_molecule count == 13 (representation: dict):  got count=13
[PASS] per_molecule mol_id set equals cross_check_n13.csv
[PASS] no FedSchNet-ReorgEnergy in generated metadata
[PASS] no audit-Phase-4/5 in paper-facing fields

summary: 15/15 checks passed
exit: 0
```

## Check meanings

| # | check | proves |
|---|---|---|
| 1 | `build_cross_check_n13.py` does not write `canonical_metrics.json` | upstream writer scope is bounded to CSV+stats only (detection looks for actual write operations, not doc references) |
| 2 | `99_emit_canonical.py` is the single canonical writer | no other script in `scripts/` writes `canonical_metrics.json` (audit/ scripts excluded as read-only by convention) |
| 3 | delete-and-regenerate chain test | `99_emit_canonical.py` can reproduce `canonical_metrics.json` from scratch |
| 4 | required aliases present | schema completeness: `generator`, `upstream_generator`, `screened_cohort_n`, `sign_disagreements`, `rule_of_three_upper_bound`, `paper_cited_signrate`, `paper_cited_scope`, `ci_method`, `repository`, `raw_provenance_status`, `audit_report_reference`, `generated_from` |
| 5 | `generator` field value matches expected | provenance pointer correct |
| 6 | `upstream_generator` field value matches expected | upstream provenance pointer correct |
| 7 | `screened_cohort_n == 13` | cohort size pinned |
| 8 | `sign_disagreements == 0` | headline result preserved |
| 9 | `paper_cited_signrate` is screened-cohort form | paper-facing wording is "0 sign disagreement within the ADC(2)-screened cohort", not "13/13" |
| 10 | `repository` == INVEST-n13 | repo identity correct |
| 11 | `raw_provenance_status` present and non-empty | raw provenance disclosure surfaced |
| 12 | `per_molecule` count == 13 | cohort size at per-molecule level; representation is "dict keyed by mol_id" (logged) |
| 13 | mol_id set equals cross_check_n13.csv | per-molecule keys match upstream CSV exactly |
| 14 | no FedSchNet-ReorgEnergy | repo-identity hygiene |
| 15 | no audit-Phase-4/5 in paper-facing fields | internal-audit terminology hygiene |

## per_molecule representation

Representation: **`dict` keyed by `mol_id`**.

Explicitly recorded in `canonical_metrics.json["scs_cc2_extended_n13"]
["per_molecule_representation"]`. Validation script does not assume
list indexing — check #12 reads `len(pm)` (works for both dict and
list), and check #13 reads `set(pm.keys())` vs falls back to
`{entry["mol_id"] for entry in pm}` for list representations.

## Single writer formal assignment

- `scripts/scscc2_extension/build_cross_check_n13.py` → writes
  `results/scscc2_extension_n13/cross_check_n13.csv` and
  `results/scscc2_extension_n13/stats_n13.json` only.
- `scripts/99_emit_canonical.py::main` → sole writer of
  `results/canonical_metrics.json`.
- `scripts/99_emit_canonical.py::build_scs_cc2_extended_n13` → sole
  writer of `canonical_metrics.json["scs_cc2_extended_n13"]`.
