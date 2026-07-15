# Claude critical review of INVEST manuscript

Reviewer position: simulated stats-rigor + computational-chemistry referee for
JCIM. Scope: independent critical reading of `paper/main.tex`, going beyond
findings already in `paper/audit_reports/consistency_audit.md` and
`paper/audit_reports/fig5_reconciliation.md`. No source files modified.

Skills consulted (in order): **stats-rigor-reviewer**,
**comp-chem-method-reviewer**, **manuscript-consistency**,
**adversarial-reviewer**.

## Summary

**Recommendation: Major revision.**

The manuscript is unusually disciplined about scope language and analysis-set
distinctions, and its single-source-of-truth audit chain
(`canonical_metrics.json` → caption JSONs → main text) is strong. However,
three Major issues remain: (1) the paper's first numerical claim ("446
Pollice ADC(2)/cc-pVDZ labels") is non-canonical — `canonical_metrics.json`
emits **465** for the same definition (`library.n_invest_labeled`), so either
the paper or the script is wrong; (2) the post-HF Methods do not state the
geometry source for ADC(2)/SCS-CC2 single points and never report SCS
parameters or any SOC/RISC information, both of which are required by the
comp-chem method-reviewer rules for an INVEST/TADF-relevant claim;
(3) the Abstract reports four small-sample point estimates (78.8% sign
accuracy, 35.7% conformal coverage, 7/15 hit count, Fisher *p* = 0.015)
without the *n*-and-CI / descriptive qualifiers that the Results section
correctly supplies, so an Abstract-only reader will misinterpret the rigour.

## Major issues

### M1 — Abstract's "446 Pollice ADC(2)/cc-pVDZ labels" disagrees with the canonical pipeline (465)

