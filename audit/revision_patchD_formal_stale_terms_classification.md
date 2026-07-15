# Patch D Step 3 — Formal stale wording classification

## Verdict: **PASS — no actionable STALE_* hit in formal files**

Total raw grep hits: 5. All five fall into OK categories. No fix
required.

## Per-hit classification

| file:line | content (excerpt) | classification |
|---|---|---|
| `DATA_AVAILABILITY.md:84` | "not yet in the release tarball, please open an issue at" | **FALSE_POSITIVE** — regex `Issue A` matches the substring `issue a` in "issue at" (case-insensitive). Not an internal-audit reference. |
| `README.md:66` | "reference state. Please open an issue at" | **FALSE_POSITIVE** — same regex artefact. |
| `figures/caption_data/Fig4_crosscheck.json:78` | `"scope_separation_note": "candidate_scscc2_crosschecks (n=4) is a targeted SCS-CC2 verification ..."` | **OK_HISTORICAL_AUDIT_REFERENCE** — describes the legacy `candidate_scscc2_crosschecks` block whose name and intended scope are 4 molecules. The text explicitly distinguishes the legacy n=4 block from the new n=13 cohort. The `n=4` label here correctly names the legacy block content; replacing it would mis-describe what that block contains. |
| `results/canonical_metrics.json:632` | same `scope_separation_note` value | **OK_HISTORICAL_AUDIT_REFERENCE** — mirror of the figure-caption metadata; internal documentation of the legacy n=4 block scope. |
| `results/canonical_metrics.json:710` | `"ci_method": "Not reported as a Clopper-Pearson population confidence interval because the 13 molecules were ADC(2)-preselected."` | **OK_NEGATION_FRAMING** — the explicit disclaimer form. Carries `Clopper-Pearson` and `population confidence interval` only inside the negation "Not reported as ... because the 13 molecules were ADC(2)-preselected." |

## Classification counts

| classification | count |
|---|---|
| OK_INTERNAL_METADATA_ONLY | 0 |
| OK_HISTORICAL_AUDIT_REFERENCE | 2 |
| OK_NEGATION_FRAMING | 1 |
| FALSE_POSITIVE | 2 |
| STALE_FORMAL_TEXT | **0** |
| STALE_STATISTICAL_SCOPE | **0** |
| STALE_REPO_REFERENCE | **0** |
| STALE_N4_REFERENCE | **0** |
| STALE_BIT_IDENTICAL_WORDING | **0** |
| NEEDS_MANUAL_REVIEW | 0 |

## Conclusion

No actionable STALE_* hit in any of the scanned formal files
(`paper/main.tex`, `paper_overleaf/main.tex`,
`figures/caption_data/*.json`, `results/Table1_invest_candidates.tex`,
`paper_overleaf/Table1_invest_candidates.tex`, `reviews/cover_letter.md`,
`README.md`, `DATA_AVAILABILITY.md`, `results/canonical_metrics.json`).

No manuscript or documentation fix needed in Step 3. Proceed to Step 4.
