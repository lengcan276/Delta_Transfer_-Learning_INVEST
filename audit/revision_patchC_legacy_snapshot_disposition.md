# Patch C — Legacy root snapshot disposition

## Verdict: **LEGACY_REFERENCE_FOUND** — root snapshots NOT deleted

Per the Step 3 decision rule: if any `ACTIVE_REFERENCE_TO_LEGACY_ROOT_PATH`
exists, do not delete root-level files; await user decision.

## Files in scope

| path | sha256 | size (B) | tracked? |
|---|---|---|---|
| `results/cross_check_n13.csv` (legacy root) | `1aed57e7…a89a8e9` | 1702 | YES (HEAD) |
| `results/stats_n13.json` (legacy root) | `da4ff33b…720d0486` | 694 | YES (HEAD; pre-Patch-B content) |

Both reverted to HEAD content in the Patch B review-fix; the canonical
upstream copies live under `results/scscc2_extension_n13/`.

## Per-hit classification of the 49 reference-grep hits

| classification | count |
|---|---|
| ACTIVE_REFERENCE_TO_EXTENSION_PATH | 39 |
| **ACTIVE_REFERENCE_TO_LEGACY_ROOT_PATH** | **1** |
| OK_AUDIT_OR_REPORT_REFERENCE | 4 (README.md captions; phase2_4 plan; figure caption metadata) |
| OK_FILENAME_GENERIC (bare filename without root-path qualifier) | 5 |
| NEEDS_MANUAL_REVIEW | 0 |

## The single ACTIVE_REFERENCE_TO_LEGACY_ROOT_PATH hit

`scripts/99_emit_canonical.py:958`:

```python
incon(
    "scs_cc2_extended_n13.rule_of_three_upper_bound",
    upstream_rule, "results/stats_n13.json",
    rule_of_three_upper_bound, "recomputed from n_total in 99_emit_canonical.py",
)
```

The second argument to `incon()` is a **source label string** for the
`upstream_rule` value. The actual file read happens at line 893:
`stats_path = upstream_dir / "stats_n13.json"` =
`results/scscc2_extension_n13/stats_n13.json`. The string literal at
line 958 is therefore a stale label — it points at the legacy root
path even though the value originated from the extension subdirectory.

This is a **mislabel**, not a real read or write of the legacy root
file. It only triggers if `upstream_rule` disagrees with the recomputed
rule-of-three value, which currently does not happen (they agree to
floating-point precision).

## Decision

- **Do not delete** `results/cross_check_n13.csv` or
  `results/stats_n13.json` at the repository root.
- Document the LEGACY_REFERENCE_FOUND status here.
- Recommend (but do not auto-execute) two follow-ups to the user:

  **Follow-up F1 (mislabel fix, trivial):**
  Edit `scripts/99_emit_canonical.py:958` to read
  `"results/scscc2_extension_n13/stats_n13.json"` instead of
  `"results/stats_n13.json"`. This is a one-character-bag string
  change in an audit-message label; behaviourally inert.

  **Follow-up F2 (root snapshot cleanup):**
  After F1 lands, the user may choose to `git rm results/cross_check_n13.csv`
  and `git rm results/stats_n13.json` since no code or text would
  then reference the root paths.

Both follow-ups are USER_DECISION_REQUIRED and orthogonal to the
Patch C deliverables.

## Other (`OK_AUDIT_OR_REPORT_REFERENCE`, `OK_FILENAME_GENERIC`) hits

- `README.md` lines 56, 102, 103 — uses the **canonical extension
  path** for tree listing and quick-reference. OK.
- `results/scscc2_extension_n13/phase2_4_plan.md:151` —
  historical phase-2.4 plan; references bare filename
  `cross_check_n13.csv`. OK (it's an audit-tree historical document
  inside the extension directory; the filename qualifier is implicit
  from context).
- `paper_overleaf/figures/caption_data/Fig4_crosscheck.json:93-94` —
  references the **canonical extension path** in figure caption
  metadata. OK.
- `scripts/audit/15_validate_patchB_single_writer.py:207-216` — reads
  the **canonical extension path** in the Patch B validator. OK.
- All `scripts/scscc2_extension/build_cross_check_n13.py` and
  `scripts/99_emit_canonical.py` hits (except line 958) — extension
  path. OK.
- `scripts/scscc2_extension/plot_fig4_n13.py:18-19` — points at the
  external compute tree `/home/nudt_cleng/2026/results/scscc2_extension_n13/`,
  not the legacy root snapshot. OK.

## Status summary

- **No active code reads or writes the root-level legacy snapshots.**
- One source-label string literal in
  `scripts/99_emit_canonical.py` still names the legacy root path;
  that literal is documented above and is a benign mislabel rather
  than an active dependency.
- Per the strict decision rule, the legacy root snapshots are kept
  in place until the user explicitly decides on follow-ups F1/F2.
