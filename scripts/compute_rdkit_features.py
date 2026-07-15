#!/usr/bin/env python3
"""Compute RDKit 2D descriptors and Morgan fingerprint PCA from SMILES.

Reads master_molecule_table.csv, computes features, saves to
data/processed/rdkit_features.csv.

Usage:
    python scripts/compute_rdkit_features.py [--project-root PROJECT_ROOT]
"""
import argparse
import logging
import os

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdMolDescriptors
from sklearn.decomposition import PCA

RDLogger.DisableLog("rdApp.*")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SEED = 42
N_FP_BITS = 2048
FP_RADIUS = 2
N_PCA = 32


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-root", default=os.path.join(os.path.dirname(__file__), ".."))
    p.add_argument("--n-pca", type=int, default=N_PCA)
    return p.parse_args()


def compute_2d_descriptors(mol):
    """Compute a set of 2D molecular descriptors."""
    if mol is None:
        return {}
    return {
        "mw": Descriptors.MolWt(mol),
        "logp": Descriptors.MolLogP(mol),
        "tpsa": Descriptors.TPSA(mol),
        "hbd": Descriptors.NumHDonors(mol),
        "hba": Descriptors.NumHAcceptors(mol),
        "rot_bonds": Descriptors.NumRotatableBonds(mol),
        "aromatic_rings": Descriptors.NumAromaticRings(mol),
        "ring_count": Descriptors.RingCount(mol),
        "n_count": sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 7),
        "b_count": sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 5),
        "o_count": sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 8),
        "s_count": sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() == 16),
        "heteroatom_ratio": sum(1 for a in mol.GetAtoms() if a.GetAtomicNum() not in (1, 6)) / max(mol.GetNumHeavyAtoms(), 1),
        "heavy_atom_count": mol.GetNumHeavyAtoms(),
        "num_atoms": mol.GetNumAtoms(),
        "fraction_csp3": Descriptors.FractionCSP3(mol),
        "num_amide_bonds": rdMolDescriptors.CalcNumAmideBonds(mol),
        "num_bridgehead_atoms": rdMolDescriptors.CalcNumBridgeheadAtoms(mol),
        "num_spiro_atoms": rdMolDescriptors.CalcNumSpiroAtoms(mol),
        "num_hetero_cycles": rdMolDescriptors.CalcNumHeterocycles(mol),
        "num_aromatic_hetero_cycles": rdMolDescriptors.CalcNumAromaticHeterocycles(mol),
        "num_saturated_rings": rdMolDescriptors.CalcNumSaturatedRings(mol),
    }


def compute_morgan_fp(mol, radius=FP_RADIUS, n_bits=N_FP_BITS):
    """Compute Morgan fingerprint as numpy array."""
    if mol is None:
        return np.full(n_bits, np.nan)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    return np.array(fp)


def main():
    args = parse_args()
    proj = os.path.expanduser(args.project_root)
    master_path = os.path.join(proj, "data/processed/master_molecule_table.csv")
    out_path = os.path.join(proj, "data/processed/rdkit_features.csv")

    master = pd.read_csv(master_path)
    log.info("Loaded master table: %d molecules", len(master))

    # Parse molecules
    mols = []
    failed = []
    for i, smi in enumerate(master["smiles"]):
        m = Chem.MolFromSmiles(str(smi))
        if m is None:
            failed.append((i, smi))
        mols.append(m)

    log.info("SMILES parsed: %d ok, %d failed", len(mols) - len(failed), len(failed))
    if failed:
        log.warning("Failed SMILES (first 10): %s", failed[:10])

    # 2D descriptors
    desc_rows = []
    for mol in mols:
        desc_rows.append(compute_2d_descriptors(mol))
    desc_df = pd.DataFrame(desc_rows)

    # Morgan fingerprints → PCA
    fp_matrix = np.array([compute_morgan_fp(mol) for mol in mols])
    valid_mask = ~np.isnan(fp_matrix).any(axis=1)
    log.info("Valid fingerprints: %d / %d", valid_mask.sum(), len(fp_matrix))

    n_pca = min(args.n_pca, fp_matrix[valid_mask].shape[0], fp_matrix.shape[1])
    pca = PCA(n_components=n_pca, random_state=SEED)
    pca.fit(fp_matrix[valid_mask])
    log.info("PCA explained variance (first 5): %s",
             np.round(pca.explained_variance_ratio_[:5], 4))

    fp_pca = np.full((len(fp_matrix), n_pca), np.nan)
    fp_pca[valid_mask] = pca.transform(fp_matrix[valid_mask])

    fp_df = pd.DataFrame(fp_pca, columns=[f"fp_pc{i+1}" for i in range(n_pca)])

    # Combine
    result = pd.concat([master[["mol_id"]], desc_df, fp_df], axis=1)
    result.to_csv(out_path, index=False)
    log.info("Saved RDKit features: %s, shape=%s", out_path, result.shape)


if __name__ == "__main__":
    main()
