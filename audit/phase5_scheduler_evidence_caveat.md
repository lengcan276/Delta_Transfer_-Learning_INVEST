# Phase 5 Step 6 — Scheduler evidence caveat

## Evidence label: **RUNTIME_BANNER_COMPUTE_NODE_SUPPORTED**

## Verified facts (no overclaim, no underclaim)

### 1. Numerical raw-output evidence
> All 13 SCS-CC2 ΔE_ST values for the n=13 cohort are independently
> reproduced from local `ricc2_scscc2_*.out` files by the audit's
> own parser (`scripts/audit/parse_scscc2_dest_audit.py`), with
> method-banner-priority enforcement (CC2 + Spin-Component Scaling +
> Grimme factors C_os=1.2, C_ss=0.333). All 13 parsed values agree
> with `cross_check_n13.csv` to <1×10⁻¹³ eV.

### 2. Runtime node evidence
> Compute-node hostnames are recorded **directly in the ricc2 program
> banner at runtime** (line of the form `ricc2 (nodeN) : TURBOMOLE
> rev. V7.5.1 …`). This is intrinsic to the Turbomole output and
> cannot be retroactively edited without breaking the rest of the
> output's internal consistency. Banners observed across the 13
> cohort molecules show hostnames `node1, node6, node11, node12, …`
> (compute nodes), never `master`, `login`, `head`, `submit`, or
> `frontend`.

### 3. Scheduler-log limitation
> Independent Slurm scheduler logs (`slurm-<jobid>.out`) were **not
> preserved in the local audit snapshot**. The release_n13 repo
> contains only the v2 wrapper templates (`run_scscc2_svp.slurm`,
> `run_scscc2_svp_v2.slurm`), not the per-job slurm stdout files.
> Scheduler provenance is therefore **runtime-banner-supported
> rather than scheduler-log-confirmed**.

### 4. Login-node red-flag check
> The audit scanned all `ricc2 (X)` banner hostnames in the 13
> SCS-CC2 cohort. **No hostname containing `login`, `head`, `master`,
> `submit`, or `frontend` was found.** The historical 4 + 9
> Phase-2 entries all report compute-node names.

## Tier assignments (per audit's tier rubric)

| Tier | Definition | Count (n=13 SCS-CC2 cohort) |
|---|---|---|
| FULL | slurm log + SLURM_JOB_ID + Hostname: line + start/end timestamps | **0** |
| PARTIAL | slurm log present but missing some fields | **0** |
| **INFERRED** | no slurm log; ricc2.out banner shows `ricc2 (nodeN)` compute hostname | **13** |
| NONE | no compute-node evidence at all | **0** |
| POSSIBLE_LOGIN_NODE_RED_FLAG | banner shows `master/login/head/submit/frontend` | **0** |

All 13 = **INFERRED** = **RUNTIME_BANNER_COMPUTE_NODE_SUPPORTED**.

## Recommended manuscript / Data Availability wording

> "The SCS-CC2 raw outputs contain runtime ricc2 banners with
> compute-node hostnames (e.g., `ricc2 (node1)`, `ricc2 (node6)`),
> and no positive login-node execution evidence was found in the
> audit snapshot. Local Slurm scheduler logs (`slurm-<jobid>.out`)
> were not preserved alongside the ricc2 outputs at the time of
> archival; scheduler provenance is therefore
> **runtime-banner-supported** rather than independently
> **scheduler-log-confirmed**. The runtime-banner evidence is
> intrinsic to the Turbomole output format and cannot be
> retroactively edited without breaking the rest of the output's
> internal consistency."

## What this audit explicitly does NOT claim

- That the calculations were executed under any specific Slurm
  partition or with any specific resource allocation. The slurm log
  that would have shown that is not preserved.
- That no human edited the ricc2.out files between writing and
  audit. The audit can only verify file content vs Turbomole format,
  not chain-of-custody.
- That the banner hostnames cannot be spoofed. They can in principle
  be edited, but doing so without also adjusting cpu-time/wall-time
  and the per-iteration timestamps would produce a detectably
  inconsistent output. None of the 13 outputs show such inconsistency.

## What this audit explicitly DOES claim

- 13/13 SCS-CC2 ΔE_ST values reproduce from local raw outputs to <
  machine precision.
- 13/13 outputs declare method = SCS-CC2 in the runtime banner.
- 13/13 outputs report compute-node hostnames (never login/master).
- 0/13 outputs trigger the login-node red-flag pattern.
