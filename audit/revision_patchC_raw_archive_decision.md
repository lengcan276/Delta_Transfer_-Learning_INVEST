# Patch C — Raw archive decision

## Decision: Branch A (release-asset candidate, NO commit to git)

The SCS-CC2 n=13 raw outputs are small (1.16 MB, 26 files), publicly
archivable, and per `audit/revision_patchC_raw_archive_diagnosis.md`
already classified **RELEASE_ASSET_RECOMMENDED**. They should be
packaged as a GitHub Release asset (and optionally minted on Zenodo)
**outside the git working tree**.

The ADC(2) raw outputs are incomplete locally (15 ybsi-pending) and
remain at **MANIFEST_ONLY_RECOMMENDED**; no tarball is recommended
for ADC(2) until the ybsi rsync is performed in a future release.

## Hard constraints enforced

- **No tarball is committed to git history by Patch C.**
- **No `git add release_assets/*.tar.gz` is performed by Patch C.**
- **No tarball is created inside the repository working tree.**
- Any tarball created by the user must live at an external path
  (e.g., `~/INVEST_n13_raw_archive/`), NOT inside `release_n13/`.

## .gitignore safety (now in place)

The repository `.gitignore` was updated to include:

```
# Release artefacts must never be committed to git history.
# Raw-output tarballs are external assets (GitHub Release / Zenodo).
release_assets/
*.tar.gz
*.tar.bz2
*.tgz
*.zip
```

This protects the repository against an accidental
`git add release_assets/*.tar.gz` or `git add *.tar.gz` operation.
The `.gitignore` does NOT ignore:

- `audit/*.md` or `audit/*.tsv`
- `results/canonical_metrics.json`
- `results/scscc2_extension_n13/*.csv`
- `results/scscc2_extension_n13/*.json`

## Recommended (NOT auto-executed) tarball-build recipe

If the user decides to publish the SCS-CC2 n=13 raw archive, the
following commands are guidance only:

```bash
# Create the external tarball directory (outside the git working tree):
mkdir -p ~/INVEST_n13_raw_archive

# Build the tarball using the canonical manifest as the file list.
# The manifest lives at audit/revision_patchC_raw_provenance_manifest.tsv;
# the relative_path column points into /home/nudt_cleng/2026/results/.
( cd /home/nudt_cleng/2026/results
  tar -czf ~/INVEST_n13_raw_archive/INVEST_n13_scscc2_raw_provenance.tar.gz \
      $(awk -F'\t' 'NR>1 && $11=="locally verified" {print $4}' \
          ~/2026/release_n13/audit/revision_patchC_raw_provenance_manifest.tsv) )

# Record the tarball sha256 and size (committed into audit/ only):
sha256sum ~/INVEST_n13_raw_archive/INVEST_n13_scscc2_raw_provenance.tar.gz \
    > audit/revision_patchC_raw_archive_external_tarball.sha256
```

Patch C does NOT auto-execute these commands. The user runs them
interactively when ready to upload the GitHub Release asset.

## Documents created in support of the archive plan

- `audit/revision_patchC_raw_provenance_manifest.tsv` (sha256 catalogue)
- `audit/revision_patchC_raw_provenance_manifest.md` (companion notes)
- `audit/revision_patchC_raw_archive_diagnosis.md` (suitability assessment)
- `audit/revision_patchC_raw_archive_release_plan.md` (release plan,
  next document)
- `audit/revision_patchC_raw_archive_decision.md` (this file)

## Branch decision recap

- SCS-CC2 n=13 → Branch A (release asset; tarball external, manifest
  committed).
- ADC(2) 15 ybsi-pending → Branch B (manifest-only; no tarball until
  ybsi rsync).
- `.gitignore` updated to protect against tarball-in-repo accident.
