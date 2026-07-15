# Patch B review-fix — audit_numbers.py summary

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
| exit code | **0** |
| non-trivial numbers extracted | 259 |
| traceable to canonical source | 257 (99%) |
| unresolved | **2** (`26.0`, `0.41`) |
| Major checks tripped | **0 / 7** |

## Unresolved numbers (2)

| number | manuscript context | origin | classification |
|---|---|---|---|
| `26.0` | "n=13 molecules, singlet + triplet = 26 files" | Patch A Data Availability section | descriptive integer (2 × 13); not a scientific number |
| `0.41` | "8 verified to within $0.41$~meV with the residual attributed entirely to processed-table rounding" | Patch A Data Availability section | ADC(2) raw-output rounding bound documented in `audit/phase5_adc2_rounding_only_audit.md` |

**Both unresolved numbers originate from Patch A's Data Availability
paragraph, not from Patch B or this review-fix.** Pre-Patch-A
`audit_numbers.py` reported 0 unresolved because the Data Availability
section did not exist; Patch A added the section and these two
informational numbers entered the manuscript.

Neither is a Major-check trigger; neither is a regression caused by
Patch B or the review-fix.

## Major checks

All seven major-issue mitigation checks pass with 0 unmitigated
trigger hits each (M1 through M7; full breakdown in
`paper/audit_reports/consistency_audit.md`).

## Conclusion

audit_numbers.py reports clean Major-check status (0/7) after the
Patch B review-fix. The 2 unresolved numbers are non-fatal Patch A
informational additions; they are not regressions and they are not
in the Patch B scope.
