# Patch C — Raw provenance manifest (companion to TSV)

## Coverage

- SCS-CC2 n=13 cohort: 26 / 26 files locally verified
  (1214456 bytes total, ~1.16 MB).
- All 13 molecules from `results/scscc2_extension_n13/cross_check_n13.csv`
  have both singlet and triplet entries in the manifest.

## Banner / basis / hostname flags

- Method-banner status: `CC2+SCS banner present` for every locally
  verified file (each `ricc2_*.out` contains the CC2 declaration AND
  the Spin-Component Scaling annotation).
- Basis-banner status: `banner-confirmed def2-SVP` for every locally
  verified file.
- Runtime-banner status: compute-node hostname recorded for every
  locally verified file. **0 / 26** files trigger
  the login-node red-flag pattern (`login|head|master|submit|frontend`).
- Scheduler-log status: **0 / 26** files have a
  sibling `slurm-<jobid>.out` preserved alongside the ricc2 output;
  the remaining 26 report
  `slurm log not preserved` and are therefore
  **runtime-banner-supported rather than scheduler-log-confirmed**
  (consistent with audit Phase 5 Step 6).

## Caveats explicitly preserved

- **POZ1 (Hz_POZ1_NPh21_CF31)** is in the historical batch and has
  no preserved sibling control file. Its basis assignment is
  banner-derived only (audit Phase 5 Issue A); the manifest records
  `historical batch, no preserved sibling control` in the notes
  column for both sing and trip rows.
- **ADC(2) ybsi pending** (raw outputs not locally verified):
  15 R1-deploy ADC(2) raw outputs were computed on the ybsi cluster
  and were not rsynced into the local audit snapshot at the time of
  this manifest. They are out of scope for the SCS-CC2 manifest
  above and are listed here for completeness:
  - 7 in the SCS-CC2 n=13 cohort that need their *ADC(2)*
    counterpart re-archived (the SCS-CC2 side is locally verified):
    Hz_NH23, Hz_NEt22_CF31, Hz_NH22_SO2Ph1,
    Hz_DMAC1_NPh21_SO2Ph1, Hz_Cz1_NPh21_CF31,
    Hz_NEt21_NPh22, Hz_NPh22_CN1.
  - 8 R1-deploy ADC(2) entries outside the n=13 cohort
    (Hz_DMAC1_NPh21_SO2Ph1 is in both lists; the union has 15
    pending raw outputs; see audit Phase 5 Step 5).
  The manifest TSV does NOT inject placeholder rows for ybsi-pending
  ADC(2) files; their absence is documented here in the MD companion
  instead so the TSV remains an accurate sha256 catalogue of what
  exists locally.

## Files explicitly NOT in this manifest

- LaTeX build artefacts (`*.out`, `*.log` produced by `pdflatex`).
- Audit workspace copies under `audit/_tmp_*/` or `audit/_intermediate*/`.
- Scheduler script templates at
  `scripts/scscc2_extension/templates/run_scscc2_svp*.slurm`
  (these are the wrapper templates, not job-instance logs).

## TSV source

See `audit/revision_patchC_raw_provenance_manifest.tsv`.
