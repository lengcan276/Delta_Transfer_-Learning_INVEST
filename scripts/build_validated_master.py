#!/usr/bin/env python3
"""Build unified validated candidates master table.

Merges three non-overlapping sources:
  - adc2_final_10mol.csv (Round 1, 10 Hz-POZ + BCz3 molecules)
  - adc2_batch2_summary.csv (Batch 2, 9 molecules)
  - master_molecule_table_round1_updated.csv (R1 deployment, 15 molecules not in above)

Cross-validation source:
  - scscc2_batch2_summary.csv (SCS-CC2, 4 molecules with second-level cross-checks)

Classification rules (per feedback_invest_classification.md):
  - |ΔEST| < 0.030 eV → borderline_near_zero (within ADC(2)/SVP 1σ error)
  - ΔEST < -0.030 eV → negative_gap
  - ΔEST > +0.030 eV → positive_gap
  - fosc < 0.001 AND ΔEST < -0.030 eV → dark_negative_gap
  - Grubbs outlier (Hz_NH23) → retain as method-level candidate unless cross-check is discussed explicitly

Output: results/validated_candidates_master.csv
"""

import os
import pandas as pd
import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ── Load sources ──
a10 = pd.read_csv(os.path.join(ROOT, "results", "adc2_final_10mol.csv"))
b2 = pd.read_csv(os.path.join(ROOT, "results", "adc2_batch2_summary.csv"))
master = pd.read_csv(os.path.join(ROOT, "data", "processed", "master_molecule_table_round1_updated.csv"))
scscc2 = pd.read_csv(os.path.join(ROOT, "results", "scscc2_batch2_summary.csv"))

# ── Source 1: adc2_final_10mol (Round 1) ──
rows = []
for _, r in a10.iterrows():
    rows.append({
        "mol_id": r["Molecule"],
        "scaffold": r["Scaffold"],
        "batch": "round1",
        "method": "RI-ADC(2)/def2-SVP",
        "S1_eV": r["S1_eV"],
        "T1_eV": r["T1_eV"],
        "DEST_eV": r["ΔEST_eV"],
        "DEST_adc2_eV": r["ΔEST_eV"],
        "DEST_scscc2_eV": np.nan,
        "fosc": r["fosc"],
        "SOC_cm": r.get("SOC_cm", np.nan),
    })

# ── Source 2: adc2_batch2_summary (Batch 2) ──
for _, r in b2.iterrows():
    scaffold = "Hz" if r["name"].startswith("Hz") else ("5AP" if r["name"].startswith("5AP") else "BN-PAH")
    rows.append({
        "mol_id": r["name"],
        "scaffold": scaffold,
        "batch": "batch2",
        "method": f"{r['S1_method']}/{r['T1_method']}",
        "S1_eV": r["S1_eV"],
        "T1_eV": r["T1_eV"],
        "DEST_eV": r["DEST_eV"],
        "DEST_adc2_eV": r["DEST_eV"],
        "DEST_scscc2_eV": np.nan,
        "fosc": r["fosc"],
        "SOC_cm": np.nan,
    })

# ── Source 3: R1 deployment molecules not already covered ──
covered = {r["mol_id"] for r in rows}
this_work = master[(master["source_domain"] == "this_work") & (master["adc2_available"] == True)]

for _, r in this_work.iterrows():
    if r["mol_id"] not in covered:
        rows.append({
            "mol_id": r["mol_id"],
            "scaffold": r["scaffold_family"],
            "batch": "r1_deploy",
            "method": "RI-ADC(2)/def2-SVP",
            "S1_eV": r["adc2_s1_ev"],
            "T1_eV": r["adc2_t1_ev"],
            "DEST_eV": r["adc2_dest_ev"],
            "DEST_adc2_eV": r["adc2_dest_ev"],
            "DEST_scscc2_eV": np.nan,
            "fosc": r["adc2_fosc"],
            "SOC_cm": np.nan,
        })

df = pd.DataFrame(rows)
df["decision_basis"] = "ADC(2) primary"

# ── Classification ──
# Threshold justification:
#   ADC(2)/def2-SVP typical error for ΔEST: ±0.05 eV (Loos et al. JCTC 2021, Table 2)
#   Conservative borderline zone: |ΔEST| < 0.030 eV (within 1σ of method error)
#   fosc threshold: 0.001 corresponds to τ_rad > 10 μs (Ehrmaier 2019),
#   below which radiative decay is negligible for OLED application
THRESHOLD_BORDERLINE = 0.030  # eV, within ADC(2)/SVP 1σ error bar
FOSC_DARK = 0.001  # below this, effectively dark state

# Confidence labels are intentionally conservative.
#   medium: classification is outside the borderline window at the reported decision level
#   low:    borderline, pending, or contradictory cross-method evidence
DDEST_REVIEW_THRESHOLD = 0.05  # eV, used only for cross-method notes

# Data freeze date: 2026-04-30 (论文投稿截止)
# After freeze: new results go to SI, not main text
DATA_FREEZE = "2026-04-30"

def classify(row):
    dest = row["DEST_eV"]
    fosc = row["fosc"]
    mol = row["mol_id"]

    if pd.isna(dest):
        return "pending", "low"

    if dest < -THRESHOLD_BORDERLINE:
        if fosc < FOSC_DARK:
            return "dark_negative_gap", "medium"
        else:
            return "negative_gap", "medium"
    elif abs(dest) <= THRESHOLD_BORDERLINE:
        return "borderline_near_zero", "low"
    else:
        return "positive_gap", "medium"

