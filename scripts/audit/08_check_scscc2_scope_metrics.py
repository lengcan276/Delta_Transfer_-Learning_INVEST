#!/usr/bin/env python3
"""
Phase 3.5 — verify SCS-CC2 scope metrics from processed tables only.

Reads (in priority order):
    results/scscc2_extension_n13/cross_check_n13.csv  (primary)
    results/scscc2_extension_n13/stats_n13.json       (cross-check)
    results/method_consistency_table.csv              (fallback)
    results/scscc2_batch2_summary.csv                 (fallback)
    results/validated_candidates_master.csv           (fallback)

Computes (all marked PROCESSED_TABLE_LEVEL, not RAW_VERIFIED):
    N checked by SCS-CC2
    N sign disagreements
    whether all SCS-CC2 more negative than ADC(2)
    min/max/mean cross-method shift
    Hz_POZ1_NPh21_CF31 values
    Hz_NPh21_Cz2 values

Outputs:
    audit/scscc2_scope_metrics.tsv
    audit/scscc2_scope_metrics.md
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PRIMARY_CSV = ROOT / "results" / "scscc2_extension_n13" / "cross_check_n13.csv"
PRIMARY_JSON = ROOT / "results" / "scscc2_extension_n13" / "stats_n13.json"

OUT_TSV = ROOT / "audit" / "scscc2_scope_metrics.tsv"
OUT_MD = ROOT / "audit" / "scscc2_scope_metrics.md"


def main():
    if not PRIMARY_CSV.exists():
        print(f"FATAL: {PRIMARY_CSV} missing", file=sys.stderr)
        sys.exit(2)

    rows = list(csv.DictReader(PRIMARY_CSV.open()))
    print(f"loaded {PRIMARY_CSV.name}: {len(rows)} rows")

    # Optional cross-check JSON
    stats_json = None
    if PRIMARY_JSON.exists():
        stats_json = json.loads(PRIMARY_JSON.read_text())
        print(f"loaded {PRIMARY_JSON.name}: keys = "
              f"{sorted(stats_json.keys())}")

    # ---- compute metrics ----
    n_total = len(rows)
    n_sign_disagree = sum(1 for r in rows if r["sign_agree"].lower() != "true")
    n_sign_agree = n_total - n_sign_disagree

    # cross-method shift in meV (SCS-CC2 ΔEST minus ADC2 ΔEST). Since both
    # are negative for INVEST, "more negative SCS-CC2" → diff < 0.
    shifts = []  # absolute meV difference
    signed_shifts = []  # signed (negative if SCS-CC2 deeper)
    all_scscc2_more_negative = True
    for r in rows:
        adc = float(r["ADC2_dEST_meV"])
        scs = float(r["SCSCC2_dEST_meV"])
        diff = scs - adc  # negative if SCS-CC2 deeper
        signed_shifts.append(diff)
        shifts.append(abs(diff))
        if scs >= adc:  # SCS-CC2 NOT more negative
            all_scscc2_more_negative = False

    shift_min = min(shifts)
    shift_max = max(shifts)
    shift_mean = sum(shifts) / len(shifts)

    # specific molecules
    by_mol = {r["name"] if "name" in r else r.get("mol_id", ""): r
              for r in rows}
    # CSV uses 'name' (per build_cross_check_n13.py header)
    by_mol = {r.get("name", r.get("mol_id", "")): r for r in rows}
    poz1 = by_mol.get("Hz_POZ1_NPh21_CF31", {})
    nph21_cz2 = by_mol.get("Hz_NPh21_Cz2", {})

    rule_of_three = 3.0 / n_total

    # ---- TSV ----
    OUT_TSV.write_text(
        "metric\tvalue\tprovenance\n"
        f"n_total_checked\t{n_total}\tPROCESSED_TABLE_LEVEL\n"
        f"n_sign_agree\t{n_sign_agree}\tPROCESSED_TABLE_LEVEL\n"
        f"n_sign_disagree\t{n_sign_disagree}\tPROCESSED_TABLE_LEVEL\n"
        f"all_scscc2_more_negative_than_adc2\t{all_scscc2_more_negative}\tPROCESSED_TABLE_LEVEL\n"
        f"shift_abs_min_meV\t{shift_min:.2f}\tPROCESSED_TABLE_LEVEL\n"
        f"shift_abs_max_meV\t{shift_max:.2f}\tPROCESSED_TABLE_LEVEL\n"
        f"shift_abs_mean_meV\t{shift_mean:.2f}\tPROCESSED_TABLE_LEVEL\n"
        f"rule_of_three_3_over_n\t{rule_of_three:.4f}\tPROCESSED_TABLE_LEVEL\n"
        f"Hz_POZ1_NPh21_CF31_ADC2_meV\t{poz1.get('ADC2_dEST_meV','MISSING')}\tPROCESSED_TABLE_LEVEL\n"
        f"Hz_POZ1_NPh21_CF31_SCSCC2_meV\t{poz1.get('SCSCC2_dEST_meV','MISSING')}\tPROCESSED_TABLE_LEVEL\n"
        f"Hz_NPh21_Cz2_ADC2_meV\t{nph21_cz2.get('ADC2_dEST_meV','MISSING')}\tPROCESSED_TABLE_LEVEL\n"
        f"Hz_NPh21_Cz2_SCSCC2_meV\t{nph21_cz2.get('SCSCC2_dEST_meV','MISSING')}\tPROCESSED_TABLE_LEVEL\n"
        f"Hz_NPh21_Cz2_abs_diff_meV\t{abs(float(nph21_cz2.get('ADC2_dEST_meV',0))-float(nph21_cz2.get('SCSCC2_dEST_meV',0))):.2f}\tPROCESSED_TABLE_LEVEL\n"
    )
    print(f"wrote {OUT_TSV}")

    # ---- MD ----
    md = [
        "# Phase 3.5 Step 2 — SCS-CC2 scope metrics (processed-table only)",
        "",
        f"Source CSV: `{PRIMARY_CSV.relative_to(ROOT)}`",
        f"Source JSON (cross-check): `{PRIMARY_JSON.relative_to(ROOT)}`",
        "",
        "All values below are **PROCESSED_TABLE_LEVEL** — they come from",
        "the project's own SCS-CC2 cross-check CSV, not from independent",
        "re-parsing of raw ricc2 outputs. Raw-output provenance is",
        "Phase 4's responsibility.",
        "",
        "## Cohort summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| N total checked by SCS-CC2 | **{n_total}** |",
        f"| N sign agreement | **{n_sign_agree}** |",
        f"| N sign disagreement | **{n_sign_disagree}** |",
        f"| All SCS-CC2 ΔE_ST more negative than ADC(2)? | **{all_scscc2_more_negative}** |",
        f"| Cross-method shift, abs min | {shift_min:.2f} meV |",
        f"| Cross-method shift, abs max | {shift_max:.2f} meV |",
        f"| Cross-method shift, abs mean | {shift_mean:.2f} meV |",
        f"| Rule-of-three upper bound (3/N) | {rule_of_three:.4f} = ~{rule_of_three*100:.0f}% |",
        "",
        "## Cross-check against stats_n13.json",
        "",
    ]
    if stats_json:
        md.extend([
            f"- `stats_n13.json.n_total` = {stats_json.get('n_total')}  →  audit re-computes {n_total}  →  {'MATCH' if stats_json.get('n_total')==n_total else 'MISMATCH'}",
            f"- `stats_n13.json.n_sign_retain` = {stats_json.get('n_sign_retain')}  →  audit re-computes {n_sign_agree}  →  {'MATCH' if stats_json.get('n_sign_retain')==n_sign_agree else 'MISMATCH'}",
            f"- `stats_n13.json.abs_ddEST_meV_summary.min` = {stats_json.get('abs_ddEST_meV_summary',{}).get('min')}  →  audit re-computes {shift_min:.2f}",
            f"- `stats_n13.json.abs_ddEST_meV_summary.max` = {stats_json.get('abs_ddEST_meV_summary',{}).get('max')}  →  audit re-computes {shift_max:.2f}",
            f"- `stats_n13.json.abs_ddEST_meV_summary.mean` = {stats_json.get('abs_ddEST_meV_summary',{}).get('mean')}  →  audit re-computes {shift_mean:.2f}",
        ])
    else:
        md.append("- stats_n13.json MISSING")

    md.extend([
        "",
        "## Two molecules called out by Phase 3.5 protocol",
        "",
        "### Hz_POZ1_NPh21_CF31 (borderline-promoted)",
        f"- ADC(2) ΔE_ST = **{poz1.get('ADC2_dEST_meV','MISSING')}** meV",
        f"- SCS-CC2 ΔE_ST = **{poz1.get('SCSCC2_dEST_meV','MISSING')}** meV",
        f"- |Δ| (cross-method shift) = "
        f"{abs(float(poz1.get('ADC2_dEST_meV',0))-float(poz1.get('SCSCC2_dEST_meV',0))):.2f} meV",
        "- ADC(2)/def2-SVP value lies inside the ±30 meV borderline window;",
        "  classification flips from ADC(2) borderline to SCS-CC2 negative-gap.",
        "  Should be flagged low-evidence pending basis-set or",
        "  method-family triangulation.",
        "",
        "### Hz_NPh21_Cz2 (narrowest cross-method margin)",
        f"- ADC(2) ΔE_ST = **{nph21_cz2.get('ADC2_dEST_meV','MISSING')}** meV",
        f"- SCS-CC2 ΔE_ST = **{nph21_cz2.get('SCSCC2_dEST_meV','MISSING')}** meV",
        f"- |Δ| (cross-method shift) = "
        f"**{abs(float(nph21_cz2.get('ADC2_dEST_meV',0))-float(nph21_cz2.get('SCSCC2_dEST_meV',0))):.2f}** meV",
        "- This is the smallest cross-method margin in the n=13 cohort.",
        "  Should be flagged as the most likely sign-flip candidate",
        "  under further theoretical refinement (different basis, different",
        "  method family).",
        "",
        "## Provenance disclaimer",
        "",
        "All numbers above were computed by re-applying simple arithmetic",
        "to `results/scscc2_extension_n13/cross_check_n13.csv`. This CSV",
        "was produced by `scripts/scscc2_extension/build_cross_check_n13.py`",
        "which in turn parses `ricc2_scscc2_*.out` files via",
        "`scripts/scscc2_extension/parsers/parse_scscc2_dest.py`. The",
        "authenticity of the underlying ricc2 outputs — i.e. whether they",
        "are real Turbomole calculations rather than fabricated text —",
        "is NOT verified at the processed-table level. Phase 4 covers that.",
    ])
    OUT_MD.write_text("\n".join(md))
    print(f"wrote {OUT_MD}")


if __name__ == "__main__":
    main()
