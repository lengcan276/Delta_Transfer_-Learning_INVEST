# Codex Review

Date: 2026-04-27

## Findings

1. Major (fixed): `paper/main.tex` referenced figures and tables with paths that did not compile reliably from the repository root.
2. Major (fixed): `scripts/99_emit_canonical.py` used the maximum validated-gap magnitude as the UQ fixed-width baseline instead of the conformal-result baseline encoded in `p0b_conformal_calibration.json`.
3. Major (fixed): `scripts/build_validated_master.py` assigned unsupported `high` confidence labels and did not preserve explicit traceability between ADC(2) values, SCS-CC2 values, and the final classification decision.
4. Moderate (fixed): the manuscript used over-strong framing for claims that are only supported at scaffold level or under method dependence.
5. Moderate (open): `results/round1_eval/task3_ablation_results.csv` is inconsistent with the `p0a` ablation outputs used elsewhere in the project.

## Residual risk

- Round-1 molecule counts still require careful wording because the deployment set has 15 molecules while the conformal test set has 14 by design.
- One final classification is promoted from the ADC(2) borderline window by an SCS-CC2 cross-check; this is now explicit in the manuscript and tables, but it should also be handled carefully in any reviewer response.
- Full bibliography auditing remains incomplete.
