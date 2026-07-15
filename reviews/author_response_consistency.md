# Author response — consistency-driven revisions

This document drafts the prose-level fixes for the six remaining Major
issues that originated in `paper/audit_reports/consistency_audit.md`,
`paper/audit_reports/fig5_reconciliation.md`, and `reviews/claude_review.md`.

**No changes have been made to `paper/main.tex` while writing this draft.**
Each item below states the manuscript anchor, the suggested replacement
text, the canonical-metric path that backs every cited number, and a short
explanation of why the suggested wording neutralises the reviewer concern.

Pipeline state at the time of writing:

- `scripts/99_emit_canonical.py` regenerates `results/canonical_metrics.json`
  idempotently with the new `library.n_invest_labeled_pollice_source = 446`
  and `per_molecule_highlights.{Hz_NH23, Hz_POZ1_NPh21_CF31}` fields.
- `scripts/audit_numbers.py` reports **0 unresolved numbers** (down from 9)
  and 2 / 7 Major checks still tripped (audit M1 and audit M6, addressed
  below in §A1 and §A2).

---

## A1 — Audit M6: Abstract Fisher *p* qualifier missing

**Manuscript anchor:** Abstract (line 26), penultimate clause:
> "the full validated cohort gives a Hz-versus-non-Hz Fisher exact *p*
> value of 0.015."

**Suggested sentence-level replacement (insert qualifier in place):**
> "the full validated cohort gives a Hz-versus-non-Hz Fisher exact *p*
> value of 0.015 (two-sided, descriptive: the queried set was selected by
> the active-learning policy, not sampled at random)."

**Why this neutralises the concern.** R1 of `stats-rigor-reviewer`
requires that any Fisher *p* on an actively selected cohort carry the
"descriptive" / "selected cohort" qualifier *wherever it appears*, not
only in the Results section. The body (§4.4 line 137) already says
"reported as evidence within the present RI-ADC(2)/def2-SVP computational
protocol rather than as a general scaffold-universality claim"; the
Abstract has to mirror that scope flag. The added parenthetical also
tells the audit script's mitigation regex that the qualifier is present,
so audit Major M6 stops tripping.

**Canonical metric paths:**
- `active_learning.fisher_full_cohort.p_value_two_sided = 0.015245`
- `active_learning.fisher_full_cohort.note` (already says
  "Two-sided Fisher exact; rounded paper value is p=0.015")
- `active_learning.fisher_full_cohort.contingency_table = [[13, 14], [0, 8]]`

---

## A2 — Audit M1: Section 4.4 first 7/15 mention has no nearby 6/14 reminder

**Manuscript anchor:** §4.4 "Active Learning Is Most Valuable as a
Scaffold-Resolution Step" (line 135), opening sentence:
> "Round-1 active learning produced 7 negative-gap hits among 15 queried
> molecules. The baseline comparison file shows comparable hit counts for
> uniform random, scaffold-stratified random, and Hz-greedy baselines …"

