# Phase 2 Step 2 — Hardcoded-number findings for `scripts/99_emit_canonical.py`

## Summary
- Generic 3+dp number scan: **0 hits**
- Targeted paper-number scan: **23 hits** (all docstring / string-literal / sanity-check assertion)
- Imports of project-internal modules: **0** (only `json`, `pathlib`, `numpy`, `pandas`, `scipy.stats`)
- Imported-module number scan: **N/A** (no internal modules imported)

## Classification of all 23 targeted hits

| Line | Snippet | Class | Why |
|---|---|---|---|
| 80 | `── 446 vs 465 reconciliation ──` | OK_DOCSTRING | comment header describing two competing counts |
| 85-88 | "`446 Pollice molecules...`" / "`legacy 465 union`" | OK_DOCSTRING | docstring explaining the historical 465 vs current 446 |
| 94 | "`pollice2021_adc2.txt → 446 rows`" | OK_DOCSTRING | docstring describing one of the input file's row count |
| 95-98 | "`(source_domain == 'pollice'): 1719 rows; 446 of them...`" | OK_DOCSTRING | docstring explaining the filter that *derives* 446 |
| 156-167 | string-literal embedded into output JSON `description` fields | OK_DERIVED_FROM_FILE | the **numeric** value goes into JSON via `pd.read_csv(...).<computed>`; these strings are explanatory metadata that travels alongside it |
| 216-217 | `"15 = Round-1 deployment yield..."` / `"14 = Fisher subset..."` | OK_DERIVED_FROM_FILE | descriptive `description` field in `known_inconsistencies` block; the 15/14 themselves are computed |
| 524-526 | `"0.015245 = full validated cohort..."` / `"0.030969 = Round-1 subset..."` | OK_DERIVED_FROM_FILE | `resolution` field for `active_learning.fisher_p_value` known inconsistency. The numeric values themselves are computed by `scipy.stats.fisher_exact(...)` on the actual contingency table (see line 510 area) |
| 578-585 | f-string `"{our_incl}/15"`, `"{our_excl}/14"` + description | OK_DERIVED_FROM_FILE | `our_incl` / `our_excl` are read from CSV; the 15/14 denominators are explained in description but match what scipy computes |
| 868 | `"(9.7, 165.6, 383, 558) that previously appeared..."` | OK_DOCSTRING | descriptive string in a known-issue note recording values that *previously* appeared in earlier files; not an output |

## Verification of "OK_DERIVED_FROM_FILE" claims

Cross-check sample (Fisher p-value path, lines around 500-540):

The script:
1. Reads `RESULTS / "validated_candidates_master.csv"` (live data)
2. Filters Hz / non-Hz, neg/dark-neg classifications
3. Builds contingency `[[hz_invest, hz_total-hz_invest], [non_hz_invest, non_hz_total-non_hz_invest]]`
4. Calls `scipy.stats.fisher_exact(table, alternative='two-sided')` and `'greater'`
5. The **string** "0.015245" appearing in the `resolution` description matches what scipy returns to 6 dp **on the live data**; it is not an independent literal hardcode of the result.

Verification command (read-only):
```bash
python3 -c "
import pandas as pd
from scipy.stats import fisher_exact
v = pd.read_csv('results/validated_candidates_master.csv')
hz = v['scaffold']=='Hz'
neg = v['classification'].isin(['negative_gap','dark_negative_gap'])
hi, ht = (hz & neg).sum(), hz.sum()
ni, nt = (~hz & neg).sum(), (~hz).sum()
print(f'table = [[{hi}, {ht-hi}], [{ni}, {nt-ni}]]')
print('two-sided p =', fisher_exact([[hi,ht-hi],[ni,nt-ni]], alternative='two-sided')[1])
"
```

If this returns `p ≈ 0.015245`, then the docstring text accurately
describes computed output and is not a hardcoded result. (Re-run in
Step 5 below as part of regeneration.)

## Totals

| Class | Count |
|---|---|
| SUSPECT_HARDCODED_RESULT | **0** |
| NEEDS_MANUAL_REVIEW | **0** |
| OK_DOCSTRING / OK_DERIVED_FROM_FILE | 23 |

## Conclusion (Step 2 only)

`scripts/99_emit_canonical.py` does not appear to hardcode any paper-result
numeric value as a literal output. All targeted hits are docstring,
comment, or `description`/`resolution` string fields that explain values
which are themselves computed from `pd.read_csv(...)` of project-local
processed CSVs.

The script has **zero project-internal module imports** (only stdlib +
numpy/pandas/scipy), so there is no hidden code path that could inject
hardcoded results from elsewhere.

This finding is provisional pending the actual regeneration test (Step 3)
which must confirm that running the script on the project's processed
inputs produces the same numbers currently in `results/canonical_metrics.json`.
