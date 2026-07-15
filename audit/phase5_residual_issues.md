# Phase 5 — Residual Issue Audit Final Checkpoint

Audit phase: Phase 5
Repository HEAD: `3a72bc9`
Date: 2026-05-20
Phase 3.6 patch: STILL NOT APPLIED (live repo unchanged)

---

## Phase 5 Status

**PASS_READY_FOR_REVISION_MODE**

Reasoning:
- SCS-CC2 n=13 raw verification stands (Phase 4: RAW_PROVENANCE_FULL
  for the SCS-CC2 cohort).
- No value/method/basis mismatch in any manuscript-critical SCS-CC2
  claim (Phase 5 cross-check on POZ1 + Cz2 in particular).
- POZ1: no unresolved method/basis conflict. Basis confirmed as
  def2-SVP from ricc2 runtime banner; existing low-evidence caveat
  needs minor strengthening but no main claim collapses.
- Cz2: narrowest-margin claim is raw-supported. New-batch with
  preserved control + 3-group basis audit clean.
- ADC(2) rounding-only cases: 0 PRECISION_TOO_TIGHT — no manuscript
  number change required.
- Scheduler evidence properly classified as runtime-banner-supported,
  not Slurm-log-confirmed. Caveat wording must be added (Patch set A
  item 4).
- ADC(2) missing raw caveat documented but not fatal — paper can
  proceed with a Data Availability paragraph; ideally raw files
  rsynced from ybsi before final archive.
- Repository identity corrected in final revision plan as
  **INVEST-n13** (`https://github.com/lengcan276/INVEST-n13`). The
  earlier FedSchNet-ReorgEnergy push location is classified as
  OLD_REPO_REFERENCE_TO_REWRITE_LATER. No FedSchNet contamination
  in paper/results/figures/scripts/reviews; remediation is metadata
  (remove `fed_old` git remote) + additive (add canonical URL to
  README/Data Availability). See Patch set C item 0 and Patch set D.

Note: this is `PASS_READY_FOR_REVISION_MODE`, not
`PASS_WITH_ADC2_RAW_CAVEAT`, because the ADC(2) missing raw is
addressable via a Data Availability paragraph that the audit has
already drafted (Patch set A item 5). The cohort of n=13 SCS-CC2 is
fully clean.

---

## Additional required conclusions

### POZ1 basis evidence tier

| | |
|---|---|
| Verdict | **A_RESOLVED_SVP** |
| Preserved control file | **No** (historical batch — typical) |
| $basis ($basis block) verified | **Yes**, banner-printed def2-SVP for all elements |
| $cbas verified | **Yes**, banner-printed def2-SVP for all elements |
| $jbas verified | **No** (lives in ridft output, not preserved) |
| Manuscript caveat needed | **Yes — low-evidence borderline-promotion wording** (already present in §3.5/§5; recommend strengthening with explicit "basis confirmed from ricc2 runtime banner, control not preserved" footnote) |

### Cz2 batch and margin evidence tier

| | |
|---|---|
| Verdict | **B_RESOLVED_NEW_BATCH** |
| SCS-CC2 batch | **9-new extension batch (Phase 2.4)** |
| ADC(2) batch | adc2_batch2_raw (historical batch2) |
| Preserved control file (SCS-CC2 side) | **Yes** |
| $basis / $jbas / $cbas (SCS-CC2 control) | **All three = def2-SVP** ✓ |
| Narrowest margin (processed) | 10.09 meV |
| Narrowest margin (raw-vs-raw) | **9.64 meV** (small rounding-induced difference; qualitative claim unchanged) |
| Manuscript caveat needed | **Yes** — narrowest-margin / sign-flip caveat (already present in §3.5/§5); optional footnote on 10.1 vs 9.6 precision |

### ADC(2) rounding-only audit

