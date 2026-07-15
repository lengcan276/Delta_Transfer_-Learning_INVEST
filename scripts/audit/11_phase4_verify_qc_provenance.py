#!/usr/bin/env python3
"""
Phase 4 — verify QC raw provenance for 13 SCS-CC2 + 35 ADC(2) claims.

For each claim:
1. Search multiple known raw-output prefixes for ricc2 sing/trip pair.
2. Apply method-banner-priority parser (independent ADC(2) or SCS-CC2).
3. Compare parsed ΔE_ST to claimed (tolerance 0.0001 eV = 0.1 meV).
4. Audit basis from accompanying control file if present
   ($basis / $jbas / $cbas — all three).
5. Tier scheduler evidence (FULL / PARTIAL / INFERRED / NONE).
6. Compute sha256 of raw output files.

Outputs:
    audit/qc_provenance_manifest.csv        — one row per (mol, method)
    audit/qc_provenance_report.csv          — per-row verification result
    audit/qc_coverage_matrix.csv            — 13 × 2 ADC(2)×SCS-CC2 matrix
    audit/qc_provenance_summary.md          — human summary

READ-ONLY: looks at /home/nudt_cleng/2026/results/... (parent project,
local FS) — does NOT modify anything.
"""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/nudt_cleng/2026/release_n13")
PARENT_RESULTS = Path("/home/nudt_cleng/2026/results")
AUDIT = ROOT / "audit"

sys.path.insert(0, str(ROOT / "scripts" / "audit"))
from parse_adc2_dest_audit import compute_dest as parse_adc2  # noqa
from parse_scscc2_dest_audit import compute_dest as parse_scscc2  # noqa

# ── claim sources ────────────────────────────────────────────────────────

VALIDATED_CSV = ROOT / "results" / "validated_candidates_master.csv"
CROSS_CHECK_CSV = ROOT / "results" / "scscc2_extension_n13" / "cross_check_n13.csv"

# ── raw-path search prefixes (in priority order) ─────────────────────────

ADC2_PREFIXES = [
    # (path template, label)
    (PARENT_RESULTS / "adc2_batch2_final" / "{mol}" / "turbo_sing" / "ricc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_final" / "{mol}" / "turbo_trip" / "ricc2_trip.out",
     "adc2_batch2_final"),
    (PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "turbo_sing" / "ricc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "turbo_trip" / "ricc2_trip.out",
     "adc2_batch2_raw"),
    (PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "ricc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "ricc2_trip.out",
     "adc2_batch2_raw_flat"),
    (PARENT_RESULTS / "scscc2_extension_n13" / "{mol}" / "turbo_sing_svp_round2" / "ricc2_adc2_sing.out",
     PARENT_RESULTS / "scscc2_extension_n13" / "{mol}" / "turbo_trip_svp_round2" / "ricc2_adc2_trip.out",
     "scscc2_extension_n13"),
    (PARENT_RESULTS / "adc2_validation_backup" / "{mol}" / "turbo_sing" / "ricc2_sing.out",
     PARENT_RESULTS / "adc2_validation_backup" / "{mol}" / "turbo_trip" / "ricc2_trip.out",
     "adc2_validation_backup"),
    (PARENT_RESULTS / "adc2_tzvp_sensitivity" / "{mol}" / "ricc2_sing.out",
     PARENT_RESULTS / "adc2_tzvp_sensitivity" / "{mol}" / "ricc2_trip.out",
     "adc2_tzvp_sensitivity"),
]

SCSCC2_PREFIXES = [
    (PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_raw" / "{mol}" / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out",
     "adc2_batch2_raw"),
    (PARENT_RESULTS / "adc2_batch2_raw" / "{mol}_scscc2" / "ricc2_scscc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_raw" / "{mol}_scscc2" / "ricc2_scscc2_trip.out",
     "adc2_batch2_raw_flat_scscc2"),
    (PARENT_RESULTS / "adc2_batch2_final" / "{mol}" / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out",
     PARENT_RESULTS / "adc2_batch2_final" / "{mol}" / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out",
     "adc2_batch2_final"),
    (PARENT_RESULTS / "scscc2_extension_n13" / "{mol}" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     PARENT_RESULTS / "scscc2_extension_n13" / "{mol}" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out",
     "scscc2_extension_n13"),
]


