# Phase 3.6 Step 4.1 — Recommended changes explained (per file, per change)

This document explains the 13 recommended edits in
`audit/phase3_6_recommended_patch.diff`. **No file in the live repo
was modified.** All edits exist only in
`audit/_tmp_phase3_6_patch_workspace/`.

---

## EDIT 1 — `paper/main.tex` line 46 (Fig 0 caption)

| Field | Value |
|---|---|
| current stale wording | `Higher-level SCS-CC2 cross-checks are available for four selected molecules only and do not constitute multi-level validation of the full candidate set.` |
| recommended replacement | `Higher-level SCS-CC2 cross-checks were applied to all 13 ADC(2)-screened negative-or-dark-negative-gap candidates; the 21 positive-gap and 1 borderline-near-zero molecules retain only the ADC(2) label.` |
| rationale | Caption asserts SCS-CC2 is restricted to 4 molecules — contradicts §3.5 body which states n=13. Reader of Figure 0 alone gets the wrong cohort size. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** — pure statistical-scope correction; does not depend on raw QC authenticity. |

---

## EDIT 2 — `paper/main.tex` line 155 (Fig 3 caption)

| Field | Value |
|---|---|
| current stale wording | `Four molecules additionally have SCS-CC2 cross-checks, and one heptazine is promoted from the ADC(2) borderline window…` |
| recommended replacement | `All 13 ADC(2)-screened INVEST candidates additionally have SCS-CC2 cross-checks (0 within-screen sign disagreement), and one heptazine is promoted from the ADC(2) borderline window…` |
| rationale | Same as EDIT 1 — caption says n=4 while body says n=13. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 3 — `paper/main.tex` line 170 (Hz_NH23 paragraph)

| Field | Value |
|---|---|
| current stale wording | `hierarchical SCS-CC2 sign confirmation on the four leads` |
| recommended replacement | `per-candidate SCS-CC2 sign confirmation across all 13 ADC(2)-screened INVEST candidates` |
| rationale | Body paragraph says "the four leads" inconsistently with §3.5 saying n=13. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDITS 4, 5, 6 — `paper_overleaf/main.tex` lines 46, 155, 170

Same as EDITS 1-3 (the JCIM-formatted mirror of `paper/main.tex`).

| Field | Value |
|---|---|
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 7 — `figures/caption_data/Fig0_workflow.json` line 44

| Field | Value |
|---|---|
| current stale wording | `"SCS-CC2 verification is restricted to 4 selected lead candidates (Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, Hz_POZ1_NPh21_CF31, Hz_NH23). It is NOT a population-scale method audit."` |
| recommended replacement | `"SCS-CC2 verification covers all 13 ADC(2)-screened INVEST candidates (10 negative-gap + 3 dark negative-gap). It is a within-screened-cohort sign audit, not a population-scale method validation."` |
| rationale | Caption-data JSON drives the audit-numbers consistency check. Stale enumerated list of 4 molecule names is a particularly hard-coded n=4 assertion. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 8 — `figures/caption_data/Fig0_workflow.json` line 47

| Field | Value |
|---|---|
| current stale wording | `"SCS-CC2 cross-checks are n = 4 selected molecules, NOT all 14 Table-1 candidates and NOT all 35 validated molecules."` |
| recommended replacement | `"SCS-CC2 cross-checks cover all 13 ADC(2)-screened INVEST candidates (Table 1 negative-gap + dark negative-gap entries; the 21 positive-gap and 1 borderline-near-zero molecules retain only the ADC(2) label)."` |
| rationale | Same as EDIT 7 — explicit "n = 4" line. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 9 — `figures/caption_data/Fig4_crosscheck.json` line 85 (visualization_caveats item 0)