| | |
|---|---|
| Rounding-only cases | **8** (Hz_POZ1_Cz2, Hz_NPh21_POZ2, Hz_NH21_POZ2, Hz_NEt21_POZ2, Hz_POZ3, Hz_NHPh1_POZ2, Hz_POZ2_SO2Ph1, BCz3) |
| max |Δ| | 0.41 meV (Hz_NEt21_POZ2) |
| PRECISION_OK count | 1 (BCz3 — calibration-anchor classification use only) |
| PRECISION_TOO_TIGHT count | **0** |
| NOT_CITED_DIRECTLY count | 7 |
| NEEDS_MANUAL_REVIEW count | 0 |
| Manuscript number rounding correction recommended | **None** |

### Repository identity

| | |
|---|---|
| Verdict | **REPO_IDENTITY_CORRECTION_REQUIRED_BUT_LOW_BLAST_RADIUS** |
| Canonical repository | **`https://github.com/lengcan276/INVEST-n13`** |
| Legacy / wrong repository | `https://github.com/lengcan276/FedSchNet-ReorgEnergy` — **OLD_REPO_REFERENCE_TO_REWRITE_LATER** |
| FedSchNet hits in `paper/`, `results/`, `figures/`, `scripts/`, `reviews/`, `paper_overleaf/` | **0** |
| FedSchNet hits in repo overall | 3 files, all `session.md` copies (historical conversation log under repo root and `audit/_tmp_*/`) |
| INVEST-n13 references in tracked content | **0** — must be added during Patch set C/D |
| Git remote `fed_old` (FedSchNet) currently configured | **Yes** — should be removed |
| Git remote `invest` (INVEST-n13) currently configured | **Yes** ✓ |
| Manuscript text changes required | **Additive only** (no FedSchNet to delete from manuscript; add INVEST-n13 URL to Data Availability / Acknowledgements / README) |
| Detail report | `audit/phase5_repository_identity.md` |

### Scheduler evidence precision

| | |
|---|---|
| Label | **RUNTIME_BANNER_COMPUTE_NODE_SUPPORTED** |
| Tier (per audit rubric) | INFERRED |
| Compute-node hostname evidence | banner-confirmed (all 13: `nodeN` strings, never `master/login/head/submit`) |
| Slurm-log evidence | **NOT PRESERVED** in local audit snapshot |
| Login-node red-flag | **0/13** (no hostname pattern match) |
| Manuscript wording recommended | Add: "scheduler provenance is **runtime-banner-supported** rather than **scheduler-log-confirmed**" (Patch set A item 4) |

---

## Key conclusions

### SCS-CC2 n=13 raw provenance
**FULL.** 13/13 raw outputs locally verified end-to-end:
- method banner = CC2 + Spin-Component Scaling (Grimme factors)
- parsed ΔE_ST matches `cross_check_n13.csv` to <1×10⁻¹³ eV
- 10 dirs have preserved control → 3-group basis audit clean
- 4 historical dirs lack control → basis verified from runtime banner
- hostname compute-node verified across all 13 outputs

### ADC(2) 35-mol provenance
**PARTIAL.** Split into three groups:
- 12/35 fully verified (parsed-vs-claimed exact match)
- 8/35 rounding-only (claim 3dp, raw 5dp; max 0.41 meV diff; no
  PRECISION_TOO_TIGHT)
- 15/35 MISSING_RAW (R1-deploy batch, raw on ybsi cluster not rsynced)

### POZ1
A_RESOLVED_SVP. Banner-printed basis is direct raw evidence; control
file absence is documented; existing low-evidence borderline caveat
covers the chemical interpretation.

### Cz2
B_RESOLVED_NEW_BATCH. Both halves raw-verified. Narrowest-margin
claim raw-supported (processed 10.09 / raw 9.64 meV).

### "Bit-identical"
File-level sha256 disagrees for the Phase-1 sanity reproduction;
wording must change to "to the printed precision" or "within 0.1 meV".

### Scheduler evidence
Runtime-banner-supported on all 13 cohort molecules. Independent
Slurm log not preserved locally. No login-node red-flag.

