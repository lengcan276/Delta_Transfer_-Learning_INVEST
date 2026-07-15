# Patch C — audit/ housekeeping plan (inventory only)

## Inventory

- **Total size of `audit/`**: 34 MB
- **Number of files (depth ≤ 4)**: 467 (see
  `audit/revision_patchC_audit_file_inventory.txt`)
- **Identified `_tmp_*` / `_intermediate*` directories**:
  - `audit/_tmp_phase3_6_patch_workspace`
  - `audit/_tmp_repro_repo`
- **Obvious temp files** (matching `*.tmp` or `*~`): 0

## Scope statement

Patch C performs **inventory only**. No audit file is moved,
deleted, classified, or reclassified.

The final disposition of `audit/` files — whether each report is
kept in the public commit, moved into an `audit/intermediate/`
subtree, or omitted from the published release — is deferred to
after Patch D. Patch C does not pre-empt those decisions.

## Recommendation

The user should review the inventory after Patch D, then decide
which `audit/` artefacts enter the public repository commit. The
two `_tmp_*` directories above are obvious candidates for either
move-to-`audit/intermediate/` or exclusion, but that decision is
not in Patch C scope.

## Files NOT classified by this plan

- Phase 0–5 audit reports
- Revision-mode Patch A / B / B-tail / C audit reports
- Generated tmp files inside `_tmp_*/`
- Validator outputs

(All inventoried in `revision_patchC_audit_file_inventory.txt`.)

## What Patch C does NOT do here

- Does NOT label any audit file `MOVE_TO_AUDIT_INTERMEDIATE`,
  `DELETE_AFTER_USER_APPROVAL`, or `KEEP_PUBLIC_AUDIT_REPORT`.
- Does NOT perform file-by-file disposition.
- Does NOT touch any file inside `audit/`.
