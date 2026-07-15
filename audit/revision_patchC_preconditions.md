# Patch C — Accepted preconditions

Date: 2026-05-20
Branch: `revision-after-phase5`
Canonical repository: `https://github.com/lengcan276/INVEST-n13`

## Accepted prior state

- **Patch A hygiene accepted.**
- **Patch B accepted after review-fix.** Status: PASS_PATCH_B_REVIEW_FIX_READY.
- **Patch B-tail accepted.** Status: PASS_PATCH_B_TAIL_UNRESOLVED_ZERO.
- **Phase 2 canonical reproducibility gap closed.**
- `results/canonical_metrics.json` has a single writer:
  `scripts/99_emit_canonical.py`.
- `audit_numbers.py` unresolved = **0**.
- `audit_numbers.py` Major checks = **0 / 7**.
- Scientific numeric drift = **0**.
- Canonical repository confirmed:
  `https://github.com/lengcan276/INVEST-n13`.
- GitHub identity confirmed by user; not USER_DECISION_REQUIRED.

## Patch C scope

Repository / archive / provenance packaging only:

1. canonical repository identity sweep
2. remote configuration report (no auto-modification)
3. legacy root snapshot disposition
4. raw-output provenance archive diagnosis
5. sha256 provenance manifest
6. raw archive decision (no tarballs committed to git)
7. README.md / DATA_AVAILABILITY.md documentation
8. audit/ inventory only (no disposition decision)
9. final-check re-run
10. summary report

## Patch C must not

- Reopen Patch A, Patch B, or Patch B-tail unless a validation
  failure appears.
- Reopen manuscript scientific interpretation.
- Reopen Patch B generator logic.
- Recompute any scientific value.
- Commit any tarball.
- Decide audit/ final commit scope (deferred until after Patch D).
- Enter Patch D.
