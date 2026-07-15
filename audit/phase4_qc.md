# Phase 4 — Quantum-Chemistry Raw-Output Provenance Checkpoint

Audit phase: Phase 4 (revised spec — see `audit/phase4_spec.md`)
Repository HEAD: `3a72bc9`
Date: 2026-05-20
Phase 3.6 patch: STILL NOT APPLIED (live repo unchanged)

---

## Phase 4 Status

**RAW_PROVENANCE_PARTIAL_n13** (with strong sub-finding:
**SCS-CC2 n=13 cohort = FULLY RAW-VERIFIED**)

### Sub-status by cohort

| cohort | status | rationale |
|---|---|---|
| **SCS-CC2 (n=13)** | **RAW_PROVENANCE_FULL** | 13/13 raw outputs found, all method-banner-verified as SCS-CC2 (CC2 + Spin-Component Scaling, C_os=1.2, C_ss=0.333), all parsed ΔE_ST match processed-table values to <1e-13 eV (effectively bit-identical on the printed `Energy:` lines), all hostnames in output banner show compute nodes (`node1`/`node6`/`node11`/etc.) |
| ADC(2) (full 35-mol set) | RAW_PROVENANCE_PARTIAL | 12/35 OK; 8/35 are rounding-only (claimed rounded to 3 dp, raw is 5 dp, all diffs ≤ 0.41 meV); 15/35 raw missing on qfh-u24 (live on ybsi cluster, beyond audit's no-network reach) |

### What this means for the paper

- **The Phase 3.5/3.6 framing — "0 sign disagreement in 13/13
  ADC(2)-screened cohort under SCS-CC2 cross-check" — is now
  raw-verified for the SCS-CC2 half.** Each of the 13 SCS-CC2 ΔE_ST
  values reported in the paper is independently reproducible from a
  local `ricc2_scscc2_*.out` file with the correct method banner and
  the standard Grimme SCS scaling.

- **The ADC(2) half is partially raw-verified.** 6 of the 13 cohort
  molecules have ADC(2) raw verified locally; the remaining 7 have
  ADC(2) raw on the ybsi cluster (R1-deploy batch) and are
  documented-but-unverified in this audit. The numbers themselves
  are consistent with the processed CSVs, but the raw-file evidence
  cannot be confirmed offline.

- **No quantitative claim collapses.** Per the Phase 3.5 framing, the
  paper reports 0 sign disagreement within a pre-screened cohort
  (descriptive), not a population CI. Sign agreement requires both
  ADC(2) sign and SCS-CC2 sign to be negative; the SCS-CC2 sign is
  raw-verified for all 13, and the ADC(2) sign is locally raw-verified
  for 6/13 + processed-CSV-consistent for the remaining 7/13.

## Per-question answers

### Is every ADC(2) label in `validated_candidates_master.csv` raw-traceable?
**Partial — 12/35 fully OK, 8/35 OK except for rounding-precision
artefacts, 15/35 missing on qfh-u24 (live on ybsi).**

### Is every SCS-CC2 label in `cross_check_n13.csv` raw-traceable?
**Yes — 13/13 OK, all method-banner verified as SCS-CC2 with standard
Grimme scaling, all ΔE_ST match to <1e-13 eV.**

### Is ΔE_ST = S1 − T1 reproduced correctly?
**Yes for SCS-CC2 13/13.** Yes for ADC(2) 12/35 (and yes-to-rounding
for 8/35 more, no for 15/35 missing).

### Method mismatch?
**No.** Every SCS-CC2 output passes the strict method-banner check
(CC2 declaration + SCS banner + standard factors). No ADC(2) output
checked was found to contain SCS markers.

### Basis mismatch?
**No mismatch detected** where audit could check. For Phase-2 SCS-CC2
dirs with `control` file preserved (10 of the 13 — see Step 6 in
`qc_provenance_summary.md`), all three basis groups (`$basis` /
`$jbas` / `$cbas`) match `def2-SVP` on every element. For historical
SCS-CC2 dirs (4 of the 13), no `control` file was preserved — basis
audit relies on the method banner alone and cannot independently
confirm.

### Scheduler evidence?
**Tier = INFERRED** for all 13 (compute-node hostname inferred from
ricc2.out program banner; no slurm-*.out files locally available). The
inference is reasonable (banners show `nodeN` strings, not `master`)
but is weaker than FULL slurm-log evidence.

### Can we now claim "quantum-chemical labels are calculation-derived"?
**Conditional yes for SCS-CC2 13/13** — each label is reproduced
end-to-end from a real Turbomole ricc2 output with the correct method
banner and standard SCS factors. **Partial yes for ADC(2)** — 12/35
fully verified, 8/35 verified-modulo-rounding, 15/35 unverified
locally (raw on ybsi).

## Hard-constraint compliance (Phase 4)

| Constraint | Status |
|---|---|
| No file under `paper/`, `results/`, `data/`, `figures/`, `reviews/`, pre-existing `scripts/` modified | ✓ |
| All audit outputs to `audit/`, all audit scripts to `scripts/audit/` | ✓ |
| No git add/commit/push/rebase/config | ✓ |
| No ssh/rsync/scp/curl/wget; no network access | ✓ |
| Did not copy raw QC files from parent project into release_n13 | ✓ (only read them in place, recorded sha256) |
| Did not modify any raw QC file | ✓ |
| Did not treat session.md as evidence | ✓ |
| Phase 3.6 patch remains UNAPPLIED | ✓ |
| Used independent parsers (not project's parse_scscc2_dest.py) | ✓ — `scripts/audit/parse_adc2_dest_audit.py` and `parse_scscc2_dest_audit.py`, both with method-banner priority |

## Known limits

1. **Raw QC outputs are NOT shipped inside `release_n13/`.** The release
   ships processed CSVs only. Raw outputs live at
   `/home/nudt_cleng/2026/results/...` (parent project, local FS) and
   on the ybsi cluster. This is itself an audit finding: a downstream
   consumer of `release_n13/` cannot reproduce the Phase 4 audit from
   the release artifact alone — they would need both the release and
   the parent project's `results/` directory (or the ybsi raw outputs).

2. **15 ADC(2) raw outputs are on ybsi only.** R1-deploy batch ADC(2)
   raw outputs are at `/public/home/ybsi/nudt_cleng/2026/round1_adc2/`
   (per phase reports). Audit cannot reach them under the no-ssh hard
   constraint.

3. **4 historical SCS-CC2 dirs lack control files.** Basis audit for
   those 4 molecules relies on the in-output method banner, not on a
   preserved `control` file. (Method banner suffices for SCS-CC2
   identification because Spin-Component Scaling is recorded inline.)

4. **No slurm-*.out files locally.** Scheduler evidence is INFERRED
   tier for all 13 SCS-CC2 outputs. The ricc2.out banner `ricc2 (nodeN)`
   does identify a compute node, but a FULL-tier audit would also
   require the slurm log alongside.

5. **Rounding-precision in ADC(2) processed labels.** 8 ADC(2) values
   in `validated_candidates_master.csv` are rounded to 3 decimal places
   while the raw outputs carry 5. The audit's strict 0.1-meV tolerance
   flagged these as VALUE_MISMATCH, but they are best classified
   `OK_ROUNDING_ONLY`. Recommended: future generator update should
   write at least 4 dp into the master CSV.

## Deliverables this phase

```
audit/phase4_spec.md
audit/phase4_git_status_before.txt
audit/raw_format_recon.md
audit/ricc2_outputs_inventory.txt
audit/control_inventory.txt
audit/scheduler_log_inventory.txt
audit/qc_provenance_report.csv                  48 rows
audit/qc_coverage_matrix.csv                    13 rows
audit/11_verify.log
audit/qc_provenance_summary.md
audit/phase4_qc.md                              (this file)

scripts/audit/parse_adc2_dest_audit.py
scripts/audit/parse_scscc2_dest_audit.py
scripts/audit/11_phase4_verify_qc_provenance.py
```

## Allowed conclusion

> SCS-CC2 ΔE_ST labels for the n=13 ADC(2)-screened cohort are
> reproducible from local raw Turbomole `ricc2_scscc2_*.out` files
> with correct method banner (CC2 + Spin-Component Scaling, standard
> Grimme factors C_os=1.2, C_ss=0.333) and ΔE_ST agreement to <1×10⁻¹³
> eV. **n=13 SCS-CC2 cohort is raw-provenance-FULL.**

## Not allowed conclusion

> This audit does **not** claim raw provenance for the 15 ADC(2)
> R1-deploy raw outputs that live on the ybsi cluster; they remain
> documented-but-unverified locally. **No ADC(2) value in the
> manuscript should be claimed as "fully calculation-derived from
> local raw files" without first making those 15 raw outputs available
> on qfh-u24.**

---

**Phase 4: COMPLETE.** Halting before Phase 5.
