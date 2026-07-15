# Patch D Step 7 — LaTeX compile summary

## Status: **PASS_LATEX_COMPILED** (with pre-existing missing-bib warnings)

## Environment

```
LATEX_AVAILABLE=latexmk
ACS_CLASS_AVAILABLE=YES
LATEX_STATUS=ATTEMPTED_LATEXMK
```

`latexmk` available at the host's TinyTeX installation; `achemso.cls`
resolvable via `kpsewhich`. Compile was attempted.

## Compile result

| metric | value |
|---|---|
| `latexmk` exit code | **0** |
| Output PDF | `main.pdf` (25 pages, 464 724 bytes) at the repo root (latexmk's CWD) |
| Compile attempted | YES |
| PDF produced | YES |
| Fatal errors | none |

## Warnings (non-fatal, pre-existing)

- **4 undefined citations** in `paper/main.tex`:
  - `Hellweg2008` on input line 161 (also on page-cited line 177)
  - `Tajti2009` on input line 161 (also on page-cited line 177)
  - These two `\cite{Hellweg2008,Tajti2009}` references describe the
    spin-component-scaling shift literature and are present in the
    Results paragraph that was authored before Patch A. The
    `thebibliography` environment in `paper/main.tex` does not contain
    matching `\bibitem{Hellweg2008}` / `\bibitem{Tajti2009}` entries.
    **This is a pre-existing manuscript bibliography gap and was NOT
    introduced by Patch A / B / B-tail / C / D.** Out of Patch D
    scope (which forbids scientific rewriting and bibliography
    expansion).
- Several Overfull / Underfull `\hbox` warnings on the new Data
  Availability URLs (long unbreakable URL strings). Cosmetic;
  acceptable per Step 7 rules.
- 4 `Package hyperref Warning: Suppressing empty link` warnings —
  cosmetic.

## Missing figures

None. All `\includegraphics` resolved
(`Fig0_workflow.pdf`, `Fig1_ablation.pdf`, `Fig2_uq_shift.pdf`,
`Fig3_classification.pdf`, `Fig4_crosscheck.pdf`, `Fig5_al_value.pdf`).

## Decision

Per Step 7 decision rules:

- Rule 1 (env not ready) — N/A (env IS ready).
- Rule 2 (external class missing) — N/A (achemso resolved).
- Rule 3 (compile fails due to patch-introduced syntax) — N/A
  (compile succeeded; 4 undefined citations are pre-existing
  bibliography gaps, not patch-introduced syntax errors).
- Rule 4 (compile succeeds) — **APPLIES**: mark
  **PASS_LATEX_COMPILED**.

## Build artefact cleanup

The compile produced the following transient files at the repo root:
`main.aux`, `main.fdb_latexmk`, `main.fls`, `main.log`, `main.out`,
`main.pdf`, `acs-main.bib`. These were removed after the compile
test (`rm -f main.* acs-main.bib`) to keep the working tree clean,
and `.gitignore` was extended to ignore them by exact path
(`/main.aux`, `/main.fdb_latexmk`, ..., `/acs-main.bib`) so any
future compile attempt at the repo root does not pollute git
status. The patterns are anchored to the root (`/main.aux`, not
`*.aux`) so they cannot accidentally ignore Turbomole `ricc2_*.out`
raw files in `results/scscc2_extension_n13/`.

## USER_DECISION_REQUIRED (carry forward)

The 4 undefined-citation warnings (`Hellweg2008`, `Tajti2009`)
should be resolved before journal submission by adding the
corresponding `\bibitem` entries to the `thebibliography`
environment in `paper/main.tex` and `paper_overleaf/main.tex`. This
is **out of Patch D scope** (would require bibliography expansion /
scientific reference addition) and is recorded here for a future
manuscript-revision pass.
