# Patch B review-fix — Step 1: Path diagnosis

## Question 1: Which files does `build_cross_check_n13.py` currently write?

After the Patch B refactor (commit-pending), the script writes to:

```
<release_n13>/results/cross_check_n13.csv
<release_n13>/results/stats_n13.json
```

via `LOCAL_REPO_RESULTS = Path(__file__).resolve().parents[2] / "results"`.

This is **incorrect**: the canonical upstream directory used by
Phase 3.5 / 4 / 5 is `results/scscc2_extension_n13/`, not the
root `results/`.

## Question 2: Which files does `99_emit_canonical.py::build_scs_cc2_extended_n13()` currently read?

```
<release_n13>/results/cross_check_n13.csv
<release_n13>/results/stats_n13.json
```

via `csv_path = RESULTS / "cross_check_n13.csv"` and
`stats_path = RESULTS / "stats_n13.json"`.

Same incorrect root-level path as the writer.

## Question 3: Duplicated stale files?

`find results -name "stats_n13.json" -o -name "cross_check_n13.csv"`:

```
results/stats_n13.json                               (1068 B, modified 18:29 — Patch B)
results/cross_check_n13.csv                          (1702 B, modified 18:29 — Patch B)
results/scscc2_extension_n13/stats_n13.json          ( 694 B, modified 09:30 — stale legacy)
results/scscc2_extension_n13/cross_check_n13.csv    (1702 B, modified 09:30 — pre-Patch-B)
```

All four are tracked in git (`git ls-files` returns all four).

sha256:

| file | sha256 |
|---|---|
| `results/cross_check_n13.csv` | `1aed57e7...a89a8e9` |
| `results/scscc2_extension_n13/cross_check_n13.csv` | `1aed57e7...a89a8e9` |
| `results/stats_n13.json` | `29d9f63f...32b79eb0` |
| `results/scscc2_extension_n13/stats_n13.json` | `da4ff33b...720d0486` |

Findings:

- **CSV root vs subdir**: byte-identical (same sha256). The script
  re-wrote root CSV with identical content, so no actual divergence
  on the CSV path.
- **JSON root vs subdir**: divergent. The subdir is the pre-Patch-B
  Clopper-Pearson primary content; the root is the Patch B rule-of-
  three content. The root-level file is **stale relative to the
  canonical upstream directory**, because the upstream directory is
  `results/scscc2_extension_n13/`, not root `results/`.
- At HEAD (pre-Patch-B), root and subdir copies of `stats_n13.json`
  were **byte-identical** (verified via `git show HEAD:...`); the
  duplication is a pre-existing tracked-snapshot pattern in the
  release_n13 repo, not something Patch B introduced.

## Question 4: Need to unify to `results/scscc2_extension_n13/`?

**Yes.** The fix is:

1. Refactor `scripts/scscc2_extension/build_cross_check_n13.py` to
   write to `results/scscc2_extension_n13/`.
2. Refactor `scripts/99_emit_canonical.py::build_scs_cc2_extended_n13()`
   to read from `results/scscc2_extension_n13/`.
3. Restore root-level `results/stats_n13.json` and
   `results/cross_check_n13.csv` to their HEAD content (this undoes
   the Patch B writes to the wrong path; the root copies remain as
   the pre-existing tracked-snapshot files they were before).
4. Run the canonical chain so that the new content lives in the
   correct upstream directory.

## Decision on tracked root-level files

Per user instruction: "如果 root-level files 是 tracked legacy
files，不要删除；只记录它们是否 stale。是否删除等用户确认."

- `results/cross_check_n13.csv` (root) — tracked legacy snapshot;
  identical to the subdir canonical version after the canonical
  chain runs; can remain as a redundant tracked snapshot or be
  removed pending user decision. **Recommendation: USER DECISION
  REQUIRED on whether to git-rm this legacy snapshot.**
- `results/stats_n13.json` (root) — tracked legacy snapshot; will
  diverge from the subdir canonical version after this fix (root
  will hold pre-Patch-B Clopper-Pearson content; subdir will hold
  Patch B rule-of-three content). **Recommendation: USER DECISION
  REQUIRED on whether to git-rm this legacy snapshot or sync it to
  the new canonical content.**

I will NOT auto-delete either file. The review-fix only restores
their content to HEAD and stops writing to those paths.
