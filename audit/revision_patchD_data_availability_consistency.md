# Patch D Step 8 — README / DATA_AVAILABILITY consistency

## Verdict: **PASS — all formal-file Data Availability statements consistent**

## Consistency matrix

| target | README.md | DATA_AVAILABILITY.md | paper/main.tex | paper_overleaf/main.tex | results/canonical_metrics.json |
|---|---|---|---|---|---|
| canonical INVEST-n13 URL | ✓ (lines 9, 67) | ✓ (lines 4, 46, 85) | ✓ (line 198) | ✓ (line 198) | ✓ (lines 711, 741) |
| ADC(2) partial provenance honestly stated | ✓ (line 79) | ✓ (lines 56–70) | ✓ (lines 210–223) | ✓ (mirror) | ✓ via `raw_provenance_status` (line 712) |
| SCS-CC2 n=13 raw verified locally | ✓ (line 73) | ✓ (lines 39–48) | ✓ (lines 204–208) | ✓ (mirror) | ✓ via `raw_provenance_status` (line 712) |
| single writer of canonical | ✓ (line 103) | implicitly via "regenerate" recipe | — | — | ✓ via `generator` / `writer` fields |
| `audit_numbers.py` target stated | ✓ (lines 47, 58, 61, 90) | ✓ (lines 77–79) | — | — | n/a |
| no FedSchNet URL in formal files | ✓ (0 hits) | ✓ (0 hits) | ✓ (0 hits) | ✓ (0 hits) | ✓ (0 hits) |
| no overclaim of "complete ADC(2) raw archive" | ✓ ("partial" stated) | ✓ ("ybsi-pending" explicit) | ✓ ("partially included") | ✓ (mirror) | ✓ ("remains partial") |
| raw archive = external (not git-tracked) | ✓ (implicit via "manifest") | ✓ (lines 36–48 GitHub Release / Zenodo) | ✓ ("separate raw-archive tarball") | ✓ (mirror) | n/a |
| no internal audit phase wording | ✓ (audit-history bullets file-path-only) | ✓ (no Phase 4/5 in formal prose) | ✓ (Patch A/B-tail hygiene scrubbed) | ✓ (mirror) | ✓ (`audit_report_reference` is a metadata field only) |

## Highlights from the grep

- `README.md:79` — "ADC(2) raw provenance: partial. 20 / 35 raw outputs are ..." — honest disclosure
- `DATA_AVAILABILITY.md:56–70` — "20 / 35 ADC(2)/def2-SVP raw outputs are locally verified ... 15 / 35 ADC(2) raw outputs were computed on the `ybsi` compute cluster and were not rsynced into the local audit snapshot ..." — honest disclosure
- `paper/main.tex:223` — "n=13 SCS-CC2 cohort that **is** fully raw-verified locally" — accurate scope
- `results/canonical_metrics.json:712` — `"raw_provenance_status": "SCS-CC2 n=13 raw-output verified from local ricc2_scscc2 outputs; ADC(2) raw provenance remains partial."` — single-source-of-truth label
- `results/canonical_metrics.json:632` — the `scope_separation_note` describing the legacy `candidate_scscc2_crosschecks (n=4)` block; this is correct internal metadata about the legacy block scope (NOT a paper-facing claim)

## Conclusion

No mismatch found. README, DATA_AVAILABILITY, paper, paper_overleaf,
and canonical_metrics all agree on:

- canonical URL `https://github.com/lengcan276/INVEST-n13`
- SCS-CC2 n=13 fully raw-verified locally
- ADC(2) 20/35 verified + 15/35 ybsi-pending (honestly disclosed)
- single canonical writer = `scripts/99_emit_canonical.py`
- raw archive = external (GitHub Release / Zenodo)
- audit_numbers target = unresolved = 0, Major = 0 / 7
- no FedSchNet URL in any formal file

No documentation fix required in Step 8. Proceed to Step 9.
