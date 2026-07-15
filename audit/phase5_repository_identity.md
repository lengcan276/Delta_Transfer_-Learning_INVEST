# Phase 5 Step 9 — Repository identity audit

Audit phase: Phase 5 (re-execution per integrated prompt)
Repository HEAD: `3a72bc9`
Date: 2026-05-20

---

## Canonical repository

**`https://github.com/lengcan276/INVEST-n13`**

This is the authoritative remote for the `release_n13` artifact and
all downstream submission/archival references.

## Legacy / wrong repository

**`https://github.com/lengcan276/FedSchNet-ReorgEnergy`** — classified
as **OLD_REPO_REFERENCE_TO_REWRITE_LATER**.

This GitHub repo belongs to an unrelated earlier project
(FedSchNet reorganization-energy work). The INVEST `release_n13`
branch was temporarily pushed there during an earlier session, but
that location is incorrect and must not be referenced in any
manuscript / Data Availability / README / CHANGELOG text going
forward.

---

## Current git remote state

```
fed_old  https://github.com/lengcan276/FedSchNet-ReorgEnergy.git  (fetch)
fed_old  https://github.com/lengcan276/FedSchNet-ReorgEnergy.git  (push)
invest   git@github.com:lengcan276/INVEST-n13.git                (fetch)
invest   git@github.com:lengcan276/INVEST-n13.git                (push)
```

Both remotes are presently configured. Only `invest` is canonical.
`fed_old` should be removed (or at minimum never used for push) once
the release is finalized.

**Audit constraint compliance:** the audit did NOT touch git config.
The remote inventory above is observational only.

---

## Reference inventory

### FedSchNet-ReorgEnergy occurrences in repository content

`grep -rln "FedSchNet"` over `*.md *.tex *.json *.py *.csv`:

| file | classification |
|---|---|
| `session.md` | historical session log (export of prior Claude Code transcript) |
| `audit/_tmp_phase3_6_patch_workspace/session.md` | tmp copy of session log (audit workspace) |
| `audit/_tmp_repro_repo/session.md` | tmp copy of session log (audit workspace) |

**Total: 3 files, all session-log copies (~21 line hits).**

**Critical finding:** zero FedSchNet references in any of
`paper/`, `results/`, `data/`, `figures/`, `reviews/`, `scripts/`,
or `paper_overleaf/`. The wrong-repo string lives only inside the
captured conversation transcript, not in the release artifact itself.

This means the manuscript and shipped artifacts have **no
substantive contamination** from the wrong-repo episode; the
remediation is purely about repo metadata (git remotes), and about
adding the *correct* INVEST-n13 reference in future-facing places
(README / Data Availability / cover-letter).

### INVEST-n13 occurrences in repository content

`grep -rln "INVEST-n13"` over the same extensions: **0 hits**.

The correct canonical repo URL is not yet present anywhere in the
release artifact. It must be added during Patch set C/D execution
(Data Availability section + README + cover-letter).

---

## Evidence tier

| | |
|---|---|
| Verdict | **REPO_IDENTITY_CORRECTION_REQUIRED_BUT_LOW_BLAST_RADIUS** |
| FedSchNet contamination in manuscript text | **None** (0 hits in paper/results/figures/scripts/reviews) |
| FedSchNet contamination in audit workspace | 3 session.md copies (historical log) |
| INVEST-n13 references in manuscript text | **None** (must be added) |
| Git remote pointing to wrong repo | **Present** (`fed_old`) — should be removed |
| Git remote pointing to correct repo | **Present** (`invest`) |
| Manuscript revision required | **Yes — additive only** (add canonical URL to Data Availability / README; no FedSchNet text to delete from the manuscript) |

---

## Recommended remediation (consolidated in Patch sets C and D)

### Patch set C — repo metadata
1. Remove `fed_old` git remote (user action, not an audit action):
   ```
   git remote remove fed_old
   ```
2. Confirm `invest` points to `git@github.com:lengcan276/INVEST-n13.git`.
3. When creating the archive tarball / DOI deposit (Patch set C
   item 1), embed `https://github.com/lengcan276/INVEST-n13` in the
   `README.md` and in any `CHANGELOG` or `CITATION.cff`.
4. The session.md historical log inside `audit/` may be retained
   as-is (audit trail), or scrubbed before public release if the
   FedSchNet string is judged confusing for downstream readers.
   Recommendation: retain with a one-line clarifying header
   (`NOTE: historical log; canonical repo is INVEST-n13, not
   FedSchNet-ReorgEnergy`).

### Patch set D — manuscript text
1. In any Data Availability / Acknowledgements / footnote that names
   the project repository, write
   `https://github.com/lengcan276/INVEST-n13` (NOT FedSchNet).
2. In the suggested Data Availability paragraph (Patch set A item 5),
   the URL placeholder `<archive URL/DOI>` should be replaced with
   `https://github.com/lengcan276/INVEST-n13` once the deposit is
   made (or its Zenodo DOI when minted).

---

## What this audit explicitly does NOT do

- Does not run any `git remote remove` / `git remote add` / `git
  config` command (read-only constraint).
- Does not push to either remote.
- Does not edit any file under `paper/`, `results/`, `data/`,
  `figures/`, `reviews/`, or `scripts/`.
- Does not delete or rewrite the historical `session.md` files.

## What this audit explicitly DOES claim

- The canonical repository for this manuscript and its release
  artifact is `https://github.com/lengcan276/INVEST-n13`.
- `https://github.com/lengcan276/FedSchNet-ReorgEnergy` is an
  OLD_REPO_REFERENCE_TO_REWRITE_LATER and must not appear in
  manuscript / DOI deposit / Data Availability text.
- No FedSchNet reference contaminates the manuscript content; the
  required correction is metadata-level (git remote) plus additive
  (add canonical URL to README/Data Availability), not destructive.
