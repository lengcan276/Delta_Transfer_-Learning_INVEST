#!/usr/bin/env python3
"""
build_cross_check_n13.py — assemble the n=13 SCS-CC2 cross-check table
and compute the Clopper-Pearson 95% binomial CI on sign retention.

Output:
    results/scscc2_extension_n13/cross_check_n13.csv
    results/scscc2_extension_n13/stats_n13.json
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "parsers"))
from parse_scscc2_dest import compute_dest  # noqa

ROOT = Path("/home/nudt_cleng/2026/results")
EXT = ROOT / "scscc2_extension_n13"

# Cohort: (mol_id, atoms, gnorm_header, ADC2_dEST_eV, sing_ricc2_path, trip_ricc2_path)
COHORT = [
    # 4 historical (adc2_batch2_raw)
    ("Hz_NH23",                 22, 7.6e-4, -0.38346,
     ROOT / "adc2_batch2_raw" / "Hz_NH23_scscc2" / "ricc2_scscc2_sing.out",
     ROOT / "adc2_batch2_raw" / "Hz_NH23_scscc2" / "ricc2_scscc2_trip.out"),
    ("Hz_DMAC1_NPh21_CF31",     70, 4.2e-4, -0.12034,
     ROOT / "adc2_batch2_raw" / "Hz_DMAC1_NPh21_CF31" / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out",
     ROOT / "adc2_batch2_raw" / "Hz_DMAC1_NPh21_CF31" / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out"),
    ("Hz_NPh22_SO2Ph1",         62, 4.8e-4, -0.09532,
     ROOT / "adc2_batch2_raw" / "Hz_NPh22_SO2Ph1" / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out",
     ROOT / "adc2_batch2_raw" / "Hz_NPh22_SO2Ph1" / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out"),
    ("Hz_POZ1_NPh21_CF31",      72, 6.6e-5, -0.00971,
     ROOT / "adc2_batch2_final" / "Hz_POZ1_NPh21_CF31" / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out",
     ROOT / "adc2_batch2_final" / "Hz_POZ1_NPh21_CF31" / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out"),
    # 9 new (Phase 2 — scscc2_extension_n13)
    ("Hz_NEt22_CF31",           47, 1.5e-4, -0.03593,
     EXT / "Hz_NEt22_CF31" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NEt22_CF31" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_DMAC2_SO2Ph1",         87, 8.2e-5, -0.03205,
     EXT / "Hz_DMAC2_SO2Ph1" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_DMAC2_SO2Ph1" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_NH22_SO2Ph1",          33, 1.2e-4, -0.064,
     EXT / "Hz_NH22_SO2Ph1" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NH22_SO2Ph1" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_DMAC1_NPh21_SO2Ph1",   80, 6.3e-5, -0.066,
     EXT / "Hz_DMAC1_NPh21_SO2Ph1" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_DMAC1_NPh21_SO2Ph1" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_Cz1_NPh21_CF31",       61, 7.1e-5, -0.136,
     EXT / "Hz_Cz1_NPh21_CF31" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_Cz1_NPh21_CF31" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_NPh23",                82, 5.6e-5, -0.123,
     EXT / "Hz_NPh23" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NPh23" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_NPh21_Cz2",            78, 8.3e-5, -0.119,
     EXT / "Hz_NPh21_Cz2" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NPh21_Cz2" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_NEt21_NPh22",          74, 1.4e-4, -0.089,
     EXT / "Hz_NEt21_NPh22" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NEt21_NPh22" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
    ("Hz_NPh22_CN1",            61, 8.1e-5, -0.054,
     EXT / "Hz_NPh22_CN1" / "turbo_sing_scscc2_svp" / "ricc2_scscc2_sing.out",
     EXT / "Hz_NPh22_CN1" / "turbo_trip_scscc2_svp" / "ricc2_scscc2_trip.out"),
]

# Geometry source per molecule
GEOM_SOURCE = {
    "Hz_NH23": "hf_calcs",
    "Hz_DMAC1_NPh21_CF31": "adc2_batch2_final",
    "Hz_NPh22_SO2Ph1": "adc2_batch2_final",
    "Hz_POZ1_NPh21_CF31": "adc2_batch2_final",
    # Phase 2 new
    "Hz_NEt22_CF31": "delta_dft",
    "Hz_DMAC2_SO2Ph1": "delta_dft",
    "Hz_NH22_SO2Ph1": "delta_dft",
    "Hz_DMAC1_NPh21_SO2Ph1": "delta_dft",
    "Hz_Cz1_NPh21_CF31": "delta_dft",
    "Hz_NPh23": "delta_dft",
    "Hz_NPh21_Cz2": "delta_dft",
    "Hz_NEt21_NPh22": "delta_dft",
    "Hz_NPh22_CN1": "delta_dft",
}

BATCH = {
    "Hz_NH23": "historical",
    "Hz_DMAC1_NPh21_CF31": "historical",
    "Hz_NPh22_SO2Ph1": "historical",
    "Hz_POZ1_NPh21_CF31": "historical",
    "Hz_NEt22_CF31": "phase2.2",
    "Hz_DMAC2_SO2Ph1": "phase2.2",
    "Hz_NH22_SO2Ph1": "phase2.4",
    "Hz_DMAC1_NPh21_SO2Ph1": "phase2.4",
    "Hz_Cz1_NPh21_CF31": "phase2.4",
    "Hz_NPh23": "phase2.4",
    "Hz_NPh21_Cz2": "phase2.4",
    "Hz_NEt21_NPh22": "phase2.4",
    "Hz_NPh22_CN1": "phase2.4",
}


def clopper_pearson(k, n, alpha=0.05):
    """Clopper-Pearson exact two-sided binomial CI."""
    from scipy.stats import beta
    lo = beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return lo, hi


def main():
    rows = []
    for mol_id, atoms, gnorm, adc2_dE, sing_path, trip_path in COHORT:
        try:
            res = compute_dest(sing_path, trip_path)
        except Exception as e:
            print(f"FAIL {mol_id}: {e}")
            continue
        scscc2_dE = res["dE_ST_eV"]
        ddE = scscc2_dE - adc2_dE
        sign_agree = (adc2_dE < 0) == (scscc2_dE < 0)
        rows.append({
            "mol_id": mol_id,
            "atoms": atoms,
            "geom_source": GEOM_SOURCE[mol_id],
            "geom_gnorm": gnorm,
            "batch": BATCH[mol_id],
            "ADC2_S1_eV": None,  # not always stored; compute later if needed
            "ADC2_T1_eV": None,
            "ADC2_dEST_eV": round(adc2_dE, 5),
            "ADC2_dEST_meV": round(adc2_dE * 1000, 2),
            "SCSCC2_S1_eV": round(res["E_S1_eV"], 5),
            "SCSCC2_T1_eV": round(res["E_T1_eV"], 5),
            "SCSCC2_dEST_eV": round(scscc2_dE, 5),
            "SCSCC2_dEST_meV": round(scscc2_dE * 1000, 2),
            "ddEST_meV": round(ddE * 1000, 2),
            "abs_ddEST_meV": round(abs(ddE) * 1000, 2),
            "sign_agree": sign_agree,
        })

    # CSV
    csv_path = EXT / "cross_check_n13.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {csv_path}")
    print(f"  n = {len(rows)}")

    # Stats
    n = len(rows)
    k = sum(1 for r in rows if r["sign_agree"])
    lo95, hi95 = clopper_pearson(k, n, 0.05)
    lo90, hi90 = clopper_pearson(k, n, 0.10)

    abs_diffs = [r["abs_ddEST_meV"] for r in rows]
    abs_diffs.sort()
    mean_abs = sum(abs_diffs) / n
    median_abs = abs_diffs[n // 2]

    stats = {
        "n_total": n,
        "n_sign_retain": k,
        "sign_retain_rate": k / n,
        "clopper_pearson_95_CI": [round(lo95, 4), round(hi95, 4)],
        "clopper_pearson_90_CI": [round(lo90, 4), round(hi90, 4)],
        "abs_ddEST_meV_summary": {
            "min": min(abs_diffs),
            "max": max(abs_diffs),
            "mean": round(mean_abs, 2),
            "median": median_abs,
        },
        "design_note": (
            "n=13 INVEST cohort: 4 historical SCS-CC2 jobs (Hz_NH23, "
            "Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, Hz_POZ1_NPh21_CF31) using "
            "adc2_batch2_final / hf_calcs geometries (gnorm 6.6e-5 to 7.6e-4); "
            "9 new Phase 2 SCS-CC2 jobs using delta_dft converged geometries "
            "(gnorm 5.6e-5 to 1.5e-4). All geometries within historical "
            "convergence baseline."
        ),
        "ci_method": "Clopper-Pearson exact two-sided 95%",
    }

    stats_path = EXT / "stats_n13.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"Wrote {stats_path}")
    print(f"  k/n = {k}/{n}, rate = {k/n:.4f}")
    print(f"  Clopper-Pearson 95% CI = [{lo95:.4f}, {hi95:.4f}]")


if __name__ == "__main__":
    main()
