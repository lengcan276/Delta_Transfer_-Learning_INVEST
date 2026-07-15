#!/usr/bin/env python3
"""
Phase 3.6 — apply recommended SCS-CC2 scope rewrites in tmp workspace ONLY.

Reads recommended replacements from Phase 3.5 audit. Applies them to the
git-archive temporary copy at audit/_tmp_phase3_6_patch_workspace/.

Hard rule: DOES NOT touch the live repo.

For JSON metadata files (canonical_metrics.json, stats_n13.json) it does
NOT make in-place JSON edits — those require a generator refactor and
are documented as REQUIRES_GENERATOR_REFACTOR in the explanation files.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TMP = ROOT / "audit" / "_tmp_phase3_6_patch_workspace"

if not TMP.exists():
    sys.exit(f"FATAL: {TMP} missing (run `git archive` first)")


def replace_once(path, old, new, label):
    """Replace exactly one occurrence; report mismatch."""
    f = TMP / path
    if not f.exists():
        print(f"  SKIP [{label}]: {path} does not exist in tmp workspace")
        return False
    text = f.read_text()
    if old not in text:
        print(f"  WARN [{label}]: pattern not found in {path}")
        return False
    n = text.count(old)
    new_text = text.replace(old, new, 1)
    f.write_text(new_text)
    extra = f" (note: {n-1} more occurrences kept as-is)" if n > 1 else ""
    print(f"  OK   [{label}]: {path}{extra}")
    return True


# ── EDIT 1 + 2 (paper/main.tex + paper_overleaf/main.tex) ──────────────────

# 1A: Fig 0 caption ("four selected molecules only ...")
OLD_1A = ("Higher-level SCS-CC2 cross-checks are available for four "
          "selected molecules only and do not constitute multi-level "
          "validation of the full candidate set.")
NEW_1A = ("Higher-level SCS-CC2 cross-checks were applied to all 13 "
          "ADC(2)-screened negative-or-dark-negative-gap candidates; "
          "the 21 positive-gap and 1 borderline-near-zero molecules "
          "retain only the ADC(2) label.")

# 1B: Fig 3 caption ("Four molecules additionally have SCS-CC2 ...")
OLD_1B = ("Four molecules additionally have SCS-CC2 cross-checks, and "
          "one heptazine is promoted from the ADC(2) borderline window "
          "by the higher-level result stored in the validated decision "
          "table.")
NEW_1B = ("All 13 ADC(2)-screened INVEST candidates additionally have "
          "SCS-CC2 cross-checks (0 within-screen sign disagreement), "
          "and one heptazine is promoted from the ADC(2) borderline "
          "window by the higher-level result stored in the validated "
          "decision table.")

# 1C: Hz_NH23 paragraph ("on the four leads")
OLD_1C = ("The combination of decisive scaffold elimination, "
          "hierarchical SCS-CC2 sign confirmation on the four leads, "
          "and explicit retention of dark cases as separate "
          "classifications gives the present workflow its specific "
          "contribution to low-data INVEST discovery.")
NEW_1C = ("The combination of decisive scaffold elimination, "
          "per-candidate SCS-CC2 sign confirmation across all 13 "
          "ADC(2)-screened INVEST candidates, and explicit retention "
          "of dark cases as separate classifications gives the present "
          "workflow its specific contribution to low-data INVEST "
          "discovery.")

for path in ["paper/main.tex", "paper_overleaf/main.tex"]:
    print(f"\n== {path} ==")
    replace_once(path, OLD_1A, NEW_1A, f"{path} :: Fig 0 caption (n=4 stale)")
    replace_once(path, OLD_1B, NEW_1B, f"{path} :: Fig 3 caption (n=4 stale)")
    replace_once(path, OLD_1C, NEW_1C, f"{path} :: Hz_NH23 para (n=4 stale)")


# ── EDIT 3 (figures/caption_data/Fig0_workflow.json) ─────────────────────

OLD_3A = ('"SCS-CC2 verification is restricted to 4 selected lead '
          'candidates (Hz_DMAC1_NPh21_CF31, Hz_NPh22_SO2Ph1, '
          'Hz_POZ1_NPh21_CF31, Hz_NH23). It is NOT a population-scale '
          'method audit."')
NEW_3A = ('"SCS-CC2 verification covers all 13 ADC(2)-screened INVEST '
          'candidates (10 negative-gap + 3 dark negative-gap). It is a '
          'within-screened-cohort sign audit, not a population-scale '
          'method validation."')

OLD_3B = ('"SCS-CC2 cross-checks are n = 4 selected molecules, NOT all '
          '14 Table-1 candidates and NOT all 35 validated molecules."')
NEW_3B = ('"SCS-CC2 cross-checks cover all 13 ADC(2)-screened INVEST '
          'candidates (Table 1 negative-gap + dark negative-gap entries; '
          'the 21 positive-gap and 1 borderline-near-zero molecules '
          'retain only the ADC(2) label)."')

print("\n== figures/caption_data/Fig0_workflow.json ==")
replace_once("figures/caption_data/Fig0_workflow.json", OLD_3A, NEW_3A,
             "Fig0 caption_data line 44 (n=4 stale)")
replace_once("figures/caption_data/Fig0_workflow.json", OLD_3B, NEW_3B,
             "Fig0 caption_data line 47 (n=4 stale)")


# ── EDIT 4 (figures/caption_data/Fig4_crosscheck.json) ───────────────────

OLD_4A = ('"Panels showing the 4-molecule SCS-CC2 cross-check and panels '
          'showing the multi-method consistency benchmark must be '
          'visually separated and individually labeled with their '
          'respective n."')
NEW_4A = ('"Panels showing the n=13 SCS-CC2 cross-check and panels '
          'showing the legacy multi-method consistency benchmark must '
          'be visually separated and individually labeled with their '
          'respective n."')

OLD_4B = ('"On the 4-molecule candidate cross-check set, ADC(2)/def2-SVP '
          'and SCS-CC2/def2-SVP agree in sign for 4/4 molecules with '
          'absolute differences spanning 100\\u2013174 meV."')
NEW_4B = ('"On the 13-molecule ADC(2)-screened cohort, ADC(2)/def2-SVP '
          'and SCS-CC2/def2-SVP agree in sign for 13/13 molecules '
          '(0 within-screen disagreement; rule-of-three upper bound on '
          'disagreement rate \\u2248 3/13 = 0.23), with absolute '
          'cross-method differences spanning 10\\u2013194 meV (mean '
          '110 meV)."')

print("\n== figures/caption_data/Fig4_crosscheck.json ==")
replace_once("figures/caption_data/Fig4_crosscheck.json", OLD_4A, NEW_4A,
             "Fig4 caption_data (n=4 stale, panel-naming)")
replace_once("figures/caption_data/Fig4_crosscheck.json", OLD_4B, NEW_4B,
             "Fig4 caption_data (n=4 stale, sign-agreement text)")


# ── EDIT 5 (Table1_invest_candidates.tex × 2 copies) ─────────────────────

OLD_5 = ("four molecules additionally have SCS-CC2 cross-checks, and "
         "one of them is promoted from the ADC(2) borderline window by "
         "the higher-level result")
NEW_5 = ("all 13 ADC(2)-screened candidates additionally have SCS-CC2 "
         "cross-checks (0 within-screen sign disagreement; rule-of-three "
         "upper bound on disagreement rate $\\approx 0.23$), and one of "
         "them (Hz\\_POZ1\\_NPh21\\_CF31) is promoted from the ADC(2) "
         "borderline window by the higher-level result")

for path in ["results/Table1_invest_candidates.tex",
             "paper_overleaf/Table1_invest_candidates.tex"]:
    print(f"\n== {path} ==")
    replace_once(path, OLD_5, NEW_5, f"{path} :: caption (n=4 stale)")


# ── EDIT 6 (reviews/cover_letter.md) ──────────────────────────────────────

OLD_6 = ("SCS-CC2/def2-SVP is concentrated on four lead candidates, "
         "where it confirms sign agreement in 4/4 cases")
NEW_6 = ("SCS-CC2/def2-SVP is applied to all 13 ADC(2)-screened INVEST "
         "candidates (the pre-registered Table~1 shortlist), where it "
         "confirms sign agreement in all 13 cases (0 within-screen "
         "disagreement; rule-of-three one-sided 95% upper bound on "
         "disagreement rate ≈ 0.23)")

print("\n== reviews/cover_letter.md ==")
replace_once("reviews/cover_letter.md", OLD_6, NEW_6,
             "cover_letter (n=4 stale)")

# ── EDIT 7 (JSON metadata) ────────────────────────────────────────────────
# DELIBERATELY NOT APPLIED — those require generator refactor.
# See audit/phase3_6_changes_explained.md for why.

print("\n--- skipped (REQUIRES_GENERATOR_REFACTOR) ---")
print("  results/canonical_metrics.json scs_cc2_extended_n13.ci_method")
print("  results/canonical_metrics.json scs_cc2_extended_n13.paper_cited_signrate")
print("  results/scscc2_extension_n13/stats_n13.json ci_method")

print("\nDone applying recommended edits to tmp workspace.")
