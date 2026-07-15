#!/usr/bin/env python3
"""audit_numbers.py

Audit every number in paper/main.tex (and the .tex tables it includes)
against the canonical numerical sources:

    - results/canonical_metrics.json
    - figures/caption_data/*.json
    - results/Table1_invest_candidates.tex
    - results/Table2_method_summary.tex

Also runs seven hard-coded "Major" checks for known scope-confusion
patterns (analysis-set mixing, selection-bias Fisher claims, etc.)
and writes a structured report to:

    paper/audit_reports/consistency_audit.md

This script DOES NOT modify paper/main.tex.

Run from project root:
    python3 scripts/audit_numbers.py
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
CANONICAL = ROOT / "results" / "canonical_metrics.json"
CAPTIONS_DIR = ROOT / "figures" / "caption_data"
TABLE1 = ROOT / "results" / "Table1_invest_candidates.tex"
TABLE2 = ROOT / "results" / "Table2_method_summary.tex"
REPORT = ROOT / "paper" / "audit_reports" / "consistency_audit.md"

# ── number extraction ────────────────────────────────────────────────────

# Strip these LaTeX constructs before number scanning so their internals
# (citation labels, ref labels, year/volume in bibliography, hyperlinks)
# do not pollute the audit.
STRIP_PATTERNS = [
    # comments — require the % not be preceded by a backslash so that
    # LaTeX-escaped percent signs (\%) are NOT clobbered.
    re.compile(r"(?<!\\)%[^\n]*"),
    re.compile(r"\\cite[a-zA-Z*]*\{[^}]*\}"),    # \cite{Foo,Bar}
    re.compile(r"\\ref\{[^}]*\}"),
    re.compile(r"\\autoref\{[^}]*\}"),
    re.compile(r"\\eqref\{[^}]*\}"),
    re.compile(r"\\label\{[^}]*\}"),
    re.compile(r"\\bibitem\{[^}]*\}"),
    re.compile(r"\\input\{[^}]*\}"),
    re.compile(r"\\IfFileExists\{[^}]*\}\{[^}]*\}\{[^}]*\}"),
    re.compile(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}"),
    re.compile(r"\\url\{[^}]*\}"),
    re.compile(r"\\href\{[^}]*\}\{[^}]*\}"),
    # Strip the entire bibliography body — bibliographic numbers
    # (years, volumes, pages) must not enter the audit.
    re.compile(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
               re.DOTALL),
]

# Strip texttt arguments (file/path identifiers may contain digits).
STRIP_PATTERNS.append(re.compile(r"\\texttt\{[^}]*\}"))

# Strip version-like labels (Phase 2.2, Phase~2.4, Round 1, etc.) — these
# are non-quantitative campaign identifiers, not numerical claims.
STRIP_PATTERNS.append(re.compile(r"\bPhase[~ ]\d+(?:\.\d+)?"))
STRIP_PATTERNS.append(re.compile(r"\bRound[~ ]\d+(?:\.\d+)?"))

# Number patterns
NUM_PATTERNS = [
    # \SI{value}{unit} and \SIrange{a}{b}{unit}
    ("si",      re.compile(r"\\SI\{(-?\d+(?:\.\d+)?)\}\{([^}]*)\}")),
    ("sirange", re.compile(r"\\SIrange\{(-?\d+(?:\.\d+)?)\}"
                           r"\{(-?\d+(?:\.\d+)?)\}\{([^}]*)\}")),
    # p = 0.031, p=0.031, p$ = $0.031, p value of 0.015
    ("pvalue",  re.compile(r"\$?\s*p\s*\$?\s*[=≤<]+\s*"
                           r"(\d+(?:\.\d+)?)", re.IGNORECASE)),
    ("pvalue_phrase", re.compile(
        r"(?:Fisher\s+exact\s+)?\$?p\$?\s*value(?:\s+of)?\s+"
        r"(\d+(?:\.\d+)?)", re.IGNORECASE)),
    # percentages: 35.7\%, 100\%
    ("percent", re.compile(r"(-?\d+(?:\.\d+)?)\s*\\?%")),
    # n = 33, N=14, with 19 calibration molecules etc.
    ("nequals", re.compile(r"\b[nN]\s*=\s*(\d+)\b")),
    # Plain integers and decimals (last to catch leftover numbers)
    ("number",  re.compile(r"(?<![A-Za-z\\\d.])(-?\d+(?:\.\d+)?)"
                           r"(?![A-Za-z.\d])")),
]


def strip_irrelevant(tex: str) -> str:
    out = tex
    for p in STRIP_PATTERNS:
        out = p.sub(" ", out)
    return out


def extract_numbers_from_tex(tex_path: Path) -> list[dict]:
    """Return one record per extracted number with source location."""
    raw = tex_path.read_text()
    cleaned = strip_irrelevant(raw)
    rows: list[dict] = []
    seen_spans: set[tuple[int, int]] = set()
    for kind, pat in NUM_PATTERNS:
        for m in pat.finditer(cleaned):
            span = (m.start(), m.end())
            if any(s[0] <= span[0] < s[1] for s in seen_spans):
                # already covered by an earlier (more specific) pattern
                continue
            seen_spans.add(span)
            ctx_lo = max(0, m.start() - 60)
            ctx_hi = min(len(cleaned), m.end() + 60)
            ctx = re.sub(r"\s+", " ", cleaned[ctx_lo:ctx_hi]).strip()

            if kind == "sirange":
                a, b, unit = m.group(1), m.group(2), m.group(3)
                rows.append({"value": float(a), "unit": unit,
                             "kind": kind, "context": ctx,
                             "source": str(tex_path.relative_to(ROOT))})
                rows.append({"value": float(b), "unit": unit,
                             "kind": kind, "context": ctx,
                             "source": str(tex_path.relative_to(ROOT))})
            elif kind == "si":
                rows.append({"value": float(m.group(1)),
                             "unit": m.group(2),
                             "kind": kind, "context": ctx,
                             "source": str(tex_path.relative_to(ROOT))})
            else:
                try:
                    val = float(m.group(1))
                except (ValueError, IndexError):
                    continue
                rows.append({"value": val, "unit": kind,
                             "kind": kind, "context": ctx,
                             "source": str(tex_path.relative_to(ROOT))})
    return rows


# ── canonical-source flattening ──────────────────────────────────────────

def _walk_numbers(obj, path: str, sink: dict[float, list[str]]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_numbers(v, f"{path}.{k}", sink)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_numbers(v, f"{path}[{i}]", sink)
    elif isinstance(obj, bool):
        return
    elif isinstance(obj, (int, float)):
        try:
            f = float(obj)
        except (TypeError, ValueError):
            return
        sink.setdefault(f, []).append(path)
    elif isinstance(obj, str):
        # Pull out any numeric substrings so e.g. "Hz 13/27" becomes
        # {13.0, 27.0}.
        for tok in re.findall(r"-?\d+(?:\.\d+)?", obj):
            try:
                f = float(tok)
                sink.setdefault(f, []).append(f"{path} (str:{obj[:40]!r})")
            except ValueError:
                continue


def flatten_canonical_sources() -> dict[float, list[str]]:
    sink: dict[float, list[str]] = {}
    _walk_numbers(json.loads(CANONICAL.read_text()),
                  "canonical_metrics.json", sink)
    for cap in sorted(CAPTIONS_DIR.glob("*.json")):
        _walk_numbers(json.loads(cap.read_text()),
                      f"caption_data/{cap.name}", sink)
    return sink


def extract_table_numbers() -> dict[float, list[str]]:
    """Numbers in the .tex tables become an additional source."""
    sink: dict[float, list[str]] = {}
    for tbl in (TABLE1, TABLE2):
        if not tbl.exists():
            continue
        cleaned = strip_irrelevant(tbl.read_text())
        for tok in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?",
                              cleaned):
            try:
                f = float(tok)
            except ValueError:
                continue
            sink.setdefault(f, []).append(str(tbl.relative_to(ROOT)))
    return sink


# ── resolution ───────────────────────────────────────────────────────────

# Bare integers that are not project numbers — ignore unresolved misses
# for these (they show up in scope explanations like "the 7 of 15 vs 6 of 14").
TRIVIAL_VALUES = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
                  10.0, 11.0, 12.0, 13.0}


def _matches(value: float, sources: dict[float, list[str]],
             tol_abs: float = 0.0, tol_rel: float = 0.005) -> list[str]:
    """Return list of source paths whose value is close to `value`."""
    hits = []
    for src_val, paths in sources.items():
        if src_val == value:
            hits.extend(paths)
            continue
        diff = abs(src_val - value)
        if value != 0 and diff / max(abs(value), 1e-9) <= tol_rel:
            hits.extend(paths)
        elif tol_abs > 0 and diff <= tol_abs:
            hits.extend(paths)
    # Dedupe while preserving order
    out = []
    seen = set()
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


def resolve(tex_numbers: list[dict],
            sources_canonical: dict[float, list[str]],
            sources_tables: dict[float, list[str]]) -> list[dict]:
    out = []
    for rec in tex_numbers:
        v = rec["value"]
        # value-specific tolerance — meV / coverage / p-value need tight
        if rec["kind"] in {"pvalue", "pvalue_phrase"}:
            tol_abs, tol_rel = 0.0005, 0.05
        elif rec["kind"] == "percent":
            tol_abs, tol_rel = 0.0, 0.01
        elif rec["kind"] in {"si", "sirange"}:
            tol_abs, tol_rel = 0.0, 0.01
        elif rec["kind"] == "nequals":
            tol_abs, tol_rel = 0.0, 0.0
        else:
            tol_abs, tol_rel = 0.0, 0.005
        # Compare against eV-form for SI{...}{meV} too: 52.1 meV ~= 0.0521 eV
        candidates = [v]
        if rec.get("unit") in {"meV"}:
            candidates.append(round(v / 1000.0, 6))
        elif rec.get("unit") in {"eV"}:
            candidates.append(round(v * 1000.0, 6))
        elif rec["kind"] == "percent":
            candidates.append(round(v / 100.0, 6))

        canonical_hits: list[str] = []
        table_hits: list[str] = []
        for cand in candidates:
            canonical_hits += _matches(cand, sources_canonical,
                                       tol_abs, tol_rel)
            table_hits += _matches(cand, sources_tables,
                                   tol_abs, tol_rel)
        rec_out = dict(rec)
        rec_out["canonical_hits"] = canonical_hits[:3]
        rec_out["table_hits"] = table_hits[:3]
        rec_out["resolved"] = bool(canonical_hits or table_hits)
        rec_out["trivial"] = (v in TRIVIAL_VALUES) and rec["kind"] in {
            "number", "nequals"
        }
        out.append(rec_out)
    return out


# ── Major checks ─────────────────────────────────────────────────────────

MAJOR_CHECKS: list[dict] = [
    {
        "id": "M1_7_15_vs_6_14_unexplained",
        "title": "7/15 and 6/14 must include an analysis-set explanation.",
        "trigger": (r"7\b[^\n]{0,80}\b15\b|\b15\b[^\n]{0,80}\b7\b",
                    r"6\b[^\n]{0,80}\b14\b|\b14\b[^\n]{0,80}\b6\b"),
        "mitigation": (r"deployment[^\n]{0,200}(Fisher|conformal|subset|"
                       r"denominator|panel)|"
                       r"(Fisher|conformal|subset)[^\n]{0,200}deployment|"
                       r"selected|excluded by design|Hz_NH23"),
        "rationale": (
            "When 7 of 15 (deployment yield) and 6 of 14 (Fisher / conformal "
            "subset) both appear, the text must explain that 14 excludes "
            "Hz_NH23 by design and the two denominators answer different "
            "questions. Otherwise readers will treat them as contradictory."
        ),
    },
    {
        "id": "M2_15_vs_14_mixed_scope",
        "title": "15-deployment and 14-conformal/Fisher subset are mixed "
                 "without a denominator rule.",
        "trigger": (r"\b15\b[^\n]{0,160}\b14\b|\b14\b[^\n]{0,160}\b15\b",),
        "mitigation": (r"(must not be used as the deployment denominator|"
                       r"different denominators|panel\s*\(?b\)?|"
                       r"excluded by design|Hz_NH23 (excluded|removed))"),
        "rationale": (
            "Sentences that put 15 and 14 close together must explicitly "
            "say which is the deployment denominator and which is the "
            "Fisher / conformal subset, otherwise the scope is ambiguous."
        ),
    },
    {
        "id": "M3_33_35_14_mixed_scope",
        "title": "33-target / 35-validated / 14-deployment mixed without "
                 "scope labels.",
        "trigger": (r"\b33\b[^\n]{0,200}\b35\b[^\n]{0,200}\b14\b|"
                    r"\b35\b[^\n]{0,200}\b33\b[^\n]{0,200}\b14\b|"
                    r"\b33\b[^\n]{0,200}\b14\b[^\n]{0,200}\b35\b",),
        "mitigation": (r"(post-round|target set|validated|deployment|"
                       r"OOD|conformal|Fisher|excluded by design|"
                       r"final validation)"),
        "rationale": (
            "33 (post-round target set), 35 (final validation), and 14 "
            "(OOD deployment subset) must each be labelled with their "
            "scope when they appear together; otherwise the reader cannot "
            "tell which n applies to which metric."
        ),
    },
    {
        "id": "M4_scscc2_overgeneralised",
        "title": "SCS-CC2 cross-check framed as covering positive-gap or full "
                 "35-molecule cohort.",
        "trigger": (r"SCS-?CC2[^\n]{0,200}(all\s+35|every\s+validated|"
                    r"comprehensive[^\n]{0,40}35|all\s+positive-gap)",),
        "mitigation": (r"(13\s+INVEST|thirteen\s+INVEST|negative-gap|"
                       r"shortlist|21\s+positive-gap[^\n]{0,40}only)"),
        "rationale": (
            "SCS-CC2/def2-SVP was performed on all 13 INVEST (negative + "
            "dark negative) candidates, not on the 21 positive-gap or 1 "
            "borderline candidates. Wording that frames SCS-CC2 as covering "
            "the full 35-molecule validated cohort must be qualified."
        ),
    },
    {
        "id": "M5_52_meV_threshold_no_caveat",
        "title": "Post-round MAE of 52.1 meV exceeds the 30 meV "
                 "borderline threshold without a caveat.",
        "trigger": (r"52\.1\s*\\?(?:SI\{)?meV?\}?",),
        "mitigation": (r"(exceed|above|larger than|borderline|"
                       r"not for confident|scaffold-level|"
                       r"coarse|prioritization|near-threshold)"),
        "rationale": (
            "The post-round LOO-CV MAE of 52.1 meV is larger than the "
            "30 meV borderline window used to classify near-zero gaps. "
            "Every mention of 52.1 meV must be accompanied by a caveat "
            "that the model is unsuitable for confident near-threshold "
            "candidate-level classification."
        ),
    },
    {
        "id": "M6_fisher_random_significance",
        "title": "Fisher p-values written as random-sampling significance.",
        "trigger": (r"Fisher\s+exact[^\n]{0,200}\bp\b[^\n]{0,40}"
                    r"\d+\.\d+|"
                    r"\bp\s*[=≤]\s*0\.0[13][15]\b",),
        "mitigation": (r"(descriptive|selected cohort|policy-selected|"
                       r"intentionally|ascertainment|subset-level|"
                       r"not a population|"
                       r"within the present (RI-)?ADC\(2\))"),
        "rationale": (
            "Fisher exact p-values arise from an actively selected, "
            "scaffold-imbalanced cohort. They must be flagged as "
            "descriptive subset statistics, not as random-sampling "
            "significance."
        ),
    },
    {
        "id": "M7_adc2_candidates_called_fully_verified",
        "title": "ADC(2)/def2-SVP candidates written as fully verified "
                 "molecules.",
        "trigger": (r"(fully|definitively|conclusively|unambiguously|"
                    r"experimentally)\s+(verified|validated|confirmed)"
                    r"[^\n]{0,200}(candidates?|molecules?|INVEST)",
                    r"(verified|validated|confirmed)\s+at[^\n]{0,80}"
                    r"(higher|gold standard|CCSD)"),
        "mitigation": (r"(scaffold-level|cross-checked|cross-check|"
                       r"within the present (RI-)?ADC\(2\)|"
                       r"level of theory|method dependence|"
                       r"basis-set dependence)"),
        "rationale": (
            "ADC(2)/def2-SVP is the highest level used here for most "
            "candidates; only 4 received SCS-CC2 cross-checks. Wording "
            "that calls the candidates fully verified or that uses "
            "gold-standard language must be flagged."
        ),
    },
]


def run_major_checks(text: str) -> list[dict]:
    findings = []
    cleaned = strip_irrelevant(text)
    for check in MAJOR_CHECKS:
        triggered: list[str] = []
        for pat in check["trigger"]:
            for m in re.finditer(pat, cleaned, flags=re.IGNORECASE):
                ctx_lo = max(0, m.start() - 80)
                ctx_hi = min(len(cleaned), m.end() + 80)
                ctx = re.sub(r"\s+", " ", cleaned[ctx_lo:ctx_hi]).strip()
                # mitigation check on the surrounding window
                mit_window = cleaned[max(0, m.start() - 400):
                                     min(len(cleaned), m.end() + 400)]
                if not re.search(check["mitigation"], mit_window,
                                 flags=re.IGNORECASE):
                    triggered.append(ctx)
        findings.append({
            "id": check["id"],
            "title": check["title"],
            "rationale": check["rationale"],
            "n_unmitigated_hits": len(triggered),
            "examples": triggered[:5],
        })
    return findings


# ── reporting ────────────────────────────────────────────────────────────

def render_report(resolved: list[dict],
                  major: list[dict],
                  n_canonical_floats: int,
                  n_caption_files: int,
                  n_table_floats: int) -> str:
    n_total = len(resolved)
    nontrivial = [r for r in resolved if not r["trivial"]]
    n_resolved = sum(1 for r in nontrivial if r["resolved"])
    n_unresolved = sum(1 for r in nontrivial if not r["resolved"])
    n_trivial = sum(1 for r in resolved if r["trivial"])

    by_unresolved: dict[str, list[dict]] = defaultdict(list)
    for r in nontrivial:
        if not r["resolved"]:
            by_unresolved[r["source"]].append(r)

    L: list[str] = []
    a = L.append
    a("# Manuscript number-consistency audit")
    a("")
    a("Generated by `scripts/audit_numbers.py`. Audit artefact only — "
      "`paper/main.tex` is not modified by this script.")
    a("")

    # ── summary
    a("## Summary")
    a("")
    a(f"- Numbers extracted from `paper/main.tex` and included tables: "
      f"**{n_total}** "
      f"(non-trivial: {len(nontrivial)}; trivial small ints: {n_trivial}).")
    a(f"- Numbers traceable to a canonical source: **{n_resolved}** "
      f"({n_resolved / max(len(nontrivial),1) * 100:.0f}% of non-trivial).")
    a(f"- Unresolved (no matching value in any canonical source): "
      f"**{n_unresolved}**.")
    a(f"- Canonical pool sampled: "
      f"{n_canonical_floats} numeric leaves from canonical_metrics.json + "
      f"{n_caption_files} caption JSONs; {n_table_floats} numeric tokens "
      "from Table1/Table2.")
    n_major_hit = sum(1 for f in major if f["n_unmitigated_hits"] > 0)
    a(f"- Major issue checks triggered without a nearby mitigation: "
      f"**{n_major_hit} / {len(major)}**.")
    a("")

    # ── major findings
    a("## Major findings")
    a("")
    a("Each check looks for a pattern that should be accompanied by a "
      "mitigating phrase within ±400 characters; if the mitigation is "
      "absent, the hit is flagged here.")
    a("")
    for f in major:
        marker = "❌" if f["n_unmitigated_hits"] > 0 else "✅"
        a(f"### {marker} {f['id']} — {f['title']}")
        a("")
        a(f"**Rule:** {f['rationale']}")
        a("")
        a(f"**Unmitigated trigger hits:** {f['n_unmitigated_hits']}")
        a("")
        if f["examples"]:
            a("Examples (first 5):")
            for ex in f["examples"]:
                a(f"- `…{ex}…`")
        else:
            a("No unmitigated occurrences detected. The text already "
              "carries the expected qualifying language nearby.")
        a("")

    # ── unresolved numbers
    a("## Unresolved numbers")
    a("")
    if not n_unresolved:
        a("No unresolved non-trivial numbers were found.")
    else:
        a("Each entry is a number that appears in the manuscript / table "
          "files but does NOT have a matching value in canonical sources "
          "(within tolerance). Review and either trace back to a result "
          "file, add it to `results/canonical_metrics.json`, or correct "
          "the manuscript.")
        a("")
        for src, recs in sorted(by_unresolved.items()):
            a(f"### `{src}` — {len(recs)} unresolved")
            a("")
            for r in recs:
                unit = f" {r['unit']}" if r["kind"] in {"si", "sirange"} \
                    else ""
                a(f"- `{r['value']}{unit}` "
                  f"(kind={r['kind']}) — context: `…{r['context']}…`")
            a("")

    # ── resolved sample (top 30)
    a("## Resolved numbers (sample)")
    a("")
    a("First 30 traceable numbers, with the canonical source that "
      "matched. Use this as a sanity check that the matcher has not "
      "drifted.")
    a("")
    sampled = [r for r in nontrivial if r["resolved"]][:30]
    for r in sampled:
        unit = f" {r['unit']}" if r["kind"] in {"si", "sirange"} else ""
        hits = (r["canonical_hits"] + r["table_hits"])[:2]
        a(f"- `{r['value']}{unit}` (kind={r['kind']}) → "
          f"{', '.join(hits)}")
    a("")

    a("## Notes on tolerance and scope")
    a("")
    a("- Plain integers in 0–13 are treated as TRIVIAL (panel labels, "
      "scaffold-bucket counts, etc.) and ignored in resolution counts.")
    a("- meV values are also matched against their eV equivalents "
      "(52.1 meV ↔ 0.0521 eV) so the canonical JSON does not need to "
      "duplicate units.")
    a("- Percentages are matched against their 0–1 fraction equivalents "
      "(35.7% ↔ 0.357).")
    a("- LaTeX comments, `\\cite/\\ref/\\label/\\bibitem/\\input/"
      "\\IfFileExists/\\includegraphics/\\url/\\href/\\texttt` arguments "
      "and the entire `thebibliography` block are stripped before "
      "scanning, so reference years and volume/page numbers do not "
      "enter the audit.")
    a("")

    return "\n".join(L)


def main() -> None:
    if not PAPER.exists():
        raise FileNotFoundError(PAPER)
    if not CANONICAL.exists():
        raise FileNotFoundError(CANONICAL)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    paper_numbers = extract_numbers_from_tex(PAPER)
    table1_numbers = extract_numbers_from_tex(TABLE1) if TABLE1.exists() else []
    table2_numbers = extract_numbers_from_tex(TABLE2) if TABLE2.exists() else []
    all_extracted = paper_numbers + table1_numbers + table2_numbers

    sources_canonical = flatten_canonical_sources()
    sources_tables = extract_table_numbers()

    resolved = resolve(all_extracted, sources_canonical, sources_tables)
    major = run_major_checks(PAPER.read_text())
    n_caption_files = len(list(CAPTIONS_DIR.glob("*.json")))

    report = render_report(
        resolved, major,
        n_canonical_floats=len(sources_canonical),
        n_caption_files=n_caption_files,
        n_table_floats=len(sources_tables),
    )
    REPORT.write_text(report)

    n_total = len(resolved)
    nontrivial = [r for r in resolved if not r["trivial"]]
    n_unresolved = sum(1 for r in nontrivial if not r["resolved"])
    n_major_hit = sum(1 for f in major if f["n_unmitigated_hits"] > 0)

    print(f"[OK] {REPORT.relative_to(ROOT)}")
    print(f"     numbers extracted     = {n_total}")
    print(f"     non-trivial numbers   = {len(nontrivial)}")
    print(f"     unresolved            = {n_unresolved}")
    print(f"     Major checks tripped  = {n_major_hit} / {len(major)}")


if __name__ == "__main__":
    main()
