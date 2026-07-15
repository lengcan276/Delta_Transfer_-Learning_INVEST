# Patch B review-fix — Final report

Repository HEAD (pre-revision): `3a72bc9`
Branch: `revision-after-phase5`
Date: 2026-05-20
Canonical repository: `https://github.com/lengcan276/INVEST-n13`

## Status

**PASS_PATCH_B_REVIEW_FIX_READY**

## What was fixed

1. **Upstream path consistency.** `build_cross_check_n13.py` was
   writing CSV + stats to root `results/` (incorrect). The canonical
   upstream directory used by Phase 3.5 / 4 / 5 is
   `results/scscc2_extension_n13/`. Both the writer
   (`build_cross_check_n13.py`) and the reader
   (`99_emit_canonical.py::build_scs_cc2_extended_n13`) were
   refactored to use the subdirectory. Root-level
   `results/cross_check_n13.csv` and `results/stats_n13.json` were
   reverted to HEAD content (`git checkout HEAD --`); these are
   tracked legacy snapshots and the decision on whether to git-rm
   them is USER_DECISION_REQUIRED (recorded in
   `audit/revision_patchB_review_path_diagnosis.md`).

2. **Explicit scs_cc2_extended_n13 schema aliases added.** The
   following top-level fields were added to
   `canonical_metrics.json["scs_cc2_extended_n13"]` so downstream
   validators / paper-facing readers can anchor on stable names:
   `generator`, `upstream_generator`, `screened_cohort_n`,
   `sign_disagreements`, `paper_cited_scope`, `repository`,
   `raw_provenance_status`, `audit_report_reference`, `generated_from`,
   `per_molecule_representation`. Pre-existing fields
   (`paper_cited_bound`, `n_total`, `n_sign_retain`, `repository_canonical`)
   were retained to avoid breaking any downstream consumer.

3. **paper_cited_signrate corrected to screened-cohort form.**
   Was: `"13/13"`. Now: `"0 sign disagreement within the
   ADC(2)-screened cohort"`. `ci_method` was also updated to the
   explicit disclaimer form: `"Not reported as a Clopper-Pearson
   population confidence interval because the 13 molecules were
   ADC(2)-preselected."`. The full-text long-form rule-of-three
   wording from the upstream stats file is preserved in a separate
   field `ci_method_long_form`.

4. **Numeric drift TSV generated.**
   `audit/revision_patchB_numeric_drift_check.tsv` lists 117
   UNCHANGED numeric cells + 19 EXPECTED_METADATA_CHANGE entries +
   0 UNEXPECTED_NUMERIC_DRIFT. The MD report
   `audit/revision_patchB_numeric_drift_check.md` is the human
   summary; the TSV is the machine-readable artifact.

5. **per_molecule representation documented.** `per_molecule` is a
   `dict` keyed by `mol_id` (13 entries). Explicitly recorded in
   `canonical_metrics.json["scs_cc2_extended_n13"]
   ["per_molecule_representation"] = "dict keyed by mol_id"`. The
   single-writer validation script
   (`scripts/audit/15_validate_patchB_single_writer.py`) handles
   both dict and list representations without assuming list indexing.

## Quality gates (all PASS)

| gate | status | evidence |
|---|---|---|
| upstream path consistency | PASS — writer + reader both target `results/scscc2_extension_n13/` | `audit/revision_patchB_review_path_diagnosis.md` |
| schema completeness | PASS — 12/12 required aliases present | `audit/revision_patchB_review_canonical_keys.txt` (post-fix re-check inside validator) |
| single-writer validation | PASS — 15/15 validator checks | `audit/revision_patchB_single_writer_validation.md` |
| numeric drift | PASS — 0 UNEXPECTED_NUMERIC_DRIFT; 117 UNCHANGED numeric cells | `audit/revision_patchB_numeric_drift_check.tsv` + `.md` |
| stale-metadata grep | PASS — 0 STALE_PAPER_FACING_METADATA in canonical writer outputs; 1 STALE entry confined to legacy root snapshot (documented) | `audit/revision_patchB_review_stale_terms_classification.md` |
| audit_numbers.py completeness | PASS — exit 0, 0/7 Major checks, 2 unresolved (both Patch A informational) | `audit/revision_patchB_review_audit_numbers_summary.md` |

## What did not change

- No raw calculation files changed.
- No scientific numerical values changed (117 UNCHANGED numeric
  cells; 0 UNEXPECTED_NUMERIC_DRIFT).
- No molecule classifications changed.
- No manuscript text changed (`paper/main.tex`, `paper_overleaf/main.tex`,
  `figures/caption_data/`, `reviews/cover_letter.md` — all untouched
  in this review-fix; the only paper-tree file touched is the
  auto-regenerated audit artefact `paper/audit_reports/consistency_audit.md`
  whose header says "Audit artefact only — `paper/main.tex` is not
  modified by this script").
- No git commit or push.
- No network, no ssh, no rsync, no scp.
- No entry into Patch set C.

## Files modified by the review-fix

| file | reason |
|---|---|
| `scripts/scscc2_extension/build_cross_check_n13.py` | output path corrected to `results/scscc2_extension_n13/` |
| `scripts/99_emit_canonical.py` | reader path corrected; explicit schema aliases added; paper_cited_signrate switched to screened-cohort form; ci_method switched to explicit disclaimer form |
| `scripts/audit/15_validate_patchB_single_writer.py` | new validator (created, then fixed false-positive writer-detection heuristic) |
| `results/scscc2_extension_n13/stats_n13.json` | regenerated by the corrected `build_cross_check_n13.py`; rule-of-three primary + CP transparency + repo URL |
| `results/scscc2_extension_n13/cross_check_n13.csv` | regenerated; **byte-identical** to pre-Patch-B file |
| `results/canonical_metrics.json` | regenerated by `99_emit_canonical.py` with the new schema aliases; per-molecule values byte-identical to pre-Patch-B |
| `results/cross_check_n13.csv` | **reverted to HEAD** (legacy root snapshot, no further writes) |
| `results/stats_n13.json` | **reverted to HEAD** (legacy root snapshot, no further writes) |
| `paper/audit_reports/consistency_audit.md` | auto-regenerated side-effect of running audit_numbers.py (header explicitly identifies it as an audit artefact) |

## audit_report_reference field

The `audit_report_reference` field in the
`scs_cc2_extended_n13` block points to `audit/phase4_qc.md`. This is
intentional: that report is the canonical raw-output provenance
verification document for the SCS-CC2 n=13 cohort. The field stores
the file path inside the audit tree; it does NOT propagate into the
paper-facing fields, which are independently grep-checked for the
strings `audit Phase`, `Phase 4`, `Phase 5`.

## USER_DECISION_REQUIRED carry-overs

- Whether to retain or git-rm the legacy root snapshots
  `results/cross_check_n13.csv` and `results/stats_n13.json`
  (currently reverted to HEAD content; orthogonal to Patch B).
- Whether to keep `https://github.com/lengcan276/INVEST-n13` as the
  permanent Data Availability URL (carried over from Patch A
  hygiene check).

Neither blocks Patch B.

## Next step

- User reviews the git diff for the Patch B review-fix.
- If approved, decide on the legacy-snapshot disposition (above).
- If everything is acceptable, proceed to Patch set C (or back to
  Patch B refinement if any gate is judged insufficient).

No commit, no push. Awaiting user confirmation. Do not enter Patch C.
