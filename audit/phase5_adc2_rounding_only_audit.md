# Phase 5 Step 5.5 — ADC(2) rounding-only precision audit

## Scope
8 of the 35 ADC(2) labels in `validated_candidates_master.csv` differ
from the parsed raw `ricc2_sing.out` / `ricc2_trip.out` value by
≤0.41 meV. Phase 4 flagged these as `VALUE_MISMATCH` only because the
audit's strict tolerance is 0.1 meV. The differences are 100%
attributable to processed-table rounding (claim stored at 3 decimal
places in eV → 1 meV precision; raw value has 5 decimal places →
~0.01 meV precision).

## Table

| mol_id | claimed (eV) | claimed (meV) | parsed raw (meV) | |Δ| (meV) | source_table | manuscript_locations | reported_precision | precision_status | recommended_action |
|---|---|---|---|---|---|---|---|---|---|
| Hz_POZ1_Cz2 | 0.068 | 68.00 | 67.69 | 0.31 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_NPh21_POZ2 | 0.083 | 83.00 | 83.37 | 0.37 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_NH21_POZ2 | 0.095 | 95.00 | 94.79 | 0.21 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_NEt21_POZ2 | 0.105 | 105.00 | 104.59 | 0.41 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_POZ3 | 0.109 | 109.00 | 108.64 | 0.36 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_NHPh1_POZ2 | 0.118 | 118.00 | 117.71 | 0.29 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| Hz_POZ2_SO2Ph1 | 0.119 | 119.00 | 118.80 | 0.20 | adc2_validation_backup | not cited in main.tex / Table 1 with numeric value | n/a | **NOT_CITED_DIRECTLY** | none |
| BCz3 | 0.197 | 197.00 | 196.84 | 0.16 | adc2_validation_backup | appears in calibration-anchor mention (TDDFT N=5) | classification-only (positive vs negative gap) | **PRECISION_OK** | none |

## Aggregate counts

| precision_status | count |
|---|---|
| PRECISION_OK | 1 (BCz3) |
| PRECISION_TOO_TIGHT | **0** |
| NOT_CITED_DIRECTLY | 7 |
| NEEDS_MANUAL_REVIEW | 0 |

## Interpretation

- **0 cases of `PRECISION_TOO_TIGHT`**: no manuscript wording quotes
  any of these 8 ADC(2) values at sub-meV precision. The largest
  diff is 0.41 meV (Hz_NEt21_POZ2), and that molecule does not appear
  in main.tex or Table 1 as a numeric quote.
- **7 NOT_CITED_DIRECTLY**: these 8 are all from the
  `adc2_validation_backup/` set (POZ2-family exploratory molecules
  that were not part of the n=13 cohort nor the Table 1 shortlist).
  The paper does not quote their ΔE_ST individually.
- **1 PRECISION_OK** (BCz3): BCz3 IS mentioned as part of the
  5-anchor TDDFT calibration set (per project notes), but only as a
  classification label (calibration-anchor), not as a high-precision
  ΔE_ST value.

## Conclusion

**The 8 rounding-only cases do NOT require any manuscript wording
change.** They are an internal data-pipeline precision artifact:
`validated_candidates_master.csv` truncates ADC(2) ΔE_ST to 3
decimals in eV (effectively 1 meV) for human readability, while the
raw ricc2.out reports 5 decimals (~0.01 meV). This truncation is
audit-traceable and does not propagate to any manuscript-cited
number.

## Optional generator-refactor recommendation

For future audit cleanliness, when regenerating
`validated_candidates_master.csv` from raw outputs, write at least
4 decimal places in eV (0.1 meV resolution) so the audit's strict
tolerance check does not trigger on rounding artifacts. This is a
build-pipeline polish only, not a manuscript correction.
