# Phase 3.6 Step 4.2 — False positives (do NOT change these)

These items were flagged by Phase 3.5's grep / classifier but are correct
as written. They must NOT appear in the recommended patch, and the user
should NOT be advised to edit them.

---

## A. Two-batch composite description (`paper/main.tex:74` + mirror)

| file | grep hit (excerpt) |
|---|---|
| `paper/main.tex` | line 74 — `"... an original 4-molecule batch (Hz_NH23, Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, Hz_POZ1_NPh21_CF31) computed using the same xtb-optimized geometries as the corresponding ADC(2) calculations ... and 9 additional molecules computed using independently re-converged δ-DFT xtb geometries ..."` |
| `paper_overleaf/main.tex` | line 74 (mirror) |

**Why this is correct (not stale):** The phrase "original 4-molecule
batch" is part of an explicit two-batch decomposition (4 historical + 9
new = 13 total). This is accurate provenance — the historical SCS-CC2
batch genuinely consisted of 4 molecules, and the 9 Phase-2 extension
molecules genuinely came later. Removing "4-molecule batch" would
delete real provenance information.

**Recommendation:** **do_not_change.**

---

## B. "Original 4-molecule pilot" contrast (`paper/main.tex:161` + mirror)

| file | grep hit (excerpt) |
|---|---|
| `paper/main.tex` | line 161 — `"Extending the higher-level audit to all 13 INVEST candidates --- rather than the original 4-molecule pilot ---"` |
| `paper_overleaf/main.tex` | line 161 (mirror) |

**Why this is correct (not stale):** The sentence contrasts the new
n=13 audit against the historical n=4 pilot. The word "4-molecule" is
load-bearing — it tells the reader where the previous baseline was.
Removing it would erase that contrast.

**Recommendation:** **do_not_change.**

---

## C. Legacy 4-molecule probe block in canonical_metrics.json (lines 634 / 681)

| file | json path |
|---|---|
| `results/canonical_metrics.json` | `candidate_scscc2_crosschecks.description` (line 634) |
| `results/canonical_metrics.json` | `method_consistency_benchmark.description` (line 681) |

The descriptions read:

> "ADC(2)/def2-SVP vs SCS-CC2/def2-SVP cross-check on the small set of
> candidate INVEST molecules promoted to higher-level verification.
> This is the 4-molecule consistency probe used to corroborate the
> negative-gap sign for the lead candidates; it is NOT a population-scale
> benchmark."

> "Population-scale multi-method consistency benchmark from
> results/method_consistency_table.csv. … This is NOT the 4-molecule
> candidate SCS-CC2 cross-check above — do not conflate the two when
> reporting method-agreement statistics."

**Why this is correct (not stale):** These descriptions document the
**legacy** `candidate_scscc2_crosschecks` block, which contains exactly
4 molecules. The block coexists with the newer `scs_cc2_extended_n13`
(n=13) block — they are two separate audit slices. The descriptions
correctly disambiguate them.

**Recommendation:** **do_not_change** the descriptions themselves. The
correct remedial action is at a structural level (Phase 4/5 may decide
whether to deprecate the legacy `candidate_scscc2_crosschecks` block
once the n=13 block is fully verified).

---

## D. CSV data rows flagged by classifier

| file | row |
|---|---|
| `results/scscc2_extension_n13/cross_check_n13.csv` | row 5 (Hz_POZ1_NPh21_CF31 data) and row 12 (Hz_NPh21_Cz2 data) |

The classifier rule fired on substring match (mol_id appears in the
data row). CSV data rows are not claim text and contain no rhetorical
content to rewrite.

**Recommendation:** **do_not_change** the CSV. Per-molecule warnings
should be added at the JSON-metadata or paper-text level, not by editing
the per-row data.

---

## E. canonical_metrics.json `scs_cc2_extended_n13.narrowest_margin_*` (line 1292 area)

The top-level fields `narrowest_margin_mol = "Hz_NPh21_Cz2"` and
`narrowest_margin_meV = 10.1` already correctly flag Hz_NPh21_Cz2.
Classifier flagged the molecule name appearing nearby and classified it
as `SIGN_SENSITIVE_CASE_NOT_FLAGGED` for context lines where the
per-molecule object header (e.g. `"Hz_NPh21_Cz2": {`) appears without
the warning in the immediate context window.

The information is present, just not duplicated inside each per-molecule
object.

**Recommendation:** **do_not_change** the existing fields. Consider
adding `narrowest_margin_warning` inside the per-molecule object as a
generator-refactor item (see `audit/phase3_6_changes_explained.md`
section D under REQUIRES_GENERATOR_REFACTOR), but this is MED priority
and not in the recommended patch.

---

## F. canonical_metrics.json `paper_cited_CI = "[0.7529, 1.0000]"` (line 1158)

This field literally records what is or was cited in the paper. It is
not the audit's job to rewrite the paper's historical citation; if the
paper text now uses rule-of-three instead of `[0.7529, 1.0000]`, the
correct fix is at the paper level (which the patch addresses) and at
the generator level (which the patch flags as REQUIRES_GENERATOR_REFACTOR).
Hand-editing `paper_cited_CI` would falsify what the JSON is recording.

**Recommendation:** **do_not_change.** The generator should be updated
to emit `paper_cited_bound = "rule-of-three 3/13 ≈ 0.23"` ALONGSIDE the
historical `paper_cited_CI` field for traceability.
