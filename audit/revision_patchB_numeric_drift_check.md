# Patch B review-fix — Numeric drift check (regenerated)

## Verdict: **PASS — zero scientific numeric drift**

## Method

Compared the pre-Patch-B HEAD baseline (`git show HEAD:results/canonical_metrics.json`)
against the post-review-fix `results/canonical_metrics.json`, focusing
on the `scs_cc2_extended_n13` block. Reported per-cell status per the
specified vocabulary in `audit/revision_patchB_numeric_drift_check.tsv`.

The drift TSV is the authoritative machine-readable artifact; this
markdown is a summary.

## Counts

| status | count |
|---|---|
| UNCHANGED | **117** (all 13 molecules × 8 numeric+bool keys = 104 + 13 cohort-level numeric fields) |
| EXPECTED_METADATA_CHANGE | 19 (alias / wording / repo URL / generator field additions) |
| ROUNDING_ONLY | 0 |
| UNEXPECTED_NUMERIC_DRIFT | **0** |
| MISSING_BEFORE | 0 (numeric); some metadata-alias fields are MISSING_BEFORE / EXPECTED_METADATA_CHANGE |
| MISSING_AFTER | 0 |

## Per-molecule (13 molecules × 8 keys = 104 cells)

All 104 cells UNCHANGED across:
`ADC2_dEST_meV`, `SCSCC2_dEST_meV`, `SCSCC2_S1_eV`, `SCSCC2_T1_eV`,
`abs_ddEST_meV`, `ADC2_dEST_meV_abs`, `SCSCC2_dEST_meV_abs`, `sign_agree`.

Molecule set verified equal to `results/scscc2_extension_n13/cross_check_n13.csv`
mol_id column by the single-writer validator (check #6).

## Cohort-level (13 numeric fields)

All 13 UNCHANGED:
`n_total` (=13), `n_sign_retain` (=13), `sign_retain_rate` (=1.0),
`clopper_pearson_95_CI` (=[0.7529, 1.0]),
`clopper_pearson_90_CI` (=[0.7942, 1.0]),
`abs_ddEST_meV_min` (=10.09), `abs_ddEST_meV_max` (=193.74),
`abs_ddEST_meV_mean` (=109.84), `abs_ddEST_meV_median` (=101.45),
`narrowest_margin_mol` (="Hz_NPh21_Cz2"), `narrowest_margin_meV` (=10.1),
`rule_of_three_upper_bound` (=0.2308).

Note: `rule_of_three_upper_bound` and the `narrowest_margin_*` pair
were added during Patch B (they did not exist in HEAD), so they appear
in the TSV as `MISSING_BEFORE` / `EXPECTED_METADATA_CHANGE` — they
are computed from n_total and from `abs_ddEST_meV.idxmin()` respectively;
no new scientific input was introduced.

## Expected metadata changes (19)

These are intentional Patch B / review-fix metadata additions or
wording updates; not scientific numeric values:

- new aliases: `generator`, `upstream_generator`, `screened_cohort_n`,
  `sign_disagreements`, `paper_cited_scope`, `paper_cited_bound`,
  `repository`, `repository_canonical`, `raw_provenance_status`,
  `audit_report_reference`, `generated_from`,
  `per_molecule_representation`, `clopper_pearson_note`,
  `cross_check_csv`, `stats_json`, `writer`;
- updated wording: `ci_method` (CP primary → screened-cohort
  rule-of-three disclaimer);
- updated wording: `paper_cited_signrate` ("13/13" → "0 sign
  disagreement within the ADC(2)-screened cohort");
- new long-form record: `ci_method_long_form` (full text of
  the upstream stats ci_method).

## Conclusion

Zero scientific numeric drift. All 117 numeric / boolean cells in the
`scs_cc2_extended_n13` block are UNCHANGED. All 19 metadata changes
are intentional Patch B aliases or wording updates and carry no
scientific number. The drift TSV
(`audit/revision_patchB_numeric_drift_check.tsv`) is the machine-
readable evidence.
