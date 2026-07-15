#!/usr/bin/env python3
"""
build_cross_check_n13.py — assemble the n=13 SCS-CC2 cross-check table
and the screened-cohort sign-retention statistics.

This script writes two upstream artifacts only:
    <release_n13>/results/scscc2_extension_n13/cross_check_n13.csv
    <release_n13>/results/scscc2_extension_n13/stats_n13.json

The canonical upstream directory used by Phase 3.5/4/5 and the Patch B
single-writer canonical pipeline is `results/scscc2_extension_n13/`.

This script does NOT write `results/canonical_metrics.json`. The single
writer of `canonical_metrics.json` is `scripts/99_emit_canonical.py`,
which reads the two upstream files above and assembles the
`canonical_metrics.json["scs_cc2_extended_n13"]` block from them.

Paper-facing statistical interpretation: the 13 molecules are an
ADC(2)-pre-screened INVEST cohort, not an i.i.d. random sample, so the
paper-facing summary is the rule-of-three one-sided 95% upper bound on
within-screen sign-disagreement rate. A Clopper-Pearson exact CI is
also emitted for transparency, but is not the paper-facing interval.

Canonical repository: https://github.com/lengcan276/INVEST-n13
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "parsers"))
from parse_scscc2_dest import compute_dest  # noqa

# Raw ricc2_*.out inputs live in the upstream compute tree (read-only).
ROOT = Path("/home/nudt_cleng/2026/results")
EXT = ROOT / "scscc2_extension_n13"

# Outputs land inside the release_n13 repository, under the canonical
# upstream subdirectory used by Phase 3.5/4/5 and the Patch B chain.
LOCAL_REPO_RESULTS = (Path(__file__).resolve().parents[2]
                      / "results" / "scscc2_extension_n13")

REPOSITORY_URL = "https://github.com/lengcan276/INVEST-n13"

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

    # CSV — written to the release_n13 repository (single source of truth
    # consumed downstream by scripts/99_emit_canonical.py).
    LOCAL_REPO_RESULTS.mkdir(parents=True, exist_ok=True)
    csv_path = LOCAL_REPO_RESULTS / "cross_check_n13.csv"
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
    n_disagree = n - k
    lo95, hi95 = clopper_pearson(k, n, 0.05)
    lo90, hi90 = clopper_pearson(k, n, 0.10)
    # Rule of three: one-sided 95% upper bound on disagreement rate when
    # zero disagreements are observed in n trials is ~3/n.
    rule_of_three_upper_bound = round(3.0 / n, 4) if n_disagree == 0 else None

    abs_diffs = [r["abs_ddEST_meV"] for r in rows]
    abs_diffs.sort()
    mean_abs = sum(abs_diffs) / n
    median_abs = abs_diffs[n // 2]

    stats = {
        "n_total": n,
        "n_sign_retain": k,
        "sign_retain_rate": k / n,
        # Paper-facing interpretation: screened-cohort rule-of-three.
        "ci_method": (
            "rule of three (one-sided 95% upper bound on within-screen "
            "sign-disagreement rate; the 13 molecules are an "
            "ADC(2)-pre-screened cohort, not an i.i.d. random sample)"
        ),
        "rule_of_three_upper_bound_disagreement_rate": rule_of_three_upper_bound,
        # Transparency-only fields: a Clopper-Pearson CI is reported as
        # an alternative numerical summary, but is NOT the paper-facing
        # statistical interpretation for this pre-screened cohort.
        "clopper_pearson_95_CI": [round(lo95, 4), round(hi95, 4)],
        "clopper_pearson_90_CI": [round(lo90, 4), round(hi90, 4)],
        "clopper_pearson_note": (
            "transparency-only; not the paper-facing interpretation for "
            "this ADC(2)-pre-screened cohort"
        ),
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
        "repository_canonical": REPOSITORY_URL,
    }

    stats_path = LOCAL_REPO_RESULTS / "stats_n13.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"Wrote {stats_path}")
    print(f"  k/n = {k}/{n}, rate = {k/n:.4f}")
    print(f"  rule-of-three one-sided 95% upper bound on disagreement rate "
          f"= {rule_of_three_upper_bound}")
    print(f"  (transparency-only) Clopper-Pearson 95% CI on retention rate "
          f"= [{lo95:.4f}, {hi95:.4f}]")


if __name__ == "__main__":
    main()