- **Section / line context:** Abstract (line 26: "uses 446 source-domain
  ADC(2)/cc-pVDZ labels"), Introduction (line 39: "446→33 source-to-target
  transfer setting"), Fig 0 caption (line 46), Methods §2.2 (line 68),
  Methods §2.4 (line 78). Five occurrences total.
- **Issue:** `canonical_metrics.json` reports
  `library.n_invest_labeled = 465`, derived in `scripts/99_emit_canonical.py`
  as `int(master["adc2_dest_ev"].notna().sum())` over
  `data/processed/master_molecule_table.csv`. The paper's 446 has no
  matching value in any canonical source (audit lists it as the first
  unresolved number, ×5).
- **Why Major (not Minor):** the size of the source-domain training set is
  the load-bearing claim of the entire transfer-learning narrative; if the
  number is wrong by ~4%, every "446 → 33" framing is wrong by the same
  margin. A reviewer who recomputes from the data files will land on 465 and
  flag the entire pipeline as not reproducible.
- **Suggested fix:** investigate first. Three plausible truths exist —
  (a) 446 is a stale value from an earlier table version, (b) 446 is the
  filtered subset (e.g., after de-duplication or after dropping molecules
  with NaN features) and 465 is the raw count, (c) one of the two pipeline
  branches has a logic bug. The reconciliation must be done against
  `data/processed/master_molecule_table.csv` directly (count
  `adc2_dest_ev.notna() & scaffold_family != 'this_work'`, vs. with/without
  duplicate `mol_id`, vs. with/without `is_invest`), and either the paper or
  the canonical script must be updated. Until then the abstract is unsafe.
- **Source files:** `data/processed/master_molecule_table.csv`,
  `scripts/99_emit_canonical.py` (line 93), `scripts/build_master_table.py`.

### M2 — Post-HF Methods do not state the geometry source, SCS parameters, or any SOC/RISC information

- **Section / line context:** §2.3 "Post-Hartree–Fock Validation" (line 72,
  three sentences only).
- **Issue (M6 of comp-chem-method-reviewer):** §2.1 states GFN2-xTB
  optimisation in implicit toluene for the low-level screen, but §2.3
  introduces ADC(2)/def2-SVP single points without stating *which*
  geometries those single points were performed on. A referee cannot tell
  whether the post-HF labels came from GFN2-xTB geometries (carried over
  from §2.1) or from re-optimised DFT geometries.
- **Issue (M5 of comp-chem-method-reviewer):** "SCS-CC2" appears in the
  abstract, §2.3, §4.4, §4.5, Fig 4 caption, and Conclusions, but the SCS
  parameters (default *c*<sub>os</sub> = 1.2, *c*<sub>ss</sub> = 0.33) are
  never specified. A reviewer cannot reproduce the numbers without that.
- **Issue (M3 of comp-chem-method-reviewer):** the title and abstract frame
  the work as INVEST discovery for materials design, yet the manuscript
  contains no SOC, spin-orbit, ISC, or RISC mention. Per the M3 rule, an
  INVEST candidate intended for emitter contexts must either supply
  SOC/RISC evidence or carry an explicit disclaimer ("RISC kinetics not
  assessed"). The paper carefully avoids the phrase "OLED emitter" but
  still inherits the implicit promise via the title.
- **Why Major:** these three omissions together prevent independent
  reproduction of any single ΔEST value reported in Table 1 and prevent the
  reader from judging whether the negative-gap classifications are
  emitter-relevant or merely electronic-structure curiosities.
- **Suggested fix:** add three sentences to §2.3: (a) name the geometry
  source for ADC(2) and SCS-CC2 single points; (b) state the SCS
  coefficients used (or "Turbomole defaults *c*<sub>os</sub> = 1.2,
  *c*<sub>ss</sub> = 0.33"); (c) add the M3 disclaimer "SOC and RISC rates
  are not assessed in this work; INVEST classifications are reported as
  electronic-structure assignments rather than as predicted emitter
  performance".
- **Source files:** `paper/main.tex` §2.3.

### M3 — Hz_POZ1_NPh21_CF31 has |ΔEST(SVP)| = 9.7 meV but only a method-substitute, not a basis-set sweep, is offered

- **Section / line context:** §4.5 (line 150: "borderline by ADC(2)
  (−9.7 meV) but negative by SCS-CC2 (−165.6 meV), so its final
  classification relies on the higher-level cross-check"), and Table 1
  ("Low" confidence, "ADC(2) + SCS-CC2" evidence column).
- **Issue (M1 of comp-chem-method-reviewer):** the rule says any molecule
  with |ΔEST| < 100 meV at any level must receive a **second-basis** check
  (e.g., def2-SVP → def2-TZVP). 9.7 meV is well inside that window. The
  manuscript substitutes a different correlation method (SCS-CC2, same
  def2-SVP basis) for what the rule demands as a basis-set sweep. The two
  do not measure the same thing — a method swap probes correlation
  treatment, not basis convergence.
- **Why Major:** Hz_POZ1_NPh21_CF31 is one of 13 negative-gap classifications
  carrying the abstract's INVEST claim, and its sign in the decision table
  rests on a single SCS-CC2/def2-SVP number. If def2-TZVP at ADC(2) (or
  CC2) flipped the sign, the corresponding Table 1 row would have to
  downgrade.
- **Suggested fix:** either (a) compute ADC(2)/def2-TZVP (or larger) for
  Hz_POZ1_NPh21_CF31 and report both, or (b) state explicitly in §4.5 and
  Table 1 footnote: "Basis-set sensitivity not yet assessed; classification
  is provisional pending TZVP-level verification." The current Table 1
  "Low" confidence flag is the right direction but does not by itself meet
  M1.
- **Source files:** `results/validated_candidates_master.csv` row for
  Hz_POZ1_NPh21_CF31 (`DEST_adc2_eV = -0.00971`, `DEST_scscc2_eV = -0.16557`);
  `canonical_metrics.method_crosscheck.candidate_scscc2_crosschecks`.

### M4 — Abstract numerical claims lack the qualifiers that the Results section supplies

- **Section / line context:** Abstract (line 26).
- **Issue (R1, R3, R4 of stats-rigor-reviewer):**
  - "78.8% sign accuracy" — no *n* stated. R3 / R-default rule: every
    accuracy point estimate must carry its *n*. The Abstract should read
    "78.8% sign accuracy (n = 33, post-round-1 LOO-CV, excl. Hz_NH23)".
  - "35.7% empirical coverage at the 95% nominal level" — no Wilson CI.
    The Fig 2 caption (line 127) gives the binomial 95% Wilson CI as
    [16.3%, 61.2%]. With *n* = 14 (< 30), R4 makes the CI mandatory
    *wherever* the point estimate appears, including the Abstract.
  - "Round-1 acquisition identifies 7 negative-gap molecules among 15
    queries" — no baseline context. §4.4 correctly notes that the baseline
    *p*-values are 1.0 / 1.0 / 0.999 / 0.971; an Abstract-only reader will
    not know that and will read 7/15 as a hit-rate advantage.
  - "Fisher exact *p* value of 0.015" — already flagged by audit M6 for
    missing the descriptive qualifier; per R1 of stats-rigor-reviewer, this
    is non-negotiable for an actively selected cohort and must be repeated
    in the Abstract, not only in §4.4.
- **Why Major:** this is the only paragraph of the paper that many readers
  will see; it currently advertises four small-sample point estimates as if
  they were settled. The body text is appropriately careful — that
  carefulness must propagate to the Abstract.
- **Suggested fix:** rewrite the four numerical clauses in the abstract to
  carry *n*, CI, baseline reference, and "descriptive" qualifier
  respectively. Concrete wording is suggested per item in
  `reviews/author_response_consistency.md` (if present) or can be drafted
  on request.
- **Source files:** `figures/caption_data/Fig2_uq_shift.json`
  (`conformal_90_wilson_95_ci`); `canonical_metrics.active_learning.baseline_comparisons`;
  `canonical_metrics.active_learning.fisher_full_cohort.note`.

### M5 — Ablation paired-test framing: "deterministic" is stated, but the inferential consequence is not

- **Section / line context:** §3.2 (line 109) "numerically identical across
  all 10 nominal random seeds because the implemented LOO-CV workflow is
  effectively deterministic for this dataset", and §4 (line 179) "the
  effect is best described as a reproducible numerical preference for the
  RDKit-only model rather than as a conventionally powered significance
  statement".
- **Issue (R2 of stats-rigor-reviewer):**
  `canonical_metrics.ablation.paired_tests` records `p_value: null,
  significant_005: null` for `no_ksod`, `no_stda_no_ksod`, `no_dft`, and
  `rdkit_only` — "Wilcoxon not applicable (n_eff = 1)". The only
  comparison with a reportable *p* is `full vs no_stda` at *p* = 1.0
  (identical). The paper says the workflow is deterministic but does not
  say what that *implies for inference*: with n_eff = 1, a single observed
  difference is consistent with any underlying effect size and any sign
  flip on a different test molecule could overturn the ranking.
- **Why Major:** §3.2 still presents an ordering of MAEs ("RDKit-only gives
  the lowest MAE among the non-redundant feature sets") and Fig 1 visually
  reinforces it. With no power statement, a referee will read this as a
  weak version of the over-claimed feature-importance bar charts that the
  literature already over-uses.
- **Suggested fix:** add one sentence to §3.2: "Because LOO-CV residuals
  are identical across seeds (paired Wilcoxon n<sub>eff</sub> = 1), the
  observed config ordering is a single realisation rather than a
  statistically resolved effect; we report it as a numerical inventory."
  Then reframe Fig 1 as such (the caption can stay numeric; the body
  prose should not say "ordering reflects the data split itself").
- **Source files:** `canonical_metrics.ablation.paired_tests`;
  `figures/caption_data/Fig1_ablation.json` (already encodes
  "deterministic" caveat in its `visualization_caveats`).

## Minor issues

### m1 — RI-ADC(2) vs ADC(2) labelling ambiguity

- Abstract (line 26) says "446 source-domain ADC(2)/cc-pVDZ labels" but
  "33-molecule RI-ADC(2)/def2-SVP target set"; §2.4 (line 78) says "446
  Pollice molecules" without RI. M5 of comp-chem-method-reviewer requires
  one consistent label. Either the source labels also used RI (then write
  "RI-ADC(2)/cc-pVDZ"), or they did not (then state the difference
  explicitly in §2.2).

### m2 — Conformal width "53 meV" vs canonical "53.4 meV" (rounding)

- Abstract and Fig 2 caption both write `\SI{53}{meV}`. Canonical
  `uncertainty.conformal_95_width_eV = 0.0533550021` → 53.4 meV. The
  rounding to "53" is harmless but not consistent with the paper's own
  three-decimal MAE numbers (52.1, 54.9, 66.9). Either round all
  uncertainty widths to one decimal (53.4 meV, 324.0 meV, 320.0 meV) or
  document the rounding rule once in §2.5.

### m3 — One-sided vs two-sided permutation direction

- §3.4 (line 135) reports "one-sided permutation *p* values are 1.0, 1.0,
  0.999, and 0.971". The direction of "one-sided" should be stated
  explicitly ("one-sided test of AL > baseline expected hit count"); a
  reader who only sees the abstract may otherwise assume a two-sided
  test was used.

### m4 — Fig 6 caption does not say whether the panel is filtered or shows the full library

- Line 62. The corresponding `figures/caption_data/Fig6_library.json`
  enforces the rule "All 155 target-domain molecules are included; no
  fosc / energy / scaffold filter is applied to this panel." The caption
  in the manuscript should mirror that line so the reader does not assume
  a screening filter was applied.

### m5 — "INVEST" is used in the title and abstract without expansion

- Acceptable for a journal whose readership knows the term, but a single
  parenthetical at first occurrence ("inverted singlet–triplet gap,
  INVEST") in the title-aware abstract opening sentence would help broader
  audiences. The abstract already does this in the third clause; consider
  moving it earlier.

### m6 — Hz_NH23 SCS-CC2 value (−558 meV) appears only in §4.5 prose

- Line 170 ("−558 meV by SCS-CC2"), but no entry exists in
  `canonical_metrics.method_crosscheck.candidate_scscc2_crosschecks`
  pointing to that specific number (the Hz_NH23 row has SCSCC2_eV =
  −0.55787 = −557.87 meV, which the prose rounds to −558). The audit lists
  this as one of the four unresolved per-molecule values; the right fix is
  to expose `candidate_details[i].scscc2_meV` in canonical so the audit
  can match.

## Strong points

The paper does several things noticeably better than the typical
INVEST/transfer-learning manuscript:

1. **Honest acknowledgement of model limits.** §3.1, §4 (Scope), and the
   Conclusions all repeat that the post-round LOO-CV MAE of 52.1 meV
   exceeds the 30 meV borderline classification window, and explicitly
   restrict the model's role to "scaffold-level prioritization and coarse
   within-domain correction, not for confident near-threshold candidate-
   level classification". Most papers in this area silently elide this
   comparison.

2. **Active learning is *not* claimed to beat baselines.** §3.4 reports
   the four baseline *p* values (1.0, 1.0, 0.999, 0.971) and reframes AL
   as a scaffold-resolution device. This is exactly the R3 reframe the
   stats-rigor-reviewer skill prescribes when AL fails to beat random
   selection.

3. **Single source-of-truth instrumentation.** `canonical_metrics.json`
   plus per-figure `caption_data/*.json` plus the audit pipeline in
   `paper/audit_reports/` give 95% number traceability (audit). The
   underlying engineering is rare and reviewer-friendly.

4. **Explicit Hz_NH23 inclusion/exclusion rule.** §2.2 names the 7/15 vs
   6/14 distinction in the same sentence ("the 14-molecule subset is used
   only for Fisher exact tests and conformal benchmarking and must not be
   used as the deployment denominator"). The Fig 5 caption also enforces
   the rule. This is the strongest version of the analysis-set
   reconciliation that I have seen in a closed-loop screening manuscript.

5. **Conformal vs bootstrap UQ honesty.** §3.3 frames the contrast
   correctly: conformal 35.7% << nominal 95% under acquisition shift,
   bootstrap 100% only at widths comparable to the 320 meV fixed baseline.
   The prose explicitly says "bootstrap intervals are too diffuse to
   prioritize near-threshold candidates efficiently" — the right
   statement, given R4.

6. **Forbidden-vocabulary discipline.** The AGENTS.md rule-8 banned terms
   ("verified", "robust", "significant", "high-confidence", "OLED emitter",
   "multi-level verification") do not appear in the body text. The single
   "multi-level validation" phrase in Fig 0 caption is an explicit *negative*
   disclaimer ("do not constitute multi-level validation of the full
   candidate set"). See the Forbidden-phrases scan below.

## Open questions for the authors

1. **What geometries underlie the post-HF single points?** §2.3 does not
   say. If they are GFN2-xTB geometries inherited from §2.1, please state
   that explicitly. If DFT-optimised at a different functional, please
   name it.
2. **Did the Pollice 446/465 source labels use the RI approximation?**
   Resolving this fixes both M1 (number) and m1 (label).
3. **Was Hz_POZ1_NPh21_CF31 (|ΔEST(SVP)| = 9.7 meV) also evaluated at
   def2-TZVP?** If yes, the value should appear in
   `canonical_metrics.method_consistency_benchmark.basis_set_coverage`. If
   no, please state "not yet assessed" in §4.5 and Table 1 footnote.
4. **Were SOC matrix elements or RISC rates computed for any of the 13
   negative-gap candidates?** If not, please add the §2.3 disclaimer
   suggested in M2.
5. **What SCS parameters define "SCS-CC2" here** — Turbomole defaults, or
   a custom set? §2.3 must state this.
6. **Hz_NH23's SCS-CC2 value of −558 meV** — please surface the full
   per-molecule SCS-CC2 values into `canonical_metrics.json` so each
   number in §4.5 can be audit-traced (audit currently lists 9.7, 165.6,
   383, 558 meV as unresolved).

## Forbidden phrases scan

Per AGENTS.md rule 8, the following terms must not appear in non-audit-
supported contexts. Scan command:
`grep -niE 'verified|validated|significant|robust|high.confidence|OLED|emitter|multi.level' paper/main.tex`.

| Term | Occurrences | Compliant? | Notes |
|------|-------------|------------|-------|
| `verified` | 0 (word-level) | ✅ | The closely related "validated" appears extensively but always as a structural adjective for the post-HF labelled set. |
| `validated` | many | ⚠ context-OK | Always paired with "set", "cohort", "candidates", "decision table", or "table"; never used as a quality grade for a single molecule. Acceptable. |
| `robust` | 0 | ✅ | Clean. |
| `significant` / `significantly` | 0 | ✅ | Even §3.4 (the natural place for "significant") avoids the word; uses "comparable hit counts" and explicit *p* values. |
| `high-confidence` / `high confidence` | 0 | ✅ | Clean. |
| `OLED emitter` | 0 | ✅ | The title says "INVEST … Discovery", which inherits an emitter implication; M2 above asks for a SOC/RISC disclaimer to neutralise that. |
| `emitter` (any) | 0 | ✅ | Clean. |
| `multi-level verification` | 0 | ✅ | The single "multi-level validation" mention (Fig 0 caption, line 46) is an explicit negative disclaimer. Compliant. |

**Conclusion:** the rule-8 vocabulary scan passes. The only structural
caveat is that "validated" is load-bearing throughout the manuscript; if
the journal style guide treats "validated" as equivalent to "verified",
the same M2 / M3 (comp-chem-method-reviewer) requirements apply to every
"validated candidate" claim — which would re-trigger the geometry,
SCS-parameters, and SOC/RISC gaps already flagged in M2.

---

## File audit

- Read-only inputs consulted: `paper/main.tex`,
  `results/canonical_metrics.json`, `figures/caption_data/*.json`,
  `paper/audit_reports/consistency_audit.md`,
  `paper/audit_reports/fig5_reconciliation.md`,
  `results/validated_candidates_master.csv`, `AGENTS.md`, `CLAUDE.md`.
- Files written: `reviews/claude_review.md` (this file).
- Files modified: none. `paper/main.tex` not touched.
