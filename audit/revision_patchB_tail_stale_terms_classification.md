# Patch B-tail Step 6 — Stale wording classification

## Verdict: **PASS — no stale paper-facing precision or internal-audit terminology**

## Scope

Grep pattern:
```
audit Phase|Phase 4|Phase 5|Step 5\.5|Issue A|audit/phase|
internal audit|1e-13|10\^|machine epsilon
```

Files scanned:
- `paper/main.tex`
- `paper_overleaf/main.tex`
- `results/canonical_metrics.json`
- `scripts/99_emit_canonical.py`
- `scripts/audit_numbers.py`

Total raw hits: 8 (stored in
`audit/revision_patchB_tail_stale_terms_grep.txt`).

## Per-hit classification

| file:line | hit text | classification | reason |
|---|---|---|---|
| `paper/main.tex:74` | `$\times\!10^{-5}$` and `$<\!10^{-3}$` (xtb gradient norms) | NEEDS_MANUAL_REVIEW → resolved as **false positive** | physical convergence gradient (Eh/a₀), pre-existing manuscript content, NOT audit-precision number |
| `paper/main.tex:150` | same | NEEDS_MANUAL_REVIEW → **false positive** | same |
| `paper/main.tex:177` | same | NEEDS_MANUAL_REVIEW → **false positive** | same |
| `paper_overleaf/main.tex:74` | same | NEEDS_MANUAL_REVIEW → **false positive** | mirror |
| `paper_overleaf/main.tex:150` | same | NEEDS_MANUAL_REVIEW → **false positive** | mirror |
| `paper_overleaf/main.tex:177` | same | NEEDS_MANUAL_REVIEW → **false positive** | mirror |
| `results/canonical_metrics.json:713` | `"audit_report_reference": "audit/phase4_qc.md"` | **OK_INTERNAL_AUDIT_REFERENCE_METADATA** | internal metadata pointer added by Patch B for downstream provenance; does NOT propagate to paper-facing fields (`paper_cited_*`, `ci_method`, `raw_provenance_status`) which are independently grep-checked |
| `scripts/99_emit_canonical.py:988` | same string literal | **OK_INTERNAL_AUDIT_REFERENCE_METADATA** | source of the metadata field above |

## Counts by allowed classification

| classification | count |
|---|---|
| OK_INTERNAL_AUDIT_REFERENCE_METADATA | 2 |
| STALE_INTERNAL_AUDIT_TERM_IN_MANUSCRIPT | **0** |
| STALE_AUDIT_PRECISION_TERM | **0** |
| NEEDS_MANUAL_REVIEW | 6 (all resolved as false positives — broad `10\^` regex matching physical xtb gradient-norm exponents) |

## Why the 6 NEEDS_MANUAL_REVIEW are false positives

The regex `10\^` matches `10^` anywhere in the file, including LaTeX
exponent notation `10^{-N}`. The 6 hits are all of the form:

- `$6.6\!\times\!10^{-5}$ to $7.6\!\times\!10^{-4}$ Eh\,a$_0^{-1}$`
  (xtb GFN2 gnorm convergence range, historical batch)
- `$5.6\!\times\!10^{-5}$ to $1.5\!\times\!10^{-4}$ Eh\,a$_0^{-1}$`
  (xtb GFN2 gnorm convergence range, delta-DFT batch)
- `$<\!10^{-3}$ Eh\,a$_0^{-1}$` (the convergence baseline criterion)

These are physical geometry-optimization gradient norms expressed in
Eh/a₀ atomic units. They are pre-existing manuscript content from
before Patch B (and before Patch A) describing the experimental
convergence criteria. They are NOT audit-precision numbers like
`10^{-13} eV` (which was the Patch A hygiene target). The Patch A
hygiene fix specifically targeted machine-epsilon-class numbers used
to describe parser-vs-CSV agreement; the xtb gradient norms are
scientific convergence parameters and remain.

## Conclusion

The grep returns no STALE_INTERNAL_AUDIT_TERM_IN_MANUSCRIPT and no
STALE_AUDIT_PRECISION_TERM in formal manuscript text. The 2
`OK_INTERNAL_AUDIT_REFERENCE_METADATA` hits are internal-metadata
fields by design. The 6 NEEDS_MANUAL_REVIEW hits are regex false
positives on physical gradient-norm exponents.

No changes required. Patch B-tail does not introduce any new
audit-precision wording or internal-audit terminology.
