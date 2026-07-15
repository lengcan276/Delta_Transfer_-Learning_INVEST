#!/usr/bin/env python3
"""Ingest Round 1 ADC(2) results and update the master table.

Reads new ADC(2) results, validates and merges them into the master table,
producing a versioned update without overwriting the frozen original.

Expected input CSV format (one of):
  mol_id, S1_eV, T1_eV, DEST_eV, fosc
  name, S1_eV, T1_eV, DEST_eV, fosc
  name, status, S1_eV, T1_eV, DEST_eV, fosc, ...

Usage:
    python scripts/ingest_round1_adc2_results.py --input <path_to_adc2_results.csv> [OPTIONS]

Options:
    --dry-run       Validate without writing output files
    --project-root  Path to project directory
"""
import argparse
import logging
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Column name mappings: various conventions → standard names
COLUMN_MAP = {
    "name": "mol_id",
    "molecule": "mol_id",
    "mol_name": "mol_id",
    "s1_ev": "adc2_s1_ev",
    "S1_eV": "adc2_s1_ev",
    "S1_ADC2_eV": "adc2_s1_ev",
    "t1_ev": "adc2_t1_ev",
    "T1_eV": "adc2_t1_ev",
    "T1_ADC2_eV": "adc2_t1_ev",
    "dest_ev": "adc2_dest_ev",
    "DEST_eV": "adc2_dest_ev",
    "DEST_ADC2_eV": "adc2_dest_ev",
    "delta_est_ev": "adc2_dest_ev",
    "fosc": "adc2_fosc",
    "fosc_S1": "adc2_fosc",
    "fosc_S1_ADC2": "adc2_fosc",
    "f_osc": "adc2_fosc",
}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, help="Path to round1 ADC(2) results CSV")
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    p.add_argument("--dry-run", action="store_true", help="Validate only, do not write")
    return p.parse_args()


