# Phase 3.5 — SCS-CC2 validation-scope audit

Audit phase: Phase 3.5
Repository HEAD: `3a72bc9`
Date: 2026-05-20

---

## Status

**PASS_WITH_REWRITE_RECOMMENDED**

The paper's main analytical text (Abstract, §3.5 main body, §3.5 cont,
§5 Limitations, §6 Conclusions) **already** uses the correct framing:
"0 sign disagreement within the ADC(2)-pre-screened cohort", rule-of-three
upper bound ≈ 0.23, systematic SCS-CC2 < ADC(2) shift framed as
ADC(2)/CC2 method-family consistency rather than method-independent
confirmation. The classifier flags 16 such occurrences as
`OK_SCREENED_COHORT_SIGN_EVIDENCE`.

However, the following non-text-body locations still contain **stale
n=4 language** or **legacy CI metadata** that contradicts the paper:

- 3 `OVERCLAIMS_POPULATION_CI` entries in JSON metadata
  (`results/canonical_metrics.json` lines 1155 / 1159, and
  `results/scscc2_extension_n13/stats_n13.json` line 20) — these still
  describe the result as "Clopper-Pearson exact two-sided 95%" CI;
- 14 `STALE_N4_WORDING` true-positives in (a) 3 figure captions inside
  `paper/main.tex` (and the mirrored `paper_overleaf/main.tex`), (b) 2
  caption-data JSONs in `figures/caption_data/`, (c) 2 Table 1 caption
  files, (d) 1 cover letter.

These are advisory rewrites only — no manuscript number is internally
contradicted by them (because the main analytical paragraphs are
correct), but a casual reader of the figure caption / cover letter
will see a different cohort size than the body text. Recommend
rewording per `audit/scscc2_recommended_language.md`.

---

## Processed-table metrics (PROCESSED_TABLE_LEVEL — Phase 4 not yet done)

Source: `results/scscc2_extension_n13/cross_check_n13.csv` +
`results/scscc2_extension_n13/stats_n13.json` (cross-check).
Verifier: `scripts/audit/08_check_scscc2_scope_metrics.py`.

| Metric | Value |
|---|---|
| N checked by SCS-CC2 | **13** |
| N sign disagreements | **0** |
| All SCS-CC2 ΔE_ST more negative than ADC(2)? | **True** |
| Cross-method shift, abs range | **10.09 — 193.74 meV** |
| Cross-method shift, abs mean | **109.84 meV** |
| Rule-of-three upper bound (3/N) | **0.2308** (~0.23) |
| Hz_POZ1_NPh21_CF31 ADC(2) ΔE_ST | **−9.71 meV** |
| Hz_POZ1_NPh21_CF31 SCS-CC2 ΔE_ST | **−165.57 meV** |
| Hz_NPh21_Cz2 ADC(2) ΔE_ST | **−119.0 meV** |
| Hz_NPh21_Cz2 SCS-CC2 ΔE_ST | **−129.09 meV** |
| Hz_NPh21_Cz2 |ΔΔE_ST| (narrowest margin) | **10.09 meV** |
| stats_n13.json cross-check | all values match |

All marked **PROCESSED_TABLE_LEVEL** — raw ricc2 / control / slurm
provenance for these numbers is Phase 4's job.

---

## Claim classification summary

Source: `audit/scscc2_claim_classification.tsv` (46 substantive claims
out of 185 grep hits).

| Classification | Count | True positives* |
|---|---|---|
| OK_SCREENED_COHORT_SIGN_EVIDENCE | 16 | 16 |
| OVERCLAIMS_POPULATION_CI | **3** | **3** |
| OVERCLAIMS_METHOD_VALIDATION | 0 | 0 |
| OVERCLAIMS_QUANTITATIVE_RANKING | 0 | 0 |
| BORDERLINE_NEEDS_LOW_EVIDENCE | 1 | 0 (false positive — CSV data row, not claim text) |
| SIGN_SENSITIVE_CASE_NOT_FLAGGED | 6 | ~2-3 (false positives on CSV data + per_molecule object headers; ~2 real annotations missing) |
| STALE_N4_WORDING | 20 | **~14** (6 are false positives: lines 74/161 of main.tex correctly describe two-batch composite or original pilot; canonical lines 634/681 correctly describe the legacy 4-molecule probe block; CSV rows are not claim text) |
| RAW_PENDING_PHASE4 | 0 | — (Phase 4) |

