# Phase 0 Addendum — answers to GPT adversarial review + P1-A/P1-E fixes

Date: 2026-05-02
Operator: Claude Code (qfh-u24)

---

## Q1. `phase0_recon.md` — actual location and content

**Status: NOT YET WRITTEN.** The mission spec's Step 0.4 was not executed in
the prior session — only the live ssh recon (squeue/sinfo) was performed.
This addendum supersedes the missing `phase0_recon.md` for the items GPT
flagged. A formal `phase0_recon.md` will be written separately if the user
wants the Step-0.4 template literally.

What was actually reconnoitered (qfh-u24 + ssh ybsi):

- `~/2026/results/scscc2_batch2_summary.csv` — not opened (TBD this turn if needed)
- `~/2026/results/method_consistency_table.csv` — opened (see Q2 below)
- `~/2026/results/scscc2_tzvp_inputs/setup_tzvp_on_login.sh` — opened (TZVP version, basis to be patched to def2-SVP)
- `~/2026/results/scscc2_tzvp_inputs/Hz_DMAC1_NPh21_CF31/run_turbo_adc2_tzvp.slurm` — opened (see Q3)
- `~/2026/results/scscc2_tzvp_inputs/Hz_DMAC1_NPh21_CF31/run_scs_cc2_tzvp.slurm` — opened (see Q3)
- `~/2026/results/scscc2_tzvp_inputs/prepare_scs_cc2_tzvp_remote.sh` — opened (see Q3 — adc(2) → cc2+scs patch logic)
- `~/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out` — opened (used in Q4 SMP evidence and parser self-test)
- `~/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_trip_scscc2/ricc2_scscc2_trip.out` — opened (parser self-test)
- ybsi `squeue`, `sinfo` — verified intel partition has `node5,6,7,12 idle`

---

## Q2. `method_consistency_table.csv` column for `-0.22033`

```
$ head -1 ~/2026/results/method_consistency_table.csv
molecule,DDFT_corr_eV,ADC2_SVP_eV,SCSCC2_SVP_eV,ADC2_TZVP_eV,SCSCC2_TZVP_eV,
n_methods_available,all_signs_agree,sign_majority

$ grep DMAC1_NPh21_CF31 ~/2026/results/method_consistency_table.csv
Hz_DMAC1_NPh21_CF31,-0.0497,-0.12034,-0.22033,-0.08088,,4,True,neg
```

**Confirmed**: `-0.22033` lives in column **`SCSCC2_SVP_eV`** (the 4th column).
The reference value is genuinely **def2-SVP**, not TZVP. The TZVP column for
this molecule is empty (SCS-CC2/TZVP was never completed). The Phase 1 sanity
target of `−0.22033 ± 0.002 eV` is therefore valid.

---

## Q3. SCF driver in original 4 SCS-CC2 jobs

**Driver: `ridft` (RI-DFT).** NOT `dscf`. Evidence from
`run_turbo_adc2_tzvp.slurm` (the SCF stage that converged the MOs that the
SCS-CC2 stage reused):

```bash
cd ${SING_DIR}
echo "--- SCF Singlet: $(date) ---"
ridft > ridft_sing.out 2>&1
if grep -q "ridft ended normally" ridft_sing.out; then ...
```

Confirmed by control-file structure (from `setup_tzvp_on_login.sh`):

```
$rij                # RI-J for SCF Coulomb fit  → triggers ridft
$ricore   8000
$denconv  1d-7
$ricc2
  adc(2)            # later patched to "cc2 + scs" by prepare_scs_cc2_tzvp_remote.sh
  maxiter 150
$excitations
  irrep=a multiplicity=1 nexc=5 npre=15 nstart=30
$end
```

The historical `ricc2.out` (SCS-CC2 stage) in `turbo_sing_scscc2/` shows:

```
$ head -2 turbo_sing_scscc2/ricc2_scscc2_sing.out | head
   OpenMP run-time library returned nthreads = 48
 ricc2 (node1) : TURBOMOLE rev. V7.5.1 compiled 23 Dec 2020 at 11:16:29

WARNING: an $rij but no $rik flag found
WARNING: $rij is ignored by ricc2!
```

Note: `$rij` is consumed by `ridft` for the SCF Coulomb fit, then ignored by
`ricc2` (which uses its own `$ricc2` block + `$cbas`). The warning is benign.

**Workflow consequence (verified):** The original 4 jobs ran the full pipeline
`ridft → ricc2(adc(2)) → patch control adc(2)→cc2+scs → ricc2(SCS-CC2)`. The
fixed slurm template in this addendum reproduces that pipeline verbatim, so
the SCF driver is already correct (not `dscf`).

---

## Q4. TURBOMOLE build flavor — SMP vs MPI

**Confirmed: SMP/OpenMP build is functional on ybsi.** Direct evidence from
the historical `turbo_sing_scscc2/ricc2_scscc2_sing.out` (line 1):

```
   OpenMP run-time library returned nthreads = 48
```

and from the historical sbatch script:

```bash
export PARA_ARCH=SMP
export PARNODES=48
export OMP_NUM_THREADS=48
```

This run wallclock-completed (`ricc2 ended normally`, `total wall-time: 11
hours 26 minutes` for the singlet stage). If the `_smp` build had been
missing, Turbomole would have either (a) silently fallen back to serial — in
which case the 18d22h CPU time in 11h26m wallclock would have been
impossible — or (b) failed at startup. Neither happened.

