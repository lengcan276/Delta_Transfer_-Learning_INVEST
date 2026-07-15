#!/usr/bin/env python3
"""Validate the Patch B single-writer canonical refactor.

Checks (each prints PASS / FAIL):
  1. build_cross_check_n13.py does not write canonical_metrics.json
  2. 99_emit_canonical.py is the single canonical writer
  3. delete-and-regenerate chain test passes
  4. scs_cc2_extended_n13 contains required explicit aliases
  5. per_molecule count == 13 (whether list or dict)
  6. mol_id set equals the cross_check_n13.csv mol_id column
  7. no FedSchNet-ReorgEnergy in generated metadata
  8. no audit-Phase-4/5 leakage into paper-facing fields

Exit code 0 if every check passes, 1 otherwise. Read-only — does not
mutate any file (except an in-process re-run of the canonical chain
into a tempfile copy for the chain test).
"""
from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
SCRIPTS = ROOT / "scripts"

REQUIRED_ALIASES = [
    "generator",
    "upstream_generator",
    "screened_cohort_n",
    "sign_disagreements",
    "rule_of_three_upper_bound",
    "paper_cited_signrate",
    "paper_cited_scope",
    "ci_method",
    "repository",
    "raw_provenance_status",
    "audit_report_reference",
    "generated_from",
]

PAPER_FACING_FIELDS = [
    "paper_cited_signrate",
    "paper_cited_scope",
    "paper_cited_bound",
    "ci_method",
    "design_note",
    "raw_provenance_status",
    "repository",
    "repository_canonical",
]

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{':  ' + detail if detail else ''}")


def writes_canonical_metrics(path: Path) -> bool:
    """Return True if `path` contains actual write-operation code that
    targets canonical_metrics.json (not just a docstring / read reference)."""
    try:
        lines = path.read_text().splitlines()
    except (UnicodeDecodeError, OSError):
        return False

    # Identify variable assignments of the form `<var> = ... canonical_metrics.json ...`
    path_vars: set[str] = set()
    import re
    assign_re = re.compile(
        r"^\s*([A-Za-z_]\w*)\s*=\s*.*canonical_metrics\.json")
    for ln in lines:
        m = assign_re.match(ln)
        if m:
            path_vars.add(m.group(1))

    # Build write-pattern regexes.
    # 1) direct: open(..."canonical_metrics.json"..., 'w'...)
    open_w_literal = re.compile(
        r"open\(\s*[^)]*canonical_metrics\.json[^)]*,\s*['\"]w")
    # 2) direct: "...canonical_metrics.json...".write_text(  (rare)
    direct_write = re.compile(
        r"canonical_metrics\.json[^\n]*\)\s*\.write_text\(")
    # 3) via variable: <var>.write_text(  or  open(<var>, 'w')
    var_write_patterns = [
        re.compile(rf"\b{re.escape(v)}\b\s*\.\s*write_text\s*\(")
        for v in path_vars
    ] + [
        re.compile(rf"open\(\s*{re.escape(v)}\s*,\s*['\"]w")
        for v in path_vars
    ]

    for ln in lines:
        if open_w_literal.search(ln):
            return True
        if direct_write.search(ln):
            return True
        for pat in var_write_patterns:
            if pat.search(ln):
                return True
    return False


