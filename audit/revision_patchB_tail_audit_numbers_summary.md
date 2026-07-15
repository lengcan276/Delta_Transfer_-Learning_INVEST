# Patch B-tail Step 4 — audit_numbers.py summary

## Result

```
$ python3 scripts/audit_numbers.py
exit code: 0

[OK] paper/audit_reports/consistency_audit.md
     numbers extracted     = 513
     non-trivial numbers   = 257
     unresolved            = 0
     Major checks tripped  = 0 / 7
```

| metric | value |
|---|---|
| exit code | **0** |
| non-trivial numbers extracted | 257 (was 259) |
| traceable to canonical source | 257 (100%) |
| **unresolved** | **0** (was 2) |
| Major checks tripped | **0 / 7** |
| 26.0 still flagged | NO — removed from manuscript |
| 0.41 still flagged | NO — replaced with "sub-meV rounding-level" |

## Numbers no longer extracted

The two unresolved values from Patch B were both PROVENANCE_EXPLANATORY
numbers in the Patch A Data Availability section. After the Treatment A
rewrite:

- `"singlet + triplet = 26 files"` → `"singlet and triplet outputs"`
  (drops the derived integer 26; n=13 elsewhere in the sentence is
  canonical)
- `"within $0.41$~meV"` → `"within sub-meV rounding-level differences"`
  (drops the audit-derived precision bound; the substantive
  "rounding-level, not method-level" content is preserved in text)

Both edits were applied in `paper/main.tex` and `paper_overleaf/main.tex`
in parallel.

## Conclusion

`audit_numbers.py` reports **unresolved = 0** and **0/7 Major checks
tripped**. The Patch B-tail target state is met.
