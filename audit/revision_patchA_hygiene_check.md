# Patch set A — hygiene check report

Repository HEAD (pre-revision): `3a72bc9`
Branch: `revision-after-phase5`
Date: 2026-05-20
Scope: hygiene-only fix on top of Patch set A. No Patch set B.

---

## Status

**PASS_WITH_USER_DECISION_REQUIRED**

(Hygiene checks pass; one user decision pending on GitHub identity for
the Data Availability URL.)

---

## What changed

1. **Internal audit phase terms removed/replaced** in
   `paper/main.tex` and `paper_overleaf/main.tex`:

   | location | before | after |
   |---|---|---|
   | §sec:limits POZ1 caveat (line ~177) | `... rather than control-file-derived (audit Phase~5, Issue~A).` | `... rather than control-file-derived.` |
   | Data Availability §1 (line ~203) | `..., and the full five-phase audit trail (\texttt{audit/phase0..5\_*.md}) are included in the release.` | (parenthetical and trailing clause deleted; sentence now ends after `figures/caption\_data/*.json`) |
   | Data Availability §2 (line ~208) | `... (audit Phase~4); they are deposited ...` | (parenthetical deleted) |
   | Data Availability §3 (line ~215) | `... in~eV; see audit Phase~5, Step~5.5) are locally raw-verified.` | `... in~eV) are locally raw-verified.` |

2. **Audit precision terms removed/replaced** in `paper/main.tex` and
   `paper_overleaf/main.tex`:

   | location | before | after |
   |---|---|---|
   | Data Availability §2 (line ~207) | `to better than $10^{-13}$~eV` | `to the precision of the reported digits` |
   | Data Availability §3 (line ~213) | `12 fully verified to $<10^{-13}$~eV` | `12 fully verified to the precision of the reported digits` |

3. **GitHub URL identity decision recorded** (see
   `USER_DECISION_REQUIRED` section below). URL itself
   not modified during hygiene fix.

---

## Verification

`audit/revision_patchA_precision_terms_grep.txt` — **empty** (no
remaining hits for `10^{-13}|1e-13|machine epsilon|machine-epsilon|
parser machine precision|numerical precision of the parser|<1×10|
<1x10` in any of the listed formal text files).

`audit/revision_patchA_internal_audit_terms_grep.txt` — **empty** (no
remaining hits for `audit Phase|Phase 4|Phase 5|Step 5\.5|Issue A|
audit/phase|internal audit|internal provenance audit` in any of the
listed formal text files).

Classification:
- STALE_INTERNAL_AUDIT_TERM_IN_MANUSCRIPT: **0**
- STALE_AUDIT_PRECISION_TERM: **0**
- NEEDS_MANUAL_REVIEW: 0
- OK_IF_IN_AUDIT_REPORT_ONLY: n/a (all formal-text hits resolved)

---

## What did not change

- No scientific numeric values changed.
- No raw calculation files changed.
- No `canonical_metrics.json` or `stats_n13.json` changed.
- No new caveat paragraphs added (only existing parenthetical
  references and audit-precision phrases edited; no sentence-level
  additions, no new claims).
- No reordering of existing manuscript content.
- No changes to `figures/caption_data/*.json`,
  `results/Table1_invest_candidates.tex`,
  `paper_overleaf/Table1_invest_candidates.tex`, or
  `reviews/cover_letter.md` during the hygiene pass (Patch set A
  edits to those files contained no internal-audit terminology and
  no machine-epsilon precision numbers, so no hygiene edits were
  needed there).
- Patch set B was not started.

---

## Remaining user decision

- **Whether to keep `https://github.com/lengcan276/INVEST-n13` as the
  permanent Data Availability URL.** See next section.

---

## USER_DECISION_REQUIRED — GitHub identity

The current Data Availability URL is:

`https://github.com/lengcan276/INVEST-n13`

The username "lengcan276" will become part of the permanent published
record if this URL is retained in the manuscript. The user should
confirm whether this is the GitHub identity they want associated
with the publication, or specify an alternative such as an
organization account before final submission.
