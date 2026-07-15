# Phase 3.5 Step 4 — Recommended SCS-CC2 validation language

This document is **advisory only**. It does not modify any file. It lists
the recommended replacement wording for the SCS-CC2 validation discussion
and itemises every grep-hit that should be reworded, kept, or left alone.

---

## 1. Recommended main-text paragraph

(Replacement for the §3.5 + §3.5-continuation discussion of SCS-CC2.)

### Title suggestion
**Hierarchical validation converts screened hits into sign-level evidence**

### Replacement text

> The validation tier changes the status of heptazine candidates from
> model-guided hits to sign-checked electronic-structure leads. ADC(2)/def2-SVP
> supplies the primary label for all 35 validated molecules, yielding 10
> negative-gap, 3 dark negative-gap, 1 borderline, and 21 positive-gap
> classifications. SCS-CC2/def2-SVP was then applied to all 13
> ADC(2)-screened negative-or-dark-negative candidates.
>
> The SCS-CC2 audit preserved the negative sign in every screened INVEST
> candidate. Because these 13 molecules were pre-selected by ADC(2), the
> statistic should be reported as **0 sign disagreement within the screened
> cohort**, with a descriptive **one-sided rule-of-three upper bound of
> approximately 3/13 = 0.23** for the within-screen sign-disagreement rate.
> It should not be presented as a Clopper–Pearson confidence interval for
> a randomly sampled chemical population.
>
> The cross-method shifts define the resolution of the claim. All 13
> SCS-CC2 ΔE_ST values are more negative than the corresponding ADC(2)
> values, with shifts from 10 to 194 meV and a mean of 110 meV. This
> systematic direction strengthens sign-level confidence **within the
> ADC(2)/CC2 hierarchy**, but it also shows that the two methods are not
> independent arbiters producing identical quantitative gaps. The present
> evidence supports heptazine scaffold retention and screened-cohort sign
> agreement; it does **not** support method-independent ranking among the
> most negative candidates.
>
> One promoted borderline molecule illustrates why the hierarchy is
> necessary. **Hz_POZ1_NPh21_CF31** lies inside the ADC(2) borderline
> region at −9.7 meV but becomes clearly negative at SCS-CC2, with
> ΔE_ST = −165.6 meV. This promotion is chemically meaningful but should
> retain **low evidence strength until a basis-set or method-family
> triangulation** is performed. Conversely, **Hz_NPh21_Cz2** has the
> narrowest cross-method margin, with ADC(2) ΔE_ST = −119.0 meV and
> SCS-CC2 ΔE_ST = −129.1 meV, making it the **most likely sign-sensitive
> case under further theoretical refinement**.

### Caption-safe short form (Fig 4 / Table 1 footnote)

> SCS-CC2 preserved the negative sign for all 13 ADC(2)-screened
> candidates. Because the molecules were pre-selected by ADC(2), this is
> reported as 0 sign disagreement within the screened cohort; the
> rule-of-three gives an approximate one-sided upper bound of 0.23 for the
> within-screen sign-disagreement rate.

---

## 2. Per-file rewrite list

### 2a. TRUE OVERCLAIMS — must rewrite

| file | line / json path | current wording | recommended replacement |
|---|---|---|---|
| `results/canonical_metrics.json` | `scs_cc2_extended_n13.ci_method` (line 1155) | `"Clopper-Pearson exact two-sided 95%"` | `"0 within-screen sign-disagreement (rule of three; one-sided 95% upper bound on disagreement rate ≈ 3/13 = 0.23). Reported Clopper-Pearson and rule-of-three values retained for traceability only — paper cites rule-of-three. 13 molecules are an ADC(2)-pre-screened cohort, not an i.i.d. random sample."` |
| `results/canonical_metrics.json` | `scs_cc2_extended_n13.paper_cited_signrate` (line 1159) | `"13/13"` | `"0 sign disagreement in n=13 ADC(2)-screened cohort"` (or keep `13/13` and ADD an adjacent field `"paper_cited_scope": "screened-cohort sign agreement, not population CI"`) |
| `results/scscc2_extension_n13/stats_n13.json` | `ci_method` (line 20) | `"Clopper-Pearson exact two-sided 95%"` | same as above — keep the CP value in the JSON for traceability but rename `ci_method` to `ci_method_legacy` and add a new `paper_cited_bound: "rule-of-three one-sided 95%, 3/13 = 0.23"` field |

