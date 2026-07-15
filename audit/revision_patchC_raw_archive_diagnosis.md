# Patch C — Raw-output archive diagnosis

## Classification

**RELEASE_ASSET_RECOMMENDED** (SCS-CC2 n=13 cohort)
**MANIFEST_ONLY_RECOMMENDED** (ADC(2) 15 ybsi-pending entries)

## SCS-CC2 n=13 raw outputs

| question | answer |
|---|---|
| All 13 cohort molecules present locally? | **YES** |
| Mapping to 13 molecules | 1:1 via canonical COHORT table in `scripts/scscc2_extension/build_cross_check_n13.py` |
| Each molecule has both singlet and triplet raw outputs? | **YES** (26 / 26 files) |
| Each raw file has CC2 + SCS method banner? | **YES** (26 / 26) |
| Each raw file has runtime hostname banner? | **YES** (26 / 26, all compute-node names; 0 login-node red flags) |
| Each raw file has banner-confirmed def2-SVP basis? | **YES** (26 / 26) |
| Slurm scheduler logs present alongside ricc2 outputs? | **NO** (0 / 26; scheduler evidence is runtime-banner-supported only) |
| Preserved Turbomole `control` file alongside ricc2 outputs? | partial — Phase-2 extension batch typically preserves control; historical adc2_batch2_raw / adc2_batch2_final batches do not |
| sha256 catalogued? | **YES** — see `audit/revision_patchC_raw_provenance_manifest.tsv` |
| Total size | 1.16 MB (1,214,456 B) for the 26 SCS-CC2 raw files |
| Suitable for public archival? | **YES** (banner-confirmed; no scheduler/path-sensitive content beyond compute-node hostnames `nodeN`) |
| GitHub Release asset suggested? | **YES** (recommended) — tarball is < 2 MB, well within GitHub Release size limits |
| Zenodo suggested? | optionally — useful if a DOI is desired for archival citation, but not required for the small size |
| Manifest-only fallback? | sha256 manifest is already in the repository at `audit/revision_patchC_raw_provenance_manifest.tsv`; tarball is the additive next step |

## ADC(2) raw outputs

| question | answer |
|---|---|
| All raw outputs present locally? | **NO** — 15 R1-deploy ADC(2) raw outputs were computed on the `ybsi` cluster and were not rsynced into the local audit snapshot |
| Locally verified count | 20 / 35 (12 verified to printed precision + 8 verified to within sub-meV rounding-level differences attributable entirely to processed-table rounding) |
| ybsi pending count | 15 / 35 (7 of which have their *SCS-CC2* counterpart in the n=13 cohort and are locally verified on the SCS-CC2 side) |
| Suitable for public archival now? | NO — incomplete |
| Recommendation | **MANIFEST_ONLY_RECOMMENDED** — keep the manifest honest about the locally-verified / ybsi-pending split; defer ADC(2) tarball until ybsi rsync is performed in a future point release |

## POZ1 banner-only caveat

`Hz_POZ1_NPh21_CF31` is in the historical `adc2_batch2_final` batch.
The wrapper consumed the Turbomole `control` file at run time, so no
preserved sibling `control` is present. The basis assignment for the
SCS-CC2/def2-SVP calculation is **banner-derived only**: the `$basis`
one-electron and `$cbas` auxiliary blocks print as `def2-SVP` for all
elements inside the `ricc2_scscc2_*.out` runtime banner. This caveat
is recorded in the manifest TSV (notes column: `"historical batch,
no preserved sibling control"` for both sing and trip rows of POZ1)
and is documented at greater length in the Phase 5 issue-A audit
report.

## Scheduler evidence: runtime-banner-supported

All 26 SCS-CC2 raw outputs report compute-node hostnames in the
`ricc2 (<host>)` banner inside the `.out` file itself; this evidence
is intrinsic to the Turbomole output format and cannot be retroactively
edited without breaking the rest of the output's internal consistency.
**No** sibling `slurm-<jobid>.out` files were preserved in the local
audit snapshot. The manifest therefore records all 26 entries as
`scheduler_log_status = "slurm log not preserved"`, and the diagnosis
is **scheduler provenance is runtime-banner-supported rather than
scheduler-log-confirmed** — consistent with the audit Phase 5 Step 6
finding.

## Conclusion

The SCS-CC2 n=13 raw output set is **archive-ready** at 1.16 MB with
a complete sha256 manifest. **A GitHub Release asset is recommended**
for the SCS-CC2 tarball; Zenodo is optional. The ADC(2) raw output
set is **incomplete locally** and should be left at **manifest-only**
disclosure until the 15 ybsi-pending raw outputs are rsynced in a
future release.
