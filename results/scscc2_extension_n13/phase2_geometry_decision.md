# Phase 2 几何源决策记录

Date: 2026-05-05
Decision: **Option A — use delta_dft/ converged geometries for all Phase 2 molecules**

## Background

After Phase 2.2 mini-batch was first submitted (jobs 4982/4983), GPT 二审 raised
P0/P1/P2 concerns about the geometry quality of the staged xtbopt.xyz files:

- Hz_DMAC2_SO2Ph1 from `adc2_batch2_final/`: gnorm=9.7e-3 (~12-147× looser than
  any historical SCS-CC2 job)
- Hz_NEt22_CF31 from R1 batch `coord` via `t2x` round-trip: no header gnorm,
  energy 1.2 eV higher than `delta_dft/` minimum (different stationary point)

Diagnostic results confirmed the concerns:

### Historical SCS-CC2 cohort gnorm baseline

| Molecule | Header gnorm | Source |
|---|---|---|
| Hz_NH23 | 7.6e-4 | hf_calcs |
| Hz_DMAC1_NPh21_CF31 | 4.2e-4 | adc2_batch2_final |
| Hz_NPh22_SO2Ph1 | 4.8e-4 | adc2_batch2_final |
| Hz_POZ1_NPh21_CF31 | 6.6e-5 | adc2_batch2_final |

All historical SCS-CC2 reference jobs used geometries with gnorm in
6.6e-5 to 7.6e-4 (< 1e-3, tightly converged).

### Original Phase 2.2 staged vs alternatives

| Molecule | adc2_batch2_final / R1 batch | delta_dft/ |
|---|---|---|
| Hz_DMAC2_SO2Ph1 | gnorm=9.7e-3 (outlier) | gnorm=8.2e-5 (in baseline range) |
| Hz_NEt22_CF31 | t2x: header empty; xtb-sp says different structure | gnorm=1.5e-4 (in baseline range) |

## Decision: Option A

Replace the staged geometries with `delta_dft/` versions for both molecules.
Apply the same rule to all 7 remaining Phase 2 molecules (#3-#9): use
`delta_dft/mol_*/xtbopt.xyz` as canonical source.

## Rationale

The scientific objective of Phase 2 is **extending SCS-CC2 sign-retention
validation from n=4 to n=13**, not reproducing the exact L2 ADC(2) reference
numbers. For the sign-retention statistic to be meaningfully homogeneous,
all 13 SCS-CC2 calculations must use comparable-quality geometries.

- Using batch2_final/R1 batch geometries (per a literal reading of RL-2 "reuse
  the geometry") would introduce gnorm outliers (9.7e-3 vs historical < 1e-3),
  violating cohort homogeneity in spirit.
- Using delta_dft/ converged geometries keeps all 13 SCS-CC2 calculations on
  comparably-tight geometries, matching historical practice.

## Trade-off acknowledged

The cited L2 ADC(2) ΔE_ST values (e.g., −0.032 for Hz_DMAC2_SO2Ph1) were
computed on the older, looser geometries. Phase 2 SCS-CC2 results will be on
the delta_dft geometries. Therefore:

- **Sign comparison** (the primary statistic): valid (geometry quality
  affects the magnitude only mildly; sign is robust)
- **Quantitative ΔE_ST(SCS-CC2) vs cited ΔE_ST(ADC(2))** numerical match:
  not directly comparable (different geometries; the difference attributable
  to geometry vs to method is mixed)

Phase 3 manuscript update will explicitly note: "Phase 2 SCS-CC2 calculations
used independently re-converged xtb geometries (delta_dft/, gnorm < 2e-4),
which differ slightly from the geometries originally used to produce the
cited ADC(2) ΔE_ST values. Sign agreement is the primary cross-method
statistic; absolute ΔE_ST differences should be interpreted as a combination
of method and geometry sensitivity."

## Action taken

1. `scancel 4982 4983` — both jobs cancelled (had run ~14 min each before kill)
2. Replaced local + ybsi xtbopt.xyz with `delta_dft/` versions:
   - Hz_DMAC2_SO2Ph1: gnorm=8.2e-5 ✓
   - Hz_NEt22_CF31: gnorm=1.5e-4 ✓
3. Cleaned stale `turbo_*` dirs and old `run.slurm` from ybsi
4. Re-ran setup script for both
5. Re-submitted: **JobID 4987 = Hz_DMAC2_SO2Ph1 (node5 RUNNING)**,
   **JobID 4988 = Hz_NEt22_CF31 (node6 RUNNING)**

## Going forward

For Phase 2.4 (#3-#9 mini-batch), use the same source rule:
`~/2026/results/invest_results/delta_dft/mol_*_<MOL>/xtbopt.xyz`

Verify each molecule's delta_dft gnorm before submission; if any candidate
falls outside the 6e-5 to 1e-3 range, escalate to user.
