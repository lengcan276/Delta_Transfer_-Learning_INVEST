# Phase 2.4 plan — 7-molecule batch with LPT scheduling

Date: 2026-05-05
Status: pre-staged on ybsi, awaiting Phase 2.2 checkpoint user GO

## Scope

After Phase 2.2 mini-batch (4988 + 4989) completes and user approves the
checkpoint, submit the remaining 7 SCS-CC2/def2-SVP jobs to ybsi intel
partition using LPT (longest-processing-time-first) scheduling on the
4 idle compute nodes.

## 7 molecules to compute (all geometries pre-staged)

Source for all: `~/2026/results/invest_results/delta_dft/mol_*_<MOL>/xtbopt.xyz`
(per phase2_geometry_decision.md — gnorm in 5.6e-5 ~ 1.4e-4, within
historical SCS-CC2 baseline 6.6e-5 ~ 7.6e-4).

| Priority # | Molecule | Atoms | gnorm | ADC(2) ΔE_ST (eV) | Wallclock estimate (intel, N⁴ scaled from sanity 70at = 48h) |
|---|---|---|---|---|---|
| 4 | Hz_NH22_SO2Ph1 | 33 | 1.2e-4 | -0.064 | ~3 h |
| 3 | Hz_NPh22_CN1 | 61 | 8.1e-5 | -0.054 | ~28 h |
| 9 | Hz_Cz1_NPh21_CF31 | 61 | 7.1e-5 | -0.136 | ~28 h |
| 6 | Hz_NEt21_NPh22 | 74 | 1.4e-4 | -0.089 | ~60 h |
| 7 | Hz_NPh21_Cz2 | 78 | 8.3e-5 | -0.119 (dark) | ~73 h |
| 5 | Hz_DMAC1_NPh21_SO2Ph1 | 80 | 6.3e-5 | -0.066 | ~82 h |
| 8 | Hz_NPh23 | 82 | 5.6e-5 | -0.123 (dark) | ~91 h |

Σ wall = 365 h ≈ 15.2 d (if serial). With 4 idle intel nodes,
the question is how to assign jobs to nodes to minimize makespan.

## LPT (longest-processing-time-first) schedule

Sort jobs by descending wallclock, place each onto the currently-shortest node:

| Step | Node A | Node B | Node C | Node D |
|---|---|---|---|---|
| 1: NPh23 (91h) | NPh23 | | | |
| 2: DMAC1_SO2Ph1 (82h) | NPh23 | DMAC1_SO2Ph1 | | |
| 3: NPh21_Cz2 (73h) | NPh23 | DMAC1_SO2Ph1 | NPh21_Cz2 | |
| 4: NEt21_NPh22 (60h) | NPh23 | DMAC1_SO2Ph1 | NPh21_Cz2 | NEt21_NPh22 |
| 5: NPh22_CN1 (28h) → shortest is D (60h) | NPh23 | DMAC1_SO2Ph1 | NPh21_Cz2 | NEt21+NPh22_CN1 (88h) |
| 6: Cz1 (28h) → shortest is B (82h) | NPh23 | DMAC1_SO2Ph1+Cz1 (110h) | NPh21_Cz2 | NEt21+NPh22_CN1 (88h) |
| 7: NH22 (3h) → shortest is C (73h) | NPh23 | DMAC1+Cz1 (110h) | NPh21_Cz2+NH22 (76h) | NEt21+NPh22_CN1 (88h) |

**Makespan check**: max over nodes = max(91, 110, 76, 88) = **110 h ≈ 4.6 d**

(My earlier estimate of 101h was a slight LPT mis-application; corrected
above.)

### Final assignment

| Node | Sequence | Total wall (estimate) |
|---|---|---|
| node5 | NPh23 (91h) | **91 h** |
| node6 | DMAC1_SO2Ph1 (82h) → Cz1_NPh21_CF31 (28h) | **110 h** |
| node7 | NPh21_Cz2 (73h) → NH22_SO2Ph1 (3h) | **76 h** |
| node12 | NEt21_NPh22 (60h) → NPh22_CN1 (28h) | **88 h** |

Round-A makespan ≈ **4.6 days** (limited by node6 sequence).

Slurm `--time=168:00:00` (7 d) cap is 56% above the longest node sequence,
giving a comfortable buffer for ssw-user contention or scaling deviations.

## Submission protocol (after user GO)

```bash
# (on ybsi master, login is OK for sbatch)
cd /public/home/ybsi/nudt_cleng/2026/orca_jobs/scscc2_extension_n13/

# Setup all 7 controls (cheap define on master, ~1 min total)
for mol in Hz_NPh23 Hz_DMAC1_NPh21_SO2Ph1 Hz_Cz1_NPh21_CF31 \
           Hz_NPh21_Cz2 Hz_NH22_SO2Ph1 \
           Hz_NEt21_NPh22 Hz_NPh22_CN1; do
    bash setup_scscc2_svp_on_login.sh "$mol"
done

# Submit in LPT order (longest first to land on its dedicated node)
for mol in Hz_NPh23 Hz_DMAC1_NPh21_SO2Ph1 Hz_NPh21_Cz2 \
           Hz_NEt21_NPh22 Hz_NPh22_CN1 Hz_Cz1_NPh21_CF31 \
           Hz_NH22_SO2Ph1; do
    cd "$mol"
    sed "s/PLACEHOLDER/$mol/" ../templates/run_scscc2_svp.slurm > run.slurm
    sbatch run.slurm
    cd ..
done

squeue -u $USER -o "%i %j %T %R %l"
```