**Conclusion**: SMP build is present and working. The Phase 1 template safely
keeps `PARA_ARCH=SMP` + `OMP_NUM_THREADS=48`. No need to switch to MPI.

(If the user still wants the literal `ls $TURBODIR/bin/` evidence, run on ybsi:
`ssh -p 22116 ybsi@10.67.4.7 "ls /public/home/ybsi/software/TURBOMOLE/bin/"` —
look for `em64t-unknown-linux-gnu_smp/`.)

---

## Q5. `rm -rf vasp_kunpeng/` on ybsi — acknowledged

User-confirmed manual cleanup, unrelated to SCS-CC2 task. No action required.
Logged here for the audit trail.

---

## Q6. `--nodelist=node5,6,7,12` — confirmed over-optimization

User-confirmed. Fixed in the new slurm template (see P1-A below).

---

## P1-A FIX — slurm template now uses partition + exclude

File: `~/2026/results/scscc2_extension_n13/templates/run_scscc2_svp.slurm`

Changes vs. the v2 prompt template:

| Header | v2 (rejected) | v3 (this addendum) |
|---|---|---|
| `--partition` | `intel` | `intel` (unchanged) |
| `--nodelist` | `node5,node6,node7,node12` | **REMOVED** |
| `--exclude` | (absent) | **`node8,node9`** (only the `down*` nodes) |
| `--cpus-per-task` | 16 | **48** (matches historical 48-thread SMP run) |
| `--mem` | 64G | 64G (unchanged) |
| `--time` | 72:00:00 | 72:00:00 (unchanged) |

Slurm will now schedule on any idle node in the intel partition (currently
node5/6/7/12; node10/11/13 may free up later) and avoid the `down*` nodes
8 and 9. If `ssw` releases their node10/11/13 jobs, our jobs become eligible
there too.

The template also now reproduces the **full** historical pipeline
(`ridft → ricc2(adc(2)) → patch → ricc2(SCS-CC2)`), not the truncated
`dscf + ricc2` from the v2 prompt. This addresses GPT P1-B in passing.

Hostname guard preserved (refuses to run if `hostname == master` or
contains `login`).

Full template content saved at:
`~/2026/results/scscc2_extension_n13/templates/run_scscc2_svp.slurm`

---

## P1-E FIX — parser written and self-tested

File: `~/2026/results/scscc2_extension_n13/parsers/parse_scscc2_dest.py`

### Parser logic

The Turbomole `ricc2` SCS-CC2 output writes per-state final excitation
energies in compact "Energy:" lines:

```
       Energy:     0.1275169 H      3.46991 eV    27986.716 cm-1
```

The 3rd numeric field (column index 4 in awk) is the eV value. The first
such line in a singlet `ricc2_scscc2_sing.out` is **S1**; in a triplet
`ricc2_scscc2_trip.out` it is **T1**. Subsequent "Energy:" lines are S2/S3/...
or T2/T3/...; we ignore them.

Regex used (anchored, strict):
```python
r'^\s*Energy:\s+[-+]?\d+\.\d+\s+H\s+([-+]?\d+\.\d+)\s+eV\s+'
```

Strictness rationale: `Energy:` also appears earlier in the file as
"Final CC2 energy" (ground state) and "Final MP2 energy" (D1 diagnostic).
Anchoring with `^` plus the H/eV/cm-1 pattern excludes those.

ΔE_ST = E(S1) − E(T1). Negative = INVEST.

### Self-test on historical Hz_DMAC1_NPh21_CF31

```
$ python3 ~/2026/results/scscc2_extension_n13/parsers/parse_scscc2_dest.py --selftest
Self-test on Hz_DMAC1_NPh21_CF31 (def2-SVP)
  Singlet: /home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out
  Triplet: /home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_trip_scscc2/ricc2_scscc2_trip.out
  E(S1)        = 3.46991 eV
  E(T1)        = 3.69024 eV
  ΔE_ST parsed = -0.22033 eV
  ΔE_ST ref    = -0.22033 eV (method_consistency_table.csv)
  difference   = -0.000 meV
  PASS — parser reproduces reference within 0.1 meV
```

**Parser is validated.** It will be the canonical extractor in Phase 1
sanity comparison and Phase 2 batch processing.

---

## Outstanding items before Phase 1 sanity sbatch

1. Need to check `~/2026/results/scscc2_batch2_summary.csv` for the existence
   of E(S1) and E(T1) columns — if so we have a second consistency reference.
2. Need to verify all 13 target molecules have `xtbopt.xyz` available on
   qfh-u24 (Step 0.2 of the original mission spec, not yet performed).
3. Need to draft `setup_scscc2_svp_on_login.sh` (Step 1.1 of mission spec).
   This will be done in Phase 1 once user signs off the addendum.

The Phase 1 sanity submit (Hz_DMAC1_NPh21_CF31 reproduction) is **NOT yet
launched**. Awaiting user approval of this addendum before proceeding.

---

## Files written this turn (all under `~/2026/results/scscc2_extension_n13/`)

```
phase0_addendum.md                            (this file)
templates/run_scscc2_svp.slurm                (P1-A fix)
parsers/parse_scscc2_dest.py                  (P1-E fix)
```

No production sbatch was issued. No canonical files were touched.
