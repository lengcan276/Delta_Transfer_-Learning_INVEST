# Patch D — Accepted preconditions

Date: 2026-05-21
Branch: `revision-after-phase5`
Canonical repository: `https://github.com/lengcan276/INVEST-n13`

## Accepted prior state

- Patch A hygiene accepted.
- Patch B = PASS_PATCH_B_REVIEW_FIX_READY.
- Patch B-tail = PASS_PATCH_B_TAIL_UNRESOLVED_ZERO.
- Patch C = PASS_PATCH_C_WITH_USER_DECISION_REQUIRED.
- Phase 2 canonical reproducibility gap closed.
- canonical_metrics.json single writer = scripts/99_emit_canonical.py.
- audit_numbers.py unresolved = 0, Major = 0/7.
- Scientific numeric drift = 0.
- README.md + DATA_AVAILABILITY.md use canonical INVEST-n13 URL.
- GitHub identity confirmed.
- No raw-output tarball tracked or staged.

## Patch D scope

Manuscript-level final verification + minimal fixes only. Steps 1–14.
No new patches, no commit, no push, no scientific rewrite.

## Carry-forward user decisions (not blocking Patch D)

1. `git remote remove fed_old`
2. Optional fix of source-label mislabel at `99_emit_canonical.py:958`
   (now mandatory in Patch D Step 2 if confirmed LABEL_ONLY_MISREFERENCE)
3. SCS-CC2 raw archive → GitHub Release / Zenodo
4. Legacy root snapshot disposition
5. `audit/` final public commit scope
6. ybsi ADC(2) raw-output retrieval
