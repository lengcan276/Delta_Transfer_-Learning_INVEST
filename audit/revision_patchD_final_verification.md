# Patch D — Final submission-readiness verification

Repository HEAD (pre-revision): `3a72bc9`
Branch: `revision-after-phase5`
Date: 2026-05-21
Canonical repository: `https://github.com/lengcan276/INVEST-n13`

## Status

**PASS_PATCH_D_SUBMISSION_READY_PENDING_USER_COMMIT**

All 14 Patch D steps completed. Every quality gate is met. The
repository is in a state where the user can review the cumulative
diff and create the final commit(s).

## Summary

| metric | value |
|---|---|
| `audit_numbers.py` unresolved | **0** |
| `audit_numbers.py` Major checks | **0 / 7** |
| numeric drift (SCS-CC2 n=13 cohort) | **0** (PASS_NUMERICALLY_INERT) |
| LaTeX local status | **compiled** (latexmk exit 0, 25-page PDF produced); 4 pre-existing undefined `\cite` warnings (`Hellweg2008`, `Tajti2009`) noted as bibliography gap — out of Patch D scope |
| stale wording status | **clean** — 0 STALE_FORMAL_TEXT / STALE_STATISTICAL_SCOPE / STALE_REPO_REFERENCE / STALE_N4_REFERENCE / STALE_BIT_IDENTICAL_WORDING |
| README / DATA_AVAILABILITY status | **consistent** with paper Data Availability section and canonical_metrics.json |
| raw archive status | SCS-CC2 n=13 = RELEASE_ASSET_RECOMMENDED (external GitHub Release; tarball NOT in git); ADC(2) = MANIFEST_ONLY_RECOMMENDED (15 ybsi-pending) |
| tarball tracking status | **0** tracked or staged `.tar.gz` / `.tgz` / `.tar.bz2`; pre-existing `INVEST_paper_overleaf_n13_v3.zip` is an Overleaf bundle, not a raw-output tarball |
| repository URL status | canonical `https://github.com/lengcan276/INVEST-n13` confirmed in `README.md`, `DATA_AVAILABILITY.md`, `paper/main.tex`, `paper_overleaf/main.tex`, `results/canonical_metrics.json` |

## What changed in Patch D

| file | change | nature |
|---|---|---|
| `scripts/99_emit_canonical.py` | line 958: source-label string `"results/stats_n13.json"` → `"results/scscc2_extension_n13/stats_n13.json"` | LABEL_ONLY_MISREFERENCE fix (Step 2); behaviour-inert; numeric drift = 0 |
| `.gitignore` | added 7 anchored LaTeX-build artefact patterns (`/main.aux`, `/main.fdb_latexmk`, `/main.fls`, `/main.log`, `/main.out`, `/main.pdf`, `/acs-main.bib`) | Step 7 cleanup; patterns are root-anchored so they cannot accidentally hide Turbomole `ricc2_*.out` raw outputs elsewhere |
| `scripts/audit/18_patchD_numeric_safety_check.py` (new) | Patch D numeric-drift checker | Step 6 helper |
| `audit/revision_patchD_*.md` / `.txt` / `.log` / `.exitcode` / `.diff` / `.tsv` | new Patch D audit reports + transient command logs | Steps 0–13 evidence trail |

No other source-of-truth file modified in Patch D.

## What did not change

- **No raw calculation files modified.**
- **No scientific numerical values changed.**
- **No molecule classifications changed.**
- **No new scientific claims added.**
- **No raw-output tarball committed to git.**
- **No git commit or push.**
- **Patch D did not upload release assets or retrieve ybsi files.**
- **No CI/CD added.**
- **No `dependencies` / `requirements` / environment file modified.**
- **No `results/` directory restructured.**
- **No `audit/` file deleted, moved, or reclassified.**

## Remaining user decisions before final commit

These are real decisions for the user; none block Patch D's PASS
status, but each affects the public release:

1. **Remove the legacy `fed_old` git remote** manually:
   ```bash
   git remote remove fed_old
   ```
   Recommended before any first push of the release.

2. **(Optional) Delete legacy root snapshots** if still considered
   stale: `git rm results/cross_check_n13.csv results/stats_n13.json`.
   These were reverted to HEAD content in the Patch B review-fix
   and are no longer actively referenced by any code or formal
   text after the Patch D Step 2 source-label fix.

3. **Upload SCS-CC2 raw archive** as a GitHub Release asset
   (and optionally as a Zenodo deposit for DOI citation). Recipe
   in `audit/revision_patchC_raw_archive_decision.md`. The tarball
   must remain external — do not `git add` it.

4. **Schedule `ybsi` rsync** for the 15 R1-deploy ADC(2) raw
   outputs in a subsequent point release; extend the manifest
   accordingly when those outputs are local.

5. **Final `audit/` public commit scope** — review
   `audit/revision_patchD_audit_file_inventory.txt` (526 files,
   35 MB) and decide which artefacts enter the public commit
   and which (e.g., `audit/_tmp_*/`) stay out.

6. **Final target branch and commit message.** The current branch
   is `revision-after-phase5`; the user decides whether to commit
   on this branch or rebase onto another branch.

7. **(Optional manuscript follow-up, out of Patch D scope)**
   Add `\bibitem` entries for `Hellweg2008` and `Tajti2009` to
   resolve the 4 pre-existing undefined-citation warnings.

## Recommended final manual commands (guidance only; NOT executed)

```bash
# inspect the cumulative state
git status --short
git diff --stat
git remote -v

# remove the legacy remote (only if the user confirms)
git remote remove fed_old

# stage and commit (only when ready; user chooses message)
git add ...
git commit -m "..."
```

Patch D does NOT run `git add`, `git commit`, `git push`, or any
network operation.
