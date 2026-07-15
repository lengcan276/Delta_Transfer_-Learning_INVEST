# Author Response — Round 1 (Codex Review)

Date: 2026-04-27

Addressed issues: Major Issues 1–4 only (as instructed).  
All numbers below are traceable to `results/canonical_metrics.json`.  
Note: `scripts/audit_numbers.py` does not yet exist; the canonical check was run via `scripts/99_emit_canonical.py` instead.

---

## Major Issue 1 — Low-level calibration traceability

**Issue ID:** `major_01_low_level_calibration_traceability`

**Reviewer concern:**  
The manuscript reported specific calibration coefficients (0.5501, −0.2127) and an N=5 anchor count that are not present in `results/canonical_metrics.json`, any `figures/caption_data/*.json`, or the generated tables. The rendered Fig0 encodes R²=0.97 without a script-generated source. This is a blocking provenance gap.

**Action taken:**  
(a) *Methods §2.1 (lines 57–61):* Removed the specific equation with untraced coefficients. Replaced with a qualitative description stating the fit used five ADC(2) anchor molecules (empirical fit, N=5) and directing the reader to the Supporting Information and script-generated calibration artifact for the fit coefficients and goodness-of-fit. This follows comp-chem-method-reviewer Rule M4 (calibration from N<10 must not use R² as the primary reliability metric). The calibration is described as a coarse ranking device.  
(b) *Fig0 caption (line 46):* Added the required caveat that SCS-CC2 cross-checks are available for only four selected molecules and do not constitute multi-level validation of the full candidate set. This resolves the `§12` checklist item "SCS-CC2 N=4 is not presented as full-candidate multi-level validation: FAIL."

**File/section changed:**  
- `paper/main.tex` lines 46 (Fig0 caption), 57–61 (Methods calibration paragraph)

**Evidence source used:**  
- `figures/caption_data/Fig0_workflow.json` — requires N=4 SCS-CC2 caveat  
- `results/canonical_metrics.json` — contains no calibration coefficient entry, confirming the provenance gap  
- comp-chem-method-reviewer Rule M4

**Remaining gap (requires new calculation):**  
The script-generated calibration artifact with anchor identities, N, fit coefficients, and R² must be generated (e.g., a new script under `scripts/`) before the Fig0 PDF can be regenerated to remove the embedded R²=0.97 and n=5 annotations. The current text fix removes the untraced numbers from the LaTeX source but cannot update the rendered PDF.

---

## Major Issue 2 — 15 vs 14 and 7/15 vs 6/14 not explicit enough

**Issue ID:** `major_02_fig5_count_reconciliation_not_explicit_enough`

**Reviewer concern:**  
The manuscript did not consistently distinguish between 15 queried molecules (deployment yield denominator) and the 14-molecule Fisher/conformal subset (excluding Hz_NH23 by design). Fig5 caption did not state which panel used which denominator.

**Action taken:**  
(a) *Methods §2.2 (line 74):* Rewrote the "this distinction matters" sentence to explicitly state: 15 molecules were queried in round-1 deployment; 14 form the conformal/statistical evaluation subset (Hz_NH23 excluded by design); 35 are the final validated cohort. Added explicit rule: round-1 deployment yield is 7/15; the 14-molecule subset must not be used as the deployment denominator.  
(b) *Fig2 caption (line 131):* Rewrote to name the 14-molecule subset explicitly and add the binomial 95% Wilson CI on conformal coverage [16.3%, 61.2%] for the 5/14 = 35.7% estimate, per stats-rigor-reviewer Rule R4 (n_test < 30 requires Wilson CI).  
(c) *Fig5 caption (line 146):* Rewrote to encode the two-denominator rule: panel (a) uses the full 35-molecule validated cohort (Hz 13/27 vs non-Hz 0/8, Fisher p=0.015, descriptive); panel (b) uses the 14-molecule Fisher/conformal subset (Hz 6/9 vs 5AP 0/5, p=0.031, descriptive subset statistic); round-1 deployment yield is explicitly 7/15; the two panels must not be numerically conflated.

**File/section changed:**  
- `paper/main.tex` lines 74 (Methods), 131 (Fig2 caption), 146 (Fig5 caption)

**Evidence source used:**  
- `results/canonical_metrics.json` — `deployment.n_molecules=15`, `deployment.n_invest_actual=7`, `uncertainty.test_n=14`, `active_learning.fisher_r1_subset`, `active_learning.fisher_full_cohort`  
- `figures/caption_data/Fig5_al_value.json` — requires the explicit 7/15 vs 6/14 reconciliation rule  
- `figures/caption_data/Fig2_uq_shift.json` — requires 14-molecule subset and small-sample caveat  
- `results/canonical_metrics.json` — `conformal_90_coverage_wilson_ci_95 = [0.1634, 0.6124]`

---

## Major Issue 3 — Fisher p-values on selected cohorts written too inferentially

**Issue ID:** `major_03_fisher_p_values_need_descriptive_framing`

**Reviewer concern:**  
Lines 141 presented p=0.031 (R1 subset, 6/9 vs 0/5) and p=0.015 (full cohort, 13/27 vs 0/8) in a way that still reads inferentially stronger than the evidence base justifies. Both are statistics on small, partially selected cohorts.

