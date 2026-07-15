# Phase 5 Step 2 — Hz_POZ1_NPh21_CF31 basis/method resolution

## Verdict: **A_RESOLVED_SVP** (with banner-printed basis evidence; control file absent)

## Evidence summary

| Field | Value |
|---|---|
| Batch assignment | **4 historical SCS-CC2 batch** (one of the original 4: Hz_NH23, Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, Hz_POZ1_NPh21_CF31) |
| Preserved control file (SCS-CC2 sing) | **No** (only `ricc2_scscc2_sing.out` present in `adc2_batch2_raw/Hz_POZ1_NPh21_CF31/turbo_sing_scscc2/`) |
| Preserved control file (ADC(2) sing) | **No** (only `ricc2_sing.out` present in `turbo_sing/`) |
| ADC(2) raw status | **OK** — parsed −9.71 meV, claimed −9.71 meV, diff 3.4×10⁻¹³ meV (machine precision) |
| SCS-CC2 raw status | **OK** — parsed −165.57 meV, claimed −165.57 meV, diff 2.2×10⁻¹³ meV |
| Method banner (SCS-CC2 output) | `CC2 - Approximate CC Singles and Doubles` + `Spin-Component Scaling will be applied` + `C_os = 1.200  C_ss = 0.333` ✓ |
| Main basis ($basis) — banner-printed | **def2-SVP** for all 5 elements (f, c, n, o, h), lines 104–110 of `ricc2_scscc2_sing.out` |
| Auxiliary basis ($cbas / fitting) — banner-printed | **def2-SVP** for all 5 elements, lines 174–180 ("Auxiliary basis set information" block) |
| $jbas (RI-J for SCF) — banner-printed | not in ricc2.out; would be in the prior ridft output (not preserved) |
| Scheduler tier | **INFERRED** — `ricc2 (nodeN)` banner shows compute node, no slurm log preserved |

## Detailed banner excerpts

Both ADC(2) and SCS-CC2 outputs contain explicit basis-set blocks at
runtime, printed by ricc2 regardless of control-file persistence
post-run. Sample from `adc2_batch2_raw/Hz_POZ1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out`:

```
98:              |               basis set information              |
104:   type   atoms  prim   cont   basis
106:    f        3     24     14   def2-SVP   [3s2p1d|7s4p1d]
107:    c       31     24     14   def2-SVP   [3s2p1d|7s4p1d]
108:    n        9     24     14   def2-SVP   [3s2p1d|7s4p1d]
109:    o        1     24     14   def2-SVP   [3s2p1d|7s4p1d]
110:    h       18      7      5   def2-SVP   [2s1p|4s1p]

168:                  |     Auxiliary basis set information      |
174:   type   atoms  prim   cont   basis
176:    f        3     72     48   def2-SVP   [6s5p4d1f|8s6p5d3f]
177:    c       31     72     48   def2-SVP   [6s5p4d1f|8s6p5d3f]
178:    n        9     72     48   def2-SVP   [6s5p4d1f|8s6p5d3f]
179:    o        1     72     48   def2-SVP   [6s5p4d1f|8s6p5d3f]
180:    h       18     23     14   def2-SVP   [3s2p1d|4s3p2d]
```

The ADC(2) sibling output (`turbo_sing/ricc2_sing.out`) shows the same
basis pattern; for that file the `cbas` keyword was missing from the
control and Turbomole auto-loaded `def2-SVP` cbas from its built-in
library (banner line 168: `Keyword $cbas missing in file <control>`).
This is benign — Turbomole still ran with `def2-SVP` cbas.

## Why this is `A_RESOLVED_SVP` rather than
## `A_INFERRED_FROM_BANNER_ONLY_INSUFFICIENT`

The Phase 4 spec's `A_INFERRED_FROM_BANNER_ONLY_INSUFFICIENT` is for
the case where the main basis can be inferred from the runtime banner
but the auxiliary basis cannot be independently re-read.

For Hz_POZ1_NPh21_CF31, the ricc2.out banner **explicitly prints both**
the one-electron basis AND the auxiliary (cbas) basis it actually
used at runtime, per-element. This is direct raw evidence at the same
level of trust as a preserved control file — arguably stronger,
because the banner records what was actually consumed by the program,
not what was supposed to be consumed.

The only basis group the ricc2.out banner does not record is `$jbas`
(RI-J for SCF), because ridft handled that in a preceding stage. The
SCS-CC2 ricc2 step itself does not use `$jbas`; it uses `$cbas`. For
the purpose of "what basis was used by the SCS-CC2 calculation that
produced the reported ΔE_ST", `$basis` + `$cbas` is the complete
relevant set, and both are banner-confirmed as `def2-SVP` for all
elements.

## Independent classification per Phase 5 spec rubric

| Spec requirement | Result |
|---|---|
| raw evidence supports SCS-CC2/def2-SVP | ✓ |
| preserved control exists with all 3 basis groups SVP | ✗ (no control), **but** banner provides equivalent evidence for $basis and $cbas |
| ricc2.out banner gives main basis AND auxiliary basis family | ✓ both **def2-SVP** |
| manuscript may write SCS-CC2/def2-SVP | ✓ |
| low-evidence caveat (because ADC(2) is near-zero borderline) | **still required** |

→ **A_RESOLVED_SVP** is the correct verdict.

## Recommended manuscript wording (kept low-evidence due to ADC(2) borderline)

> "Hz_POZ1_NPh21_CF31 was promoted from ADC(2)-borderline (|ΔE_ST| =
> 9.7 meV, inside the ±30 meV near-zero window) to a clear
> negative-gap classification at SCS-CC2/def2-SVP (ΔE_ST = −165.6
> meV). Both the orbital basis and the correlation auxiliary basis are
> confirmed as def2-SVP from the ricc2 runtime banner; the historical
> calculation directory does not preserve the post-run `control` file
> in the local audit snapshot. The entry is retained at low evidence
> strength in Table 1 pending an independent basis-set sensitivity
> check (e.g., def2-TZVP) or method-family triangulation (CCSD, CC3,
> NEVPT2 on a small subset)."

## What this audit does NOT establish

- That `$jbas` (RI-J for SCF) was def2-SVP. The relevant ridft output
  is not preserved in the audit snapshot. (Note: this does not affect
  the SCS-CC2 ΔE_ST itself; ricc2 does not read $jbas.)
- That the basis was identical to what was specified in the
  pre-edit `control` file. The control file was overwritten or
  removed at run-end. The banner records what ricc2 actually used at
  runtime, which is the audit-relevant fact.
- That no manual editing happened between SCF and the ricc2 invocation.
  This level of guarantee would require a sealed audit trail
  (containerised runs + signed logs), which is out of scope.