The §2.2 sentence ("Round-1 deployment yield is expressed as 7 out of 15
queried molecules; the 14-molecule subset is used only for Fisher exact
tests and conformal benchmarking and must not be used as the deployment
denominator.") is far away; the audit's mitigation window is ±400
characters and finds no analysis-set reminder near the 7/15 mention.

**Suggested in-place clarifier (one short clause appended to the opening
sentence):**
> "Round-1 active learning produced 7 negative-gap hits among 15 queried
> molecules (the panel-b 6/14 number is the Fisher / conformal subset that
> excludes Hz_NH23; see §2.2 for the analysis-set rule)."

**Why this neutralises the concern.** It puts the explicit "7/15 for
deployment, 6/14 for the Fisher / conformal subset, see §2.2" reminder
inside the §4.4 paragraph, exactly where the figure-legend contrast
appears. The audit's mitigation regex matches on the
"Fisher … subset … excluded by design" phrasing and stops firing M1.
This change does NOT modify the underlying numbers (both 7/15 and 6/14
remain canonical) and does NOT contradict the §2.2 sentence — it
cross-references it.

**Canonical metric paths:**
- `datasets.round1_deployment_n = 15`
- `datasets.round1_conformal_test_n = 14`
- `active_learning.r1_invest_count_7_vs_6` in `known_inconsistencies`
  (status = `intentional_analysis_set_distinction`)
- `paper/audit_reports/fig5_reconciliation.md` (full molecule-level audit)

---

## A3 — Review M1: 446 vs 465 — already resolved in the canonical pipeline

**Investigation outcome.** I traced the data files
(`scripts/build_master_table.py` line 6 docstring;
`data/processed/master_molecule_table.csv` grouped by `source_domain`):

| `source_domain` | Total rows | Rows with non-null `adc2_dest_ev` |
|---|---|---|
| pollice | 1719 | **446** |
| this_work | 155 | 19 |
| omar2023 | 150 | 0 |
| pang2025 | 2 | 0 |
| **Total** | 2026 | **465** |

The paper's "446 Pollice ADC(2)/cc-pVDZ labels" is **correct**: it counts
the Pollice source-domain ADC(2) labels (= 446). The earlier canonical
field `library.n_invest_labeled = 465` was the union across all
`source_domain` values, which conflates the source training set with the
19 pre-Round-1 labelled target molecules. That field has now been
replaced in `scripts/99_emit_canonical.py` with explicit names:

- `library.n_invest_labeled_pollice_source = 446`
- `library.n_invest_labeled_thiswork_target_preR1 = 19`
- `library.n_invest_labeled_total = 465`
- `library.n_invest_labeled_filter_description` (human-readable)
- `library.n_invest_labeled_source_files` (file pointers)

Downstream, `figures/caption_data/Fig0_workflow.json` and
`Fig6_library.json` now resolve `n_invest_labeled_source` to **446**.
The audit's five "446 unresolved" entries are gone.

**Manuscript-side action required:** none. The five "446" mentions in
the manuscript (Abstract line 26, Introduction line 39, Fig 0 caption
line 46, §2.2 line 68, §2.4 line 78) are all correct as cited and now
resolve cleanly to a canonical leaf.

**Optional polish (recommended, not required).** §2.2 currently says
"The labeled source domain contains 446 molecules from the Pollice
dataset with ADC(2)/cc-pVDZ reference gaps." Append a parenthetical to
make the source-vs-target partition explicit:
> "The labeled source domain contains 446 molecules from the Pollice
> dataset with ADC(2)/cc-pVDZ reference gaps (a further 19 ADC(2) labels
> exist on the pre-Round-1 target subset — these are the calibration set
> for split conformal prediction, not part of the source training set)."

**Canonical metric paths:**
- `library.n_invest_labeled_pollice_source = 446`
- `library.n_invest_labeled_thiswork_target_preR1 = 19`
- `library.n_invest_labeled_total = 465`
- `library.n_invest_labeled_source_files`

---

## A4 — Review M2: §2.3 "Post-Hartree–Fock Validation" missing geometry, SCS, SOC/RISC

**Manuscript anchor:** §2.3 (lines 72–74), three sentences only.

**Suggested three-sentence insertion (between the existing second and
third sentence, i.e. after "…sign consistency and quantitative method
dependence." and before "The final validation table…"):**

> "All ADC(2) and SCS-CC2 single points were performed on the GFN2-xTB
> S<sub>0</sub> geometries described in §2.1 (no further re-optimisation
> at correlated levels). SCS-CC2 used the Turbomole defaults
> *c*<sub>os</sub> = 1.2, *c*<sub>ss</sub> = 0.33. Spin–orbit matrix
> elements and reverse intersystem crossing rates were not computed; the
> reported INVEST classifications are therefore electronic-structure
> assignments at the ADC(2)/def2-SVP level (with selected SCS-CC2
> cross-checks) rather than predicted emitter performance."

**Why this neutralises the concern.** Three independent rules from
`comp-chem-method-reviewer` (M3 = SOC/RISC disclaimer, M5 = SCS
parameters, M6 = geometry source) collapse §2.3 into a "not
reproducible" risk. The three suggested sentences address each rule
literally, and none of them changes any number — they add provenance
that should already have been in §2.3.

**Verification step required from the authors:** confirm that the
ADC(2)/SCS-CC2 single points were indeed run on the GFN2-xTB geometries
(not, e.g., on DFT-relaxed geometries). If the geometries differ, the
sentence should be amended accordingly.

**Canonical metric paths (no numbers added; this is provenance prose):**
- `method_crosscheck.candidate_scscc2_crosschecks.molecule_details`
  (per-molecule ADC(2) and SCS-CC2 values for the four cross-checks)
- `per_molecule_highlights.Hz_NH23.{adc2_gap_meV, scs_cc2_gap_meV}`
- `per_molecule_highlights.Hz_POZ1_NPh21_CF31.{adc2_gap_meV, scs_cc2_gap_meV}`

---

## A5 — Review M3: Hz_POZ1_NPh21_CF31 basis-set sensitivity disclaimer

**Manuscript anchor:** §4.5 (line 150), the sentence beginning
"One of the 13 heptazine classifications deserves explicit qualification:
\texttt{Hz\_POZ1\_NPh21\_CF31} is borderline by ADC(2) (−9.7 meV) but
negative by SCS-CC2 (−165.6 meV)…", and the corresponding row in
Table 1 (`results/Table1_invest_candidates.tex`).

**Suggested clause appended to the existing §4.5 sentence:**
> "… and is kept at low evidence strength in
> Table~\ref{tab:invest_candidates}. Because |ΔEST(ADC(2)/def2-SVP)| of
> 9.7 meV lies well inside the basis-set sensitivity window
> (< 100 meV), basis-set sensitivity at the ADC(2) level was not
> independently assessed for this molecule and the classification should
> be treated as provisional pending an ADC(2)/def2-TZVP (or larger basis)
> verification."

**Suggested Table 1 footnote** (one extra footnote attached to the
Hz_POZ1_NPh21_CF31 row's "Confidence: Low" cell):
> "Provisional: |ΔEST(ADC(2)/def2-SVP)| = 9.7 meV is inside the basis-
> set sensitivity window. Sign promotion to negative-gap rests on the
> SCS-CC2/def2-SVP value; basis-set sensitivity at the ADC(2) level not
> yet assessed."

**Why this neutralises the concern.** Rule M1 of
`comp-chem-method-reviewer` requires either a second-basis calculation
or an explicit "basis-set sensitivity not yet assessed; classification
provisional pending TZVP-level verification" disclaimer. The §4.5
clause and the Table 1 footnote add that disclaimer literally, while the
row stays in Table 1 with its already-low confidence flag.

**Canonical metric paths:**
- `per_molecule_highlights.Hz_POZ1_NPh21_CF31.adc2_gap_meV = -9.7`
- `per_molecule_highlights.Hz_POZ1_NPh21_CF31.scs_cc2_gap_meV = -165.6`
- `per_molecule_highlights.Hz_POZ1_NPh21_CF31.context` (already records
  the "kept at low confidence pending basis-set sensitivity check"
  framing)

---

## A6 — Review M4: Abstract small-sample qualifiers (n / Wilson CI / baseline / "descriptive")

**Manuscript anchor:** Abstract (line 26). Four numerical clauses need
in-place qualifiers; the existing numbers stay unchanged.

The current Abstract sentence reads (compressed for clarity):
> "…reaching a leave-one-out cross-validation mean absolute error of 52.1
> meV, an RMSE of 66.9 meV, and 78.8% sign accuracy. … On the 14-molecule
> out-of-distribution deployment benchmark used for conformal evaluation,
> split conformal prediction gives 35.7% empirical coverage at the 95%
> nominal level with 53 meV mean intervals … Round-1 acquisition
> identifies 7 negative-gap molecules among 15 queries, but its clearest
> value is scaffold resolution: all five queried 5-aminopyrimidines are
> positive-gap molecules, and the full validated cohort gives a
> Hz-versus-non-Hz Fisher exact *p* value of 0.015."

**Suggested in-place qualifiers (italics mark the inserts):**

1. "78.8% sign accuracy" → "78.8% sign accuracy *(n = 33 post-Round-1
   target molecules, LOO-CV, deterministic across 10 seeds, MAE_std =
   0)*."
2. "35.7% empirical coverage at the 95% nominal level" → "35.7%
   empirical coverage at the 95% nominal level *(5/14, binomial 95%
   Wilson CI [16.3%, 61.2%]; n_test = 14 < 30)*."
3. "Round-1 acquisition identifies 7 negative-gap molecules among 15
   queries" → "Round-1 acquisition identifies 7 negative-gap molecules
   among 15 queries *(against expected counts of 13.2, 13.1, 12.2, and
   10.0 under the four reference baselines; one-sided permutation
   p ≥ 0.97)*."
4. "Hz-versus-non-Hz Fisher exact *p* value of 0.015" — covered in **A1**
   above with the "(two-sided, descriptive: …)" insert.

**Six candidate qualifying phrases for the *p* = 0.015 / *p* = 0.031
clauses (please choose one):**

   a. "(descriptive)"
   b. "(descriptive on a selected cohort)"
   c. "(descriptive, post-hoc, on an actively selected cohort)"
   d. "(post-hoc, descriptive)"
   e. "(reported as a descriptive subset statistic, not a population-level
      rate estimate)"
   f. "(two-sided, descriptive: the queried set was selected by the
      active-learning policy, not sampled at random)"