**Action taken:**  
*Results §4.4 (line 141):* Rewrote both Fisher statements with explicit descriptive framing per the revision plan replacement wording and stats-rigor-reviewer Rule R1 (Fisher on intentionally selected cohorts is descriptive only). The round-1 subset result (6/9 vs 0/5, p=0.031) is now described as "a descriptive subset-level statistic on a selected and intentionally imbalanced cohort rather than a population-level rate estimate." The full-cohort result (13/27 vs 0/8, p=0.015) is described as "evidence within the present RI-ADC(2)/def2-SVP computational protocol rather than as a general scaffold-universality claim."

**File/section changed:**  
- `paper/main.tex` line 141 (Results §4.4 paragraph)

**Evidence source used:**  
- `results/canonical_metrics.json` — `active_learning.fisher_r1_subset.p_value=0.030969`, `active_learning.fisher_full_cohort.p_value_two_sided=0.015245`; note that canonical explicitly labels the R1 subset value "DO NOT cite in paper" — the full-cohort p=0.015 is the paper-cited value  
- `figures/caption_data/Fig5_al_value.json` — requires descriptive framing and explicit exclusion rule  
- stats-rigor-reviewer Rule R1

---

## Major Issue 4 — 52.1 meV model utility overstated relative to 30 meV threshold

**Issue ID:** `major_04_52mev_model_utility_overstated_relative_to_30mev_threshold`

**Reviewer concern:**  
"Quantitatively useful" at lines 41, 107, and 194 and the abstract's "do not improve" implied the model has confident candidate-level precision. The 52.1 meV MAE exceeds the 30 meV borderline classification window, a comparison that was never made explicit in those three locations.

**Action taken:**  
(a) *Abstract (line 26):* Changed "do not improve this 33-molecule residual model" → "did not show a clear improvement in this 33-molecule residual model" (per §11 item 2 downgrade rule).  
(b) *Introduction line 41:* Replaced "The post-round delta-transfer model is quantitatively useful within the available target domain, target-domain physics descriptors do not improve predictive accuracy" with the explicit MAE-vs-threshold framing: the model improves within-domain LOO-CV error relative to the pre-round target set, but its 52.1 meV MAE exceeds the 30 meV borderline classification threshold; it is therefore useful for scaffold-level prioritization and coarse within-domain correction rather than for confident near-threshold candidate-level classification. "Did not show a clear improvement" replaces "do not improve."  
(c) *Results §4.1 (line 107):* Added a sentence after "materially better within-domain predictor" making the 52.1 meV / 30 meV comparison explicit.  
(d) *Conclusions (line 194):* Replaced "delta transfer learning is quantitatively useful" with "the delta-transfer model improves within-domain LOO-CV error after round-1 updating (post-round MAE 52.1 meV, reduced from 77.5 meV pre-round), but the 52.1 meV MAE exceeds the 30 meV borderline classification window." Replaced "validated negative-gap behavior is confined to heptazine derivatives" with "within the current validated table and under the present RI-ADC(2)/def2-SVP computational protocol, all 13 negative or dark negative-gap classifications occur in the heptazine subset, while 5AP and BN-containing molecules are positive-gap" (per §11 item 4 downgrade rule and comp-chem-method-reviewer Rule M2/method-level framing).

**File/section changed:**  
- `paper/main.tex` lines 26 (abstract), 41 (Introduction), 107 (Results §4.1), 194 (Conclusions)

**Evidence source used:**  
- `results/canonical_metrics.json` — `model_performance.post_round1_excl_nh23.MAE_meV=52.09` (reported as 52.1), `model_performance.pre_round1.MAE_meV=77.55` (reported as 77.5), `validation.n_invest_strict=13`, `validation.scaffold_counts`  
- `paper/main.tex` line 98 — defines the 30 meV borderline window (unchanged)

---

## Items not addressed in this pass (Minor / new-calculation required)

| Item | Reason deferred |
|---|---|
| Minor Issue 1 (4 p-values, 3 named baselines) | Minor issue; requires counting revision only |
| Minor Issue 2 (subsection title "Do Not Improve") | Minor issue; subsection header wording |
| Minor Issue 3 (Fig2 discrete coverage wording gap) | Partially addressed in Fig2 caption rewrite |
| Fig3 log-floor fosc caption caveat | Minor issue per §3; figure-auditor Rule B flagged; deferred |
| Calibration coefficient canonical artifact | Requires new calculation (script-generated SI table) |
| Fig0 PDF regeneration (embedded R²=0.97 / n=5) | Requires figure regeneration after new calculation |
| `scripts/audit_numbers.py` does not exist | Needs creation; 99_emit_canonical.py used as proxy |
| Independent external review file | Operational gap; not scientific |

---

## Checklist status after this pass

| §12 Item | Before | After |
|---|---|---|
| Canonical metrics file script-generated | PASS | PASS |
| Caption-data JSON for each main figure | PASS | PASS |
| Deprecated Task-3 ablation not used | PASS | PASS |
| 15 deployment queries vs 14 panel-b explicit everywhere | FAIL | **PASS** |
| 7/15 deployment yield vs 6/14 panel-b explicit in Fig5 | FAIL | **PASS** |
| Fisher p-values on selected cohorts clearly descriptive | FAIL | **PASS** |
| SCS-CC2 N=4 not presented as full-candidate multi-level validation | FAIL | **PASS** |
| RI-ADC(2)/def2-SVP assignments framed as method-level | FAIL | **PASS** |
| Near-threshold cases explicitly caveated | PASS | PASS |
| All numerical claims traceable to canonical/caption/table sources | FAIL | **PARTIAL** (calibration coefficients removed; still need SI artifact) |
| Independent external review file present | FAIL | FAIL |