| Field | Value |
|---|---|
| current stale wording | `"Panels showing the 4-molecule SCS-CC2 cross-check and panels showing the multi-method consistency benchmark must be visually separated and individually labeled with their respective n."` |
| recommended replacement | `"Panels showing the n=13 SCS-CC2 cross-check and panels showing the legacy multi-method consistency benchmark must be visually separated and individually labeled with their respective n."` |
| rationale | Fig 4 IS the n=13 cross-check panel (regenerated Phase 3); caption-data should say n=13. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 10 — `figures/caption_data/Fig4_crosscheck.json` line 86 (visualization_caveats item 1)

| Field | Value |
|---|---|
| current stale wording | `"Absolute ADC(2)-vs-SCS-CC2 differences in the candidate set span 100.0–174.4 meV; signs agree in 4/4 molecules."` |
| recommended replacement | `"Absolute ADC(2)-vs-SCS-CC2 differences in the n=13 ADC(2)-screened cohort span 10.1–193.7 meV (mean 109.8 meV); signs agree in 13/13 molecules (0 within-screen disagreement; rule-of-three upper bound on disagreement rate ≈ 3/13 = 0.23)."` |
| rationale | The 100–174 meV range and 4/4 sign-agreement are stale n=4 numbers. New cohort range is 10.1–193.7 meV (audit-verified, see `audit/scscc2_scope_metrics.tsv`). |
| priority | HIGH |
| depends_on_phase4 | **MAYBE — see note** |
| safe_to_apply_before_phase4 | **yes**, with caveat: the numeric range 10.1–193.7 meV depends on the n=13 cross_check_n13.csv values. Phase 4 will independently verify those values against raw ricc2 outputs. If Phase 4 finds any of those values incorrect, this edit will need to be revisited. But the *direction* of the change (n=4 → n=13 framing) is correct regardless of Phase 4 numeric outcome. |

---

## EDIT 11 — `figures/caption_data/Fig4_crosscheck.json` line 90 (manuscript_claims_allowed item 0)

Same edit pattern as EDIT 10, in `manuscript_claims_allowed` block.

| Field | Value |
|---|---|
| current stale wording | `"On the 4-molecule candidate cross-check set, ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for 4/4 molecules with absolute differences spanning 100–174 meV."` |
| recommended replacement | `"On the n=13 ADC(2)-screened cohort, ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for 13/13 molecules (0 within-screen disagreement; rule-of-three one-sided 95% upper bound on disagreement rate ≈ 0.23), with absolute cross-method differences spanning 10–194 meV (mean 110 meV)."` |
| priority | HIGH |
| depends_on_phase4 | MAYBE (same caveat as EDIT 10) |
| safe_to_apply_before_phase4 | **yes**, with same caveat |

---

## EDITS 12, 13 — `results/Table1_invest_candidates.tex` line 3 + `paper_overleaf/Table1_invest_candidates.tex` line 3

| Field | Value |
|---|---|
| current stale wording | `four molecules additionally have SCS-CC2 cross-checks, and one of them is promoted from the ADC(2) borderline window by the higher-level result` |
| recommended replacement | `all 13 ADC(2)-screened candidates additionally have SCS-CC2 cross-checks (0 within-screen sign disagreement; rule-of-three upper bound on disagreement rate $\approx 0.23$), and one of them (Hz\_POZ1\_NPh21\_CF31) is promoted from the ADC(2) borderline window by the higher-level result` |
| rationale | Table 1 caption stale n=4 wording. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## EDIT 14 — `reviews/cover_letter.md` line 21

| Field | Value |
|---|---|
| current stale wording | `SCS-CC2/def2-SVP is concentrated on four lead candidates, where it confirms sign agreement in 4/4 cases` |
| recommended replacement | `SCS-CC2/def2-SVP is applied to all 13 ADC(2)-screened INVEST candidates (the pre-registered Table~1 shortlist), where it confirms sign agreement in all 13 cases (0 within-screen disagreement; rule-of-three one-sided 95% upper bound on disagreement rate ≈ 0.23)` |
| rationale | Cover letter must match paper claims; current text is stale n=4 inherited from earlier draft. |
| priority | HIGH |
| depends_on_phase4 | no |
| safe_to_apply_before_phase4 | **yes** |

