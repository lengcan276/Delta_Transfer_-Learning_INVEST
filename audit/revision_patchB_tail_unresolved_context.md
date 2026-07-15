# Patch B-tail Step 1 — Unresolved value context + classification

## Value: `26.0`

| field | value |
|---|---|
| file (primary) | `paper/main.tex` |
| line | 205 |
| file (mirror) | `paper_overleaf/main.tex` |
| line (mirror) | 205 |
| full surrounding context | "Raw Turbomole `ricc2` outputs for the SCS-CC2/def2-SVP cross-check cohort (n=13 molecules, singlet + triplet = 26 files) are locally verified end-to-end against the parsed values to the precision of the reported digits;" |
| appears in formal manuscript text | YES (Data Availability section, added in Patch A) |
| is a scientific result claim | NO — derived arithmetic (2 × 13) |
| is Data Availability / provenance explanatory text | YES |
| is software-version / path-like text | NO |
| classification | **PROVENANCE_EXPLANATORY_NUMBER** |
| recommended handling | Treatment A — rewrite. Replace `"singlet + triplet = 26 files"` with `"singlet and triplet outputs"`. The substantive content (two energies per molecule) is preserved; the redundant derived integer is dropped. |

## Value: `0.41`

| field | value |
|---|---|
| file (primary) | `paper/main.tex` |
| line | 213 |
| file (mirror) | `paper_overleaf/main.tex` |
| line (mirror) | 213 |
| full surrounding context | "Twenty raw outputs (12 fully verified to the precision of the reported digits and 8 verified to within $0.41$~meV with the residual attributed entirely to processed-table rounding to 3~decimals in~eV) are locally raw-verified." |
| appears in formal manuscript text | YES (Data Availability section, added in Patch A) |
| is a scientific result claim | NO — audit-derived upper bound on parsed-vs-CSV rounding deviation; not a quantum-chemistry result, not a method-comparison claim |
| is Data Availability / provenance explanatory text | YES |
| is software-version / path-like text | NO |
| classification | **PROVENANCE_EXPLANATORY_NUMBER** (audit-precision number that documents rounding behaviour rather than a physical observable) |
| recommended handling | Treatment A — rewrite. Replace `"within $0.41$~meV"` with `"within sub-meV rounding-level differences"`. The substantive content (rounding-level, not method-level) is preserved; the precise audit-derived bound is dropped from the manuscript and remains available in `audit/phase5_adc2_rounding_only_audit.md` for any reader who wants it. |

## Treatment decision

Both values are **PROVENANCE_EXPLANATORY_NUMBER** added in Patch A and
are **not core scientific claims** (no S1/T1/ΔE_ST value, no molecule
classification, no headline statistic).

**Preferred treatment: A (rewrite).** This avoids:
- adding new canonical metrics (Treatment B) for two informational
  values that the manuscript does not cite as scientific evidence;
- allowlisting in `audit_numbers.py` (Treatment C), which would mask
  the audit signal rather than remove it.

Edits are confined to `paper/main.tex` and `paper_overleaf/main.tex`
in the Data Availability section that was introduced in Patch A.
No scientific value is changed. No molecule classification is changed.
No canonical JSON is hand-edited.

## Other constraints respected

- No new caveat paragraphs introduced.
- No `audit Phase` / `Step` / `internal audit` wording introduced.
- No `1e-13` / `10^` / machine-epsilon numbers introduced.
- `paper/main.tex:211` ("singlet + triplet = 70 files") is left
  untouched because 70 is not currently in the unresolved list;
  this pass narrowly fixes the two flagged values and does not
  reach beyond them.
