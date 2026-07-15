#!/usr/bin/env python3
"""Build unified master_molecule_table.csv from all data sources.

Data sources:
  1. invest_highquality_dataset.csv  (1079 mol, ΔDFT-level DEST)
  2. pollice2021_adc2.txt            (446 Pollice ADC(2) labels)
  3. pollice2021_smiles.txt          (1719 Pollice SMILES)
  4. adc2_validation_results.csv     (10 this-work ADC(2) batch1)
  5. adc2_batch2_summary.csv         (9 this-work ADC(2) batch2)
  6. scscc2_batch2_summary.csv       (3 SCS-CC2 cross-check)
  7. master_table_v3.csv             (155 this-work ΔDFT + auxiliary)
  8. ks_od_descriptors.csv           (127 KS-OD orbital descriptors)

Usage:
    python scripts/build_master_table.py [--data-root DATA_ROOT] [--output OUTPUT]
"""
import argparse
import logging
import os
import sys

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--data-root",
        default=os.path.join(os.path.dirname(__file__), ".."),
        help="Project root (default: parent of scripts/)",
    )
    p.add_argument(
        "--repo-root",
        default=os.path.join(os.path.dirname(__file__), ".."),
        help="Project root (default: parent of scripts/)",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Output CSV path (default: <data-root>/data/processed/master_molecule_table.csv)",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_pollice_smiles(repo_root: str) -> pd.DataFrame:
    """Load 1719 Pollice SMILES."""
    path = os.path.join(repo_root, "data/invest_core/literature_data/pollice2021_smiles.txt")
    df = pd.read_csv(path, sep=r"\s+", names=["mol_id", "smiles"], skiprows=1)
    log.info("Pollice SMILES: %d rows", len(df))
    return df


def load_pollice_adc2(repo_root: str) -> pd.DataFrame:
    """Load 446 Pollice ADC(2) results."""
    path = os.path.join(repo_root, "data/invest_core/literature_data/pollice2021_adc2.txt")
    df = pd.read_csv(path, sep=r"\s+", skiprows=1,
                      names=["mol_id", "s1_ev", "t1_ev", "dest_ev", "fosc"])
    log.info("Pollice ADC(2): %d rows", len(df))
    return df


def load_highquality(repo_root: str) -> pd.DataFrame:
    """Load invest_highquality_dataset.csv (1079 mol with ΔDFT)."""
    path = os.path.join(repo_root, "data/invest_core/invest_highquality_dataset.csv")
    df = pd.read_csv(path)
    log.info("invest_highquality: %d rows, sources: %s",
             len(df), df["source"].value_counts().to_dict())
    return df


def load_thiswork_adc2_batch1(repo_root: str) -> pd.DataFrame:
    """Load 10 this-work ADC(2) batch1 results."""
    path = os.path.join(repo_root, "results/adc2_validation_results.csv")
    df = pd.read_csv(path)
    log.info("This-work ADC(2) batch1: %d rows", len(df))
    return df


def load_thiswork_adc2_batch2(repo_root: str) -> pd.DataFrame:
    """Load 9 this-work ADC(2) batch2 results."""
    path = os.path.join(repo_root, "results/adc2_batch2_summary.csv")
    df = pd.read_csv(path)
    log.info("This-work ADC(2) batch2: %d rows", len(df))
    return df


def load_scscc2(repo_root: str) -> pd.DataFrame:
    """Load SCS-CC2 cross-check (3 mol)."""
    path = os.path.join(repo_root, "results/scscc2_batch2_summary.csv")
    df = pd.read_csv(path)
    log.info("SCS-CC2: %d rows", len(df))
    return df


def load_master_v3(repo_root: str) -> pd.DataFrame:
    """Load master_table_v3.csv (155 this-work ΔDFT)."""
    path = os.path.join(repo_root, "data/master_table_v3.csv")
    df = pd.read_csv(path)
    log.info("master_table_v3: %d rows", len(df))
    return df


def load_ks_od(repo_root: str) -> pd.DataFrame:
    """Load KS-OD orbital descriptors (127 mol)."""
    path = os.path.join(repo_root, "results/invest_results/ks_od_descriptors.csv")
    df = pd.read_csv(path)
    log.info("KS-OD descriptors: %d rows", len(df))
    return df


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_master_table(repo_root: str) -> pd.DataFrame:
    """Merge all data sources into a unified master table."""

    # --- 1. Start from Pollice SMILES (source domain) ---
    pol_smi = load_pollice_smiles(repo_root)
    pol_adc2 = load_pollice_adc2(repo_root)

    pollice = pol_smi.merge(pol_adc2, on="mol_id", how="left")
    pollice["source_domain"] = "pollice"
    pollice["scaffold_family"] = "pollice_heptazine_deriv"  # generic
    pollice["adc2_available"] = pollice["dest_ev"].notna()

    # Rename ADC(2) columns
    pollice = pollice.rename(columns={
        "s1_ev": "adc2_s1_ev",
        "t1_ev": "adc2_t1_ev",
        "dest_ev": "adc2_dest_ev",
        "fosc": "adc2_fosc",
    })

    log.info("Pollice merged: %d total, %d with ADC(2)",
             len(pollice), pollice["adc2_available"].sum())

    # --- 2. This-work molecules from master_table_v3 ---
    mv3 = load_master_v3(repo_root)

    thiswork = pd.DataFrame()
    thiswork["mol_id"] = mv3["molecule_id"]
    thiswork["smiles"] = mv3["SMILES"]
    thiswork["scaffold_family"] = mv3["scaffold_family"]
    thiswork["source_domain"] = "this_work"
    thiswork["dft_dest_raw_ev"] = mv3["dft_delta_est_raw"]
    thiswork["dft_dest_calibrated_ev"] = mv3["dft_delta_est_calibrated"]
    thiswork["fosc_dft"] = mv3["fosc_dft"]

    # --- 3. Merge this-work ADC(2) batch1 + batch2 ---
    b1 = load_thiswork_adc2_batch1(repo_root)
    b2 = load_thiswork_adc2_batch2(repo_root)

    # Standardize batch1
    adc2_tw = pd.DataFrame()
    adc2_tw = pd.concat([
        b1.rename(columns={
            "molecule": "mol_id",
            "S1_ADC2_eV": "adc2_s1_ev",
            "T1_ADC2_eV": "adc2_t1_ev",
            "DEST_ADC2_eV": "adc2_dest_ev",
            "fosc_S1_ADC2": "adc2_fosc",
        })[["mol_id", "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc"]],
        b2.rename(columns={
            "name": "mol_id",
            "S1_eV": "adc2_s1_ev",
            "T1_eV": "adc2_t1_ev",
            "DEST_eV": "adc2_dest_ev",
            "fosc": "adc2_fosc",
        })[["mol_id", "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc"]],
    ], ignore_index=True)

    # Drop duplicates (some mol may appear in both batches)
    adc2_tw = adc2_tw.drop_duplicates(subset="mol_id", keep="first")
    log.info("This-work ADC(2) combined: %d unique molecules", len(adc2_tw))

    thiswork = thiswork.merge(adc2_tw, on="mol_id", how="left")
    thiswork["adc2_available"] = thiswork["adc2_dest_ev"].notna()

    # --- 4. Merge KS-OD descriptors ---
    ksod = load_ks_od(repo_root)
    ksod_clean = ksod[ksod["status"] == "complete"][
        ["name", "OD_eV", "HOMO_m1_eV", "HOMO_eV", "LUMO_eV", "LUMO_p1_eV"]
    ].rename(columns={
        "name": "mol_id",
        "OD_eV": "od_index",
        "HOMO_m1_eV": "homo_m1_ev",
        "HOMO_eV": "homo_ev",
        "LUMO_eV": "lumo_ev",
        "LUMO_p1_eV": "lumo_p1_ev",
    })
    ksod_clean["hl_gap_ev"] = ksod_clean["lumo_ev"] - ksod_clean["homo_ev"]

    thiswork = thiswork.merge(ksod_clean, on="mol_id", how="left")

    # --- 5. Load SCS-CC2 for cross-check (store as separate columns) ---
    scscc2 = load_scscc2(repo_root)
    scscc2_clean = scscc2[["name", "S1_eV", "T1_eV", "DEST_eV"]].rename(columns={
        "name": "mol_id",
        "S1_eV": "scscc2_s1_ev",
        "T1_eV": "scscc2_t1_ev",
        "DEST_eV": "scscc2_dest_ev",
    })
    thiswork = thiswork.merge(scscc2_clean, on="mol_id", how="left")

    # --- 6. Also pull Omar / Pang from highquality dataset ---
    hq = load_highquality(repo_root)
    omar_pang = hq[hq["source"].isin(["Omar2023_JACS", "Pang2025_npj"])].copy()
    other = pd.DataFrame()
    other["mol_id"] = omar_pang["name"]
    other["smiles"] = omar_pang["canonical_SMILES"]
    other["scaffold_family"] = omar_pang["core_type"]
    other["source_domain"] = omar_pang["source"].map({
        "Omar2023_JACS": "omar2023",
        "Pang2025_npj": "pang2025",
    })
    other["dft_dest_calibrated_ev"] = omar_pang["DEST_eV"]
    other["fosc_dft"] = omar_pang["fosc"]
    other["adc2_available"] = False

    # --- 7. Concatenate all ---
    master = pd.concat([pollice, thiswork, other], ignore_index=True)

    # --- 8. Derived labels (use nullable boolean to allow NaN) ---
    master["is_invest"] = pd.array(master["adc2_dest_ev"] < 0, dtype=pd.BooleanDtype())
    master["is_near_zero"] = pd.array(master["adc2_dest_ev"].abs() <= 0.10, dtype=pd.BooleanDtype())
    master["is_high_fosc"] = pd.array(master["adc2_fosc"] >= 0.10, dtype=pd.BooleanDtype())

    # Where ADC(2) is not available, set derived labels to pd.NA
    no_adc2 = ~master["adc2_available"]
    master.loc[no_adc2, "is_invest"] = pd.NA
    master.loc[no_adc2, "is_near_zero"] = pd.NA
    master.loc[no_adc2, "is_high_fosc"] = pd.NA

    # --- 9. Split group assignment ---
    # pollice = source, this_work with ADC(2) = target_labeled,
    # this_work without ADC(2) = target_unlabeled, omar/pang = auxiliary
    def assign_split(row):
        if row["source_domain"] == "pollice":
            return "source" if row["adc2_available"] else "source_unlabeled"
        elif row["source_domain"] == "this_work":
            return "target_labeled" if row["adc2_available"] else "target_unlabeled"
        else:
            return "auxiliary"

    master["split_group"] = master.apply(assign_split, axis=1)

    # --- 10. Reorder columns ---
    col_order = [
        "mol_id", "smiles", "scaffold_family", "source_domain", "split_group",
        # ADC(2) labels
        "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev", "adc2_fosc", "adc2_available",
        # SCS-CC2 cross-check
        "scscc2_s1_ev", "scscc2_t1_ev", "scscc2_dest_ev",
        # DFT-level
        "dft_dest_raw_ev", "dft_dest_calibrated_ev", "fosc_dft",
        # Orbital / physics
        "homo_ev", "lumo_ev", "hl_gap_ev", "homo_m1_ev", "lumo_p1_ev", "od_index",
        # Derived
        "is_invest", "is_near_zero", "is_high_fosc",
    ]
    # Keep only columns that exist
    col_order = [c for c in col_order if c in master.columns]
    # Add any remaining columns
    remaining = [c for c in master.columns if c not in col_order]
    master = master[col_order + remaining]

    return master


def print_summary(master: pd.DataFrame):
    """Print a summary of the master table."""
    log.info("=" * 60)
    log.info("MASTER TABLE SUMMARY")
    log.info("=" * 60)
    log.info("Total molecules: %d", len(master))
    log.info("Unique mol_ids: %d", master["mol_id"].nunique())

    log.info("\nBy source_domain:")
    for src, cnt in master["source_domain"].value_counts().items():
        log.info("  %-15s %d", src, cnt)

    log.info("\nBy split_group:")
    for grp, cnt in master["split_group"].value_counts().items():
        log.info("  %-20s %d", grp, cnt)

    n_adc2 = master["adc2_available"].sum()
    log.info("\nADC(2) available: %d / %d (%.1f%%)",
             n_adc2, len(master), 100 * n_adc2 / len(master))

    adc2_mask = master["adc2_available"]
    if adc2_mask.any():
        dest = master.loc[adc2_mask, "adc2_dest_ev"]
        log.info("ADC(2) ΔEST range: [%.3f, %.3f] eV", dest.min(), dest.max())
        log.info("INVEST (ΔEST<0): %d", (dest < 0).sum())
        log.info("Near-zero (|ΔEST|≤0.10): %d", (dest.abs() <= 0.10).sum())

    log.info("\nMissing values (selected columns):")
    for col in ["smiles", "adc2_dest_ev", "dft_dest_calibrated_ev",
                "homo_ev", "od_index"]:
        if col in master.columns:
            n_miss = master[col].isna().sum()
            log.info("  %-25s %d / %d missing", col, n_miss, len(master))


def main():
    args = parse_args()
    repo_root = os.path.expanduser(args.repo_root)
    data_root = os.path.expanduser(args.data_root)

    master = build_master_table(repo_root)
    print_summary(master)

    if args.output:
        out_path = args.output
    else:
        out_path = os.path.join(data_root, "data", "processed", "master_molecule_table.csv")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    master.to_csv(out_path, index=False)
    log.info("\nSaved master table to: %s", out_path)
    log.info("Shape: %s", master.shape)


if __name__ == "__main__":
    main()
