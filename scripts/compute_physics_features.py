#!/usr/bin/env python3
"""Collect physics-based features from existing computed data.

Reads master_molecule_table.csv (which already has KS-OD orbital data)
and augments with any additional physics descriptors available.

Usage:
    python scripts/compute_physics_features.py [--project-root PROJECT_ROOT]
"""
import argparse
import logging
import os

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    p.add_argument("--repo-root", default=os.path.join(os.path.dirname(__file__), ".."))
    return p.parse_args()


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    repo = os.path.expanduser(args.repo_root)

    master_path = os.path.join(proj, "data/processed/master_molecule_table.csv")
    out_path = os.path.join(proj, "data/processed/physics_features.csv")

    master = pd.read_csv(master_path)
    log.info("Loaded master table: %d molecules", len(master))

    # Physics features from master table (already merged from KS-OD)
    physics_cols = ["mol_id", "homo_ev", "lumo_ev", "hl_gap_ev",
                    "homo_m1_ev", "lumo_p1_ev", "od_index",
                    "dft_dest_raw_ev", "dft_dest_calibrated_ev", "fosc_dft"]

    existing = [c for c in physics_cols if c in master.columns]
    phys = master[existing].copy()

    # Derived features
    if "homo_ev" in phys.columns and "lumo_ev" in phys.columns:
        phys["hl_gap_ev"] = phys["lumo_ev"] - phys["homo_ev"]

    if "homo_m1_ev" in phys.columns and "homo_ev" in phys.columns:
        phys["homo_spacing"] = phys["homo_ev"] - phys["homo_m1_ev"]

    if "lumo_p1_ev" in phys.columns and "lumo_ev" in phys.columns:
        phys["lumo_spacing"] = phys["lumo_p1_ev"] - phys["lumo_ev"]

    # Try loading sTDA-xTB features if available
    stda_path = os.path.join(repo, "feasibility_gate/results_v3/feasibility_gate_v3_results.json")
    if os.path.exists(stda_path):
        import json
        with open(stda_path) as f:
            stda_data = json.load(f)
        stda_rows = []
        for mol_id, info in stda_data.items():
            if info.get("status") == "success":
                stda_rows.append({
                    "mol_id": mol_id,
                    "stda_s1_ev": info.get("s1_ev"),
                    "stda_t1_ev": info.get("t1_ev"),
                    "stda_dest_ev": info.get("dest_ev"),
                    "stda_fosc": info.get("fosc_s1"),
                })
        if stda_rows:
            stda_df = pd.DataFrame(stda_rows)
            phys = phys.merge(stda_df, on="mol_id", how="left")
            log.info("Merged sTDA-xTB features: %d molecules", stda_df["mol_id"].nunique())
    else:
        log.info("sTDA-xTB results not found locally at %s; skipping", stda_path)
        for col in ["stda_s1_ev", "stda_t1_ev", "stda_dest_ev", "stda_fosc"]:
            phys[col] = np.nan

    n_avail = phys.drop(columns=["mol_id"]).notna().any(axis=1).sum()
    log.info("Molecules with any physics feature: %d / %d", n_avail, len(phys))

    log.info("Feature availability:")
    for col in phys.columns:
        if col == "mol_id":
            continue
        n = phys[col].notna().sum()
        log.info("  %-30s %d / %d (%.1f%%)", col, n, len(phys), 100 * n / len(phys))

    phys.to_csv(out_path, index=False)
    log.info("Saved physics features: %s, shape=%s", out_path, phys.shape)


if __name__ == "__main__":
    main()
