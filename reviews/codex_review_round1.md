# Codex Review Round 1

Date: 2026-04-27

## 1. Recommendation: major

The draft is materially improved and most headline numbers now match the current repository evidence chain. It is not yet ready for direct submission because several high-risk claims are still under-caveated or under-traceable, especially around Fig5 denominators, descriptive Fisher tests on selected cohorts, and the practical meaning of a 52.1 meV MAE relative to a 30 meV classification threshold.

## 2. Major issues

1. The low-level calibration numbers in the manuscript are not traceable to the current canonical evidence chain.
   - `paper/main.tex:57-61` states a five-anchor linear calibration with coefficients `0.5501` and `-0.2127`.
   - The rendered workflow figure also encodes `n=5` and `R^2=0.97`.
   - Those values are not present in `results/canonical_metrics.json`, the current `figures/caption_data/*.json`, `results/Table1_invest_candidates.tex`, or `results/Table2_method_summary.tex`.
   - For a manuscript governed by canonical traceability, this is a blocking provenance gap even if the numbers may be historically correct.

2. The manuscript still does not communicate the `15` vs `14` and `7/15` vs `6/14` distinction cleanly enough at the figure-caption level.
   - `paper/main.tex:74` says the manuscript reports `14` molecules for round-1 deployment benchmarking, which is incomplete without simultaneously reminding the reader that the actual deployment set has `15` queried molecules.
   - `paper/main.tex:146` describes Fig5 panel (b) without stating that it is the `14`-molecule Fisher/conformal subset excluding `Hz_NH23`.
   - `paper/audit_reports/fig5_reconciliation.md` and `figures/caption_data/Fig5_al_value.json` already define the required rule: use `7/15` for deployment yield and `6/14` only for the panel-b Fisher/conformal subset. The manuscript caption still underspecifies that rule.

3. Selected-cohort Fisher p-values are still written too inferentially for the current evidence base.
   - `paper/main.tex:141` presents `p=0.031` for the `6/9` vs `0/5` round-1 subset and `p=0.015` for the full `13/27` vs `0/8` validated cohort.
   - The manuscript avoids claiming hit-rate improvement over baselines, which is correct, but it still needs explicit descriptive-only wording for these Fisher results because the cohorts are small and partially selected by the workflow itself.
   - `figures/caption_data/Fig5_al_value.json` already says panel-b is a subset with an explicit exclusion rule and should not be conflated with deployment yield.

4. The current wording still overstates practical predictive utility relative to the decision threshold.
   - `paper/main.tex:98` defines a `30 meV` borderline window.
   - `paper/main.tex:107` and `paper/main.tex:194` describe the post-round model as “useful” based on a `52.1 meV` LOO-CV MAE.
   - A model whose MAE exceeds the classification threshold can still be useful for scaffold-level prioritization, but not for confident candidate-level near-threshold classification. That limitation should be explicit wherever `52.1 meV` is used as a positive headline result.

## 3. Minor issues

1. `paper/main.tex:139` names “uniform random, scaffold-stratified random, and Hz-greedy baselines” but then lists four p-values: `1.0`, `1.0`, `0.999`, and `0.971`. The text should either name both Hz-greedy variants or reduce the p-value list to the categories explicitly introduced.

2. `paper/main.tex:113-122` is directionally careful, but the subsection title “Target-Domain Physics Descriptors Do Not Improve the 33-Molecule Residual Model” is slightly stronger than the underlying evidence. The repository’s own caption metadata supports “no clear improvement” more directly than an absolute negative conclusion.

3. `paper/main.tex:126-135` correctly reports the conformal and bootstrap numbers, but the figure caption for Fig2 does not disclose that the coverage estimate is discrete on only `14` test molecules. That is a wording gap rather than a numerical error.

4. `paper/main.tex:154-165` appropriately caveats `Hz_POZ1_NPh21_CF31`, but the conclusion later returns to broader wording about validated negative-gap behavior without always repeating that these remain method-level candidate assignments under the present computational protocol.

## 4. Cosmetic issues

1. The manuscript alternates between “negative-gap”, “negative or dark negative-gap”, and “validated negative-gap behavior” in ways that are semantically close but rhetorically uneven.

