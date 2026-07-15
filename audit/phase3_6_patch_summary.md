# Phase 3.6 — patch summary

Audit phase: Phase 3.6 (recommended patch generation — dry-run, no apply)
Repository HEAD at audit start: `3a72bc9`
Date: 2026-05-20

---

## Status

**PATCH_GENERATED_WITH_PHASE4_DEPENDENCIES**

Reasoning:
- 13 recommended text edits successfully reconstructed in
  `audit/_tmp_phase3_6_patch_workspace/` (a git-archive copy).
- Unified diff written to `audit/phase3_6_recommended_patch.diff`
  (129 lines, 7 files touched).
- 11 of the 13 edits are safe to apply before Phase 4 (pure
  statistical-scope / cohort-size rewrites with no numeric or method
  dependency).
- 2 of the 13 edits (Fig4 caption_data numeric ranges) are direction-safe
  but their *exact numbers* depend on Phase 4 raw-output verification.
- Several additional corrections (3 JSON metadata fields, 2 per-molecule
  annotations) are deliberately **not** in the patch — they require a
  generator refactor that is most efficient post-Phase-4.

---

## Read-only compliance

| Check | Result |
|---|---|
| Live repo `paper/` modified | **No** |
| Live repo `results/` modified | **No** |
| Live repo `figures/` modified | **No** |
| Live repo `reviews/` modified | **No** |
| Live repo `data/` modified | **No** |
| Live repo `scripts/` modified (outside `scripts/audit/`) | **No** |
| Only `audit/` and `scripts/audit/` written | **Yes** |
| `git status --short` after Phase 3.6 | `?? audit/` and `?? scripts/audit/` only — verified by `audit/phase3_6_git_status_after.txt` |

The patch exists only as a `.diff` artifact under `audit/`. The live
repo is byte-for-byte identical to its state at the start of Phase 3.6
(modulo new audit-only output files).

---

## Files written this phase

```
audit/
├── _tmp_phase3_6_patch_workspace/         (git-archive scratch — modified copies live here, NOT in live repo)
├── 10_apply_log.txt                       12 applied + 1 WARN + 2 inline-fixed
├── phase3_6_recommended_patch.diff        129 lines, 7 files
├── phase3_6_changes_explained.md          per-edit explanation + priority + Phase 4 dependency
├── phase3_6_false_positives.md            grep hits that must NOT be edited
├── phase3_6_dependencies_on_phase4.md     edits whose exact form depends on Phase 4 outcomes
├── phase3_6_git_status_after.txt          post-phase repo state (clean)
└── phase3_6_patch_summary.md              (this file)

scripts/audit/
└── 10_generate_phase3_6_patch.py          dry-run edit applier (operates only on tmp workspace)
```

---

## What the patch contains

7 files, 13 edits (see `phase3_6_changes_explained.md` for line-by-line
detail):

| file | n edits | priority | safe_to_apply_before_phase4 |
|---|---|---|---|
| `paper/main.tex` | 3 | HIGH | yes |
| `paper_overleaf/main.tex` | 3 | HIGH | yes |
| `figures/caption_data/Fig0_workflow.json` | 2 | HIGH | yes |
| `figures/caption_data/Fig4_crosscheck.json` | 2 | HIGH | yes (direction); maybe (exact numbers) |
| `results/Table1_invest_candidates.tex` | 1 | HIGH | yes |
| `paper_overleaf/Table1_invest_candidates.tex` | 1 | HIGH | yes |
| `reviews/cover_letter.md` | 1 | HIGH | yes |

## What the patch does NOT contain (deferred, with reason)

| item | reason |
|---|---|
| `results/canonical_metrics.json` `scs_cc2_extended_n13.ci_method` | REQUIRES_GENERATOR_REFACTOR — hand-edit would be silently overwritten when generator re-runs |
| `results/canonical_metrics.json` `scs_cc2_extended_n13.paper_cited_signrate` | REQUIRES_GENERATOR_REFACTOR (add `paper_cited_scope` adjacent) |
| `results/scscc2_extension_n13/stats_n13.json` `ci_method` | REQUIRES_GENERATOR_REFACTOR (same generator) |
| per-molecule `narrowest_margin_warning` (Hz_NPh21_Cz2) | REQUIRES_GENERATOR_REFACTOR + depends on Phase 4 per-molecule verification |
| per-molecule `borderline_low_evidence_warning` (Hz_POZ1_NPh21_CF31) | REQUIRES_GENERATOR_REFACTOR + depends on Phase 4 per-molecule verification |

---

## Recommended action (3 options for the user)

### (a) Apply only safe_to_apply_before_phase4 changes manually, then continue Phase 4
- Apply the 11 fully-safe edits now (everything except Fig4 numeric
  ranges); leave the 2 maybe-numeric edits and the 5 generator-refactor
  items for after Phase 4.
- Pro: removes the most visible reader-facing inconsistencies
  immediately (the four-vs-thirteen mismatch between body text and
  captions).
- Con: requires a two-step revision process (rewrite now, generator
  refactor + maybe number-tweak after Phase 4).

### (b) **[RECOMMENDED DEFAULT]** Do not apply anything now; continue Phase 4 and merge all corrections after Phase 5
- Keep the live repo in its current state (which is internally
  consistent at the body-text level).
- Run Phase 4 (raw QC provenance) and Phase 5 (post-audit consolidation).
- Then apply the patch (possibly with revised numbers) in one
  coordinated revision pass, plus the generator refactor.
- Pro: one revision pass, all corrections coherent; avoids the risk
  of having to revisit Fig4 numeric ranges twice.
- Con: the n=4 / n=13 caption inconsistency persists in the live repo
  until after Phase 5.

### (c) End audit temporarily and enter manuscript-revision mode explicitly
- Stop the audit pipeline here. Switch operator role from auditor to
  author. Apply the patch (potentially with judgment-call modifications),
  refactor the generator, regenerate canonical_metrics.json /
  stats_n13.json, re-run audit_numbers.py.
- Pro: maximally fast convergence to a JCIM-ready paper.
- Con: leaves Phase 4 (raw quantum-chemistry authenticity) and Phase 5
  unfinished; the resulting paper would still rely on
  PROCESSED_TABLE_LEVEL evidence only for the n=13 cohort.

### Recommended default

**Option (b): Do not apply anything now; continue Phase 4 and merge all
corrections after Phase 5.**

This is the conservative choice that preserves audit integrity and
avoids double-rewriting.

---

## Not allowed conclusion

> This Phase 3.6 did **not** modify the manuscript or results. It only
> generated a recommended patch. **No raw SCS-CC2 or ADC(2) calculation
> authenticity has been verified in this phase.**

---

## Halting per protocol

**Phase 3.6: COMPLETE.** Patch artifact, explanation files, false-positive
list, Phase 4 dependency map, and post-phase git-status check all
written under `audit/`. Live repository is unchanged.

**Do not enter Phase 4 without explicit user instruction.**
