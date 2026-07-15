# Phase 0 — Repository Snapshot & Sensitive-Info Scan

Audit start: 2026-05-20
Audit working directory: `/home/nudt_cleng/2026/release_n13`
Audit role: independent auditor (NOT project collaborator)

---

## 0.1 Working-tree state

`git status --short` (initial check, after removing scratch file):
```
(empty)
```
Status: **clean**. No uncommitted/untracked work present before audit. Audit
proceeds.

### Repository HEAD
```
commit  3a72bc9599c8bda2bdf70f53303b01b76b47d9d3
title   docs: add exported session log
```
(see `AUDIT_COMMIT.txt`)

### Last 20 commits
First 5 lines of `AUDIT_GIT_LOG.txt`:
```
3a72bc9 docs: add exported session log
2441973 INVEST paper release — n=13 SCS-CC2 cross-check extension (audit-clean)
```
(only 2 commits in this release_n13 fork — earlier history lives in
the parent github_upload repo and is not part of this audit boundary;
see `AUDIT_GIT_LOG.txt` for full list)

### File inventory + sha256 manifest
- Total files snapshotted: **189**
- Manifest: `sha256_manifest_all_files.txt` (sha256 + path, sorted)
- Counter: `sha256_manifest_count.txt`
- Scope: all files under repository root, excluding `.git/` and `audit/`

This is the immutable evidence baseline for the rest of the audit. Any
later step that compares file content uses these sha256 sums.

---

## 0.2 Sensitive-information scan

Patterns scanned (case-insensitive):
`token | password | passwd | secret | github_pat | ghp_ | private[-_ ]?key |
BEGIN RSA | BEGIN OPENSSH | Authorization | Bearer`

Files scanned: `*.md *.txt *.py *.sh *.json *.yaml *.yml *.tex` (excluding
`.git/` and `audit/`).

Raw scan output: `session_secret_scan.txt` (8 lines).

### Hit triage

| Line in scan | Origin file | Match | Classification |
|---|---|---|---|
| 1 | `paper/audit_reports/consistency_audit.md` | "numeric tokens" | **benign** — NLP/regex sense of "token" |
| 2 | `scripts/audit_numbers.py` | "numeric tokens" | **benign** — same |
| 3 | `session.md:1087` | "token 匹配" (Chinese) | **benign** — discussion of pattern matching |
| 4 | `session.md:2520` | "不要主动轮询 squeue 浪费 token" | **benign** — discussion of API budget tokens, no value present |
| 5 | `session.md:9388` | "用 gh CLI 登录（需要交互浏览器/token）" | **benign** — discussion of OAuth flow, no value present |
| 6 | `session.md:9392` | "跟着提示输 token" | **benign** — same |
| 7 | `session.md:9394` | "临时切到 HTTPS + Personal Access Token" | **benign** — instructions only |
| 8 | `session.md:9399` | "https://github.com/settings/tokens 生成" | **benign** — link, no value |

### Findings

- **0** actual credentials, OAuth tokens, GitHub PATs, SSH private keys,
  Bearer tokens, or "BEGIN ... KEY" blocks found.
- The 8 matches are all natural-language occurrences of the word "token"
  in either (a) statistical/NLP context ("numeric tokens" in audit code)
  or (b) procedural instruction text about how to authenticate to GitHub.
- No remediation required.

---

## 0.3 Deliverables produced this Phase

Files written by Phase 0:
```
audit/AUDIT_COMMIT.txt                       (1 line)
audit/AUDIT_GIT_LOG.txt                      (2 lines — only 2 commits in this fork)
audit/sha256_manifest_all_files.txt          (189 entries)
audit/sha256_manifest_count.txt              (count file)
audit/session_secret_scan.txt                (8 hits, all benign)
audit/phase0_snapshot.md                     (this file)
```

Hard-constraint compliance:
- ✓ No file under `paper/`, `results/`, `data/`, `figures/`, `scripts/`
  (other than `scripts/audit/` which is empty so far) was modified.
- ✓ All audit output written under `audit/`.
- ✓ No `git add`, `git commit`, `git push`, `git rebase`, no git config
  changes.
- ✓ No remote connection. No `ssh`, no `rsync`, no `scp`, no `curl`/`wget`.
- ✓ No claim made about data authenticity yet — only snapshot + secret
  scan.

---

## 0.4 Status & gate

**Phase 0: COMPLETE.**

Repository state is captured. Sensitive-information scan is clean. The
audit baseline is now fixed at commit `3a72bc9` with the sha256 manifest
above.

**Halting.** Waiting for user instruction "继续 Phase 1" before proceeding
to Phase 1 (Pollice 446 external cross-check).