(Note: Slurm picks the actual node, not us. The above sequencing only
controls submit order, which biases dispatch toward longer jobs reaching
nodes first; under heavy contention we may not get the planned mapping,
but the LPT ordering still minimizes expected makespan.)

## Fallback for 4989 (DMAC2_SO2Ph1, 87at, --time=168h)

Estimated wall is ~115 h (well below 168 h cap), but if the SCF or ricc2
iterations diverge or scaling is worse than N⁴:

1. **In-place restart** — Turbomole writes `.cao` and `RE0/RE1` checkpoint
   files that resume from the last completed iteration. If 4989 hits 168h
   limit:
   ```bash
   ssh -p 22116 ybsi@10.67.4.7 \
     'cd /public/home/ybsi/nudt_cleng/2026/orca_jobs/scscc2_extension_n13/Hz_DMAC2_SO2Ph1/turbo_<sing|trip>_scscc2_svp; \
      ls *.cao RE0* 2>/dev/null && echo "restart possible" || echo "no checkpoint"; \
      sbatch ../../<restart-script>.slurm'
   ```
2. **Reduce nstart in $excitations** — currently `nstart=30` for singlet,
   could be reduced to `nstart=20` for restart to save startup cost.
3. **Worst case**: skip Hz_DMAC2_SO2Ph1, n=13 → n=12, Clopper-Pearson CI
   becomes [0.6402, 0.9981] (still publishable).

## Fallback for any Phase 2.4 job timeout

If any of the 7 jobs hits 168 h:
- Same restart-from-checkpoint logic as above.
- If checkpoint also fails: drop that molecule from n=13. Worst case n=11
  → CI [0.5450, 0.9619] — still publishable, narrative slightly weakened.
- All 13 must drop ≥3 to invalidate Innovation 2 narrative; this would
  require simultaneous failure of multiple SCS-CC2 jobs, very unlikely.

## Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| ssw user occupies node5/6/7/12 mid-run | medium | +1-2 d wallclock | LPT minimizes contention impact |
| node hardware fault during 4-day run | low | +2-3 d (resubmit from checkpoint) | Checkpoint restart |
| 4989 timeout despite 168h cap | low (<10%) | +2 d (restart) | Checkpoint restart; worst-case n=12 |
| Methods reviewer objects to mixed geometry source | medium | +2 h (text revision) | Already documented in phase2_geometry_decision.md |
| Phase 2.4 job SCF non-convergence | low | drop 1 mol, n=12 | Acceptable per CI table |
| Phase 3 audit fails (new numbers don't match) | low | +1 d (debug) | 5 skills automate audit |

## Timeline (best / expected / worst)

| Milestone | Best | Expected | Worst |
|---|---|---|---|
| 4988 (NEt22) finish | 2026-05-06 | 2026-05-06 | 2026-05-07 |
| 4989 (DMAC2) finish | 2026-05-09 | 2026-05-10 | 2026-05-12 (after restart) |
| Phase 2.2 checkpoint user review | 2026-05-10 | 2026-05-11 | 2026-05-13 |
| Phase 2.4 batch submit | 2026-05-10 | 2026-05-11 | 2026-05-13 |
| Phase 2.4 makespan (LPT 4.6 d) | 2026-05-15 | 2026-05-16 | 2026-05-18 |
| Phase 3 (~1 d) | 2026-05-16 | 2026-05-17 | 2026-05-19 |
| **🎯 Submission-ready** | **2026-05-16** | **2026-05-17** | **2026-05-19** |

## Why this lets us write the paper

Phase 3 is **mechanical text + figure replacement**, not new science:

1. New `cross_check_n13.csv` from 4 historical + 9 new ricc2 outputs
2. Clopper-Pearson n=13 CI replaces n=4 CI [0.40, 1.00]:
   - 13/13 → [0.7529, 1.0000]
   - 12/13 → [0.6402, 0.9981]
   - 11/13 → [0.5450, 0.9619]
3. Replace all `[0.40, 1.00]` strings + "four molecules"/"four lead candidates"
   wording in main.tex (Abstract, §3.5, Conclusion, Fig 4 caption)
4. Regenerate Fig 4 with 13 markers (preserve original 4 + add 9 new)
5. Methods section + SI: add 1 paragraph on geometry source mixing
   (per phase2_geometry_decision.md decision)
6. Re-run audit_numbers.py → unresolved = 0
7. Repackage Overleaf zip

All of this is **already designed in 5 audit skills** (manuscript-consistency,
stats-rigor-reviewer, figure-auditor, comp-chem-method-reviewer,
adversarial-reviewer). The Phase 3 work is just running them and applying
the diff they suggest.

**The paper is currently audit-clean (unresolved = 0). After Phase 2 compute
finishes, Phase 3 only updates numbers and regenerates one figure.**
