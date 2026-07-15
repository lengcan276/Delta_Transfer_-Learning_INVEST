# Phase 5 Step 5 — ADC(2) missing-raw caveat

## Scope
15 of the 35 ADC(2) labels in `validated_candidates_master.csv` have
no local raw `ricc2_sing.out` / `ricc2_trip.out` in the parent
`/home/nudt_cleng/2026/results/` tree. Per the audit's no-network
constraint, they cannot be retrieved from the ybsi cluster, where they
nominally live (see Phase 0/1 reports referencing
`/public/home/ybsi/nudt_cleng/2026/round1_adc2/`).

## List of 15 missing ADC(2) raw outputs (all `batch=r1_deploy`)

| # | mol_id | claimed_method | in n=13 cohort? |
|---|---|---|---|
| 1 | Hz_NH23 | RI-ADC(2)/def2-SVP | **YES** (also has SCS-CC2 verified) |
| 2 | Hz_NEt22_CF31 | RI-ADC(2)/def2-SVP | **YES** (also has SCS-CC2 verified) |
| 3 | Hz_NH22_SO2Ph1 | RI-ADC(2)/def2-SVP | **YES** |
| 4 | Hz_DMAC1_NPh21_SO2Ph1 | RI-ADC(2)/def2-SVP | **YES** |
| 5 | Hz_Cz1_NPh21_CF31 | RI-ADC(2)/def2-SVP | **YES** |
| 6 | Hz_NEt21_NPh22 | RI-ADC(2)/def2-SVP | **YES** |
| 7 | Hz_NPh22_CN1 | RI-ADC(2)/def2-SVP | **YES** |
| 8 | Hz_NEt22_CN1 | RI-ADC(2)/def2-SVP | no (positive-gap cohort) |
| 9 | Hz_NMe22_CN1 | RI-ADC(2)/def2-SVP | no |
| 10 | Hz_POZ1_NPh21_SO2Ph1 | RI-ADC(2)/def2-SVP | no |
| 11 | 5AP_NPh2_Me | RI-ADC(2)/def2-SVP | no (positive-gap 5AP elimination) |
| 12 | 5AP_NEt2_Ph | RI-ADC(2)/def2-SVP | no |
| 13 | 5AP_NPh22 | RI-ADC(2)/def2-SVP | no |
| 14 | 5AP_NPh2_OMe | RI-ADC(2)/def2-SVP | no |
| 15 | 5AP_NMe2_NPh2 | RI-ADC(2)/def2-SVP | no |

**7 of 15 are in the n=13 SCS-CC2 cohort.** Their ADC(2) values are
documented in cross_check_n13.csv but their ADC(2) ricc2 raw outputs
are not locally verifiable. The SCS-CC2 raw outputs for these 7 ARE
locally verified (Phase 4, all OK).

## Which manuscript claims depend on these 15

### 1. Model training
- **Indirect dependency.** The delta transfer model trains on these
  ADC(2) labels (post-round target set, n=33). The processed
  `model_input_table.csv` contains the labels; the audit verified
  that the processed labels are internally consistent with master
  tables (Phase 2). Local raw verification cannot be done.

### 2. Validated cohort classification
- **Direct dependency.** Each molecule's `negative_gap` / `positive_gap`
  / `borderline` classification in `validated_candidates_master.csv`
  uses the (rounded) ADC(2) value. For the 7 cohort members, the
  classification IS the basis for inclusion in n=13.

### 3. SCS-CC2 n=13 cross-check
- **Partial dependency.** The 13/13 sign-agreement statistic is
  computed by comparing the SIGN of ADC(2) to the SIGN of SCS-CC2.
  Local raw verification of SCS-CC2 is complete. Local raw verification
  of the corresponding ADC(2) is not done for 7 of the 13 cohort
  members, but their signs as recorded in processed CSVs are consistent
  with the cross_check_n13.csv table.

### 4. Table 1 shortlist
- **Direct dependency.** Table 1 lists the 14 INVEST-relevant entries
  (13 negative + 1 borderline). 7 of these 13 have ADC(2) raw on ybsi
  only.

### 5. Fisher contingency 13/27 vs 0/8
- **Direct dependency.** The contingency table counts Hz negative-gap
  vs Hz total and non-Hz negative-gap vs non-Hz total in the
  35-validated cohort. ADC(2) values determine "negative-gap".
  Although raw is missing for 15/35, the processed CSV is internally
  consistent (Phase 2 audit confirmed regeneration of canonical from
  these CSVs).

## Is processed-table consistency enough for current submission?

For an internal-pipeline audit, yes: processed labels are reproducible
from upstream master tables (Phase 2). For external raw-output
provenance — what a referee asking "show me the calculation outputs"
would want — no: 15/35 ADC(2) raw outputs are not locally available.

## Should the raw files be retrieved before final archive?

Strongly recommended. Until they are pulled back to a local archive,
the release_n13 artifact cannot stand alone as a fully reproducible
deposit for ADC(2) claims. The SCS-CC2 half stands alone (13/13 raw
verified locally). Recommended pre-publication action: rsync from ybsi
`/public/home/ybsi/nudt_cleng/2026/round1_adc2/jobs/` and bundle into
the release.

## Recommended Data Availability wording

> "Of the 35 ADC(2)/def2-SVP raw output files referenced in
> `validated_candidates_master.csv`, 20 are bundled with the release
> archive and are independently raw-parser verified (12 with
> machine-precision agreement to the processed values; 8 within a
> 0.5 meV rounding-precision window — see
> `audit/phase5_adc2_rounding_only_audit.md`). The remaining 15
> ADC(2) raw outputs were computed on the ybsi compute cluster under
> `/public/home/ybsi/nudt_cleng/2026/round1_adc2/jobs/` and were not
> rsynced back into the local audit snapshot at the time of release;
> their processed labels in the master CSVs are internally consistent
> with downstream tables (Phase 2 reproducibility audit), but full
> raw-output provenance for these 15 ADC(2) entries requires
> retrieval or archival of the corresponding ybsi calculation outputs.
> Of these 15, 7 are members of the n=13 SCS-CC2 cross-check cohort;
> the SCS-CC2 side for all 7 is locally raw-verified (machine
> precision)."

## Cross-link

ADC(2) provenance has **two separate limitations**: 15 missing local
raw outputs (this document) and 8 rounding-only cases whose
manuscript precision was separately audited in
`audit/phase5_adc2_rounding_only_audit.md`.
