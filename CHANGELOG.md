# Changelog

## 2026-05-20 — n=13 SCS-CC2 cross-check extension

**Major paper update**: SCS-CC2/def2-SVP cross-check extended from 4 lead
candidates (original audit-clean version) to all **13 ADC(2)-screened INVEST
candidates** (the Table 1 shortlist).

### Headline result
- **0 sign disagreement in the n=13 ADC(2)-screened cohort**.
- One-sided 95% rule-of-three upper bound on within-screen sign-disagreement
  rate: **≈ 3/13 = 0.23**.
- All 13 SCS-CC2 ΔE_ST values are systematically more negative than the
  corresponding ADC(2) values (range −10 to −194 meV, mean −110 meV).
- Result is framed as **method-family consistency** within the ADC(2)/CC2
  hierarchy, *not* method-independent confirmation against an unrelated
  theory level. An independent-family triangulation (CCSD, CC3, or NEVPT2
  on a small subset) is identified as the natural next validation step.

### Statistical reframing (vs previous n=4 version)
| | Before (n=4) | After (n=13) |
|---|---|---|
| Claim | "Clopper–Pearson 95% CI [0.40, 1.00]" | "0 disagreement; rule-of-three upper bound on failure rate ≈ 0.23" |
| Scope | 4-molecule lead-set spot-check | per-molecule sign confirmation of the entire pre-registered shortlist |
| Cohort framing | "homogeneous lead set" | "two-batch composite": 4 historical + 9 new |

### Why rule-of-three, not Clopper–Pearson
The 13 molecules are **not** an i.i.d. random sample — they are the cohort
ADC(2) pre-screens as INVEST. Reporting `[0.7529, 1.0000]` (4-decimal
Clopper–Pearson lower bound) implicitly treats them as a random-sample hit
rate and is statistically misleading. We instead report an honest one-sided
upper bound on within-screen sign-disagreement.

### Caveats now explicit in the paper
1. ADC(2)-pre-screened cohort, not i.i.d. → rule-of-three, not CP CI.
2. Monotonic SCS-CC2 > ADC(2) (in absolute |ΔEST|) → method-family
   consistency, not method-independence.
3. **Hz_NPh21_Cz2** sits at the narrowest cross-method margin (ΔΔEST = 10
   meV), comparable to typical SCS-CC2 uncertainty; flagged as the most
   likely sign-flip candidate under further method change.
4. Two-batch composite: 4 historical use `adc2_batch2_final` geometries
   (gnorm 6.6e-5 to 7.6e-4 Eh/a0); 9 new use `delta_dft` geometries (gnorm
   5.6e-5 to 1.5e-4). Cross-geometry stability verified only on **one**
   bit-identical reproduction (Hz_DMAC1_NPh21_CF31, Phase 1 sanity).
   A broader cross-geometry sensitivity sweep is deferred to future work.

### What's new in this commit
- `results/scscc2_extension_n13/cross_check_n13.csv` — 13-row cross-check table
- `results/scscc2_extension_n13/stats_n13.json` — Clopper–Pearson + rule-of-three stats
- `results/scscc2_extension_n13/phase{0,1,2}_*.md` — Phase-by-phase execution
  reports (geometry decision, sanity reproduction, mini-batch checkpoint,
  Phase 2.4 plan + submission record)
- `scripts/scscc2_extension/build_cross_check_n13.py` — assembles the
  13-molecule table + Clopper–Pearson / rule-of-three stats from raw
  Turbomole `ricc2.out` files
- `scripts/scscc2_extension/plot_fig4_n13.py` — regenerates Fig 4 with
  13 markers (Times New Roman, 300 DPI) + caption JSON
- `scripts/scscc2_extension/parsers/parse_scscc2_dest.py` — robust regex
  parser with `ricc2 : all done` precondition + `--selftest` mode
  (reproduces historical -0.22033 eV bit-identical)
- `scripts/scscc2_extension/templates/run_scscc2_svp_v2.slurm` — hardened
  Slurm wrapper with stage-skip restart, `$actual` zombie defense,
  `--no-requeue`, auto-clean of Turbomole CC* scratch on success
- `scripts/scscc2_extension/templates/run_scscc2_svp.slurm` — v1 (legacy,
  no stage-skip)
- `scripts/scscc2_extension/setup_scscc2_svp_on_login.sh` — byte-aligned
  with historical `setup_tzvp_on_login.sh` (def2-SVP variant)
- `paper/main.tex` — 7 framing rewrites (Abstract / Intro / §3.5 / §3.5
  continuation / Fig 4 caption / §5 Limitations / §6 Conclusions), plus
  Methods §74 cohort + nexc disclaimer; `\input` paths made
  Overleaf-compatible
- `figures/Fig4_crosscheck.pdf` / `.png` — regenerated with 13 markers
- `results/canonical_metrics.json` — added `scs_cc2_extended_n13` block
  with per-molecule data (ADC2 / SCS-CC2 ΔEST, abs values for audit
  matching), rule-of-three bound, narrowest-margin molecule
- `scripts/audit_numbers.py` — M4 rule updated (was "n=4 selected" → now
  "n=13 INVEST, not 21 positive-gap"); STRIP_PATTERNS adds Phase~N.N /
  Round~N to avoid version-label false positives

### Audit status
```
numbers extracted     = 485
non-trivial numbers   = 251
unresolved            = 0       ✓
Major checks tripped  = 0 / 7   ✓
```

### Overleaf package
`/home/nudt_cleng/2026/INVEST_paper_overleaf_n13_v3.zip` (3.1 MB)
- Contains main.tex + Table1/Table2 + figures/ (all PDF/PNG)
- Path `\input{Table1_invest_candidates.tex}` works when extracted at
  Overleaf root

### Compute campaign log
- Phase 1 sanity: Hz_DMAC1_NPh21_CF31, **bit-identical** reproduction of
  historical SCS-CC2 ΔEST = −0.22033 eV (parser self-test PASS)
- Phase 2.2 (2 molecules): Hz_NEt22_CF31, Hz_DMAC2_SO2Ph1 — both sign-retain
- Phase 2.4 (7 molecules): Hz_NH22_SO2Ph1, Hz_DMAC1_NPh21_SO2Ph1,
  Hz_Cz1_NPh21_CF31, Hz_NPh22_CN1, Hz_NEt21_NPh22, Hz_NPh21_Cz2, Hz_NPh23
  — all sign-retain (Hz_NPh23 required `nexc=5→2` patch for SCS-CC2 sing
  convergence; S1 unaffected)
- Cluster events handled: zombie `$actual` contamination after `scancel`
  race (v2 wrapper defensive `sed`), filesystem read-only window
  post-maintenance, intel-partition `down*` recovery
- Storage cleanup: 42 TB ORCA scratch tmp in `adc2_validation/` removed
  (`.out`/`.gbw`/`.energy` results backed up locally first)

## Earlier history
See `git log` for prior commits (audit pipeline, cover letter retargeting,
Fisher p-value reconciliation, etc.).
