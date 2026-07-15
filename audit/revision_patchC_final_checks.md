# Patch C — Final checks

## Targets

- `audit_numbers.py` unresolved = **0**
- `audit_numbers.py` Major checks tripped = **0 / 7**
- No formal-file `FedSchNet-ReorgEnergy` references
- No formal-file internal audit phase terms
- No `release_assets/*.tar.gz` tracked or staged
- No raw-output tarball inside the git working tree

## Results

| check | result |
|---|---|
| `scripts/99_emit_canonical.py` exitcode | **0** |
| `scripts/audit_numbers.py` exitcode | **0** |
| `audit_numbers.py` unresolved | **0** |
| `audit_numbers.py` Major checks tripped | **0 / 7** |
| `audit_numbers.py` non-trivial numbers extracted | 257 |
| stale-term grep total raw hits | 2 (both false positives, see classification) |
| `FedSchNet-ReorgEnergy` references in formal files | **0** |
| internal `Phase 4` / `Phase 5` / `Step 5.5` in formal files | **0** |
| `release_assets/` tracked or staged | **0** |
| `release_assets/*.tar.gz` tracked or staged | **0** |
| raw-output tarball (`.tar.gz` / `.tgz`) in git working tree | **0** |
| README uses canonical INVEST-n13 URL? | **YES** |
| DATA_AVAILABILITY uses canonical INVEST-n13 URL? | **YES** |
| `.gitignore` protects against new tarball additions? | **YES** (added `release_assets/`, `*.tar.gz`, `*.tar.bz2`, `*.tgz`, `*.zip`) |

## Stale-term grep — full hit classification

`grep -RniE "FedSchNet-ReorgEnergy|audit Phase|Phase 4|Phase 5|Step 5\.5|Issue A|1e-13|machine epsilon"`
over `README*`, `DATA_AVAILABILITY*`, `paper/main.tex`,
`paper_overleaf/main.tex`, `reviews/cover_letter.md`,
`results/canonical_metrics.json`:

| file:line | match | classification |
|---|---|---|
| `README.md:66` | `reference state. Please open an issue at` | **FALSE_POSITIVE** — regex `Issue A` matches the substring `issue a` in `issue at` (case-insensitive). Not an internal-audit reference. |
| `DATA_AVAILABILITY.md:84` | `not yet in the release tarball, please open an issue at` | **FALSE_POSITIVE** — same regex artefact (`issue a` ↔ `Issue A`). |

After the README audit-history wording was tightened (Phase / Patch
prose removed from the bullet list; file-path-only descriptions
retained), no substantive internal-audit phase terminology remains
in formal documentation.

## Pre-existing tracked artefacts (informational)

- `INVEST_paper_overleaf_n13_v3.zip` (3.1 MB, tracked in git at HEAD)
  is a **paper-overleaf bundle**, not a raw-output tarball. It is
  pre-existing tracked content unrelated to Patch C. The new
  `.gitignore` rules apply only to **future untracked** zip /
  tarball additions and do not affect this already-tracked file.
- `audit/_tmp_phase3_6_patch_workspace/INVEST_paper_overleaf_n13_v3.zip`
  and `audit/_tmp_repro_repo/INVEST_paper_overleaf_n13_v3.zip` are
  copies inside historical audit workspaces; Patch C does not touch
  them, and the future disposition of `audit/_tmp_*/` is deferred
  to the post-Patch-D audit-housekeeping decision.

## Conclusion

All Patch C final-check targets are met. No regressions introduced
in `audit_numbers.py`; no FedSchNet leakage; no internal audit
phase terms in formal documentation; no raw-output tarball in the
git working tree; `.gitignore` protects against future accidental
tarball commits.
