#!/usr/bin/env python3
"""
Phase 3.5 — classify SCS-CC2-related claims by scope-of-overclaim.

Reads:
    audit/scscc2_scope_grep_hits.txt   (from Step 1)
    paper/main.tex
    results/canonical_metrics.json
    figures/caption_data/Fig4_crosscheck.json
    paper_overleaf/main.tex
    paper_overleaf/Table*.tex

Classifies each substantive claim with one of:
    OK_SCREENED_COHORT_SIGN_EVIDENCE
    OK_PROCESSED_TABLE_PENDING_RAW
    OVERCLAIMS_POPULATION_CI
    OVERCLAIMS_METHOD_VALIDATION
    OVERCLAIMS_QUANTITATIVE_RANKING
    BORDERLINE_NEEDS_LOW_EVIDENCE
    SIGN_SENSITIVE_CASE_NOT_FLAGGED
    RAW_PENDING_PHASE4

This script does not modify any file.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "audit" / "scscc2_claim_classification.tsv"


def has_rule_of_three_nearby(text):
    return bool(re.search(r"rule[\s-]of[\s-]three|3\s*/\s*13|0\.23",
                          text, re.I))


def has_pre_screened_disclaimer_nearby(text):
    return bool(re.search(
        r"ADC\(2\)-screened|pre-screened|pre-registered|"
        r"not.{0,40}i\.?i\.?d|screened cohort",
        text, re.I))


def has_method_family_caveat_nearby(text):
    return bool(re.search(
        r"method-family|ADC\(2\)/CC2 hierarchy|"
        r"not.{0,80}method-independent|"
        r"systematically more negative|"
        r"monotonic.{0,40}shift|"
        r"CCSD.{0,40}CC3.{0,40}NEVPT2|"
        r"triangulation",
        text, re.I))


def has_low_evidence_for_borderline(text):
    return bool(re.search(
        r"borderline.{0,200}low evidence|"
        r"low evidence.{0,200}borderline|"
        r"provisional.{0,200}Hz_POZ1|"
        r"Hz_POZ1.{0,200}provisional|"
        r"Hz_POZ1.{0,200}low|"
        r"Hz_POZ1.{0,300}pending.{0,40}(basis|TZVP|triangulation)|"
        r"Hz_POZ1.{0,300}TZVP|"
        r"promotion rests on the SCS-CC2 sign",
        text, re.I | re.S))


def has_sign_sensitive_callout(text):
    return bool(re.search(
        r"Hz_NPh21_Cz2.{0,200}(narrowest|10\s*meV|sign-?flip|"
        r"most likely sign|comparable to.{0,40}SCS-CC2 uncertainty)",
        text, re.I | re.S))


def classify_one(snippet, ctx_window):
    """Return list of (classification, reason) — may have multiple."""
    results = []
    s = snippet.lower()

    # OVERCLAIMS_POPULATION_CI
    if re.search(r"clopper.?pearson.{0,80}(95|ci|interval|0\.7529|1\.0000)",
                 s):
        if has_rule_of_three_nearby(ctx_window) and \
           has_pre_screened_disclaimer_nearby(ctx_window):
            # Used to contrast/reject — OK
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Clopper-Pearson is mentioned but explicitly disclaimed in "
                "favour of rule-of-three within ±400 chars."
            ))
        else:
            results.append((
                "OVERCLAIMS_POPULATION_CI",
                "Clopper-Pearson 95% CI for a pre-screened cohort without "
                "nearby disclaimer / rule-of-three substitution."
            ))
        return results

    if re.search(r"\[0\.7529.{0,5}1\.0000\]|paper_cited_CI", s):
        if has_rule_of_three_nearby(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "[0.7529, 1.0000] mentioned but rule-of-three present nearby."
            ))
        else:
            results.append((
                "OVERCLAIMS_POPULATION_CI",
                "[0.7529, 1.0000] CI cited as if a random-sample CI."
            ))
        return results

    # OVERCLAIMS_METHOD_VALIDATION
    if re.search(
        r"method.?independent.{0,80}(confirm|valid)|"
        r"validates? ADC\(2\)|"
        r"gold standard.{0,80}SCS|"
        r"SCS.{0,80}gold standard",
        s
    ):
        if has_method_family_caveat_nearby(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Method-independent or gold-standard language is used in a "
                "contrastive 'not X' construction with a method-family "
                "caveat nearby."
            ))
        else:
            results.append((
                "OVERCLAIMS_METHOD_VALIDATION",
                "Implies SCS-CC2 acts as a method-independent or "
                "gold-standard validator of ADC(2)."
            ))
        return results

    # OVERCLAIMS_QUANTITATIVE_RANKING
    if re.search(
        r"(ranking|ranks|rank-order|quantitative.{0,40}order)"
        r".{0,80}(SCS|cross.?check|13)",
        s
    ):
        if re.search(r"not.{0,80}(ranking|rank-order|quantitative)|"
                     r"scaffold-level.{0,40}rather than.{0,40}rank|"
                     r"sign.{0,40}scaffold.{0,40}rather than.{0,40}rank",
                     ctx_window, re.I | re.S):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Mentions ranking only to disclaim it (e.g. 'scaffold-level "
                "rather than fine ranking')."
            ))
        else:
            results.append((
                "OVERCLAIMS_QUANTITATIVE_RANKING",
                "Implies SCS-CC2 cross-check supports fine ranking."
            ))
        return results

    # BORDERLINE_NEEDS_LOW_EVIDENCE — only triggered if snippet mentions Hz_POZ1
    # with promotion language but no low-evidence/pending caveat in 400-char
    # window around it.
    if "hz_poz1_nph21_cf31" in s and re.search(
        r"promot|negative-gap|borderline.{0,80}negative|"
        r"165\.6|-9\.7", s
    ):
        if has_low_evidence_for_borderline(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Hz_POZ1_NPh21_CF31 promotion is paired with low-evidence / "
                "pending-triangulation / pending-TZVP language."
            ))
        else:
            results.append((
                "BORDERLINE_NEEDS_LOW_EVIDENCE",
                "Hz_POZ1_NPh21_CF31 is promoted without nearby low-evidence "
                "or pending-basis-set caveat."
            ))
        return results

    # SIGN_SENSITIVE_CASE_NOT_FLAGGED — only triggered if Hz_NPh21_Cz2 mentioned
    # with values but no narrowest-margin / sign-flip caveat in window.
    if "hz_nph21_cz2" in s:
        if has_sign_sensitive_callout(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Hz_NPh21_Cz2 is paired with narrowest-margin / sign-flip "
                "caveat."
            ))
        else:
            results.append((
                "SIGN_SENSITIVE_CASE_NOT_FLAGGED",
                "Hz_NPh21_Cz2 mentioned without narrowest-margin / "
                "sign-flip caveat."
            ))
        return results

    # generic 13/13 or sign-retention claim
    if re.search(r"13\s*/\s*13|all 13.{0,40}sign|sign.{0,40}all 13", s):
        if has_pre_screened_disclaimer_nearby(ctx_window) and \
           has_rule_of_three_nearby(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "13/13 claim with both screened-cohort disclaimer and "
                "rule-of-three present in window."
            ))
        elif has_pre_screened_disclaimer_nearby(ctx_window):
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "13/13 claim with screened-cohort disclaimer (rule-of-three "
                "perhaps further away)."
            ))
        elif "0 sign disagreement" in s or "0 disagreement" in s or \
             "0 within-screen" in s:
            results.append((
                "OK_SCREENED_COHORT_SIGN_EVIDENCE",
                "Phrased as 0 disagreement within screened cohort."
            ))
        else:
            results.append((
                "OVERCLAIMS_POPULATION_CI",
                "Bare 13/13 sign-retention claim without screened-cohort "
                "framing."
            ))
        return results

    # Stale n=4 wording that contradicts the n=13 narrative
    if re.search(r"four (selected|molecules|leads|cross-checks)|"
                 r"4-molecule|4 selected|four lead",
                 s):
        results.append((
            "STALE_N4_WORDING",
            "Caption / paragraph still uses n=4 language inconsistent with "
            "the rest of the paper saying n=13."
        ))
        return results

    # Anything else is informational only
    return results


def main():
    hits_file = ROOT / "audit" / "scscc2_scope_grep_hits.txt"
    if not hits_file.exists():
        print(f"FATAL: {hits_file} missing", file=sys.stderr); sys.exit(2)

    # We also want context windows. Re-read the source files once.
    file_cache = {}

    classifications = []
    for line in hits_file.read_text().splitlines():
        if not line.strip():
            continue
        # format: "<path>|<lineno>:<text>"
        try:
            path, rest = line.split("|", 1)
            lineno_str, claim_text = rest.split(":", 1)
            lineno = int(lineno_str)
        except ValueError:
            continue

        full_path = ROOT / path
        if not full_path.exists():
            continue
        if path not in file_cache:
            file_cache[path] = full_path.read_text().splitlines()
        lines = file_cache[path]
        # Window of ±5 lines for plain text / ±2 for JSON (big lines)
        win_radius = 5
        lo = max(0, lineno - 1 - win_radius)
        hi = min(len(lines), lineno - 1 + win_radius + 1)
        window = "\n".join(lines[lo:hi])

        # claim_text itself can be very long (a whole paragraph) — that's
        # already plenty of context for in-snippet checks
        ctx = window + "\n" + claim_text

        cls_list = classify_one(claim_text, ctx)
        if not cls_list:
            continue  # not a substantive scope claim

        for cls, reason in cls_list:
            classifications.append({
                "file": path,
                "line_or_json_path": str(lineno),
                "claim_text": claim_text[:300].replace("\t", " "),
                "classification": cls,
                "reason": reason,
                "recommended_action": (
                    "no action" if cls.startswith("OK_") else
                    "rewrite — see audit/scscc2_recommended_language.md"
                ),
            })

    # write tsv
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "file", "line_or_json_path", "claim_text", "classification",
            "reason", "recommended_action",
        ], delimiter="\t")
        w.writeheader()
        for r in classifications:
            w.writerow(r)
    print(f"wrote {OUT}  ({len(classifications)} substantive claims classified)")

    # summary tally
    tally = {}
    for r in classifications:
        tally[r["classification"]] = tally.get(r["classification"], 0) + 1
    print("\n--- classification tally ---")
    for k in sorted(tally):
        print(f"  {k:48s} {tally[k]}")


if __name__ == "__main__":
    import sys
    main()
