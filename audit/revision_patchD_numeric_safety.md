# Patch D Step 6 — Numeric safety check

## Status: **PASS_NUMERICALLY_INERT**

## Method

Compared `results/canonical_metrics.json` HEAD baseline against the
current (post-Step-5 regeneration) state via
`scripts/audit/18_patchD_numeric_safety_check.py`.

## Result

```
PASS — 0 drift across 13 molecules × 8 per-molecule keys
       + cohort invariants + non-scs top blocks
```

| invariant | status |
|---|---|
| SCS-CC2 n=13 mol_id set unchanged (13 molecules) | PASS |
| per-molecule `ADC2_dEST_meV` unchanged | PASS (13/13) |
| per-molecule `SCSCC2_dEST_meV` unchanged | PASS (13/13) |
| per-molecule `SCSCC2_S1_eV`, `SCSCC2_T1_eV` unchanged | PASS (13/13 each) |
| per-molecule `abs_ddEST_meV` (shift) unchanged | PASS (13/13) |
| per-molecule `sign_agree` unchanged | PASS (13/13) |
| `n_total = 13` | PASS |
| `n_sign_retain = 13` | PASS |
| `sign_retain_rate = 1.0` | PASS |
| `screened_cohort_n = 13` | PASS |
| `sign_disagreements = 0` | PASS |
| `rule_of_three_upper_bound = 3/13 = 0.2308` | PASS |
| `clopper_pearson_95_CI` / `90_CI` unchanged | PASS |
| `abs_ddEST_meV_min/max/mean/median` unchanged | PASS |
| non-scs top-level canonical blocks unchanged | PASS |
| no molecule added or removed | PASS |

## Conclusion

The Patch D Step 2 source-label fix is numerically inert. All
scientific values in the canonical metrics file are byte-identical
to the HEAD baseline. Proceed to Step 7.
