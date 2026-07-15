# Patch C — Raw archive release plan

## SCS-CC2 n=13 raw archive

### Branch A — external tarball as GitHub Release asset

- **Tarball name (recommended)**:
  `INVEST_n13_scscc2_raw_provenance.tar.gz`
- **External path (NOT in repository)**:
  `~/INVEST_n13_raw_archive/INVEST_n13_scscc2_raw_provenance.tar.gz`
- **Tarball size estimate**: ~1.5 MB compressed (uncompressed
  payload is 1.16 MB, 26 files; gzip on Turbomole text outputs
  typically yields ~50% compression).
- **Tarball sha256**: to be recorded in
  `audit/revision_patchC_raw_archive_external_tarball.sha256`
  after the user runs the recommended `sha256sum` command from
  `audit/revision_patchC_raw_archive_decision.md`.
- **Recommended upload target**:
  - **GitHub Release asset** on
    `https://github.com/lengcan276/INVEST-n13/releases` —
    primary recommendation for the n=13 SCS-CC2 archive
    (small size, citable URL, no DOI minting required).
  - **Optionally also Zenodo**: if a DOI is desired for archival
    citation, the same tarball can be deposited at Zenodo and the
    DOI added to the Data Availability section of the manuscript
    in a future revision. Patch C does not require this.
- **Repository commits only the manifest / checksums /
  documentation, not the tarball itself.** Committed artefacts:
  - `audit/revision_patchC_raw_provenance_manifest.tsv`
  - `audit/revision_patchC_raw_provenance_manifest.md`
  - `audit/revision_patchC_raw_archive_external_tarball.sha256`
    (after user runs the recommended `sha256sum` command)

## ADC(2) raw archive

### Branch B — manifest-only

- 20 / 35 raw outputs are locally verified (covered transitively
  via the SCS-CC2 manifest for the cohort overlap; ADC(2)
  per-file manifest is deferred).
- 15 / 35 raw outputs are ybsi-pending; they were computed on the
  `ybsi` compute cluster and were not rsynced into the local audit
  snapshot at the time of this release.
- **No ADC(2) tarball is produced in Patch C.**
- Recommendation: in a future point release, after ybsi rsync,
  extend the manifest generator
  (`scripts/audit/17_make_raw_provenance_manifest.py`) with an
  `ADC2_COHORT` table and emit an ADC(2)-specific manifest plus
  a `INVEST_n13_adc2_raw_provenance.tar.gz` external tarball.
- Until that happens, the manuscript Data Availability section
  honestly states "Raw outputs for the ADC(2)/def2-SVP validation
  set (35 molecules, singlet and triplet outputs) are partially
  included in the present release ... The remaining 15 ADC(2) raw
  outputs were computed on the `ybsi` compute cluster and were not
  rsynced into the local audit snapshot at the time of submission;
  they will be added to the raw-archive tarball in a subsequent
  point release."

## Action items the user runs interactively (NOT automated)

1. Decide whether to build and upload the SCS-CC2 tarball now or
   defer to first public release.
2. If building now, run the recipe in
   `audit/revision_patchC_raw_archive_decision.md` (Section
   "Recommended (NOT auto-executed) tarball-build recipe").
3. After upload, append the GitHub Release asset URL (or Zenodo
   DOI) to the manuscript Data Availability section in a
   subsequent revision pass — not in Patch C.
4. Schedule ybsi rsync for the 15 ADC(2) raw outputs and extend
   the manifest accordingly when those outputs are local.

## Constraints (recap)

- No tarball committed to git history by Patch C.
- No network / ssh / rsync / scp executed by Patch C.
- `.gitignore` updated to protect against accidental
  `git add *.tar.gz`.
