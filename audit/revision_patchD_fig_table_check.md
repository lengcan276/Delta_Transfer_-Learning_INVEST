# Patch D Step 10 — Figure / table check

## Verdict: **PASS — figure caption metadata and Table 1 caption consistent with n=13 + rule-of-three framing**

## Per-hit review

### figures/caption_data/Fig4_crosscheck.json

| line | content | status |
|---|---|---|
| 24, 43 | `Hz_POZ1_NPh21_CF31` molecule reference (no overclaim) | OK — promotion mention is faithful to Patch A/B framing (high-confidence borderline-rescue; not "method-independent") |
| 63 | `Hz_POZ1_DMAC2` | OK — different molecule, not POZ1 cohort entry |
| 78 | `scope_separation_note`: explicit "candidate_scscc2_crosschecks (n=4) is a targeted SCS-CC2 verification on lead INVEST candidates ... NOT interchangeable with population-scale benchmark" | OK — internal documentation distinguishing the legacy n=4 block from the n=13 cohort; correct scope |
| 86 | "Absolute ADC(2)-vs-SCS-CC2 differences in the n=13 ADC(2)-screened cohort span 10.1–193.7 meV (mean 109.8 meV); signs agree in 13/13 molecules (0 within-screen disagreement; rule-of-three upper bound on disagreement rate ≈ 3/13 = 0.23)." | OK — n=13 scope correct; rule-of-three primary citation; numeric values match canonical_metrics.json (`abs_ddEST_meV_min` = 10.09, `_max` = 193.74, `_mean` = 109.84; rounding to 10.1 / 193.7 / 109.8 is display-only) |
| 90 | "On the n=13 ADC(2)-screened cohort, ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for 13/13 molecules (0 within-screen disagreement; rule-of-three one-sided 95% upper bound on disagreement rate ≈ 0.23) ..." | OK — consistent with Patch A wording |

### figures/caption_data/Fig0_workflow.json

| line | content | status |
|---|---|---|
| 33 | `Hz_POZ1_NPh21_CF31` reference inside the workflow caption metadata | OK — molecule mention only, no overclaim |

### results/Table1_invest_candidates.tex and paper_overleaf mirror

| line | content | status |
|---|---|---|
| 3 | "all 13 ADC(2)-screened candidates additionally have SCS-CC2 cross-checks (0 within-screen sign disagreement; rule-of-three upper bound on disagreement rate ≈ 0.23), and one of them (Hz_POZ1_NPh21_CF31) is promoted from the ADC(2) borderline window by the higher-level result" | OK — n=13 scope correct; rule-of-three primary; POZ1 promotion mention is faithful to the §sec:limits low-evidence caveat in the main text |

## Checklist

| check | status |
|---|---|
| Fig0 scope is n=13 where appropriate | YES (Fig0 caption itself was updated in Patch A line 44/47; here Fig0 metadata mentions Hz_POZ1 only as a molecule ID, no scope claim) |
| Fig4 cross-check says screened cohort, not population validation | YES — "n=13 ADC(2)-screened cohort" (line 86, 90) |
| Table 1 caption scope is correct (n=13, not n=4) | YES (lines 3 in both Table1 files) |
| POZ1 caveat not overclaimed | YES — Table 1 caption notes promotion only; §sec:limits in main.tex carries the low-evidence + banner-derived caveat |
| Cz2 narrowest margin caveat not contradicted | YES — Fig4 metadata reports cohort min = 10.1 meV (consistent with `narrowest_margin_meV` = 10.1 in canonical_metrics.json); Cz2 narrowest-margin caveat is in main.tex line 150 |
| No Clopper-Pearson population CI as paper-facing primary | YES — only the negation-form mentions in main.tex lines 150/166/177 (already classified OK by Step 3 / Patch B) |

## Counts

| status | count |
|---|---|
| OK_AS_CURRENT | 9 |
| STALE_WORDING_TO_FIX | 0 |
| NEEDS_USER_REVIEW | 0 |

## Conclusion

No stale wording in figure caption metadata or Table 1 captions.
All 9 hits are correct framing or scope-correct molecule references.
No edit required in Step 10. Proceed to Step 11.