A6.f is the most explicit and is the version pre-installed in §A1
above. A6.b is the most compact and would survive a journal that
imposes a hard abstract word limit.

**Why this neutralises the concern.** R3 (every accuracy / hit-rate
must carry *n* and a baseline reference), R4 (small-sample coverage
must carry a Wilson CI when *n* < 30), and R1 (Fisher *p* on a selected
cohort must carry the "descriptive" qualifier) collapse the Abstract's
four small-sample claims into a non-trivial overstatement risk. The
inserted parentheticals carry exactly the information the corresponding
Results-section sentences already carry.

**Canonical metric paths:**
- `model_performance.post_round1_excl_nh23.{n_target = 33, MAE_meV = 52.087,
  sign_accuracy = 0.7878787879}`
- `uncertainty.{test_n = 14, conformal_90_test_coverage = 0.357,
  conformal_90_coverage_wilson_ci_95 = [0.1634, 0.6124]}`
- `active_learning.baseline_comparisons.{B1_uniform_random,
  B2_scaffold_stratified, B3_hz_greedy_dft, B3_hz_greedy_empirical}`
- `active_learning.fisher_full_cohort.p_value_two_sided = 0.015245`

---

## A7 — Review M5: Ablation deterministic — n_eff = 1 inferential statement

**Manuscript anchor:** §3.2 "Target-Domain Physics Descriptors Do Not
Improve the 33-Molecule Residual Model" (line 109). The existing
sentence: "The ablation results are numerically identical across all 10
nominal random seeds because the implemented LOO-CV workflow is
effectively deterministic for this dataset."