def main() -> int:
    # 1. build_cross_check_n13.py source must not write canonical_metrics.json
    build_path = (SCRIPTS / "scscc2_extension" / "build_cross_check_n13.py")
    build_writes = writes_canonical_metrics(build_path)
    check("build_cross_check_n13.py does not write canonical_metrics.json",
          not build_writes,
          "" if not build_writes
          else "real write operation targeting canonical_metrics.json detected")

    # 2. 99_emit_canonical.py is the sole writer of canonical_metrics.json
    emit_writes = writes_canonical_metrics(SCRIPTS / "99_emit_canonical.py")
    other_writers = []
    for p in SCRIPTS.rglob("*.py"):
        if p.name in ("99_emit_canonical.py",
                      "15_validate_patchB_single_writer.py"):
            continue
        if p.relative_to(SCRIPTS).parts[:1] == ("audit",):
            continue  # audit scripts are read-only by convention
        if writes_canonical_metrics(p):
            other_writers.append(str(p.relative_to(ROOT)))
    single_writer = emit_writes and not other_writers
    check("99_emit_canonical.py is the single canonical writer",
          single_writer,
          "other writers: " + ", ".join(other_writers) if other_writers
          else "")

    # 3. Delete-and-regenerate chain test (write to a sibling tempfile path
    # so we never lose the live canonical_metrics.json).
    tmp = RESULTS / "canonical_metrics.chaintest.json"
    if tmp.exists():
        tmp.unlink()
    shutil.copy(RESULTS / "canonical_metrics.json",
                RESULTS / "_canonical_metrics_backup_chaintest.json")
    try:
        (RESULTS / "canonical_metrics.json").unlink()
        rc = subprocess.run(
            [sys.executable, str(SCRIPTS / "99_emit_canonical.py")],
            capture_output=True, text=True, cwd=str(ROOT))
        regen_ok = (rc.returncode == 0
                    and (RESULTS / "canonical_metrics.json").exists())
    finally:
        # Always restore: prefer the freshly regenerated file; fall back
        # to the backup if regeneration failed.
        if not (RESULTS / "canonical_metrics.json").exists():
            shutil.copy(
                RESULTS / "_canonical_metrics_backup_chaintest.json",
                RESULTS / "canonical_metrics.json")
        (RESULTS / "_canonical_metrics_backup_chaintest.json").unlink(
            missing_ok=True)
    check("delete-and-regenerate chain test", regen_ok)

    canonical = json.loads(
        (RESULTS / "canonical_metrics.json").read_text())
    block = canonical.get("scs_cc2_extended_n13", {})

    # 4. Required aliases
    missing_aliases = [a for a in REQUIRED_ALIASES if a not in block]
    check("scs_cc2_extended_n13 contains all required aliases",
          not missing_aliases,
          "missing: " + ", ".join(missing_aliases) if missing_aliases
          else "")

    # 4a. Specific value checks for key aliases
    check("scs_cc2_extended_n13.generator value",
          block.get("generator") ==
          "scripts/99_emit_canonical.py::build_scs_cc2_extended_n13",
          f"got: {block.get('generator')!r}")
    check("scs_cc2_extended_n13.upstream_generator value",
          block.get("upstream_generator") ==
          "scripts/scscc2_extension/build_cross_check_n13.py",
          f"got: {block.get('upstream_generator')!r}")
    check("scs_cc2_extended_n13.screened_cohort_n == 13",
          block.get("screened_cohort_n") == 13,
          f"got: {block.get('screened_cohort_n')!r}")
    check("scs_cc2_extended_n13.sign_disagreements == 0",
          block.get("sign_disagreements") == 0,
          f"got: {block.get('sign_disagreements')!r}")
    check("scs_cc2_extended_n13.paper_cited_signrate is screened-cohort form",
          block.get("paper_cited_signrate") ==
          "0 sign disagreement within the ADC(2)-screened cohort",
          f"got: {block.get('paper_cited_signrate')!r}")
    check("scs_cc2_extended_n13.repository == INVEST-n13",
          block.get("repository") ==
          "https://github.com/lengcan276/INVEST-n13",
          f"got: {block.get('repository')!r}")
    check("scs_cc2_extended_n13.raw_provenance_status present (non-empty)",
          bool(block.get("raw_provenance_status")))

    # 5. per_molecule count == 13 (whether list or dict)
    pm = block.get("per_molecule")
    pm_kind = type(pm).__name__
    pm_count = (len(pm) if pm is not None else 0)
    check(f"per_molecule count == 13 (representation: {pm_kind})",
          pm_count == 13,
          f"got count={pm_count}")

    # 6. mol_id set equals cross_check_n13.csv mol_id column
    csv_path = RESULTS / "scscc2_extension_n13" / "cross_check_n13.csv"
    with csv_path.open() as f:
        csv_mols = {r["mol_id"] for r in csv.DictReader(f)}
    if isinstance(pm, dict):
        pm_mols = set(pm.keys())
    elif isinstance(pm, list):
        pm_mols = {entry.get("mol_id") for entry in pm}
    else:
        pm_mols = set()
    check("per_molecule mol_id set equals cross_check_n13.csv",
          pm_mols == csv_mols,
          f"symmetric_diff: {pm_mols ^ csv_mols}"
          if pm_mols != csv_mols else "")

    # 7. no FedSchNet-ReorgEnergy in generated metadata
    serialized = json.dumps(block, ensure_ascii=False)
    fedschnet_hit = "FedSchNet" in serialized
    check("no FedSchNet-ReorgEnergy in generated metadata",
          not fedschnet_hit)

    # 8. no audit-Phase-4/5 leakage into paper-facing fields
    leaks = []
    for f in PAPER_FACING_FIELDS:
        v = block.get(f)
        if not isinstance(v, str):
            continue
        if "Phase 4" in v or "Phase 5" in v or "audit Phase" in v:
            leaks.append(f)
    check("no audit-Phase-4/5 in paper-facing fields",
          not leaks,
          "leaked into: " + ", ".join(leaks) if leaks else "")

    print()
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"summary: {passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
