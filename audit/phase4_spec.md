# Phase 4 — Quantum-Chemistry Raw-Output Provenance Audit (revised spec)

Date: 2026-05-20
Repository HEAD: `3a72bc9` (still)
Phase 3.6 patch: NOT APPLIED (live repo unchanged)

## Goal
Verify that the n=13 SCS-CC2 and n=35 ADC(2) ΔE_ST labels reported in
processed tables can be independently reproduced from local raw Turbomole
ricc2 outputs. Establish (or honestly fail to establish) raw-output
authenticity — the part Phase 2 / Phase 3 explicitly could not.

## Hard constraints (unchanged)
1. No file under `paper/`, `results/`, `data/`, `figures/`, `reviews/`,
   `scripts/` (outside `scripts/audit/`) modified.
2. All new outputs to `audit/`. All new scripts to `scripts/audit/`.
3. No git add/commit/push/rebase/config.
4. No network. No ssh / rsync / scp / curl / wget.
5. session.md is not evidence.
6. Phase 3.6 patch stays UNAPPLIED.

## Revised additions (vs original Phase 4 spec)

### Step 2.5 — Raw format reconnaissance
Before parsing, sample 1 example raw `ricc2.out` from each calc type
(historical ADC(2), historical SCS-CC2, Phase-2 SCS-CC2) and dump:
- program banner (`R I C C 2 - PROGRAM` + revision string)
- "ricc2 (nodeN)" hostname line
- method declaration block (e.g., `model    : adc(2)` or
  `model    : cc2  +  scs`)
- the "Energy:" lines for excited states (format string)
- normal-termination marker(s) actually used by Turbomole 7.5.1
- where basis information appears in the output (vs the control file)

Output: `audit/raw_format_recon.md`. All later parsing must match the
formats observed here.

### Independent ADC(2) parser
Existing `scripts/scscc2_extension/parsers/parse_scscc2_dest.py` handles
SCS-CC2 only. Write a parallel `scripts/audit/parse_adc2_dest_audit.py`
for ADC(2) ricc2 outputs. Self-test against a historical ADC(2) calc
where the ΔE_ST value is known from a processed table.

### Method-banner priority over control
At parse time, prefer the **runtime banner / method declaration block
inside the raw ricc2.out** over the current `control` file. The control
file may have been edited between successive stages (e.g., adc(2) →
cc2 + scs patch in Stage 2 of `run_scscc2_svp_v2.slurm`). The output
file is a permanent record of what was actually computed at runtime.
Mismatch between the two is recorded, but the banner wins.

### Three-set basis audit
Turbomole `control` has three basis groups:
- `$basis` — one-electron orbital basis
- `$jbas` — Coulomb auxiliary basis (for RI-J)
- `$cbas` — correlation auxiliary basis (for RI-CC2/RI-ADC(2))
Audit all three. Flag if any is not def2-SVP. Report each explicitly.

### Stricter raw matching
- Numeric tolerance: ΔE_ST mismatch only acceptable if |Δ| ≤ 0.0001 eV
  (0.1 meV). Anything larger is `VALUE_MISMATCH`.
- Method match: case-insensitive, but exact substring (no fuzzy).
- Basis match: exact string after normalisation (whitespace collapsed).

### Tiered scheduler evidence
| Tier | Definition |
|---|---|
| FULL | `slurm-<jobid>.out` present AND contains `SLURM_JOB_ID` value AND `Hostname:` line AND start+end timestamps |
| PARTIAL | slurm log present but missing one of the above fields |
| INFERRED | no slurm log; but ricc2.out banner shows `ricc2 (nodeN)` hostname |
| NONE | no evidence of compute-node execution |

### ADC(2) × SCS-CC2 coverage matrix
For each of the 13 SCS-CC2 molecules, cross-tabulate ADC(2) raw
evidence × SCS-CC2 raw evidence: 13 × 2 = 26 cells. Identify
fully-evidenced cohort (both raw paths present + verified) vs partially-
evidenced.

## Status options
- `RAW_PROVENANCE_FULL_n13` — every label fully verified
- `RAW_PROVENANCE_PARTIAL_n13` — some labels missing or unverified
- `RAW_PROVENANCE_FAILED` — substantive mismatches found
- `RAW_PROVENANCE_BLOCKED` — no raw files present at all