def standardize_columns(df):
    """Map input column names to standard names."""
    rename = {}
    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]
    df = df.rename(columns=rename)

    # Ensure mol_id exists
    if "mol_id" not in df.columns:
        log.error("Cannot find mol_id column. Available: %s", list(df.columns))
        sys.exit(1)

    required = ["adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev"]
    missing = [c for c in required if c not in df.columns]

    # Try to compute dest from s1 - t1 if missing
    if "adc2_dest_ev" not in df.columns and "adc2_s1_ev" in df.columns and "adc2_t1_ev" in df.columns:
        df["adc2_dest_ev"] = df["adc2_s1_ev"] - df["adc2_t1_ev"]
        log.info("Computed adc2_dest_ev = S1 - T1")
        missing = [c for c in required if c not in df.columns]

    if missing:
        log.error("Missing required columns after mapping: %s", missing)
        log.error("Available columns: %s", list(df.columns))
        sys.exit(1)

    return df


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    processed = os.path.join(proj, "data/processed")

    # Load input
    log.info("Reading input: %s", args.input)
    new_data = pd.read_csv(args.input)
    log.info("Input: %d rows, columns: %s", len(new_data), list(new_data.columns))

    # Standardize
    new_data = standardize_columns(new_data)

    # Filter to completed results
    if "status" in new_data.columns:
        completed = new_data[new_data["status"] == "complete"]
        log.info("Completed: %d / %d", len(completed), len(new_data))
        if len(completed) < len(new_data):
            skipped = new_data[new_data["status"] != "complete"]
            log.warning("Skipping incomplete: %s", skipped["mol_id"].tolist())
        new_data = completed

    # Ensure fosc column exists
    if "adc2_fosc" not in new_data.columns:
        new_data["adc2_fosc"] = np.nan
        log.warning("No fosc column found; filling with NaN")

    # Select standard columns
    new_clean = new_data[["mol_id", "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc"]].copy()
    new_clean["adc2_available"] = True
    new_clean["round"] = 1

    log.info("\n=== New ADC(2) Results ===")
    log.info("\n%s", new_clean.to_string(index=False))

    # Load existing master table
    master_path = os.path.join(processed, "master_molecule_table.csv")
    master = pd.read_csv(master_path)
    log.info("\nExisting master table: %d rows", len(master))

    # Load frozen round1 candidates to validate mol_ids
    frozen_path = os.path.join(proj, "results/tables/round1_candidates_frozen.csv")
    frozen = pd.read_csv(frozen_path)
    expected_ids = set(frozen["mol_id"])
    incoming_ids = set(new_clean["mol_id"])

    unexpected = incoming_ids - expected_ids
    if unexpected:
        log.warning("Unexpected mol_ids not in frozen candidates: %s", unexpected)

    missing_from_input = expected_ids - incoming_ids
    if missing_from_input:
        log.info("Expected but not yet returned: %s", missing_from_input)

    # Check for existing ADC(2) data that would be overwritten
    already_labeled = master[master["mol_id"].isin(incoming_ids) & (master["adc2_available"] == True)]
    if len(already_labeled) > 0:
        log.warning("These molecules already have ADC(2) — will be UPDATED:")
        log.warning("  %s", already_labeled["mol_id"].tolist())

    # Build changelog
    changelog = []
    for _, row in new_clean.iterrows():
        mid = row["mol_id"]
        old_row = master[master["mol_id"] == mid]
        if len(old_row) == 0:
            changelog.append({
                "mol_id": mid, "action": "NOT_IN_MASTER",
                "old_dest": np.nan, "new_dest": row["adc2_dest_ev"],
            })
            continue
        old_dest = old_row.iloc[0].get("adc2_dest_ev", np.nan)
        old_avail = old_row.iloc[0].get("adc2_available", False)
        action = "UPDATE" if old_avail else "NEW_LABEL"
        changelog.append({
            "mol_id": mid, "action": action,
            "old_dest": old_dest, "new_dest": row["adc2_dest_ev"],
            "delta": row["adc2_dest_ev"] - old_dest if pd.notna(old_dest) else np.nan,
        })

    changelog_df = pd.DataFrame(changelog)
    log.info("\n=== Changelog ===")
    log.info("\n%s", changelog_df.to_string(index=False))

    if args.dry_run:
        log.info("\n*** DRY RUN — no files written ***")
        return

    # Apply updates to master table
    master_updated = master.copy()
    for _, row in new_clean.iterrows():
        mid = row["mol_id"]
        mask = master_updated["mol_id"] == mid
        if mask.any():
            master_updated.loc[mask, "adc2_s1_ev"] = row["adc2_s1_ev"]
            master_updated.loc[mask, "adc2_t1_ev"] = row["adc2_t1_ev"]
            master_updated.loc[mask, "adc2_dest_ev"] = row["adc2_dest_ev"]
            master_updated.loc[mask, "adc2_fosc"] = row["adc2_fosc"]
            master_updated.loc[mask, "adc2_available"] = True
            # Update derived labels
            dest = row["adc2_dest_ev"]
            master_updated.loc[mask, "is_invest"] = dest < 0
            master_updated.loc[mask, "is_near_zero"] = abs(dest) <= 0.10
            master_updated.loc[mask, "is_high_fosc"] = row["adc2_fosc"] >= 0.10 if pd.notna(row["adc2_fosc"]) else pd.NA
            # Update split_group
            master_updated.loc[mask, "split_group"] = "target_labeled"
        else:
            log.warning("mol_id '%s' not found in master table — skipping", mid)

    # Save versioned output
    out_path = os.path.join(processed, "master_molecule_table_round1_updated.csv")
    master_updated.to_csv(out_path, index=False)
    log.info("Saved updated master table: %s", out_path)

    n_new_labeled = master_updated["adc2_available"].sum() - master["adc2_available"].sum()
    log.info("New ADC(2) labels added: %d (total now: %d)",
             n_new_labeled, master_updated["adc2_available"].sum())

    # Save changelog
    os.makedirs(os.path.join(proj, "results/tables"), exist_ok=True)
    changelog_path = os.path.join(proj, "results/tables/round1_ingest_changelog.csv")
    changelog_df.to_csv(changelog_path, index=False)
    log.info("Saved changelog: %s", changelog_path)

    # Generate ingest report
    os.makedirs(os.path.join(proj, "results/reports"), exist_ok=True)
    report = f"""# Round 1 ADC(2) Ingest Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Input file**: {args.input}
**Molecules ingested**: {len(new_clean)}
**New labels added**: {n_new_labeled}
**Total labeled after update**: {master_updated['adc2_available'].sum()}

## Changelog

| mol_id | Action | Old ΔEST (eV) | New ΔEST (eV) | Delta |
|--------|--------|---------------|---------------|-------|
"""
    for _, row in changelog_df.iterrows():
        old = f"{row['old_dest']:.4f}" if pd.notna(row.get("old_dest")) else "N/A"
        new = f"{row['new_dest']:.4f}"
        delta = f"{row.get('delta', float('nan')):.4f}" if pd.notna(row.get("delta")) else "N/A"
        report += f"| {row['mol_id']} | {row['action']} | {old} | {new} | {delta} |\n"

    report += f"""
## Validation

- Expected candidates (frozen): {len(expected_ids)}
- Returned in this batch: {len(incoming_ids)}
- Still pending: {len(missing_from_input)}
- Unexpected mol_ids: {len(unexpected)}

## Output Files

- `data/processed/master_molecule_table_round1_updated.csv`
- `results/tables/round1_ingest_changelog.csv`
- `results/reports/round1_ingest_report.md`

## Notes

- Original master table (`master_molecule_table.csv`) is preserved unchanged.
- Updated table uses `_round1_updated` suffix for version control.
- Downstream scripts should use the updated table for retraining.
"""

    report_path = os.path.join(proj, "results/reports/round1_ingest_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    log.info("Saved ingest report: %s", report_path)


if __name__ == "__main__":
    main()
