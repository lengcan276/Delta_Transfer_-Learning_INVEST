# Author Response

Date: 2026-04-27

## Major issues addressed

1. Asset reproducibility
   The manuscript now compiles from the repository root, and the figure/table references in `paper/main.tex` were updated accordingly.

2. Numerical traceability
   `results/canonical_metrics.json` was regenerated from script after correcting the uncertainty baseline logic, and main-figure caption data JSON files were added under `figures/caption_data/`.

3. Validation-table evidence labeling
   `scripts/build_validated_master.py` now keeps explicit ADC(2) and SCS-CC2 columns, records the decision basis for each row, and removes unsupported `high` confidence labels.

4. Cross-method discussion
   The manuscript now states explicitly that the four SCS-CC2 cross-checks preserve sign but differ in magnitude by 100--174 meV, so the chemical conclusion is scaffold-level selection rather than method-independent ranking.

5. Innovation framing
   The abstract, results/discussion, and conclusions were rewritten to emphasize the actual novelty supported by the repository: source-to-target correction across electronic-structure levels, explicit uncertainty auditing under deployment shift, and scaffold-level resolution from active learning.

## Open follow-up items

- Decide whether to regenerate or retire `results/round1_eval/task3_ablation_results.csv`.
- Perform an external independent review and add the corresponding report file expected by the project checklist.
- Optionally perform a full bibliography metadata audit before submission.