**Suggested follow-on sentence, inserted immediately after that one:**
> "Because the per-seed residuals collapse to a single realisation, the
> Wilcoxon paired test is not meaningful for the four pairwise
> comparisons that involve a non-zero deterministic difference (n_eff =
> 1; reported as `p_value: null` in
> `canonical_metrics.ablation.paired_tests`); the only comparison with a
> formal *p* value is `full vs no_stda` at *p* = 1.0, where the per-seed
> residuals are identical. The configuration ordering reported below
> should therefore be read as a numerical inventory, not as a
> statistically resolved feature-importance ranking."

**Why this neutralises the concern.** R2 of `stats-rigor-reviewer`
requires that LOO-CV on a deterministic model be flagged as one number,
not a distribution, and that the inferential consequence (n_eff = 1)
be stated. The existing §3.2 wording stops one sentence short — it says
"deterministic" but does not say "therefore Wilcoxon is not applicable
and the ordering is a single realisation". The added sentence closes
that gap and pairs neatly with the §4 ("Scope") wording on line 179.

**Canonical metric paths:**
- `ablation.paired_tests.paired_tests.no_stda.{p_value = 1.0,
  significant_005 = false}`
- `ablation.paired_tests.paired_tests.no_ksod.{p_value = null,
  deterministic_diff = -0.0025269076151919964,
  interpretation = "LOO-CV is deterministic for this data: …
  Wilcoxon not applicable (n_eff = 1)."}`
- (same `null` *p* and `interpretation` for `no_stda_no_ksod`,
  `no_dft`, `rdkit_only`)

---

## File-touch summary

| File | Status | Reason |
|---|---|---|
| `paper/main.tex` | not modified | this document drafts only |
| `scripts/99_emit_canonical.py` | modified | refactored library section + added per_molecule_highlights |
| `scripts/emit_figure_caption_data.py` | modified | switched to `n_invest_labeled_pollice_source` |
| `results/canonical_metrics.json` | regenerated (idempotent) | output of the two scripts above |
| `figures/caption_data/*.json` | regenerated | 7/7 enforcement rules pass |
| `paper/audit_reports/consistency_audit.md` | regenerated | unresolved 9 → 0; Major checks 2 / 7 (M1, M6 — addressed in §A1, §A2 above) |
| `reviews/author_response_consistency.md` | new | this file |
