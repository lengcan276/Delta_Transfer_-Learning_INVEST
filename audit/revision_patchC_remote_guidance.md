# Patch C — Git remote configuration: report and guidance

## Current state (`git remote -v`)

```
fed_old   https://github.com/lengcan276/FedSchNet-ReorgEnergy.git  (fetch)
fed_old   https://github.com/lengcan276/FedSchNet-ReorgEnergy.git  (push)
invest    git@github.com:lengcan276/INVEST-n13.git                 (fetch)
invest    git@github.com:lengcan276/INVEST-n13.git                 (push)
```

## Classification

| remote | URL | classification |
|---|---|---|
| `invest` | `git@github.com:lengcan276/INVEST-n13.git` | **CANONICAL** — matches the user-confirmed Data Availability URL `https://github.com/lengcan276/INVEST-n13` |
| `fed_old` | `https://github.com/lengcan276/FedSchNet-ReorgEnergy.git` | **OLD_REPO_REMOTE** — legacy / wrong location; should be removed before any future push to avoid accidentally publishing to the wrong repository |

## Recommended user-side commands (NOT auto-executed)

The audit does not auto-modify git remote configuration. The
following commands are **guidance only** for the user to run
interactively when ready:

```bash
# Remove the legacy/wrong remote (recommended):
git remote remove fed_old

# Verify only the canonical remote remains:
git remote -v
# Expected output:
#   invest  git@github.com:lengcan276/INVEST-n13.git  (fetch)
#   invest  git@github.com:lengcan276/INVEST-n13.git  (push)
```

Optionally, rename `invest` → `origin` if the user prefers the
default name (also not auto-executed):

```bash
git remote rename invest origin
```

## Constraints respected

- No `git remote remove` was executed by Patch C.
- No `git remote set-url` was executed by Patch C.
- No `git remote add` was executed by Patch C.
- No `git remote rename` was executed by Patch C.

The remote-configuration change is **USER_DECISION_REQUIRED**: the
user should run the recommended `git remote remove fed_old` (or
equivalent) manually before any first push of the release.