### 2b. TRUE STALE n=4 — must rewrite

| file | line | current wording | recommended replacement |
|---|---|---|---|
| `paper/main.tex` | 46 (Fig 0 caption) | "Higher-level SCS-CC2 cross-checks are available for **four selected molecules only** and do not constitute multi-level validation of the full candidate set." | "Higher-level SCS-CC2 cross-checks were applied to **all 13 ADC(2)-screened negative-gap candidates**; the larger 21 positive-gap subset retains only the ADC(2) label." |
| `paper/main.tex` | 155 (Fig 3 caption) | "**Four molecules** additionally have SCS-CC2 cross-checks, and one heptazine is promoted from the ADC(2) borderline window…" | "**All 13 ADC(2)-screened INVEST candidates** additionally have SCS-CC2 cross-checks, with sign agreement in every case; one heptazine is promoted from the ADC(2) borderline window by the higher-level result." |
| `paper/main.tex` | 170 (Hz_NH23 paragraph) | "The combination of decisive scaffold elimination, hierarchical SCS-CC2 sign confirmation on **the four leads**, and explicit retention of dark cases as separate classifications…" | "The combination of decisive scaffold elimination, **per-candidate SCS-CC2 sign confirmation across all 13 INVEST candidates**, and explicit retention of dark cases as separate classifications…" |
| `paper_overleaf/main.tex` | 46, 155, 170 | same as above (mirror file) | same replacements |
| `figures/caption_data/Fig0_workflow.json` | 44 | `"SCS-CC2 verification is restricted to 4 selected lead candidates (Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, Hz_POZ1_NPh21_CF31, Hz_NH23). It is NOT a population-scale method audit."` | `"SCS-CC2 verification covers all 13 ADC(2)-screened INVEST candidates (10 negative-gap + 3 dark negative-gap). It is a within-screened-cohort sign audit, not a population-scale method validation."` |
| `figures/caption_data/Fig0_workflow.json` | 47 | `"SCS-CC2 cross-checks are n = 4 selected molecules, NOT all 14 Table-1 candidates and NOT all 35 validated molecules."` | `"SCS-CC2 cross-checks cover all 13 ADC(2)-screened INVEST candidates (Table 1 negative-gap + dark negative-gap entries). The 21 positive-gap and 1 borderline-near-zero molecules retain only the ADC(2) label."` |
| `figures/caption_data/Fig4_crosscheck.json` | 85 | `"Panels showing the 4-molecule SCS-CC2 cross-check and panels showing the multi-method consistency benchmark must be visually separated and individually labeled with their respective n."` | `"Panels showing the n=13 SCS-CC2 cross-check and panels showing the legacy multi-method consistency benchmark must be visually separated and individually labeled with their respective n."` |
| `figures/caption_data/Fig4_crosscheck.json` | 90 | `"On the 4-molecule candidate cross-check set, ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for 4/4 molecules with absolute differences spanning 100–174 meV."` | `"On the 13-molecule ADC(2)-screened cohort, ADC(2)/def2-SVP and SCS-CC2/def2-SVP agree in sign for 13/13 molecules (0 within-screen disagreement), with absolute cross-method differences spanning 10–194 meV (mean 110 meV)."` |
| `results/Table1_invest_candidates.tex` | 3 (caption) | "…**four molecules** additionally have SCS-CC2 cross-checks, and one of them is promoted from the ADC(2) borderline window…" | "…**all 13 candidates** additionally have SCS-CC2 cross-checks (0 within-screen sign disagreement; rule-of-three upper bound on disagreement rate ≈ 0.23), and one of them (Hz_POZ1_NPh21_CF31) is promoted from the ADC(2) borderline window…" |
| `paper_overleaf/Table1_invest_candidates.tex` | 3 | (mirror) | same |
| `reviews/cover_letter.md` | 21 | "SCS-CC2/def2-SVP is **concentrated on four lead candidates**, where it confirms sign agreement in **4/4 cases**…" | "SCS-CC2/def2-SVP is applied to **all 13 ADC(2)-screened INVEST candidates** (the pre-registered Table 1 shortlist), where it confirms sign agreement in **all 13 cases**; rule-of-three one-sided 95% upper bound on within-screen disagreement ≈ 0.23." |

