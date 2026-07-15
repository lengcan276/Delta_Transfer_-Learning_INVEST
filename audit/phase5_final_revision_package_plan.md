# Phase 5 Step 8 — Final revision package outline

## Patch set A — Safe wording fixes (APPLY_NOW_SAFE, 18 edits)

**Contents:**
1. n=4 stale → n=13 ADC(2)-screened wording (13 original Phase 3.6 edits):
   - `paper/main.tex` lines 46, 155, 170 (3 edits) + mirror in `paper_overleaf/main.tex` (3 edits)
   - `figures/caption_data/Fig0_workflow.json` lines 44, 47 (2 edits)
   - `figures/caption_data/Fig4_crosscheck.json` lines 85, 86, 90 (3 edits)
   - `results/Table1_invest_candidates.tex` line 3 + mirror (2 edits)
   - `reviews/cover_letter.md` line 21 (1 edit)
2. "Bit-identical" rewording (Phase 5 Issue C, 2 paper files × 2 occurrences = 4 edits):
   - `paper/main.tex` line 74 + line 150 + mirrors → "parser-recovered to the printed precision (within 0.1 meV)"
3. Hz_POZ1_NPh21_CF31 wording strengthening (Phase 5 Issue A):
   - Add explicit "basis confirmed from ricc2 runtime banner; control file not preserved" to existing low-evidence caveat
4. Scheduler evidence caveat (Phase 5 Step 6):
   - Add one sentence: "scheduler provenance is runtime-banner-supported rather than scheduler-log-confirmed"
5. ADC(2) Data Availability caveat (Phase 5 Step 5):
   - New Data Availability paragraph listing 20 ADC(2) raw outputs verified locally + 15 raw outputs on ybsi pending retrieval

**Apply method:** unified diff already prepared in
`audit/phase3_6_recommended_patch.diff` for items 1; items 2-5 need
appending to that patch or applying separately. Both options leave
the diff inspectable before any commit.

**Estimated post-apply audit re-run cost:**
- `scripts/audit_numbers.py` — should re-pass with `unresolved=0,
  Major=0/7`. May need to add new caveat-text patterns to mitigation
  rules.
- Phase 4 verifier — already passes; not affected by text edits.

---

## Patch set B — Generator refactor (APPLY_AFTER_GENERATOR_REFACTOR, 5 items)

**Goal:** make `scs_cc2_extended_n13` block in
`results/canonical_metrics.json` reproducible from raw outputs without
the manual JSON-patch step that was logged in session.md.

**Required script changes (all in `scripts/scscc2_extension/build_cross_check_n13.py`):**

1. Replace hard-coded `ci_method = "Clopper-Pearson exact two-sided 95%"`
   with:
   ```
   ci_method = "rule of three (one-sided 95% upper bound on within-screen sign-disagreement rate; the 13 molecules are an ADC(2)-pre-screened cohort, not an i.i.d. random sample)"
   ```
   (and emit both `clopper_pearson_95_CI` AND
   `rule_of_three_upper_bound_disagreement_rate` for traceability)

2. Add `paper_cited_scope = "screened-cohort sign agreement, not population CI"`
   field next to `paper_cited_signrate`.

3. Add `paper_cited_bound = "rule of three; one-sided 95% upper bound ≈ 3/13 = 0.23"`
   field next to `paper_cited_CI`.

4. For per-molecule `Hz_NPh21_Cz2` entry, ADD:
   ```
   "narrowest_margin_warning": "smallest |ΔΔE_ST| in n=13 cohort (10.1 meV processed; 9.64 meV raw-vs-raw); most likely sign-flip candidate under further method change"
   ```

5. For per-molecule `Hz_POZ1_NPh21_CF31` entry, ADD:
   ```
   "borderline_low_evidence_warning": "ADC(2)/def2-SVP value (|ΔE_ST|=9.7 meV) inside ±30 meV near-zero window; SCS-CC2 promotion to negative-gap should retain low evidence strength until basis-set sensitivity (def2-TZVP) or method-family triangulation (CCSD/CC3/NEVPT2) is performed; main and auxiliary basis confirmed as def2-SVP from ricc2 runtime banner (control file not preserved in historical batch)"
   ```

**Then re-run:**
```
python3 scripts/scscc2_extension/build_cross_check_n13.py
```
…and **add a second helper** (`scripts/scscc2_extension/patch_canonical_with_scs_cc2_extended_n13.py`)
that programmatically merges the regenerated `stats_n13.json` into
`canonical_metrics.json` under the `scs_cc2_extended_n13` key —
replacing the previously-manual JSON patch step.

After Patch set B, the Phase 2 audit should report
**REGENERATION_EXACT_MATCH** (current is REGENERATION_PARTIAL_BUT_EXPECTED).

---

## Patch set C — Data archive / provenance (action items, not text edits)

0. **Update repository identity to INVEST-n13 where needed.**
   Canonical repo: `https://github.com/lengcan276/INVEST-n13`.
   Legacy/wrong: `https://github.com/lengcan276/FedSchNet-ReorgEnergy`
   (OLD_REPO_REFERENCE_TO_REWRITE_LATER). Actions:
   - Remove the `fed_old` git remote (`git remote remove fed_old`).
     Only the `invest` remote should be retained.
   - Add `README.md` (or update existing) inside `release_n13/`
     declaring the canonical repo URL.
   - Ensure any future `CITATION.cff` / `CHANGELOG` / DOI deposit
     metadata references INVEST-n13, never FedSchNet-ReorgEnergy.
   - Optional: prepend the three `session.md` copies under
     `audit/` and `audit/_tmp_*/` with a one-line clarifying header
     noting that any FedSchNet string is historical log content
     and the canonical repo is INVEST-n13.
   See `audit/phase5_repository_identity.md` for the full inventory
   (3 session.md files with FedSchNet hits; 0 hits in
   paper/results/figures/scripts/reviews).

