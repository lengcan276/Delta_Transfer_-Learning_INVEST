# Phase 1 Sanity Report — PASS

Date completed: 2026-05-04 13:30:32 CST
Operator: Claude Code (qfh-u24)
Sanity molecule: Hz_DMAC1_NPh21_CF31
SLURM_JOB_ID: 4981

## A. Why this matters

Phase 1 sanity is **not** an isolated engineering task. It is the load-bearing
anchor for the n=13 statistical unit in Innovation 2 (Hierarchical Cross-
Fidelity Validation):

```
  Innovation 2: Hierarchical Cross-Fidelity Validation
                    │
                    ├─ Upstream dependency: original 4 RI-SCS-CC2 results trustworthy
                    ├─ Phase 1 sanity = prove "we can precisely reproduce the
                    │                   historical result in the new environment"
                    │                   → establishes the credibility anchor for
                    │                     Phase 2's 9 new molecules
                    └─ Downstream claim: n=13 sign-retention CI is defensible
```

If sanity had failed (|diff| > 2 meV), the new RI-SCS-CC2/def2-SVP results
on the 9 incoming molecules would not have been comparable to the original
4 — the n=13 cohort could not be defended as a single statistical unit, and
the entire hierarchical-validation narrative for Innovation 2 would collapse.

The real meaning of Phase 1 sanity is **not** "is my software install correct?"
It is **"can we make a methodologically consistent boundary statement about
n=13 as a single statistical population?"**

This statement now has empirical grounding: **the new pipeline reproduces the
historical SCS-CC2/def2-SVP ΔE_ST to better than the parser's printed
precision (0.00001 eV).**

## B. 数值复现结果

| Quantity | Value |
|---|---|
| Historical ΔE_ST(RI-SCS-CC2/def2-SVP, Hz_DMAC1_NPh21_CF31) | **−0.22033 eV** (from `method_consistency_table.csv`, col `SCSCC2_SVP_eV`) |
| New pipeline ΔE_ST | **−0.22033 eV** (from `parsers/parse_scscc2_dest.py` on Stage 2 outputs) |
| ǀdiffǀ | **0.00000 eV = 0.00 meV** |
| Acceptance threshold | ≤ 2 meV |
| **验收 1** | ✅ **PASS** |

Component breakdown (new run, both spins from `ricc2_scscc2_*.out` first `Energy:` line):
- E(S1, SCS-CC2/def2-SVP) = 3.46991 eV
- E(T1, SCS-CC2/def2-SVP) = 3.69024 eV
- ΔE_ST = E(S1) − E(T1) = −0.22033 eV  (INVEST candidate, sign confirmed)

## C. RL-1 合规证据

slurm-4981.out 顶部前 5 行:
```
=== Job started ===
Hostname: node12
Date: Sat May  2 01:24:43 PM CST 2026
Slurm Job ID: 4981
Slurm Nodelist: node12
```

| Check | Value |
|---|---|
| Hostname recorded | `node12` |
| Allowed compute nodes (intel partition idle at submit) | node5, node6, node7, node12 |
| Master / login? | NO |
| Hostname guard at job start (`exit 99` if master) | did not trigger |
| **验收 2** | ✅ **PASS** |

`node12` is in the intel partition compute pool (verified Phase 0 v2 via
`scontrol show node node12 → CPUTot=48, State=IDLE`), and is not the master
login node. RL-1 satisfied prospectively for this job.

## D. 方法学一致性（P2-NEW-C 事后验证）

The Stage 1 ridft (RI-DFT/HF, def2-SVP) SCF reference must be the same
stationary state as the historical SVP run. If the SCF converged to a
different stationary state (rare but possible for large π-systems), the
downstream ricc2 result could differ.

```
$ grep "RHF energy" historical/turbo_sing/ricc2_sing.out
     *   RHF  energy                             :  -2088.3411972310      *

$ grep "total energy" new/turbo_sing_svp_round2/ridft_sing.out
                 |  total energy      =  -2088.34119723099  |
```

