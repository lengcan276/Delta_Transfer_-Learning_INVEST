# Phase 5 Step 4 — "Bit-identical precision" wording resolution

## Verdict: **REWRITE REQUIRED** — file-level sha256 differs; the
## "bit-identical precision" wording is correct only at parsed-value
## level, not at file level.

## Evidence

| File | sha256 (16-char prefix) |
|---|---|
| Historical SCS-CC2 sing: `adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out` | `c8688b4249f67f51` |
| Phase-2 sanity SCS-CC2 sing: `scscc2_extension_n13/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out` | `3b83a268fe464c68` |
| **File-level identical?** | **NO** |
| Parsed ΔE_ST (historical) | -0.22033 eV (raw, 5 dp printed) |
| Parsed ΔE_ST (Phase-2 sanity) | -0.22033 eV (raw, 5 dp printed) |
| **Parsed-value identical?** | **YES**, to all printed decimals |

The two outputs differ in:
- runtime timestamps in the program banner
- hostname (`ricc2 (node11)` vs `ricc2 (node1)` per Phase 4 banner check)
- CPU/wall time blocks
- possibly per-iteration log lines
- (basically every per-run metadata line)

…but the numerical content — the final-state `Energy:` lines that
produce ΔE_ST — agrees to the printed precision (7 decimals in
Hartree, 5 decimals in eV).

## Manuscript locations of the phrase

| file | line | current wording | OK? |
|---|---|---|---|
| `paper/main.tex` | 74 | "a single **bit-identical reproduction** of \texttt{Hz\_DMAC1\_NPh21\_CF31} (Phase 1 sanity, the new pipeline recovers the historical SCS-CC2 $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ **to all 7 printed decimals**)" | **ambiguous** — the "to all 7 printed decimals" qualifier saves it, but "bit-identical reproduction" leading the phrase will be read by a reviewer as file-level |
| `paper/main.tex` | 150 | "the new pipeline recovers the historical SCS-CC2 $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ **to bit-identical precision**" | **MISLEADING** — "bit-identical precision" is the same thing as file-level identity in common usage |
| `paper_overleaf/main.tex` | 74 and 150 | (mirrors) | same |

## Recommended replacements

### Line 74 (paper/main.tex + mirror)
Current:
> "Cross-geometry stability was verified only on a single
> **bit-identical reproduction** of \texttt{Hz\_DMAC1\_NPh21\_CF31}
> (Phase 1 sanity, the new pipeline recovers the historical SCS-CC2
> $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ to all 7 printed decimals)"

Proposed:
> "Cross-geometry stability was verified only on a single
> **parser-recovered reproduction** of \texttt{Hz\_DMAC1\_NPh21\_CF31}
> (Phase 1 sanity, the new pipeline recovers the historical SCS-CC2
> $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ to the printed precision
> of the ricc2 \texttt{Energy:} lines (7 decimals in Hartree, 5
> decimals in eV); the two raw output files themselves are not
> sha256-identical because of differing run-time metadata)"

### Line 150 (paper/main.tex + mirror)
Current:
> "where the new pipeline recovers the historical SCS-CC2
> $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ **to bit-identical precision**
> (Phase~1 sanity, see Methods)"

Proposed:
> "where the new pipeline recovers the historical SCS-CC2
> $\Delta E_\mathrm{ST}=-\SI{220.33}{meV}$ **to the printed precision
> of the ricc2 output (5 decimals in eV; within 0.1 meV)** (Phase~1
> sanity, see Methods)"

### Why "to the printed precision" is the strongest defensible claim

- It is what the audit independently verifies (parsed-value match to <
  1e-13 eV, which is below the printed precision).
- It does not imply file-level identity.
- It does not understate the reproduction (which IS exact at the
  precision Turbomole prints).

### Where "bit-identical" IS allowed

The phrase "bit-identical" should be reserved for cases where raw file
sha256 hashes match. In this manuscript, no such case exists for the
SCS-CC2 comparisons. The audit has not surfaced any case where
"bit-identical" at file level would be a defensible claim.

## Priority

**HIGH** — this is a sharp-edged technical word ("bit-identical") that
a reviewer will challenge if they ask for file-level evidence. Two
occurrences in each of two files (`paper/main.tex` and
`paper_overleaf/main.tex`) = 4 locations to rewrite.

This rewrite is **safe to apply now** (no dependency on Phase 4 raw
verification — Phase 4 ALREADY established the file-level
non-identity).
