# Phase 4 Step 2.5 — Raw Turbomole ricc2 format reconnaissance

Sample sources (READ-ONLY, outside release_n13 baseline):
- `/home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing/ricc2_sing.out` — historical ADC(2)
- `/home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out` — historical SCS-CC2
- `/home/nudt_cleng/2026/results/scscc2_extension_n13/Hz_NPh22_CN1/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out` — Phase-2 SCS-CC2
- `/home/nudt_cleng/2026/results/scscc2_extension_n13/Hz_NPh22_CN1/turbo_sing_scscc2_svp/control` — Phase-2 control

## Common header banner (all ricc2 outputs)

```
   OpenMP run-time library returned nthreads = 48
 ricc2 (nodeN) : TURBOMOLE rev. V7.5.1 compiled 23 Dec 2020 at 11:16:29
 ...
                              R I C C 2 - PROGRAM
 ...
```

→ `ricc2 (nodeN)` line is the in-output hostname. `nodeN` = compute node
(e.g. `node1`, `node6`, `node11`).

## Method declaration block (wavefunction model)

Both ADC(2) and SCS-CC2 outputs contain (around line 143-148):

```
     restricted closed shell calculation for the wavefunction models:
               <MODEL>     - <DESCRIPTION>
```

| Method | `<MODEL>` text | `<DESCRIPTION>` text |
|---|---|---|
| ADC(2) | `ADC(2)` | `Algebraic Diagrammatic Construction to 2. Order (strict)` |
| CC2 / SCS-CC2 | `CC2` | `Approximate CC Singles and Doubles` |

**SCS-CC2 is distinguished from plain CC2 by the additional banner:**

```
     Spin-Component Scaling will be applied...
          scaling factors:  C_os = 1.200  C_ss = 0.333
```

If `Spin-Component Scaling will be applied` is present AND model is CC2,
the calculation is **SCS-CC2 (with c_os=1.2, c_ss=0.333)**.

If model is CC2 and SCS banner is absent, the calculation is plain CC2.

If model is ADC(2), it's ADC(2) — SCS does not apply.

This gives the **method-banner priority** rule: parse the output's
declaration block + Spin-Component Scaling presence, not the control
file. The control file may have been edited post-run (e.g., for the
next stage).

## Per-state excitation energy lines

For each computed excited state, the output contains:

```
       Energy:     0.1275169 H      3.46991 eV    27986.716 cm-1
```

Format: `^\s*Energy:\s+<H_value>\s+H\s+<eV_value>\s+eV\s+<cm-1_value>\s+cm-1`.

The **first** "Energy:" line in a singlet ricc2.out is S1. The first in
a triplet ricc2.out is T1. Higher-state lines (S2, S3, ...) follow.

**Caveat — overlapping context lines:**
The same eV value also appears in transition blocks later:
```
  |  Transition                                             model: <X>      |
  |    number, symmetry, multiplicity:    1 a    1                          |
  |    frequency :   0.1275169 a.u.     3.46991 e.V.     27986.716 rcm     |
```
The audit parser must use the `^\s*Energy:\s+...\s+H\s+...\s+eV\s+`
pattern (not the `frequency :` pattern) to avoid double-counting.

## Normal termination markers

End of a successful ricc2 output:
```
    YYYY-MM-DD HH:MM:SS.fff

 ricc2 ended normally
```

Alternative success marker (sometimes present at end of stage block):
```
  ****  ricc2 : all done  ****
```

Audit parser accepts either as "normal termination".

## Control file format (Turbomole)

For molecules where the control file is preserved (Phase-2 batches only),
the basis declaration is split:

```
$atoms
n  3,7,9,11,16,18,24,26-27
   basis =n def2-SVP    ← one-electron basis per element
   jbas  =n def2-SVP    ← Coulomb auxiliary per element
   cbas  =n def2-SVP    ← correlation auxiliary per element
...
$basis    file=basis    ← orbital basis file reference
$rij                    ← RI-J marker (Coulomb fit)
$ricc2
  cc2                   ← method declaration
  scs                   ← SCS modifier (turns CC2 into SCS-CC2)
  maxiter 150
$excitations
  irrep=a  multiplicity=1  nexc=5  npre=15  nstart=30
$jbas file=auxbasis     ← Coulomb auxiliary file reference
$cbas file=auxbasis     ← correlation auxiliary file reference
$last step     ricc2    ← post-run marker (Turbomole writes this on exit)
```

Audit checks: each of `basis`/`jbas`/`cbas` declarations per element should
match the claimed basis string (e.g., `def2-SVP`). All three groups
audited.

## Control-file preservation: historical vs Phase-2

| Batch | control preserved? | ricc2 outputs preserved? |
|---|---|---|
| Historical ADC(2) (`adc2_batch2_raw/Hz_*/turbo_sing/` etc.) | sometimes — varies per molecule | yes |
| Historical SCS-CC2 (`adc2_batch2_raw/Hz_*/turbo_*_scscc2/`) | **no** (only ricc2_scscc2_*.out + some `CC*` intermediates) | yes |
| Phase-2 SCS-CC2 (`scscc2_extension_n13/Hz_*/turbo_*_scscc2_svp/`) | **yes** | yes |

This is a real audit constraint: for historical SCS-CC2 jobs, the basis
audit (Step 6) can only be inferred from output text, not from the
control file directly.

## Implication for parsers

Two parsers needed:

1. `scripts/audit/parse_adc2_dest_audit.py` — looks for ADC(2) model
   declaration in output; rejects if `Spin-Component Scaling` is present
   (because that would mean SCS-CC2).

2. `scripts/audit/parse_scscc2_dest_audit.py` — looks for CC2 model
   declaration AND `Spin-Component Scaling will be applied` banner;
   rejects if either missing.

Both use `^\s*Energy:\s+...\s+H\s+(<eV>)\s+eV\s+` for state energy
extraction. Both require `ricc2 ended normally` or `ricc2 : all done`
before trusting any number.

## Paths under audit

All raw outputs live at `/home/nudt_cleng/2026/results/...` (the parent
project), NOT under `/home/nudt_cleng/2026/release_n13/...`. The release
artifact ships processed CSVs but does **not** bundle raw QC outputs.
This is itself an audit finding — see `phase4_qc.md` for the
implication.

Inventory:
- 318 `ricc2*.out` files exist under `/home/nudt_cleng/2026/`
- 1107 `control` files exist under `/home/nudt_cleng/2026/`
- 0 `ricc2*.out` files exist under `/home/nudt_cleng/2026/release_n13/`
- 0 `control` files exist under `/home/nudt_cleng/2026/release_n13/`