def find_pair(mol, prefixes):
    for sing_tmpl, trip_tmpl, label in prefixes:
        s = Path(str(sing_tmpl).replace("{mol}", mol))
        t = Path(str(trip_tmpl).replace("{mol}", mol))
        if s.exists() and t.exists():
            return s, t, label
    return None, None, None


def sha256_file(p):
    if not p or not p.exists():
        return "MISSING"
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def audit_control_basis(control_path, claimed_basis="def2-SVP"):
    """Audit $basis / $jbas / $cbas in a Turbomole control file."""
    if not control_path or not control_path.exists():
        return {"control_present": False}
    text = control_path.read_text()
    out = {"control_present": True}
    for tag in ("basis", "jbas", "cbas"):
        # match "basis =c def2-SVP" or "jbas  =n def2-SVP" etc.
        pat = re.compile(rf"{tag}\s*=[A-Za-z]+\s+(\S+)")
        vals = set(m.group(1) for m in pat.finditer(text))
        out[f"{tag}_values"] = sorted(vals) if vals else []
        out[f"{tag}_match_{claimed_basis}"] = (
            list(vals) == [claimed_basis] if vals else False
        )
    return out


def scheduler_tier(ricc2_out_path):
    """Tier: FULL / PARTIAL / INFERRED / NONE."""
    if not ricc2_out_path or not ricc2_out_path.exists():
        return "NONE", None
    # look for slurm-*.out in same dir or parent dirs
    cur = ricc2_out_path.parent
    slurm_log = None
    for _ in range(3):
        for f in cur.glob("slurm-*.out"):
            slurm_log = f
            break
        if slurm_log:
            break
        cur = cur.parent
    if slurm_log:
        s = slurm_log.read_text(errors="replace")
        has_jobid = bool(re.search(r"SLURM_JOB_ID\s*:?\s*\d+", s))
        has_host = bool(re.search(r"Hostname\s*:\s*\S+", s))
        has_start = bool(re.search(r"Job started|started:", s, re.I))
        has_end = bool(re.search(r"finished|ended:|Date:", s, re.I))
        if has_jobid and has_host and has_start and has_end:
            return "FULL", str(slurm_log)
        return "PARTIAL", str(slurm_log)
    # inferred: ricc2.out header contains "ricc2 (nodeN)"
    text = ricc2_out_path.read_text()
    m = re.search(r"ricc2\s*\(\s*(\S+?)\s*\)\s*:\s*TURBOMOLE", text)
    if m and re.match(r"node\d+", m.group(1)):
        return "INFERRED", f"ricc2.out banner: ricc2 ({m.group(1)})"
    return "NONE", None


# ── verify ADC(2) claims ─────────────────────────────────────────────────

def verify_adc2(mol, claimed_dE_eV):
    sing, trip, prefix_label = find_pair(mol, ADC2_PREFIXES)
    if not sing:
        return {
            "status": "MISSING_RAW",
            "prefix": None,
            "sing_path": None, "trip_path": None,
        }
    try:
        r = parse_adc2(sing, trip)
    except Exception as e:
        return {
            "status": "PARSE_FAIL",
            "prefix": prefix_label,
            "sing_path": str(sing), "trip_path": str(trip),
            "error": str(e),
        }
    diff_meV = (r["dE_ST_eV"] - claimed_dE_eV) * 1000
    value_match = abs(diff_meV) <= 0.1
    sched_tier, sched_evidence = scheduler_tier(sing)
    # control file: ADC(2) control is at parent of sing
    control = sing.parent / "control"
    basis_audit = audit_control_basis(control)
    status = "OK" if value_match else "VALUE_MISMATCH"
    return {
        "status": status,
        "prefix": prefix_label,
        "sing_path": str(sing), "trip_path": str(trip),
        "method_banner": r["method"],
        "E_S1_eV": r["E_S1_eV"], "E_T1_eV": r["E_T1_eV"],
        "parsed_dE_eV": r["dE_ST_eV"],
        "claimed_dE_eV": claimed_dE_eV,
        "diff_meV": diff_meV,
        "value_match": value_match,
        "normal_term_sing": r["sing"]["normal_termination"],
        "normal_term_trip": r["trip"]["normal_termination"],
        "hostname_in_output_sing": r["sing"]["hostname_in_output"],
        "hostname_in_output_trip": r["trip"]["hostname_in_output"],
        "scheduler_tier": sched_tier,
        "scheduler_evidence": sched_evidence,
        "control_basis_audit": basis_audit,
        "sha256_sing": sha256_file(sing),
        "sha256_trip": sha256_file(trip),
    }


