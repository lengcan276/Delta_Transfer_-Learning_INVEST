# Patch D Step 5 — Final canonical regeneration + audit_numbers

## Result

| step | exitcode | result |
|---|---|---|
| `python3 scripts/scscc2_extension/build_cross_check_n13.py` | **0** | regenerated `results/scscc2_extension_n13/{cross_check_n13.csv, stats_n13.json}` |
| `python3 scripts/99_emit_canonical.py` | **0** | regenerated `results/canonical_metrics.json` |
| `python3 scripts/audit_numbers.py` | **0** | regenerated `paper/audit_reports/consistency_audit.md` |

| audit metric | value |
|---|---|
| non-trivial numbers extracted | 257 |
| **unresolved** | **0** |
| **Major checks tripped** | **0 / 7** |

## Drift check

`diff` of `results/canonical_metrics.json` before vs after Step 5
regeneration: **no diff** (byte-identical). The Step 2 source-label
fix did not perturb any generated output beyond what was already
present in canonical_metrics.json (the label only fires inside a
dormant inconsistency record, which produces no output today).

## Conclusion

All Step 5 targets met:
- build_cross_check_n13 exit = 0 ✓
- emit_canonical exit = 0 ✓
- audit_numbers exit = 0 ✓
- unresolved = 0 ✓
- Major = 0 / 7 ✓
- No unexpected file changes from regeneration

Proceed to Step 6.