### Repository identity
Canonical = `https://github.com/lengcan276/INVEST-n13`. FedSchNet-
ReorgEnergy is OLD_REPO_REFERENCE_TO_REWRITE_LATER. No FedSchNet
contamination in manuscript text; remediation is metadata-level
(remove `fed_old` git remote) plus additive (add canonical URL to
README / Data Availability / cover-letter). See Patch set C item 0
and Patch set D.

### Patch strategy
- **18 edits APPLY_NOW_SAFE** (13 original Phase 3.6 + 5 new from
  Phase 5).
- **5 edits APPLY_AFTER_GENERATOR_REFACTOR** (canonical_metrics.json
  + stats_n13.json metadata).
- **3 deferred-pending-user-decision** (generator refactor scope +
  ybsi retrieval + optional footnote).
- **2 DO_NOT_APPLY** (CSV precision change + legacy block removal).

---

## Allowed conclusion

The release_n13 manuscript is **ready for revision-mode work**. The
SCS-CC2 n=13 sign-retention claim has full raw-output provenance for
each of the 13 cohort members locally. The remaining manuscript
adjustments are bounded, well-scoped, and listed line-by-line in
`audit/phase5_patch_triage_after_raw_qc.md` and
`audit/phase5_final_revision_package_plan.md`. None of the residual
issues require new quantum-chemistry calculations or new statistical
analyses; all are wording / metadata / archive corrections.

The ADC(2) half is partially raw-verified. A Data Availability
paragraph documenting the 20-verified / 15-pending split brings the
manuscript into an honestly-disclosed state suitable for submission.

---

## Not allowed conclusion

> "This audit does not prove absence of fabrication in an absolute
> sense. It establishes traceability only for the local raw files and
> processed outputs available in the audited snapshot. The 15 ADC(2)
> R1-deploy raw outputs on the ybsi cluster were not audited locally.
> Future verifiability of those 15 ADC(2) entries depends on rsync
> from ybsi or equivalent archival before the cluster's raw data is
> rotated out."

---

## Hard-constraint compliance (Phase 5)

| Constraint | Status |
|---|---|
| No file under `paper/`, `results/`, `data/`, `figures/`, `reviews/`, pre-existing `scripts/` modified | ✓ |
| All audit outputs to `audit/`, all audit scripts to `scripts/audit/` | ✓ |
| No git add/commit/push/rebase/config | ✓ |
| No network access | ✓ |
| Did not apply Phase 3.6 patch | ✓ |
| Did not enter manuscript rewrite mode | ✓ |
| Did not run any quantum-chemistry calculation | ✓ |
| Did not modify any raw QC file | ✓ |
| Did not treat session.md as evidence | ✓ |

---

## Deliverables this phase

```
audit/phase5_issue_A_POZ1_resolution.md         A_RESOLVED_SVP
audit/phase5_issue_B_NPh21_Cz2_resolution.md    B_RESOLVED_NEW_BATCH
audit/phase5_issue_C_bit_identical_resolution.md  REWRITE_REQUIRED
audit/phase5_adc2_missing_raw_caveat.md         15 mol on ybsi; 7 in n=13
audit/phase5_adc2_rounding_only_audit.md        0 PRECISION_TOO_TIGHT
audit/phase5_scheduler_evidence_caveat.md       RUNTIME_BANNER_COMPUTE_NODE_SUPPORTED
audit/phase5_patch_triage_after_raw_qc.md       18 APPLY_NOW_SAFE + 5 generator-refactor
audit/phase5_final_revision_package_plan.md     Patch sets A/B/C/D (C0 = repo identity)
audit/phase5_repository_identity.md             Canonical = INVEST-n13; FedSchNet = OLD_REPO_REFERENCE_TO_REWRITE_LATER
audit/phase5_residual_issues.md                 (this file)
```

**Phase 5: COMPLETE.** Halting. Awaiting user decision on whether to
enter revision mode (apply Patch set A) or refactor generator first
(Patch set B) or retrieve ybsi raw files first (Patch set C).