def verify_scscc2(mol, claimed_dE_eV):
    sing, trip, prefix_label = find_pair(mol, SCSCC2_PREFIXES)
    if not sing:
        return {
            "status": "MISSING_RAW",
            "prefix": None,
            "sing_path": None, "trip_path": None,
        }
    try:
        r = parse_scscc2(sing, trip)
    except Exception as e:
        return {
            "status": "PARSE_FAIL",
            "prefix": prefix_label,
            "sing_path": str(sing), "trip_path": str(trip),
            "error": str(e),
        }
    diff_meV = (r["dE_ST_eV"] - claimed_dE_eV) * 1000
    value_match = abs(diff_meV) <= 0.1
    sched_tier, sched_evidence = scheduler_tier(sing)
    control = sing.parent / "control"
    basis_audit = audit_control_basis(control)
    status = "OK" if value_match else "VALUE_MISMATCH"
    return {
        "status": status,
        "prefix": prefix_label,
        "sing_path": str(sing), "trip_path": str(trip),
        "method_banner": r["method"],
        "scs_c_os": r["scs_c_os"], "scs_c_ss": r["scs_c_ss"],
        "E_S1_eV": r["E_S1_eV"], "E_T1_eV": r["E_T1_eV"],
        "parsed_dE_eV": r["dE_ST_eV"],
        "claimed_dE_eV": claimed_dE_eV,
        "diff_meV": diff_meV,
        "value_match": value_match,
        "normal_term_sing": r["sing"]["normal_termination"],
        "normal_term_trip": r["trip"]["normal_termination"],
        "hostname_in_output_sing": r["sing"]["hostname_in_output"],
        "hostname_in_output_trip": r["trip"]["hostname_in_output"],
        "scheduler_tier": sched_tier,
        "scheduler_evidence": sched_evidence,
        "control_basis_audit": basis_audit,
        "sha256_sing": sha256_file(sing),
        "sha256_trip": sha256_file(trip),
    }


