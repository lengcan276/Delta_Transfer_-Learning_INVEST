# Patch B-tail Step 5 — Numeric safety check

## Status

**PASS_NUMERICALLY_INERT**

## Method

Compared `canonical_metrics.json["scs_cc2_extended_n13"]` between the
HEAD baseline and the post-Patch-B-tail state. Per-molecule numeric
fields and cohort-level invariants were checked exactly.

## Results

```
per-molecule drift count: 0
screened_cohort_n:        current=13
sign_disagreements:       current=0
n_total:                  HEAD=13  current=13
n_sign_retain:            HEAD=13  current=13
narrowest_margin_mol:     current=Hz_NPh21_Cz2
narrowest_margin_meV:     current=10.1
molecule count:           HEAD=13  current=13
```

| invariant | status |
|---|---|
| SCS-CC2 n=13 per-molecule values unchanged | PASS (0 drift across 13 × 8 cells) |
| ADC(2) ΔE_ST unchanged | PASS (per-molecule `ADC2_dEST_meV` unchanged) |
| SCS-CC2 ΔE_ST unchanged | PASS (per-molecule `SCSCC2_dEST_meV` unchanged) |
| shift_meV unchanged | PASS (per-molecule `abs_ddEST_meV` unchanged) |
| sign_agreement unchanged | PASS (per-molecule `sign_agree` unchanged) |
| screened_cohort_n = 13 | PASS |
| sign_disagreements = 0 | PASS |
| no molecule added or removed | PASS (count = 13 in both) |

## Files touched by Patch B-tail

- `paper/main.tex` — Data Availability section: "26 files" wording
  removed; "0.41 meV" replaced with "sub-meV rounding-level
  differences"
- `paper_overleaf/main.tex` — mirror of above

No source-of-truth file (raw QC, processed CSV, stats JSON,
canonical JSON, generator script) was touched.

## Conclusion

The Patch B-tail manuscript edits are **numerically inert** with
respect to all SCS-CC2 n=13 scientific values, all ADC(2) ΔE_ST
values, and all molecule classifications.