1. **Archive local SCS-CC2 raw outputs into the release artifact.**
   Currently the release_n13 repo ships processed CSVs only; the 26
   raw `ricc2_scscc2_*.out` files live at
   `/home/nudt_cleng/2026/results/scscc2_extension_n13/Hz_*/turbo_*_scscc2_svp/`
   and at `/home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_*/turbo_*_scscc2/`.
   Recommended: bundle into a separate `release_n13_raw_archive/` tarball
   alongside the release, with sha256 manifest. (Adding raw outputs
   directly into release_n13/ would inflate the repo from ~21 MB to
   ~hundreds of MB; tarball deposit is cleaner.)

2. **Retrieve missing 15 ADC(2) raw outputs from ybsi cluster.** Path:
   `/public/home/ybsi/nudt_cleng/2026/round1_adc2/jobs/` (per phase
   reports). After retrieval, rsync to a local mirror (NOT into
   release_n13/), include in same tarball as item 1, re-run Phase 4
   verifier. If sucessful, the Phase 4 status upgrades to
   `RAW_PROVENANCE_FULL`.

3. **Add `audit/` and `scripts/audit/` to release_n13.** After
   user-acceptance of audit reports, commit the audit tree into the
   release as immutable evidence. This makes the audit reproducible
   by downstream reviewers without requiring access to ybsi.

4. **Add Data Availability section to manuscript** documenting the
   above structure. Suggested:
   > "Data availability — Raw Turbomole ricc2 output files for
   > SCS-CC2/def2-SVP cross-checks (n=13, sing + trip = 26 files) are
   > deposited at <archive URL/DOI>. Raw outputs for ADC(2)/def2-SVP
   > (35 molecules, sing + trip = 70 files) are partial in the
   > present archive: 20 files (5+15 historical batches) are
   > locally raw-verified at machine precision; 15 R1-deploy-batch
   > ADC(2) raw outputs were computed on the ybsi cluster
   > (/public/home/ybsi/nudt_cleng/2026/round1_adc2/jobs/) and will be
   > added to the archive in a subsequent release. The processed
   > validation tables (`validated_candidates_master.csv`,
   > `cross_check_n13.csv`) plus all 5 phase-audit reports
   > (`audit/phase{0..5}_*.md`) are included in this release."

---

## Patch set D — Manuscript scientific caveats (mostly already in body)

These are the high-level scientific claims that must be present in
the manuscript. Most are already in §3.5 / §5 / §6 from prior phases;
this list confirms each is supported by Phase 4/5 evidence.

| caveat | status | location | Phase 5 backing |
|---|---|---|---|
| Correct project repository identity: `https://github.com/lengcan276/INVEST-n13` (NOT FedSchNet-ReorgEnergy) | ✗ MISSING | new — add to Data Availability / Acknowledgements / footnote | Phase 5 Step 9 (`phase5_repository_identity.md`) |
| SCS-CC2 n=13 raw-verified sign agreement | ✓ present | Abstract / §3.5 / §6 | Phase 4 confirms 13/13 raw |
| ADC(2) partial raw provenance | ✗ MISSING | new — add to §5 or Data Availability | Phase 5 Step 5 |
| Scheduler evidence runtime-banner-supported | ✗ MISSING | new — add to Methods or Data Availability | Phase 5 Step 6 |
| No method-independent ranking | ✓ present | §3.5 cont / §5 / §6 | Phase 3.5 framing |
| POZ1 low-evidence caveat | ✓ present (needs strengthening for banner-source basis) | §3.5 / §5 | Phase 5 Issue A |
| Cz2 narrowest-margin caveat | ✓ present | §3.5 / §5 | Phase 5 Issue B |
| No "bit-identical" unless raw sha256 identical | ✗ MISSING (rewording needed) | §3.5 / §3.5cont | Phase 5 Issue C |
| ADC(2) rounding-only precision | not needed | (no manuscript impact) | Phase 5 Step 5.5 |

---

## Recommended apply order

1. **Patch set A** first (text rewrites; no dependencies). Re-run audit_numbers.py.
2. **Patch set C item 1+2** (raw archive + ybsi retrieval). After C2, Phase 4 verifier re-run.
3. **Patch set B** (generator refactor). After B, Phase 2 regeneration test re-run; should now be REGENERATION_EXACT_MATCH.
4. **Patch set C item 3** (commit audit/ into release). After A/B/C1-2 land.
5. **Final commit + DOI mint + journal submission.**

## Total effort estimate

- Patch set A: ~2 h author time (text edits + audit re-run)
- Patch set B: ~4 h author time (generator refactor + JSON patcher + re-test)
- Patch set C: variable — depends on ybsi access + archive size
  - C0 (repo identity: remove fed_old remote + add canonical URL to README): ~15 min
  - C1 (local tarball): ~1 h
  - C2 (ybsi retrieval): depends on network/access
  - C3 (audit commit): 15 min
  - C4 (Data Availability text): 30 min
- Patch set D: subsumed by A/C above