classifications = df.apply(classify, axis=1, result_type="expand")
df["classification"] = classifications[0]
df["confidence"] = classifications[1]

# ── SCS-CC2 cross-check metadata ──
scscc2_dict = {}
for _, r in scscc2.iterrows():
    scscc2_dict[r["name"]] = {"DEST_scscc2": r["DEST_eV"], "S1_scscc2": r["S1_eV"], "T1_scscc2": r["T1_eV"]}

for mol, scs_data in scscc2_dict.items():
    mask = df["mol_id"] == mol
    if mask.any():
        adc2_dest = df.loc[mask, "DEST_adc2_eV"].values[0]
        scs_dest = scs_data["DEST_scscc2"]
        delta_dest = abs(adc2_dest - scs_dest)
        df.loc[mask, "DEST_scscc2_eV"] = scs_dest

        # Both methods agree on sign?
        same_sign = (adc2_dest < 0 and scs_dest < 0) or (adc2_dest > 0 and scs_dest > 0)

        if same_sign:
            if delta_dest > DDEST_REVIEW_THRESHOLD:
                quant_note = (
                    f"ΔΔEST={delta_dest:.3f}eV>{DDEST_REVIEW_THRESHOLD}eV, "
                    "sign confirmed but magnitude is method-dependent"
                )
            else:
                quant_note = (
                    f"ΔΔEST={delta_dest:.3f}eV<={DDEST_REVIEW_THRESHOLD}eV, "
                    "sign and magnitude agree within the review threshold"
                )

            if abs(adc2_dest) <= THRESHOLD_BORDERLINE and abs(scs_dest) > THRESHOLD_BORDERLINE:
                df.loc[mask, "DEST_eV"] = scs_dest
                df.loc[mask, "method"] = df.loc[mask, "method"].values[0] + " + SCS-CC2/TZVP"
                df.loc[mask, "decision_basis"] = "SCS-CC2 override after ADC(2) borderline result"
            else:
                df.loc[mask, "decision_basis"] = "ADC(2) primary with SCS-CC2 cross-check"

            sign_label = "negative" if adc2_dest < 0 else "positive"
            df.loc[mask, "note"] = (
                f"ADC(2)={adc2_dest:+.4f}, SCS-CC2={scs_dest:+.4f}, "
                f"both {sign_label}, {quant_note}"
            )
        else:
            df.loc[mask, "confidence"] = "low"
            df.loc[mask, "note"] = (
                f"CONTRADICTORY: ADC(2)={adc2_dest:+.4f} vs SCS-CC2={scs_dest:+.4f}, "
                f"ΔΔEST={delta_dest:.3f}eV, reclassified by SCS-CC2"
            )
            df.loc[mask, "DEST_eV"] = scs_dest
            df.loc[mask, "method"] = df.loc[mask, "method"].values[0] + " → SCS-CC2 override"
            df.loc[mask, "decision_basis"] = "SCS-CC2 override after sign conflict"

# Re-classify molecules that got SCS-CC2 overrides
for mol in scscc2_dict:
    mask = df["mol_id"] == mol
    if mask.any():
        row = df.loc[mask].iloc[0]
        cls, conf = classify(row)
        df.loc[mask, "classification"] = cls
        current_conf = df.loc[mask, "confidence"].values[0]
        if current_conf != "low":
            df.loc[mask, "confidence"] = conf

# ── Add notes for specific cases ──
df["note"] = df["note"].fillna("")

# ── Sort and save ──
order = {"negative_gap": 0, "dark_negative_gap": 1,
         "borderline_near_zero": 2, "positive_gap": 3, "pending": 4}
df["_sort"] = df["classification"].map(order)
df = df.sort_values(["_sort", "DEST_eV"]).drop(columns=["_sort"])

df.to_csv(os.path.join(ROOT, "results", "validated_candidates_master.csv"), index=False)

# ── Summary ──
print("=" * 70)
print("Validated Candidates Master Table")
print("=" * 70)
print(f"\nTotal molecules: {len(df)}")
print(f"\nBy batch:")
print(df["batch"].value_counts().to_string())
print(f"\nBy classification:")
print(df["classification"].value_counts().to_string())
print(f"\nBy scaffold × classification:")
print(pd.crosstab(df["scaffold"], df["classification"]).to_string())

print(f"\n{'='*70}")
print("Negative-gap molecules (DEST < -0.030 eV):")
print("=" * 70)
neg = df[df["classification"].isin(["negative_gap", "dark_negative_gap"])]
for _, r in neg.iterrows():
    flag = " ⚠" if r["confidence"] == "low" else ""
    print(f"  {r['mol_id']:35s} DEST={r['DEST_eV']:+.4f} fosc={r['fosc']:.4f} "
          f"[{r['classification']}] conf={r['confidence']}{flag}")

print(f"\nBorderline molecules (|DEST| ≤ 0.030 eV):")
border = df[df["classification"] == "borderline_near_zero"]
for _, r in border.iterrows():
    print(f"  {r['mol_id']:35s} DEST={r['DEST_eV']:+.4f} fosc={r['fosc']:.4f}")

print(f"\nOutput: {os.path.join(ROOT, 'results', 'validated_candidates_master.csv')}")
