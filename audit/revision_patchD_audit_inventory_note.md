# Patch D Step 12 — audit/ inventory (user review only)

## Inventory snapshot

- **Total size of `audit/`**: 35 MB
- **Number of files (depth ≤ 4)**: 526 (see
  `audit/revision_patchD_audit_file_inventory.txt`)
- **Pre-existing tmp directories (not introduced by Patch D)**:
  - `audit/_tmp_phase3_6_patch_workspace`
  - `audit/_tmp_repro_repo`

## Scope statement

Patch D performs **inventory only**. No audit file is moved,
deleted, classified, or reclassified.

The final public-commit scope for `audit/` (whether each artefact
is committed to the public repository, moved into an
`audit/intermediate/` subtree, or omitted from the published
release) is a USER decision and is out of Patch D scope.

## Core evidence files likely worth keeping for the public commit

These are the canonical evidence artefacts that document the
audit trail and that downstream readers may want to reference:

- `audit/phase5_residual_issues.md` — read-only audit completion
  summary
- `audit/revision_patchB_tail_summary.md` — closes
  `audit_numbers.py` unresolved values to 0
- `audit/revision_patchC_summary.md` — Patch C
  repository / archive / provenance packaging summary
- `audit/revision_patchC_raw_provenance_manifest.tsv` — sha256
  manifest for the SCS-CC2 n=13 raw outputs (machine-readable)
- `audit/revision_patchC_raw_provenance_manifest.md` — companion
  notes
- `audit/revision_patchD_final_verification.md` — final
  submission-readiness summary (Step 13)

## What this note does NOT do

- Does NOT delete any audit file.
- Does NOT move any audit file.
- Does NOT label any audit file `KEEP` / `MOVE` / `DELETE`.
- Does NOT decide what the public commit scope of `audit/` is.

The user should review the inventory after Patch D, then decide
the final disposition.

Proceed to Step 13.