| Quantity | Value |
|---|---|
| Historical SCF total energy (HF/def2-SVP, Hz_DMAC1, singlet) | **−2088.3411972310** a.u. |
| New SCF total energy (HF/def2-SVP, Hz_DMAC1, singlet) | **−2088.34119723099** a.u. |
| ǀdiffǀ | **≈ 1 × 10⁻¹¹ a.u.** (within numerical printout precision; effectively zero) |
| Acceptance threshold | < 1 × 10⁻⁶ a.u. |
| **验收 3** | ✅ **PASS** (5 orders of magnitude below threshold) |

→ The new pipeline converges the SCF to the **same stationary state** as
the historical run. SCS-CC2 reproduction of −0.22033 eV is therefore not
a coincidence; it is causally tied to consistent SCF starting conditions.

## E. 时间和资源

| Phase | Wallclock | CPU time |
|---|---|---|
| Stage 1 ridft singlet | 38 s | 26 min |
| Stage 1 ricc2(adc2) singlet | 11h 54m | 12d 17h |
| Stage 1 ridft triplet | 7 s | 5 min |
| Stage 1 ricc2(adc2) triplet | 6h 44m | 7d 2h |
| Stage 2 ricc2(SCS-CC2) singlet | **22h 14m** | 23d 20h |
| Stage 2 ricc2(SCS-CC2) triplet | 7h 14m | 8d 0h |
| **Total wallclock (slurm sacct)** | **2d 0h 6m** = 48h 6m | — |
| Node | node12 (intel partition, 48 cores) | — |
| Memory peak | not captured (Slurm RealMemory=1 quirk; FreeMem at submit was 345 GB on node12) | — |

Comparison with historical SCS-CC2/def2-SVP singlet on the same molecule:

| Run | Stage 2 SCS-CC2 sing wallclock | Stage 2 SCS-CC2 sing CPU time | Threading speedup |
|---|---|---|---|
| Historical (2026-04-10, batch partition node1) | 11h 26m | 18d 22h | ≈ 39.7× (≈ 48 threads ≈ ideal) |
| New (2026-05-02, intel partition node12) | **22h 14m** | 23d 20h | ≈ 25.7× (poor scaling) |

→ The new run's Stage 2 singlet took **~2× as long wallclock-wise**, despite
nominally identical 48-thread SMP setup. CPU time is comparable (23.8d vs
18.9d). This indicates **lower OpenMP threading efficiency on node12 vs
node1**, possibly due to memory bandwidth or NUMA topology differences
between batch and intel partition hardware. **Numerically, the result is
identical**, so this is purely a throughput observation, not a correctness
issue. Recorded for Phase 2 capacity planning: each Phase 2 molecule may
take ~24-48h on intel partition (vs ~12-18h on batch partition historically).

## F. 决策

Three acceptance criteria — 验收 1 数值复现 (PASS, 0.00 meV diff), 验收 2
RL-1 合规 (PASS, hostname=node12), 验收 3 方法学一致 (PASS, SCF diff ~1e-11)
— **all PASS**.

**Decision: PROCEED to Phase 2** (9 new INVEST molecules, borderline-first
order per mission spec):

| # | Molecule | ADC(2) ΔE_ST (eV) | Notes |
|---|---|---|---|
| 1 | Hz_DMAC2_SO2Ph1 | −0.032 | most borderline |
| 2 | Hz_NEt22_CF31 | −0.036 | borderline |
| 3 | Hz_NPh22_CN1 | −0.054 | borderline |
| 4 | Hz_NH22_SO2Ph1 | −0.064 | |
| 5 | Hz_DMAC1_NPh21_SO2Ph1 | −0.066 | |
| 6 | Hz_NEt21_NPh22 | −0.089 | |
| 7 | Hz_NPh21_Cz2 | −0.119 | dark |
| 8 | Hz_NPh23 | −0.123 | dark |
| 9 | Hz_Cz1_NPh21_CF31 | −0.136 | least borderline |

Per mission Phase 2.2: submit #1 + #2 first as mini-batch, checkpoint after
both complete, then submit #3-#9 after user approval.

Capacity note: at ~24-48h per molecule on intel partition (4 idle nodes),
the 2-of-9 mini-batch will take ~1-2 days; the full 9 in parallel
~2-4 days (resource-permitting; ssw user may compete for intel nodes
node10/11/13 if they free up).

**Awaiting user GO for Phase 2.2 (Hz_DMAC2_SO2Ph1 + Hz_NEt22_CF31 mini-batch).**
