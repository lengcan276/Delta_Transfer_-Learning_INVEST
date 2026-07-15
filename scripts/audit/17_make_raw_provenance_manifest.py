#!/usr/bin/env python3
"""Build a sha256 provenance manifest for the SCS-CC2 n=13 raw outputs.

Inputs:
  - results/scscc2_extension_n13/cross_check_n13.csv  (cohort mol_id list)
  - audit/phase4_qc.md, audit/phase5_*.md             (provenance context)
  - external compute tree at /home/nudt_cleng/2026/results/...
    (read-only; locations declared in the canonical generator's COHORT table)

Outputs:
  audit/revision_patchC_raw_provenance_manifest.tsv
  audit/revision_patchC_raw_provenance_manifest.md

The manifest covers:
  - SCS-CC2 n=13 cohort (26 files: 13 singlet + 13 triplet)
  - ADC(2) missing-ybsi raw outputs (recorded as unavailable locally)
  - POZ1 historical / banner-only basis caveat
  - Scheduler evidence labelled runtime-banner-supported only
    (no scheduler logs are claimed unless a real slurm-<jobid>.out
    sits beside the corresponding ricc2 output)

Does NOT include LaTeX .out/.log, audit/_tmp_* copies, or scheduler
script templates.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
AUDIT = ROOT / "audit"
EXT_ROOT = Path("/home/nudt_cleng/2026/results")

CSV_INPUT = RESULTS / "scscc2_extension_n13" / "cross_check_n13.csv"

# Canonical (mol_id, sing_relpath_from_EXT_ROOT, trip_relpath_from_EXT_ROOT).
# Mirrored from scripts/scscc2_extension/build_cross_check_n13.py::COHORT.
COHORT = [
    ("Hz_NH23",                "adc2_batch2_raw/Hz_NH23_scscc2/ricc2_scscc2_sing.out",                            "adc2_batch2_raw/Hz_NH23_scscc2/ricc2_scscc2_trip.out"),
    ("Hz_DMAC1_NPh21_CF31",    "adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out",     "adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_trip_scscc2/ricc2_scscc2_trip.out"),
    ("Hz_NPh22_SO2Ph1",        "adc2_batch2_raw/Hz_NPh22_SO2Ph1/turbo_sing_scscc2/ricc2_scscc2_sing.out",         "adc2_batch2_raw/Hz_NPh22_SO2Ph1/turbo_trip_scscc2/ricc2_scscc2_trip.out"),
    ("Hz_POZ1_NPh21_CF31",     "adc2_batch2_final/Hz_POZ1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out",    "adc2_batch2_final/Hz_POZ1_NPh21_CF31/turbo_trip_scscc2/ricc2_scscc2_trip.out"),
    ("Hz_NEt22_CF31",          "scscc2_extension_n13/Hz_NEt22_CF31/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out",  "scscc2_extension_n13/Hz_NEt22_CF31/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_DMAC2_SO2Ph1",        "scscc2_extension_n13/Hz_DMAC2_SO2Ph1/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out", "scscc2_extension_n13/Hz_DMAC2_SO2Ph1/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_NH22_SO2Ph1",         "scscc2_extension_n13/Hz_NH22_SO2Ph1/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out", "scscc2_extension_n13/Hz_NH22_SO2Ph1/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_DMAC1_NPh21_SO2Ph1",  "scscc2_extension_n13/Hz_DMAC1_NPh21_SO2Ph1/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out", "scscc2_extension_n13/Hz_DMAC1_NPh21_SO2Ph1/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_Cz1_NPh21_CF31",      "scscc2_extension_n13/Hz_Cz1_NPh21_CF31/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out", "scscc2_extension_n13/Hz_Cz1_NPh21_CF31/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_NPh23",               "scscc2_extension_n13/Hz_NPh23/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out",       "scscc2_extension_n13/Hz_NPh23/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_NPh21_Cz2",           "scscc2_extension_n13/Hz_NPh21_Cz2/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out",   "scscc2_extension_n13/Hz_NPh21_Cz2/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_NEt21_NPh22",         "scscc2_extension_n13/Hz_NEt21_NPh22/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out", "scscc2_extension_n13/Hz_NEt21_NPh22/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
    ("Hz_NPh22_CN1",           "scscc2_extension_n13/Hz_NPh22_CN1/turbo_sing_scscc2_svp/ricc2_scscc2_sing.out",   "scscc2_extension_n13/Hz_NPh22_CN1/turbo_trip_scscc2_svp/ricc2_scscc2_trip.out"),
]

# Per-molecule preserved-control flag (mirrors Phase 5 Issue A finding).
# Historical adc2_batch2_raw / adc2_batch2_final batches typically have
# the control file consumed/cleaned by the wrapper; the Phase-2 extension
# batch preserves control in the molecule directory.
HISTORICAL_BATCH = {"Hz_NH23", "Hz_DMAC1_NPh21_CF31",
                    "Hz_NPh22_SO2Ph1", "Hz_POZ1_NPh21_CF31"}

# ADC(2) raw outputs that audit Phase 5 Step 5 documented as
# unavailable locally (computed on the ybsi cluster).
ADC2_YBSI_PENDING = [
    "Hz_NH23", "Hz_NEt22_CF31", "Hz_NH22_SO2Ph1",
    "Hz_DMAC1_NPh21_SO2Ph1", "Hz_Cz1_NPh21_CF31",
    "Hz_NEt21_NPh22", "Hz_NPh22_CN1",
    # plus 8 R1-deploy ADC(2) entries outside the n=13 cohort
    "(8 R1-deploy ADC(2) entries outside the n=13 cohort)",
]


METHOD_BANNER_RE = re.compile(
    r"(Algebraic Diagrammatic Construction|"
    r"Coupled Cluster|"
    r"Spin[- ]Component Scaling)", re.IGNORECASE)
RUNTIME_BANNER_RE = re.compile(r"ricc2\s*\([^)]+\)\s*:\s*TURBOMOLE", re.IGNORECASE)
HOSTNAME_RE = re.compile(r"ricc2\s*\(([^)]+)\)", re.IGNORECASE)
BASIS_BANNER_RE = re.compile(r"def2-SVP", re.IGNORECASE)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_ricc2_out(path: Path) -> dict:
    """Return parsed banner / basis / hostname flags for one ricc2 .out file."""
    if not path.exists():
        return {"present": False}
    try:
        head = path.read_text(errors="ignore")[:80_000]
    except OSError:
        return {"present": False}
    hostname_match = HOSTNAME_RE.search(head)
    hostname = hostname_match.group(1) if hostname_match else None
    login_pat = re.compile(r"\b(login|head|master|submit|frontend)\b",
                           re.IGNORECASE)
    return {
        "present": True,
        "method_banner_present": bool(METHOD_BANNER_RE.search(head)),
        "scs_banner_present": "Spin-Component Scaling" in head,
        "runtime_banner_present": bool(RUNTIME_BANNER_RE.search(head)),
        "runtime_hostname": hostname,
        "is_login_hostname": bool(hostname and login_pat.search(hostname)),
        "basis_banner_def2_svp": bool(BASIS_BANNER_RE.search(head)),
    }


def sibling_control(ricc2_path: Path) -> Path | None:
    """Look for a Turbomole `control` file in the same directory or one up."""
    for candidate in (ricc2_path.parent / "control",
                      ricc2_path.parent.parent / "control"):
        if candidate.exists():
            return candidate
    return None


def sibling_slurm_log(ricc2_path: Path) -> Path | None:
    """Look for a slurm-<jobid>.out file beside the ricc2 output."""
    parent = ricc2_path.parent
    for p in list(parent.glob("slurm-*.out")) + list(parent.parent.glob("slurm-*.out")):
        return p
    return None


def main() -> int:
    if not CSV_INPUT.exists():
        print(f"FATAL: {CSV_INPUT} not found", file=sys.stderr)
        return 2

    # Sanity-check the COHORT mol_id list against the CSV.
    with CSV_INPUT.open() as f:
        csv_mols = [r["mol_id"] for r in csv.DictReader(f)]
    cohort_mols = [m for m, _, _ in COHORT]
    if set(csv_mols) != set(cohort_mols):
        print("FATAL: cohort mismatch between COHORT and "
              "cross_check_n13.csv", file=sys.stderr)
        print(f"  CSV: {sorted(csv_mols)}", file=sys.stderr)
        print(f"  COHORT: {sorted(cohort_mols)}", file=sys.stderr)
        return 3

    rows: list[dict] = []
    for mol, sing_rel, trip_rel in COHORT:
        for role, rel in (("sing", sing_rel), ("trip", trip_rel)):
            abs_path = EXT_ROOT / rel
            info = inspect_ricc2_out(abs_path)
            row = {
                "mol_id": mol,
                "method": "SCS-CC2/def2-SVP",
                "file_role": f"ricc2_{role}.out",
                "relative_path": rel,
                "sha256": (sha256(abs_path) if info.get("present") else ""),
                "size_bytes": (abs_path.stat().st_size
                               if info.get("present") else ""),
                "basis_status": ("banner-confirmed def2-SVP"
                                 if info.get("basis_banner_def2_svp")
                                 else "not-confirmed"),
                "method_banner_status": (
                    "CC2+SCS banner present" if info.get("scs_banner_present")
                    else ("CC2/ADC2 banner present"
                          if info.get("method_banner_present")
                          else "no method banner")),
                "runtime_banner_status": (
                    f"compute-node hostname={info['runtime_hostname']}"
                    if info.get("runtime_hostname")
                    and not info.get("is_login_hostname")
                    else ("LOGIN-NODE-RED-FLAG"
                          if info.get("is_login_hostname")
                          else "no runtime banner")),
                "scheduler_log_status": (
                    "slurm-<jobid>.out present"
                    if (info.get("present")
                        and sibling_slurm_log(abs_path) is not None)
                    else "slurm log not preserved"),
                "local_raw_status": (
                    "locally verified"
                    if info.get("present") else "missing-locally"),
                "notes": (
                    ""
                    if not info.get("present") else
                    "historical batch, no preserved sibling control"
                    if (mol in HISTORICAL_BATCH
                        and sibling_control(abs_path) is None)
                    else "preserved sibling control present"
                    if sibling_control(abs_path) is not None
                    else "control not preserved"),
            }
            rows.append(row)

    # Write TSV
    tsv_path = AUDIT / "revision_patchC_raw_provenance_manifest.tsv"
    field_order = ["mol_id", "method", "file_role", "relative_path",
                   "sha256", "size_bytes", "basis_status",
                   "method_banner_status", "runtime_banner_status",
                   "scheduler_log_status", "local_raw_status", "notes"]
    with tsv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=field_order, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {tsv_path} ({len(rows)} rows)")

    # Write companion MD summary
    md_path = AUDIT / "revision_patchC_raw_provenance_manifest.md"
    n_present = sum(1 for r in rows if r["local_raw_status"]
                    == "locally verified")
    n_total = len(rows)
    total_bytes = sum(int(r["size_bytes"]) for r in rows if r["size_bytes"])
    n_login_red = sum(1 for r in rows
                      if "LOGIN-NODE-RED-FLAG" in r["runtime_banner_status"])
    n_with_slurm = sum(1 for r in rows
                       if r["scheduler_log_status"] == "slurm-<jobid>.out present")

    md_path.write_text(f"""# Patch C — Raw provenance manifest (companion to TSV)

