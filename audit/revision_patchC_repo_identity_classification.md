# Patch C — Repository identity classification

## Verdict: **PASS — formal repository text uses canonical INVEST-n13 URL only**

## Counts

| classification | count |
|---|---|
| CORRECT_CANONICAL_INVEST_N13 | 12 |
| OLD_REPO_REFERENCE_TO_REWRITE | **0** |
| OK_HISTORICAL_AUDIT_ONLY | 2 |
| NEEDS_MANUAL_REVIEW | 0 |

## Per-hit classification

| file:line | content | classification |
|---|---|---|
| `paper/main.tex:198` | `\href{https://github.com/lengcan276/INVEST-n13}{...}` (Data Availability section) | CORRECT_CANONICAL_INVEST_N13 |
| `paper_overleaf/main.tex:198` | mirror | CORRECT_CANONICAL_INVEST_N13 |
| `results/canonical_metrics.json:711` | `"repository": "https://github.com/lengcan276/INVEST-n13"` | CORRECT_CANONICAL_INVEST_N13 |
| `results/canonical_metrics.json:741` | `"repository_canonical": "https://github.com/lengcan276/INVEST-n13"` | CORRECT_CANONICAL_INVEST_N13 |
| `results/scscc2_extension_n13/stats_n13.json:23` | `"repository_canonical": "https://github.com/lengcan276/INVEST-n13"` | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/99_emit_canonical.py:983` | source literal for canonical `repository` field | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/99_emit_canonical.py:1026` | source literal for `repository_canonical` field | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/scscc2_extension/build_cross_check_n13.py:24` | docstring naming canonical repo | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/scscc2_extension/build_cross_check_n13.py:43` | `REPOSITORY_URL = "https://github.com/lengcan276/INVEST-n13"` | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/audit/15_validate_patchB_single_writer.py:191` | `check("scs_cc2_extended_n13.repository == INVEST-n13", ...)` | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/audit/15_validate_patchB_single_writer.py:193` | comparison literal `"https://github.com/lengcan276/INVEST-n13"` | CORRECT_CANONICAL_INVEST_N13 |
| `scripts/audit/15_validate_patchB_single_writer.py:11` | docstring: `"no FedSchNet-ReorgEnergy in generated metadata"` | OK_HISTORICAL_AUDIT_ONLY (validator declaring the negation check) |
| `scripts/audit/15_validate_patchB_single_writer.py:221` | comment for check #7 | OK_HISTORICAL_AUDIT_ONLY |
| `scripts/audit/15_validate_patchB_single_writer.py:224` | `check("no FedSchNet-ReorgEnergy in generated metadata", not fedschnet_hit)` | OK_HISTORICAL_AUDIT_ONLY (validator string literal naming the forbidden term) |

## Result

- **Zero OLD_REPO_REFERENCE_TO_REWRITE hits** in formal documentation,
  manuscript, captions, tables, cover letter, canonical metrics, or
  scripts.
- All 12 substantive `INVEST-n13` mentions are CORRECT_CANONICAL form
  (`https://github.com/lengcan276/INVEST-n13`).
- The only `FedSchNet-ReorgEnergy` literals in the working tree are
  inside `scripts/audit/15_validate_patchB_single_writer.py` as part
  of the negation/forbidden-string check (the validator's check #7
  proves the term does NOT appear in canonical metadata). These are
  OK_HISTORICAL_AUDIT_ONLY: they live in audit code that asserts the
  absence of the term, not in any formal-text reference to the wrong
  repo.

## Manuscript decision

`paper/main.tex` and `paper_overleaf/main.tex` already use the correct
INVEST-n13 URL in the Data Availability section (introduced in Patch
A). **No manuscript edits required from Patch C.**