2. `paper/main.tex:150` uses “numerically encouraging”, which reads slightly promotional relative to the otherwise restrained style.

3. Fig captions are numerically much stronger than they were before, but their caveat density is still uneven across figures: Fig4 is disciplined, while Fig0/Fig2/Fig5 still rely too much on the main text to supply boundary conditions.

## 5. Exact manuscript sentences that overclaim

1. `paper/main.tex:41`
   - “The post-round delta-transfer model is quantitatively useful within the available target domain, target-domain physics descriptors do not improve predictive accuracy at the present data scale, uncertainty estimates degrade under the observed shift, and active learning contributes primarily by refining which scaffold family remains worth validating.”
   - Problem: “quantitatively useful” needs explicit threshold context; “do not improve” is stronger than “did not show a clear improvement”.

2. `paper/main.tex:107`
   - “The main methodological point is therefore not that the model has solved INVEST ranking, but that a residual correction trained on a small target-domain sample can translate a larger historical corpus into a materially better within-domain predictor.”
   - Problem: directionally fair, but still needs a direct reminder that `52.1 meV` exceeds the `30 meV` borderline threshold.

3. `paper/main.tex:141`
   - “In the round-1 statistical test, the Hz-versus-5AP contingency table is 6/9 versus 0/5, yielding Fisher's exact $p=0.031$.”
   - Problem: selected-cohort p-value should be framed explicitly as descriptive, not inferentially self-standing.

4. `paper/main.tex:194`
   - “First, delta transfer learning is quantitatively useful in the small-data regime studied here: after round-1 updating, the post-round target-set LOO-CV MAE is \SI{52.1}{meV}.”
   - Problem: same threshold issue; this is too strong as a conclusion headline without the `30 meV` caveat.

5. `paper/main.tex:194`
   - “In this library it supports the conclusion that validated negative-gap behavior is confined to heptazine derivatives, while 5AP and BN-containing molecules remain positive-gap under the present computational protocol.”
   - Problem: better than an unconditional chemical claim, but still should read more explicitly as a current method-level validation-table outcome, not a broader chemical truth.

## 6. Exact figure/caption problems

1. Fig0 caption in `paper/main.tex:46`
   - The caption reports the `446 -> 33 -> 15 -> 35` chain but does not state that higher-level SCS-CC2 evidence exists for only `4` selected molecules.
   - This is inconsistent with `figures/caption_data/Fig0_workflow.json`, which explicitly requires the `N=4` caveat.

2. Fig2 caption in `paper/main.tex:131`
   - The caption does not state that the benchmark is the `14`-molecule subset excluding `Hz_NH23`.
   - It also does not note that coverage is small-sample and discrete.
   - Both caveats are explicitly required by `figures/caption_data/Fig2_uq_shift.json`.

3. Fig3 caption in `paper/main.tex:159`
   - The caption does not disclose that `fosc = 0` is clipped to a positive floor for log-scale plotting.
   - This is not a numerical error, but it is a real plotting caveat already documented in `figures/caption_data/Fig3_classification.json`.

4. Fig5 caption in `paper/main.tex:146`
   - This is the most important caption problem remaining.
   - The caption does not tell the reader that panel (a) uses the full `35`-molecule validated cohort, while panel (b) uses the `14`-molecule Fisher/conformal subset excluding `Hz_NH23`.
   - It also does not encode the repository’s required reconciliation rule: `7/15` for deployment yield, `6/14` only for panel-b.

## 7. Numerical claims not supported by canonical sources

1. `paper/main.tex:57-60`
   - The calibration coefficients `0.5501` and `-0.2127` are not present in `results/canonical_metrics.json`, any current caption-data JSON, or the generated manuscript tables.

2. `paper/main.tex:57`
   - The claim that the calibration uses `five` ADC(2) anchor molecules is not currently anchored in `results/canonical_metrics.json` or the generated tables/caption-data.

3. The workflow figure itself encodes `R^2 = 0.97`, but that value is not represented in the current canonical or caption-data evidence chain used for manuscript traceability.

## 8. Statistical misuse or overinterpretation

