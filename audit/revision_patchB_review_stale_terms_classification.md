# Patch B review-fix — Stale terms classification

## Verdict: **PASS — no STALE_PAPER_FACING_METADATA in canonical writer outputs; one STALE entry confined to the legacy root snapshot (documented)**

## Scope

Grep pattern:
```
Clopper|Pearson|population confidence|randomly sampled|
method-independent validation|method-independent ranking|
FedSchNet|audit Phase|Phase 4|Phase 5|1e-13|10\^|machine epsilon
```

Files scanned:
- `results/canonical_metrics.json`
- `results/scscc2_extension_n13/stats_n13.json` (upstream canonical)
- `results/stats_n13.json` (root legacy snapshot)
- `scripts/scscc2_extension/build_cross_check_n13.py`
- `scripts/99_emit_canonical.py`

Total hits: 28 (raw grep stored in
`audit/revision_patchB_review_stale_terms_grep.txt`).

## Classification

| classification | count |
|---|---|
| OK_INTERNAL_DIAGNOSTIC_ONLY (transparency-CP fields & helper code) | 21 |
| OK_INTERNAL_AUDIT_REFERENCE_METADATA | 0 |
| OK_NEGATION_FRAMING (e.g. "NOT a Clopper-Pearson population CI") | 6 |
| STALE_PAPER_FACING_METADATA | **1** (confined to `results/stats_n13.json`, the tracked legacy root snapshot; documented in path diagnosis) |
| STALE_REPO_IDENTITY | 0 |
| STALE_INTERNAL_AUDIT_TERM | 0 |
| STALE_GENERATOR_TERM | 0 |
| NEEDS_MANUAL_REVIEW | 0 |

## Per-hit detail

### `results/stats_n13.json` (root legacy snapshot)

| line | content | classification |
|---|---|---|
| 5 | `clopper_pearson_95_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY (legacy transparency field) |
| 9 | `clopper_pearson_90_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 20 | `ci_method: "Clopper-Pearson exact two-sided 95%"` | **STALE_PAPER_FACING_METADATA** — but contained inside the legacy root snapshot that the user instructed not to auto-modify; documented in `audit/revision_patchB_review_path_diagnosis.md` as USER_DECISION_REQUIRED. The canonical upstream file `results/scscc2_extension_n13/stats_n13.json` carries the corrected rule-of-three framing. |

### `results/scscc2_extension_n13/stats_n13.json` (canonical upstream)

| line | content | classification |
|---|---|---|
| 7 | `clopper_pearson_95_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 11 | `clopper_pearson_90_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 15 | `clopper_pearson_note: "transparency-only; not the paper-facing ..."` | OK_INTERNAL_DIAGNOSTIC_ONLY (explicit transparency annotation) |

Also: `ci_method` here is the screened-cohort rule-of-three text, not Clopper-Pearson.

### `results/canonical_metrics.json` (assembled by 99_emit_canonical)

| line | content | classification |
|---|---|---|
| 709 | `paper_cited_scope: "ADC(2)-screened negative-or-dark-negative cohort; not a randomly sampled chemical population"` | OK_NEGATION_FRAMING (explicit "not a randomly sampled population") |
| 710 | `ci_method: "Not reported as a Clopper-Pearson population confidence interval because the 13 molecules were ADC(2)-preselected."` | OK_NEGATION_FRAMING (explicit "Not reported as...") |
| 723 | `clopper_pearson_95_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 727 | `clopper_pearson_90_CI: [...]` | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 731 | `clopper_pearson_note: "transparency-only; not the paper-facing ..."` | OK_INTERNAL_DIAGNOSTIC_ONLY (explicit annotation) |

### `scripts/scscc2_extension/build_cross_check_n13.py`

| line | content | classification |
|---|---|---|
| 21 | docstring: "A Clopper-Pearson exact CI is also emitted for transparency" | OK_INTERNAL_DIAGNOSTIC_ONLY (transparency annotation) |
| 125-126 | `def clopper_pearson(...)` helper definition | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 179-180 | calls to `clopper_pearson()` for transparency arrays | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 201-206 | emission of transparency CP fields | OK_INTERNAL_DIAGNOSTIC_ONLY |
| 233 | print: "(transparency-only) Clopper-Pearson 95% CI..." | OK_INTERNAL_DIAGNOSTIC_ONLY (explicit transparency-only marker) |

### `scripts/99_emit_canonical.py`

| line | content | classification |
|---|---|---|
| 977 | `paper_cited_scope ... "not a randomly sampled chemical population"` | OK_NEGATION_FRAMING |
| 980 | `ci_method ... "Not reported as a Clopper-Pearson population confidence interval ..."` | OK_NEGATION_FRAMING |
| 1005-1010 | transparency CP fields + note | OK_INTERNAL_DIAGNOSTIC_ONLY |

### Other patterns
- `FedSchNet` — 0 hits in any scanned file
- `audit Phase` / `Phase 4` / `Phase 5` — 0 hits in any scanned file (the
  `audit_report_reference` field stores `audit/phase4_qc.md` as a file
  path, which my grep would not match because it's `phase4` lowercase
  without the `Phase ` prefix)
- `1e-13` / `10^` / `machine epsilon` — 0 hits

## Conclusion

The Patch B canonical writer outputs (`results/canonical_metrics.json`,
`results/scscc2_extension_n13/stats_n13.json`) and the source files
(`scripts/scscc2_extension/build_cross_check_n13.py`,
`scripts/99_emit_canonical.py`) are clean of stale paper-facing
Clopper-Pearson primary citations.

The single STALE_PAPER_FACING_METADATA hit is confined to the
tracked legacy snapshot `results/stats_n13.json` which the user
instructed not to auto-modify (USER_DECISION_REQUIRED on whether to
sync or git-rm it; see `audit/revision_patchB_review_path_diagnosis.md`).
