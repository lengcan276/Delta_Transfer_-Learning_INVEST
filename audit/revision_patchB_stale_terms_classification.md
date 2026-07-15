# Patch B — Stale-terms classification

## Verdict: **PASS — no stale Clopper-Pearson paper-facing primary citation**

## Scope

Audit all formal-text and canonical-metadata locations for the
Clopper-Pearson 95% binomial CI being cited as the **paper-facing
primary** statistical interpretation of the n=13 SCS-CC2 sign-
retention result. Such citations would be stale because the
paper-facing primary interpretation has been moved to the
screened-cohort rule-of-three one-sided 95% upper bound on
within-screen sign-disagreement rate.

## canonical_metrics.json scs_cc2_extended_n13 metadata

```
ci_method: "rule of three (one-sided 95% upper bound on within-screen
            sign-disagreement rate; the 13 molecules are an
            ADC(2)-pre-screened cohort, not an i.i.d. random sample)"
  starts with 'rule of three': True

clopper_pearson_note: "transparency-only; not the paper-facing
                       interpretation for this ADC(2)-pre-screened cohort"
  has 'transparency-only': True

STALE_METADATA detected in canonical_metrics.json::ci_method: False
```

The `clopper_pearson_95_CI` and `clopper_pearson_90_CI` arrays are
retained for transparency but explicitly annotated as not
paper-facing, satisfying the design constraint of "emit both for
traceability".

## results/stats_n13.json

`ci_method` field updated by the refactored
`build_cross_check_n13.py` to the rule-of-three text. The Clopper-
Pearson arrays remain present as transparency-only fields
(annotated with `clopper_pearson_note`). No stale paper-facing
primary citation remains.

## Manuscript files

`grep -RniE "Clopper"` over `paper/main.tex`, `paper_overleaf/main.tex`,
`figures/caption_data/`, `results/Table1_invest_candidates.tex`,
`paper_overleaf/Table1_invest_candidates.tex`, `reviews/cover_letter.md`:

| location | classification |
|---|---|
| `paper/main.tex:150` | OK — `rather than a Clopper--Pearson lower bound on a population proportion` (contrast form; rule-of-three is the primary citation in the same sentence) |
| `paper/main.tex:166` (Fig 4 caption) | OK — `rather than a Clopper--Pearson lower bound` (same contrast form) |
| `paper/main.tex:177` (sec:limits caveat (a)) | OK — `rather than a Clopper--Pearson lower bound on a population proportion` (same contrast form) |
| `paper_overleaf/main.tex:150` | OK — mirror of `paper/main.tex:150` |
| `paper_overleaf/main.tex:166` | OK — mirror of Fig 4 caption |
| `paper_overleaf/main.tex:177` | OK — mirror of sec:limits caveat (a) |

All 6 mentions are in the **contrast form** "rule-of-three ... rather
than a Clopper--Pearson ...". Rule-of-three is cited as the primary
paper-facing interpretation; Clopper-Pearson is named only to be
explicitly contrasted. No standalone primary Clopper-Pearson citation
remains in any formal text file.

`figures/caption_data/`, `results/Table1_invest_candidates.tex`,
`paper_overleaf/Table1_invest_candidates.tex`, `reviews/cover_letter.md`:
**0 hits** for `Clopper`.

## Classification summary

| classification | count |
|---|---|
| STALE_CLOPPER_PEARSON_PAPER_FACING_PRIMARY | **0** |
| OK_CLOPPER_PEARSON_CONTRAST_FORM | 6 (manuscript) |
| OK_CLOPPER_PEARSON_TRANSPARENCY_FIELD | canonical_metrics.json + stats_n13.json |
| NEEDS_MANUAL_REVIEW | 0 |

## Conclusion

No stale paper-facing Clopper-Pearson primary citations remain in
either the manuscript or the canonical metadata. The transparency-
only Clopper-Pearson CI arrays are properly annotated and present
for downstream traceability.
