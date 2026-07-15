#!/usr/bin/env python3
"""
Audit Phase 1 — extract local 446 Pollice ADC(2)/cc-pVDZ source subset.

Uses the EXACT filter logic from the project's own
`scripts/diag_distance_to_source.py` (lines 81-89), which is the only
script that explicitly asserts N == 446. The filter is:

    pollice = master[
        (master["source_domain"] == "pollice")
        & master["adc2_dest_ev"].notna()
    ]

We do NOT invent a new filter. SMILES are canonicalised with RDKit
(version pinned by the project's requirements.txt / current environment).

Outputs:
    audit/pollice_446_local.csv

This script does NOT modify any file under data/, results/, scripts/
(except its own location scripts/audit/).
"""

import csv
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
MASTER = ROOT / "data" / "processed" / "master_molecule_table.csv"
MODEL_INPUT = ROOT / "data" / "processed" / "model_input_table.csv"
OUT = ROOT / "audit" / "pollice_446_local.csv"

try:
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    RDKIT_OK = True
except ImportError:
    RDKIT_OK = False


def canonicalise(smiles):
    if not RDKIT_OK or not isinstance(smiles, str) or not smiles:
        return "MISSING_RDKIT" if not RDKIT_OK else ""
    try:
        m = Chem.MolFromSmiles(smiles)
        if m is None:
            return "PARSE_FAIL"
        return Chem.MolToSmiles(m, canonical=True)
    except Exception:
        return "PARSE_FAIL"


def main():
    if not MASTER.exists():
        print(f"FATAL: {MASTER} not found", file=sys.stderr)
        sys.exit(2)
    if not MODEL_INPUT.exists():
        print(f"FATAL: {MODEL_INPUT} not found", file=sys.stderr)
        sys.exit(2)

    master = pd.read_csv(MASTER)
    print(f"loaded master_molecule_table.csv: {len(master)} rows")

    # --- Apply the project's authoritative filter (from
    # scripts/diag_distance_to_source.py lines 81-89) ---
    FILTER_RULE = ('source_domain == "pollice" AND adc2_dest_ev.notna(); '
                   'source = data/processed/master_molecule_table.csv; '
                   'filter copied from scripts/diag_distance_to_source.py '
                   'lines 81-89.')
    pollice = master[
        (master["source_domain"] == "pollice")
        & master["adc2_dest_ev"].notna()
    ].copy()
    n_local = len(pollice)
    print(f"local Pollice subset (project filter): {n_local} rows  "
          f"[expected 446]")

    # --- Sanity cross-check against model_input_table.csv ---
    model_input = pd.read_csv(MODEL_INPUT)
    mit_pollice = model_input[
        (model_input["source_domain"] == "pollice")
        & (model_input["adc2_available"] == True)
        & model_input["adc2_dest_ev"].notna()
    ].copy()
    n_mit = len(mit_pollice)
    print(f"model_input_table parallel filter: {n_mit} rows")

    # --- SMILES canonicalisation ---
    if not RDKIT_OK:
        print("WARNING: RDKit not available; canonical column = MISSING_RDKIT",
              file=sys.stderr)
    pollice["canonical_smiles_rdkit"] = pollice["smiles"].map(canonicalise)

    # Method/basis are not explicit columns in master_molecule_table.csv;
    # they are documented elsewhere as "ADC(2)/cc-pVDZ" (the Pollice 2021
    # source-domain protocol). We tag them with the project-documented values
    # and flag the documentation source so the auditor sees it is metadata,
    # not extracted from raw output.
    pollice["method"] = "ADC(2)"
    pollice["basis"] = "cc-pVDZ"
    pollice["method_basis_source"] = (
        "PROJECT_METADATA — declared as ADC(2)/cc-pVDZ in "
        "scripts/diag_distance_to_source.py docstring + Pollice 2021 "
        "(Matter 4, 1654-1682). NOT extracted from local raw output for "
        "the source domain (source-domain raw outputs are external "
        "Pollice supplementary data and may not be present locally)."
    )
    pollice["source_dataset"] = "pollice"
    pollice["source_file"] = "data/processed/master_molecule_table.csv"
    pollice["filter_rule_used"] = FILTER_RULE

    # --- Output ---
    out_cols = [
        "mol_id", "smiles", "canonical_smiles_rdkit",
        "adc2_s1_ev", "adc2_t1_ev", "adc2_dest_ev",
        "method", "basis", "method_basis_source",
        "source_dataset", "source_file", "filter_rule_used",
    ]
    # Rename adc2_dest_ev → DEST_eV_local per audit spec
    pollice["DEST_eV_local"] = pollice["adc2_dest_ev"]
    out = pollice[[
        "mol_id", "smiles", "canonical_smiles_rdkit",
        "DEST_eV_local", "adc2_s1_ev", "adc2_t1_ev",
        "method", "basis", "method_basis_source",
        "source_dataset", "source_file", "filter_rule_used",
    ]].rename(columns={"mol_id": "name"})

    out.to_csv(OUT, index=False)
    print(f"wrote {OUT}  ({len(out)} rows)")

    # --- Summary stats ---
    print("\n--- summary ---")
    print(f"  N rows                = {len(out)}")
    print(f"  expected              = 446")
    print(f"  N==446                = {len(out) == 446}")
    print(f"  canonical SMILES OK   = "
          f"{(out['canonical_smiles_rdkit'].str.len() > 5).sum()}")
    print(f"  canonical SMILES fail = "
          f"{(out['canonical_smiles_rdkit'].isin(['PARSE_FAIL', 'MISSING_RDKIT', ''])).sum()}")
    print(f"  RDKit available       = {RDKIT_OK}")

    # cross-check sanity vs model_input_table
    if n_mit != n_local:
        print(f"  WARNING: master filter ({n_local}) != model_input filter "
              f"({n_mit}); see audit/phase1 report for set-diff.")


if __name__ == "__main__":
    main()
