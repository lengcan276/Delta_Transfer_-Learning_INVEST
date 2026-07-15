# Phase 3.5 Step 2 — SCS-CC2 scope metrics (processed-table only)

Source CSV: `results/scscc2_extension_n13/cross_check_n13.csv`
Source JSON (cross-check): `results/scscc2_extension_n13/stats_n13.json`

All values below are **PROCESSED_TABLE_LEVEL** — they come from
the project's own SCS-CC2 cross-check CSV, not from independent
re-parsing of raw ricc2 outputs. Raw-output provenance is
Phase 4's responsibility.

## Cohort summary

| Metric | Value |
|---|---|
| N total checked by SCS-CC2 | **13** |
| N sign agreement | **13** |
| N sign disagreement | **0** |
| All SCS-CC2 ΔE_ST more negative than ADC(2)? | **True** |
| Cross-method shift, abs min | 10.09 meV |
| Cross-method shift, abs max | 193.74 meV |
| Cross-method shift, abs mean | 109.84 meV |
| Rule-of-three upper bound (3/N) | 0.2308 = ~23% |

## Cross-check against stats_n13.json

- `stats_n13.json.n_total` = 13  →  audit re-computes 13  →  MATCH
- `stats_n13.json.n_sign_retain` = 13  →  audit re-computes 13  →  MATCH
- `stats_n13.json.abs_ddEST_meV_summary.min` = 10.09  →  audit re-computes 10.09
- `stats_n13.json.abs_ddEST_meV_summary.max` = 193.74  →  audit re-computes 193.74
- `stats_n13.json.abs_ddEST_meV_summary.mean` = 109.84  →  audit re-computes 109.84

## Two molecules called out by Phase 3.5 protocol

### Hz_POZ1_NPh21_CF31 (borderline-promoted)
- ADC(2) ΔE_ST = **-9.71** meV
- SCS-CC2 ΔE_ST = **-165.57** meV
- |Δ| (cross-method shift) = 155.86 meV
- ADC(2)/def2-SVP value lies inside the ±30 meV borderline window;
  classification flips from ADC(2) borderline to SCS-CC2 negative-gap.
  Should be flagged low-evidence pending basis-set or
  method-family triangulation.

### Hz_NPh21_Cz2 (narrowest cross-method margin)
- ADC(2) ΔE_ST = **-119.0** meV
- SCS-CC2 ΔE_ST = **-129.09** meV
- |Δ| (cross-method shift) = **10.09** meV
- This is the smallest cross-method margin in the n=13 cohort.
  Should be flagged as the most likely sign-flip candidate
  under further theoretical refinement (different basis, different
  method family).

## Provenance disclaimer

All numbers above were computed by re-applying simple arithmetic
to `results/scscc2_extension_n13/cross_check_n13.csv`. This CSV
was produced by `scripts/scscc2_extension/build_cross_check_n13.py`
which in turn parses `ricc2_scscc2_*.out` files via
`scripts/scscc2_extension/parsers/parse_scscc2_dest.py`. The
authenticity of the underlying ricc2 outputs — i.e. whether they
are real Turbomole calculations rather than fabricated text —
is NOT verified at the processed-table level. Phase 4 covers that.