def main():
    # ── load claims ──
    validated = list(csv.DictReader(VALIDATED_CSV.open()))
    crosscheck = list(csv.DictReader(CROSS_CHECK_CSV.open()))
    print(f"validated_candidates_master.csv: {len(validated)} rows "
          f"(35 ADC(2) claims)")
    print(f"cross_check_n13.csv: {len(crosscheck)} rows "
          f"(13 SCS-CC2 claims)")

    # ── ADC(2) ──
    adc2_reports = []
    for r in validated:
        mol = r["mol_id"]
        try:
            claimed = float(r["DEST_adc2_eV"]) if r["DEST_adc2_eV"] else (
                float(r["DEST_eV"]) if r["DEST_eV"] else None
            )
        except ValueError:
            claimed = None
        if claimed is None:
            res = {"status": "NO_ADC2_CLAIM"}
        else:
            res = verify_adc2(mol, claimed)
        res["mol_id"] = mol
        res["scaffold"] = r.get("scaffold", "")
        res["batch"] = r.get("batch", "")
        res["claimed_method"] = r.get("method", "")
        adc2_reports.append(res)

    # ── SCS-CC2 ──
    scscc2_reports = []
    for r in crosscheck:
        mol = r["mol_id"]
        claimed = float(r["SCSCC2_dEST_eV"])
        res = verify_scscc2(mol, claimed)
        res["mol_id"] = mol
        res["batch"] = r.get("batch", "")
        scscc2_reports.append(res)

    # ── flatten to CSV ──
    def flatten(d, prefix=""):
        out = {}
        for k, v in d.items():
            if isinstance(v, dict):
                out.update(flatten(v, f"{prefix}{k}_"))
            else:
                out[f"{prefix}{k}"] = v
        return out

    AUDIT.mkdir(exist_ok=True)

    # write reports
    adc2_flat = [flatten(r) for r in adc2_reports]
    scscc2_flat = [flatten(r) for r in scscc2_reports]
    all_keys = set()
    for r in adc2_flat + scscc2_flat:
        all_keys.update(r.keys())
    fieldnames = ["mol_id", "method_audit"] + sorted(k for k in all_keys
                                                     if k != "mol_id")

    with (AUDIT / "qc_provenance_report.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in adc2_flat:
            r["method_audit"] = "ADC(2)"
            w.writerow(r)
        for r in scscc2_flat:
            r["method_audit"] = "SCS-CC2"
            w.writerow(r)

    # coverage matrix: per molecule × method
    # build by mol_id
    by_mol_adc = {r["mol_id"]: r for r in adc2_reports}
    by_mol_scs = {r["mol_id"]: r for r in scscc2_reports}
    matrix_rows = []
    cohort_13 = [r["mol_id"] for r in crosscheck]
    for mol in cohort_13:
        a = by_mol_adc.get(mol, {"status": "NOT_IN_ADC2_TABLE"})
        s = by_mol_scs.get(mol, {"status": "NOT_IN_SCS_TABLE"})
        matrix_rows.append({
            "mol_id": mol,
            "ADC2_status": a.get("status"),
            "ADC2_sing_path": a.get("sing_path", ""),
            "ADC2_value_match": a.get("value_match", ""),
            "ADC2_diff_meV": a.get("diff_meV", ""),
            "ADC2_scheduler_tier": a.get("scheduler_tier", ""),
            "ADC2_method_banner": a.get("method_banner", ""),
            "SCSCC2_status": s.get("status"),
            "SCSCC2_sing_path": s.get("sing_path", ""),
            "SCSCC2_value_match": s.get("value_match", ""),
            "SCSCC2_diff_meV": s.get("diff_meV", ""),
            "SCSCC2_scheduler_tier": s.get("scheduler_tier", ""),
            "SCSCC2_method_banner": s.get("method_banner", ""),
            "SCSCC2_scs_c_os": s.get("scs_c_os", ""),
            "SCSCC2_scs_c_ss": s.get("scs_c_ss", ""),
        })
    with (AUDIT / "qc_coverage_matrix.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(matrix_rows[0].keys()))
        w.writeheader()
        w.writerows(matrix_rows)

    # ── tallies ──
    print(f"\n--- ADC(2) tally ({len(adc2_reports)} claims) ---")
    adc_tally = {}
    for r in adc2_reports:
        s = r.get("status", "?")
        adc_tally[s] = adc_tally.get(s, 0) + 1
    for s in sorted(adc_tally):
        print(f"  {s:35s} {adc_tally[s]}")

    print(f"\n--- SCS-CC2 tally ({len(scscc2_reports)} claims) ---")
    scs_tally = {}
    for r in scscc2_reports:
        s = r.get("status", "?")
        scs_tally[s] = scs_tally.get(s, 0) + 1
    for s in sorted(scs_tally):
        print(f"  {s:35s} {scs_tally[s]}")

    print(f"\n--- n=13 cohort coverage matrix ---")
    full = sum(1 for r in matrix_rows if r["ADC2_status"] == "OK"
               and r["SCSCC2_status"] == "OK")
    scs_only = sum(1 for r in matrix_rows if r["ADC2_status"] != "OK"
                   and r["SCSCC2_status"] == "OK")
    none_ok = sum(1 for r in matrix_rows if r["ADC2_status"] != "OK"
                  and r["SCSCC2_status"] != "OK")
    print(f"  both ADC(2) + SCS-CC2 OK : {full}")
    print(f"  only SCS-CC2 OK          : {scs_only}")
    print(f"  neither OK               : {none_ok}")

    print("\nWrote:")
    print(f"  {AUDIT / 'qc_provenance_report.csv'}")
    print(f"  {AUDIT / 'qc_coverage_matrix.csv'}")


if __name__ == "__main__":
    main()
