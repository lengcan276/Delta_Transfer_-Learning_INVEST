# Phase 5 Step 3 — Hz_NPh21_Cz2 narrowest-margin / batch resolution

## Verdict: **B_RESOLVED_NEW_BATCH** (SCS-CC2 side is full-control-verified; ADC(2) side is banner-only)

## Evidence summary

| Field | Value |
|---|---|
| **Batch assignment (SCS-CC2)** | **9-new extension batch** (Phase 2.4) — raw path `/home/nudt_cleng/2026/results/scscc2_extension_n13/Hz_NPh21_Cz2/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out` |
| Batch assignment (ADC(2)) | adc2_batch2_raw (historical batch2 ADC(2) — pre-dates the n=13 extension campaign) |
| **Preserved control file (SCS-CC2)** | **Yes** |
| Preserved control file (ADC(2)) | **No** (typical of historical batch2 — only ricc2.out preserved) |
| $basis values (SCS-CC2 control) | `['def2-SVP']` ✓ |
| $jbas values (SCS-CC2 control) | `['def2-SVP']` ✓ |
| $cbas values (SCS-CC2 control) | `['def2-SVP']` ✓ |
| ADC(2) raw status | **OK** — parsed −119.45 meV, claim −119.45 meV (diff −5.6×10⁻¹⁴ meV) |
| SCS-CC2 raw status | **OK** — parsed −129.09 meV, claim −129.09 meV (diff −1.4×10⁻¹³ meV) |
| Method banner (SCS-CC2) | `CC2` + `Spin-Component Scaling will be applied` + `C_os = 1.200  C_ss = 0.333` ✓ |
| Scheduler tier | **INFERRED** for both — `ricc2 (nodeN)` banner present, no local slurm log |
| Narrowest-margin claim | **10.09 meV** (per cross_check_n13.csv) |
| Actual raw-vs-raw margin | **9.64 meV** (= |−129.09 − (−119.45)|) |
| Rounding note | cross_check_n13.csv populated ADC(2) as `-0.119` (3-dp truncation); validated_master has `-0.11945` (5-dp). The "10 meV" margin claim is approximate-rounded; true raw margin is **9.6 meV** |

## Why B_RESOLVED_NEW_BATCH (not banner-only)

The SCS-CC2 calculation — the half of the cross-method pair that
defines this molecule as the n=13 cohort entry — is from a Phase-2
extension run whose `control` file is preserved on local disk. All
three basis groups (`$basis`, `$jbas`, `$cbas`) are independently
verified per element as `def2-SVP`. The ADC(2) raw is also verified
(value-match), even though that side's control was not preserved
(typical of historical batch2 — ADC(2) banner separately confirms
def2-SVP, see analogous Step 2 finding for Hz_POZ1_NPh21_CF31).

## Narrowest margin: raw-supported

Both halves of the cross-method comparison are raw-output verified:
- ADC(2) = −119.45 meV (raw, exact)
- SCS-CC2 = −129.09 meV (raw, exact)
- |ΔΔ_ST| = **9.64 meV** (raw-vs-raw)

The processed `cross_check_n13.csv` reports this margin as **10.09
meV** because it uses the rounded ADC(2) value `-0.119` (from the
processed `master_molecule_table.csv` truncation). The discrepancy is
0.45 meV — below any chemically meaningful threshold but worth a
footnote.

**Conclusion**: Hz_NPh21_Cz2 IS the narrowest-margin cohort member
both at processed-table level (10.09 meV) and at raw-output level
(9.64 meV). The narrowest-margin warning is raw-supported.

## Recommended manuscript wording

Stays as Phase 3.5 recommendation, but the precise number warrants a
small change:

> "Hz_NPh21_Cz2 has the narrowest ADC(2)/SCS-CC2 cross-method margin
> in the n=13 cohort (ADC(2)/def2-SVP ΔE_ST = −119.5 meV, SCS-CC2/def2-SVP
> ΔE_ST = −129.1 meV, |ΔΔ| ≈ 10 meV). The SCS-CC2 calculation has a
> preserved control file with all three basis groups
> ($basis / $jbas / $cbas) confirmed as def2-SVP from the local
> audit snapshot. This molecule should be treated as the most
> sign-sensitive member of the screened cohort under further
> theoretical refinement (different basis, different method family)."

**Optionally**: footnote that the cross_check_n13.csv table reports
|ΔΔ| as 10.09 meV using the processed (3-dp) ADC(2) value, whereas
raw-vs-raw gives 9.64 meV. The qualitative claim ("narrowest, near
10 meV, sign-sensitive") is unchanged.

## What this audit does NOT establish

- That `$jbas` was def2-SVP for the ADC(2) calc (no preserved control
  + no ridft output preserved on this side). The ricc2 banner records
  $basis and $cbas-equivalent but not $jbas. Same caveat as POZ1's
  ADC(2) half.
- That Hz_NPh21_Cz2's cohort margin is invariant to further method
  changes. The 10 meV margin is precisely why the audit flags this
  molecule as a sign-flip risk.