1. The round-1 Fisher exact result (`6/9` vs `0/5`, `p=0.031`) is currently being used in a way that still reads inferentially stronger than the repository’s own caveats justify. It should be described as a descriptive scaffold-resolution statistic on a selected subset.

2. The full-cohort Fisher exact result (`13/27` vs `0/8`, `p=0.015`) is more manuscript-appropriate than the round-1 subset p-value, but it is still based on a small validated set and should be framed as evidence within the present computational protocol rather than as a population-level rate estimate.

3. The deterministic 10-seed ablation replay is handled much better than before, but the manuscript should remain careful not to let “10 seeds” read as 10 independent stochastic replications.

4. The baseline comparison is correctly used to reject any hit-rate-improvement claim for active learning. That part passes and should not be re-strengthened later in revision.

## 9. Computational chemistry overclaims

1. RI-ADC(2)/def2-SVP negative-gap assignments still need to be treated as method-level candidate classifications. The manuscript mostly does this correctly, but the conclusions should be more consistent about it.

2. The four SCS-CC2 cross-checks do not justify language that sounds like full multi-level validation of the candidate set. The body text is disciplined here; Fig0 remains the main weak point.

3. `Hz_POZ1_NPh21_CF31` is appropriately flagged as a low-confidence SCS-CC2-promoted case. Any broader conclusion about “validated heptazine candidates” should continue to keep this edge case visible rather than letting it disappear into the aggregate count of 13.

4. Method-consistency evidence remains mixed outside the four cross-checked molecules. `results/method_consistency_table.csv` shows several DFT/ADC(2) sign conflicts (`5AP_NEt2_NPh2`, `Hz_POZ1_DMAC2`, `Hz_POZ2_CN1`, `POZ-BN`), which reinforces the need to avoid over-generalized claims about transferable quantitative ordering across methods.

## 10. Missing analyses or calculations

1. A script-generated canonical source for the low-level calibration fit is missing. The manuscript needs an auditable result artifact containing at least the anchor identities, `n`, fit coefficients, and `R^2`.

2. The low-confidence/near-threshold cases still warrant additional higher-level or basis-set follow-up if the authors want stronger candidate-level chemical claims:
   - `Hz_POZ1_NPh21_CF31`
   - `Hz_POZ1_DMAC2`

3. If the authors want to retain Fisher p-values in the Results section, they should consider adding explicit descriptive framing or confidence-interval language already available in the statistical outputs, especially for the `0/5` 5AP branch.

4. For direct submission under the current repository rules, the missing independent external review file remains an operational gap even though it is not a scientific calculation.

## 11. Statements that must be downgraded

1. “quantitatively useful” should become something like “improves within-domain LOO-CV error but remains coarse relative to the 30 meV decision threshold”.

2. “target-domain physics descriptors do not improve the 33-molecule residual model” should become “do not show a clear improvement in this 33-molecule residual-model setting”.

3. The round-1 Fisher statement should become explicitly descriptive, for example by saying the `6/9` vs `0/5` contrast is a subset-level scaffold-resolution result rather than a generalizable rate estimate.

4. “validated negative-gap behavior is confined to heptazine derivatives” should be downgraded to “within the current validated table and computational protocol, all negative/dark-negative classifications occur in the heptazine subset”.

## 12. Pass/fail checklist for direct submission

- Canonical metrics file exists and is script-generated: PASS
- Caption-data JSON exists for each main figure: PASS
- Deprecated Task-3 ablation files are not used as manuscript evidence: PASS
- Round-1 `15` deployment queries vs `14` panel-b/conformal subset is explicit everywhere it needs to be: FAIL
- `7/15` deployment yield vs `6/14` panel-b subset is explicit in Fig5 captioning: FAIL
- Fisher p-values on selected cohorts are clearly described as descriptive: FAIL
- SCS-CC2 `N=4` is not presented as full-candidate multi-level validation: FAIL
- RI-ADC(2)/def2-SVP negative-gap assignments are consistently framed as method-level candidates: FAIL
- Near-threshold/low-confidence cases are explicitly caveated: PASS
- All numerical claims are traceable to current canonical/caption/table sources: FAIL
- Repository completion standard requiring independent external review is met: FAIL
