#!/usr/bin/env python3
"""Patch D numeric safety check: confirm zero scientific drift.

Compares the current `results/canonical_metrics.json` against the
HEAD baseline. Reports per-molecule numeric drift for the
`scs_cc2_extended_n13` block and verifies cohort-level invariants.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read_head(path: str) -> dict:
    r = subprocess.run(["git", "show", f"HEAD:{path}"],
                       capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(f"FATAL: cannot read HEAD:{path}: {r.stderr}")
    return json.loads(r.stdout)


def main() -> int:
    before = read_head("results/canonical_metrics.json")
    after = json.loads((ROOT / "results"
                        / "canonical_metrics.json").read_text())
    hb = before["scs_cc2_extended_n13"]
    cb = after["scs_cc2_extended_n13"]

    failures: list[str] = []

    # per-molecule numeric / boolean keys
    pm_keys = ["ADC2_dEST_meV", "SCSCC2_dEST_meV",
               "SCSCC2_S1_eV", "SCSCC2_T1_eV",
               "abs_ddEST_meV", "ADC2_dEST_meV_abs",
               "SCSCC2_dEST_meV_abs", "sign_agree"]
    hpm, cpm = hb["per_molecule"], cb["per_molecule"]
    h_mols, c_mols = set(hpm.keys()), set(cpm.keys())
    if h_mols != c_mols:
        failures.append(f"mol_id set changed: only_before={h_mols-c_mols} "
                        f"only_after={c_mols-h_mols}")
    for mol in h_mols & c_mols:
        for k in pm_keys:
            vb, va = hpm[mol].get(k), cpm[mol].get(k)
            if vb != va:
                failures.append(f"per_molecule.{mol}.{k}: {vb!r} -> {va!r}")

    # cohort invariants
    inv_eq = {
        "n_total": 13,
        "n_sign_retain": 13,
        "sign_retain_rate": 1.0,
    }
    for k, want in inv_eq.items():
        if cb.get(k) != want:
            failures.append(f"cohort.{k}: want {want}, got {cb.get(k)!r}")

    # Patch B aliases (new in revision-mode; only verify expected values)
    alias_eq = {
        "screened_cohort_n": 13,
        "sign_disagreements": 0,
        "rule_of_three_upper_bound": round(3.0 / 13.0, 4),
    }
    for k, want in alias_eq.items():
        if cb.get(k) != want:
            failures.append(f"alias.{k}: want {want}, got {cb.get(k)!r}")

    # Cohort numeric fields that existed pre-Patch-B
    cohort_keys = ["clopper_pearson_95_CI", "clopper_pearson_90_CI",
                   "abs_ddEST_meV_min", "abs_ddEST_meV_max",
                   "abs_ddEST_meV_mean", "abs_ddEST_meV_median"]
    for k in cohort_keys:
        vb, va = hb.get(k), cb.get(k)
        if vb != va:
            failures.append(f"cohort.{k}: {vb!r} -> {va!r}")

    # non-scs top-level blocks should be unchanged
    for k in before:
        if k == "scs_cc2_extended_n13":
            continue
        if before[k] != after.get(k):
            failures.append(f"top_block.{k} changed (non-scs)")

    if failures:
        print("FAILED — drift detected:")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"PASS — 0 drift across {len(h_mols)} molecules "
          f"× {len(pm_keys)} per-molecule keys + cohort invariants + "
          f"non-scs top blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