*True-positive count is human-judged after reviewing each flagged
location for context. See `audit/scscc2_recommended_language.md` §3 for
the false-positive list.

---

## Required wording changes (advisory — files NOT modified)

Full per-line replacement list is in `audit/scscc2_recommended_language.md`
§2. Summary:

### High priority — JSON metadata contradicts paper body
- `results/canonical_metrics.json` line 1155: rename `ci_method` from
  "Clopper-Pearson exact two-sided 95%" to a rule-of-three description
- `results/canonical_metrics.json` line 1159: keep `paper_cited_signrate`
  = "13/13" but add `paper_cited_scope` field clarifying screened-cohort
- `results/scscc2_extension_n13/stats_n13.json` line 20: same rename

### High priority — captions contradict body
- `paper/main.tex` line 46 (Fig 0 caption): "four selected molecules
  only" → "all 13 ADC(2)-screened negative-gap candidates"
- `paper/main.tex` line 155 (Fig 3 caption): "Four molecules additionally
  have SCS-CC2 cross-checks" → "All 13 ADC(2)-screened INVEST
  candidates additionally have SCS-CC2 cross-checks"
- `paper/main.tex` line 170 (Hz_NH23 paragraph): "on the four leads" →
  "across all 13 INVEST candidates"
- Mirrors in `paper_overleaf/main.tex` lines 46, 155, 170

### High priority — caption-data JSONs are stale
- `figures/caption_data/Fig0_workflow.json` lines 44, 47
- `figures/caption_data/Fig4_crosscheck.json` lines 85, 90
- `results/Table1_invest_candidates.tex` line 3
- `paper_overleaf/Table1_invest_candidates.tex` line 3
- `reviews/cover_letter.md` line 21 ("concentrated on four lead
  candidates" + "4/4 cases")

### Medium priority — annotations to ADD (not rewrites)
- `scs_cc2_extended_n13.per_molecule.Hz_NPh21_Cz2`: ADD
  `narrowest_margin_warning` field
- `scs_cc2_extended_n13.per_molecule.Hz_POZ1_NPh21_CF31`: ADD
  `borderline_low_evidence_warning` field

---

## Hard-constraint compliance (Phase 3.5)

| Constraint | Status |
|---|---|
| No file under `paper/`, `results/`, `data/`, `figures/`, `scripts/` (non-`scripts/audit/`) modified | ✓ |
| All new files written under `audit/` and `scripts/audit/` | ✓ |
| No git add/commit/push/rebase/config | ✓ |
| No network access | ✓ |
| Did not treat session.md as evidence | ✓ |
| Did not claim raw QC authenticity | ✓ |
| Did not auto-rewrite any flagged location | ✓ |

---

## Deliverables this phase

```
audit/scscc2_scope_grep_hits.txt              185 hits across 7 files
audit/08_metrics.log                          stdout
audit/scscc2_scope_metrics.tsv                13-row metrics table
audit/scscc2_scope_metrics.md                 human-readable summary
audit/09_classify.log                         stdout
audit/scscc2_claim_classification.tsv         46 substantive classifications
audit/scscc2_recommended_language.md          replacement text + per-line list
audit/phase3_5_scscc2_scope.md                (this file)
scripts/audit/08_check_scscc2_scope_metrics.py
scripts/audit/09_classify_scscc2_claims.py
```

---

## Allowed conclusion

> At the processed-table level, the SCS-CC2 extension can support
> **screened-cohort sign agreement**, not population-level method
> validation or method-independent quantitative ranking. The paper's
> main analytical text (Abstract / §3.5 body / §5 / §6) already uses
> this framing; the remaining gap is a small set of stale n=4 captions
> and legacy CI-metadata fields that should be reworded for consistency
> with the body text.

---

## Not allowed conclusion

> This phase does **not** verify raw SCS-CC2 calculations. Raw
> ricc2/control/slurm provenance remains to be tested in Phase 4.

---

**Phase 3.5: COMPLETE. Halting. Do not enter Phase 4 without explicit
user instruction.**