### 2c. SIGN_SENSITIVE_CASE_NOT_FLAGGED — recommend ADD wording

Per-molecule context entries in `results/canonical_metrics.json` (e.g.
`scs_cc2_extended_n13.per_molecule.Hz_NPh21_Cz2`) currently contain only
numeric values without a `narrowest_margin_warning` annotation. Recommended
ADD to that nested object:

```json
"narrowest_margin_warning": "smallest |ΔΔE_ST| in n=13 cohort (10.1 meV); most likely sign-flip candidate under further method change",
"abs_ddEST_meV": 10.1
```

(The top-level `scs_cc2_extended_n13.narrowest_margin_mol` /
`narrowest_margin_meV` already exist and are OK. This recommendation
duplicates the flag inside the per-molecule block so a downstream
consumer reading only the per-molecule entry sees the warning.)

### 2d. BORDERLINE_NEEDS_LOW_EVIDENCE — recommend ADD wording

Same pattern for `scs_cc2_extended_n13.per_molecule.Hz_POZ1_NPh21_CF31`.
Recommended ADD:

```json
"borderline_low_evidence_warning": "ADC(2)/def2-SVP value (|ΔE_ST|=9.7 meV) lies inside the ±30 meV borderline window; SCS-CC2 promotion to negative-gap should retain low evidence strength until basis-set sensitivity (def2-TZVP) or method-family triangulation (CCSD/CC3/NEVPT2) is performed",
"adc2_abs_meV": 9.7,
"basis_set_window_meV": 30
```

The top-level `per_molecule_highlights.Hz_POZ1_NPh21_CF31` already has
the relevant context (line 1087 says "kept at low confidence pending
basis-set sensitivity check"). This duplicates that flag inside the
`scs_cc2_extended_n13` block.

---

## 3. False-positive grep hits — do NOT rewrite

These were flagged by the classifier but are correct as written.

| file | line | reason it's correct |
|---|---|---|
| `paper/main.tex` | 74 (Methods §) | Uses "original 4-molecule batch" to describe the two-batch composite (4 historical + 9 new = 13). This is accurate two-batch terminology, not a stale n=4 claim. |
| `paper/main.tex` | 161 | "Extending the higher-level audit to all 13 INVEST candidates --- rather than the **original 4-molecule pilot** ---" correctly contrasts the new n=13 audit against the historical n=4 pilot. |
| `paper_overleaf/main.tex` | 74, 161 (mirrors) | same |
| `results/canonical_metrics.json` | 634 (`candidate_scscc2_crosschecks.description`) | The block is the **legacy 4-molecule consistency probe**, explicitly named that way and explicitly contrasted with the **population-scale** `method_consistency_benchmark` below. The "4-molecule" label is correct because the block contains exactly 4 molecules. |
| `results/canonical_metrics.json` | 681 (`method_consistency_benchmark.description`) | Same — describes the legacy population-scale benchmark and explicitly disclaims confusion with the candidate cross-check. |
| `results/scscc2_extension_n13/cross_check_n13.csv` | 5, 12 | Just CSV data rows, not claim text. Classifier false positive (rule fired on substring match). |

---

## 4. Wording principles to enforce going forward

1. Never present 13/13 as a Clopper–Pearson CI without also saying "the
   13 molecules are an ADC(2)-pre-screened cohort".
2. Always pair "0 sign disagreement" with the rule-of-three upper bound
   (≈ 3/13 = 0.23) when reporting in a quantitative claim.
3. Always pair the systematic SCS-CC2 < ADC(2) shift with the words
   "method-family consistency within the ADC(2)/CC2 hierarchy" — never
   leave 13/13 as the punchline without the systematic-shift caveat.
4. Always pair Hz_POZ1_NPh21_CF31's promotion with "low evidence strength
   pending basis-set or method-family triangulation".
5. Always pair Hz_NPh21_Cz2's value with "narrowest cross-method margin"
   or "most likely sign-flip candidate".
6. Distinguish (a) the **legacy 4-molecule consistency probe** (a separate
   small audit in `canonical_metrics.json.method_crosscheck`), (b) the
   **historical 4-molecule batch** within the new n=13 cohort, and (c)
   the **new n=13 audit**. The word "four" / "4-molecule" is only allowed
   in contexts (a) and (b); never in context (c).