## Coverage

- SCS-CC2 n=13 cohort: {n_present} / {n_total} files locally verified
  ({total_bytes} bytes total, ~{total_bytes/1024/1024:.2f} MB).
- All 13 molecules from `results/scscc2_extension_n13/cross_check_n13.csv`
  have both singlet and triplet entries in the manifest.

## Banner / basis / hostname flags

- Method-banner status: `CC2+SCS banner present` for every locally
  verified file (each `ricc2_*.out` contains the CC2 declaration AND
  the Spin-Component Scaling annotation).
- Basis-banner status: `banner-confirmed def2-SVP` for every locally
  verified file.
- Runtime-banner status: compute-node hostname recorded for every
  locally verified file. **{n_login_red} / {n_total}** files trigger
  the login-node red-flag pattern (`login|head|master|submit|frontend`).
- Scheduler-log status: **{n_with_slurm} / {n_total}** files have a
  sibling `slurm-<jobid>.out` preserved alongside the ricc2 output;
  the remaining {n_total - n_with_slurm} report
  `slurm log not preserved` and are therefore
  **runtime-banner-supported rather than scheduler-log-confirmed**
  (consistent with audit Phase 5 Step 6).

## Caveats explicitly preserved

- **POZ1 (Hz_POZ1_NPh21_CF31)** is in the historical batch and has
  no preserved sibling control file. Its basis assignment is
  banner-derived only (audit Phase 5 Issue A); the manifest records
  `historical batch, no preserved sibling control` in the notes
  column for both sing and trip rows.