---

## NOT INCLUDED in patch — REQUIRES_GENERATOR_REFACTOR

The following JSON-metadata corrections are **intentionally omitted** from
the recommended patch because they require modifying the script that
generates the JSON block, not the JSON file itself. Hand-editing JSON
that is later regenerated by a script will be silently overwritten.

### A. `results/canonical_metrics.json` `scs_cc2_extended_n13.ci_method` (line 1155)

| Field | Value |
|---|---|
| current stale wording | `"ci_method": "Clopper-Pearson exact two-sided 95%"` |
| recommended treatment | **REQUIRES_GENERATOR_REFACTOR**. The `scs_cc2_extended_n13` block is written by `scripts/scscc2_extension/build_cross_check_n13.py` (which also writes `results/scscc2_extension_n13/stats_n13.json`) plus a manual JSON patch step. Recommended action: update `build_cross_check_n13.py` to emit `ci_method` = "rule of three (one-sided 95% upper bound on within-screen sign-disagreement; the 13 molecules are an ADC(2)-pre-screened cohort, not an i.i.d. random sample)" and re-run the generator. Until then, the live JSON's `ci_method` field is misleading. |
| depends_on_phase4 | **partial** — generator refactor itself does not depend on Phase 4; but `scs_cc2_extended_n13.per_molecule.<mol>.SCSCC2_dEST_meV` values depend on raw ricc2 outputs (Phase 4). It is therefore most efficient to do the generator refactor AFTER Phase 4 confirms which (if any) per-molecule values stand. |
| safe_to_apply_before_phase4 | **no** (recommended) — defer to post-Phase-4 generator refactor. |

### B. `results/canonical_metrics.json` `scs_cc2_extended_n13.paper_cited_signrate` (line 1159)

| Field | Value |
|---|---|
| current wording | `"paper_cited_signrate": "13/13"` |
| recommended treatment | Add adjacent field `"paper_cited_scope": "screened-cohort sign agreement, not population CI"` (do not delete `"13/13"`). REQUIRES_GENERATOR_REFACTOR. |
| safe_to_apply_before_phase4 | **no** (recommended). |

### C. `results/scscc2_extension_n13/stats_n13.json` `ci_method` (line 20)

| Field | Value |
|---|---|
| current stale wording | `"ci_method": "Clopper-Pearson exact two-sided 95%"` |
| recommended treatment | Same as A — REQUIRES_GENERATOR_REFACTOR. |
| safe_to_apply_before_phase4 | **no** (recommended). |

### D. Per-molecule `narrowest_margin_warning` / `borderline_low_evidence_warning` annotations

| Recommended treatment | These annotations should be added to `scs_cc2_extended_n13.per_molecule.Hz_NPh21_Cz2` and `scs_cc2_extended_n13.per_molecule.Hz_POZ1_NPh21_CF31`. Same generator-refactor pattern. |
| depends_on_phase4 | **yes** — the numeric thresholds (10.1 meV margin, 9.7 meV borderline) depend on Phase 4 raw verification. |
| safe_to_apply_before_phase4 | **no** — wait for Phase 4. |

---

## Patch summary

- **HIGH priority, safe_to_apply_before_phase4=yes**: 13 edits in 7
  text/Markdown/LaTeX files (paper/main.tex × 3, paper_overleaf/main.tex × 3,
  Fig0 caption_data × 2, Fig4 caption_data × 2, Table1 × 2, cover_letter × 1)
- **HIGH priority, depends_on_phase4=MAYBE**: 2 edits (Fig4 caption_data
  numeric ranges 10.1–193.7 meV); direction is correct, exact numbers
  may be revisited after Phase 4
- **HIGH priority, REQUIRES_GENERATOR_REFACTOR**: 3 JSON metadata fields
  (canonical_metrics.json × 2, stats_n13.json × 1) — NOT in patch
- **MED priority, depends_on_phase4=yes**: per-molecule annotations —
  NOT in patch (wait for Phase 4)
