#!/usr/bin/env python3
"""Merge all feature blocks into a unified model_input_table.csv.

Combines:
  - master_molecule_table.csv (labels + split info)
  - rdkit_features.csv (2D descriptors + FP PCA)
  - physics_features.csv (orbital, DFT, sTDA)

Usage:
    python scripts/merge_feature_blocks.py [--project-root PROJECT_ROOT]
"""
import argparse
import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    return p.parse_args()


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    processed = os.path.join(proj, "data/processed")

    master = pd.read_csv(os.path.join(processed, "master_molecule_table.csv"))
    rdkit_feat = pd.read_csv(os.path.join(processed, "rdkit_features.csv"))
    phys_feat = pd.read_csv(os.path.join(processed, "physics_features.csv"))

    log.info("Master: %d rows", len(master))
    log.info("RDKit features: %d rows, %d cols", *rdkit_feat.shape)
    log.info("Physics features: %d rows, %d cols", *phys_feat.shape)

    # Merge on mol_id
    merged = master.merge(rdkit_feat, on="mol_id", how="left")
    merged = merged.merge(phys_feat, on="mol_id", how="left", suffixes=("", "_phys"))

    # Drop duplicate columns from physics merge
    dup_cols = [c for c in merged.columns if c.endswith("_phys")]
    if dup_cols:
        log.info("Dropping duplicate physics columns: %s", dup_cols)
        merged = merged.drop(columns=dup_cols)

    out_path = os.path.join(processed, "model_input_table.csv")
    merged.to_csv(out_path, index=False)

    # Summary
    label_cols = ["adc2_dest_ev", "is_invest", "is_near_zero"]
    feat_cols = [c for c in merged.columns if c not in [
        "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
        "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
        "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
        "is_invest", "is_near_zero", "is_high_fosc",
    ]]

    log.info("Output: %s, shape=%s", out_path, merged.shape)
    log.info("Feature columns: %d", len(feat_cols))
    log.info("Molecules with ADC(2) label: %d", merged["adc2_available"].sum())

    # Feature availability for labeled molecules
    labeled = merged[merged["adc2_available"] == True]
    log.info("\nFeature availability (labeled molecules, n=%d):", len(labeled))
    for col in feat_cols:
        n = labeled[col].notna().sum()
        if n < len(labeled):
            log.info("  %-30s %d / %d (%.0f%%)", col, n, len(labeled), 100 * n / len(labeled))


if __name__ == "__main__":
    main()
