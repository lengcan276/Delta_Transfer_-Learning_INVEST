# Patch D Step 9 — Cover letter check

## Verdict: **PASS — cover letter consistent with current paper-facing wording**

## Grep result

Single hit at `reviews/cover_letter.md:21`:

```
Hierarchical validation with concentrated higher-level cross-checks.
ADC(2)/def2-SVP serves as the primary post-Hartree–Fock label across
all 35 molecules, and SCS-CC2/def2-SVP is applied to all 13
ADC(2)-screened INVEST candidates (the pre-registered Table 1
shortlist), where it confirms sign agreement in all 13 cases
(0 within-screen disagreement; rule-of-three one-sided 95% upper bound
on disagreement rate ≈ 0.23) and promotes one ADC(2)-borderline
heptazine to negative-gap. The absolute method differences span
100–174 meV; the cross-check therefore supports scaffold-level
selection and per-molecule sign confirmation rather than fine
quantitative ranking among the most negative heptazines, which is
the resolution we explicitly target.
```

## Verification checklist

| check | status |
|---|---|
| Stale `n=4` / "four lead" wording remaining? | **NO** — text says "all 13 ADC(2)-screened INVEST candidates" |
| Clopper-Pearson overclaim remaining? | **NO** — no `Clopper` or `Pearson` substring in cover letter |
| Correct n=13 screened-cohort framing? | **YES** — "0 within-screen disagreement" + rule-of-three upper bound ≈ 0.23 |
| INVEST-n13 URL? | the cover letter does not include the canonical URL; the manuscript Data Availability section does. Cover letters typically do not reference the GitHub URL, so this is acceptable. |
| No internal audit terms? | **YES** — no `Phase 4` / `Phase 5` / `audit Phase` / `FedSchNet` / `1e-13` / `machine epsilon` in the file |

## Conclusion

The cover letter wording at line 21 was updated in Patch A (n=4 →
n=13 + rule-of-three) and continues to reflect the current
manuscript-level paper-facing statistical interpretation. No
correction needed in Patch D. Proceed to Step 10.