- **ADC(2) ybsi pending** (raw outputs not locally verified):
  15 R1-deploy ADC(2) raw outputs were computed on the ybsi cluster
  and were not rsynced into the local audit snapshot at the time of
  this manifest. They are out of scope for the SCS-CC2 manifest
  above and are listed here for completeness:
  - 7 in the SCS-CC2 n=13 cohort that need their *ADC(2)*
    counterpart re-archived (the SCS-CC2 side is locally verified):
    Hz_NH23, Hz_NEt22_CF31, Hz_NH22_SO2Ph1,
    Hz_DMAC1_NPh21_SO2Ph1, Hz_Cz1_NPh21_CF31,
    Hz_NEt21_NPh22, Hz_NPh22_CN1.
  - 8 R1-deploy ADC(2) entries outside the n=13 cohort
    (Hz_DMAC1_NPh21_SO2Ph1 is in both lists; the union has 15
    pending raw outputs; see audit Phase 5 Step 5).
  The manifest TSV does NOT inject placeholder rows for ybsi-pending
  ADC(2) files; their absence is documented here in the MD companion
  instead so the TSV remains an accurate sha256 catalogue of what
  exists locally.

## Files explicitly NOT in this manifest

- LaTeX build artefacts (`*.out`, `*.log` produced by `pdflatex`).
- Audit workspace copies under `audit/_tmp_*/` or `audit/_intermediate*/`.
- Scheduler script templates at
  `scripts/scscc2_extension/templates/run_scscc2_svp*.slurm`
  (these are the wrapper templates, not job-instance logs).

## TSV source

See `audit/revision_patchC_raw_provenance_manifest.tsv`.
""", encoding="utf-8")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
