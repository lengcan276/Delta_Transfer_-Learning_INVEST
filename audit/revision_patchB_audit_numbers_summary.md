# Patch B — audit_numbers.py completeness check

## Note on scope

This is a **completeness check**, not the primary quality gate for
Patch B. The primary quality gate for Patch B is the conjunction of:
single-writer validation + numeric drift check + stale metadata grep.
`audit_numbers.py` is run here as an end-to-end sanity check that
the manuscript still resolves to canonical sources after the
generator refactor.

## Result

```
$ python3 scripts/audit_numbers.py
exit code: 0

[OK] paper/audit_reports/consistency_audit.md
     numbers extracted     = 515
     non-trivial numbers   = 259
     unresolved            = 2
     Major checks tripped  = 0 / 7
```

| metric | value |
|---|---|
| exitcode | **0** |
| non-trivial numbers extracted | 259 |
| traceable to canonical source | 257 (99%) |
| unresolved | **2** |
| Major checks tripped (M1..M7) | **0 / 7** |

## Major checks status

All seven major-issue mitigation checks pass cleanly (0 unmitigated
trigger hits each):

- M1_7_15_vs_6_14_unexplained
- M2_15_vs_14_mixed_scope
- M3_33_35_14_mixed_scope
- M4_scscc2_overgeneralised
- M5_52_meV_threshold_no_caveat
- M6_fisher_random_significance
- (one additional check; see `paper/audit_reports/consistency_audit.md`)

## Unresolved numbers (2)

Both unresolved numbers originate from the Patch A Data Availability
section, not from Patch B:

| number | manuscript context | classification |
|---|---|---|
| `26.0` | "n=13 molecules, singlet + triplet = 26 files" | descriptive integer (2 × 13); not a scientific number; safe to leave unresolved or add as a derived metadata field in a future polish pass |
| `0.41` | "8 verified to within $0.41$~meV with the residual attributed entirely to processed-table rounding" | upper-bound ADC(2) rounding deviation; documented in `audit/phase5_adc2_rounding_only_audit.md` but not surfaced into `canonical_metrics.json`; safe to leave unresolved or add as a derived metadata field in a future polish pass |

**Neither unresolved number is a Patch B regression.** Pre-Patch-A
audit_numbers.py showed no occurrences of these strings because the
Data Availability section did not yet exist; Patch A added the
section and these two informational numbers entered the manuscript.
They are not Major-check triggers and do not block submission.

## Conclusion

audit_numbers.py reports clean Major-check status (0/7) after the
Patch B refactor. The two unresolved numbers are non-fatal Patch A
informational additions and are not regressions introduced by
Patch B's generator refactor.
