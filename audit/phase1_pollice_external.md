# Phase 1 — Pollice 446 ADC(2)/cc-pVDZ Source Subset Audit

Audit phase: Phase 1
Repository HEAD: `3a72bc9` (from `audit/AUDIT_COMMIT.txt`)
Date: 2026-05-20
Network: OFFLINE (hard constraint — no ssh/rsync/scp/curl/wget/git push)

---

## Files inspected

### Search outputs
- `audit/pollice_source_candidates.txt` — 24 candidate files
  (csv/json/xlsx containing "pollice", "cc-pvdz", "cc_pvdz", or "ADC(2)")
- `audit/pollice_filter_logic_candidates.txt` — 50 candidate code lines
  (grep on `scripts/`, `data/`, `results/` for the same keywords +
  "source_domain", "model_input_table", "446")
- `audit/external_ref_filename_search.txt` — filename search for
  `pollice*`, `matter2021*`, `*supporting_information*`, `supplementary*`,
  `SI_*`, `*aspuru*` (empty)
- `audit/external_ref_content_search.txt` — content search for the
  Pollice 2021 DOI `10.1016/j.matt.2021.02.017` and related strings
  (3 hits, all string-mention only in caption JSONs / our own audit CSV;
  none is the SI data file)

### Candidate source data files containing Pollice / ADC(2) data
Only the following are *actual data files* (the rest were caption JSONs,
audit reports, or downstream results that merely cite Pollice):

| File | Pollice rows | Pollice + adc2_dest_ev not NA |
|---|---|---|
| `data/processed/master_molecule_table.csv` | 1719 | **446** |
| `data/processed/model_input_table.csv` | 1719 | **446** |
| `data/processed/master_molecule_table_round1_updated.csv` | (not opened — same parent) | — |
| `data/source/invest_master_dataset.csv` | (parent source, opened by other scripts) | — |

---

## Local Pollice subset extraction

### Filter rule (NOT invented — copied from project's own script)

Authoritative source: **`scripts/diag_distance_to_source.py` lines 81-89**,
which is the only script that explicitly asserts `len(pollice) == 446` and
raises if violated:

```python
pollice = mas[
    (mas["source_domain"] == "pollice")
    & mas["adc2_dest_ev"].notna()
].copy()
if len(pollice) != 446:
    raise RuntimeError(
        f"Pollice source filter returned {len(pollice)} rows, "
        "expected 446. Check master_molecule_table.csv."
    )
```

Source file used: `data/processed/master_molecule_table.csv`.

This same filter is reproduced by:
- `scripts/p0a_ablation_fixed.py` line 95-96 (uses
  `master_molecule_table_round1_updated.csv` + `model_input_table.csv`
  merge, but the source-side filter is equivalent: `adc2_available == True
  AND source_domain == "pollice"` and `adc2_dest_ev.notna()` after the
  `dropna(subset=["adc2_dest_ev"])` on `labeled`)
- `scripts/p0b_conformal_prediction.py` line 49 (same)
- `scripts/retrain_after_round1.py` line 155-156 (same)

### Extraction script
`scripts/audit/01_extract_pollice_subset.py` — applies the above filter
verbatim, canonicalises SMILES with RDKit 2026.03.1, writes
`audit/pollice_446_local.csv`.

### Result
```
loaded master_molecule_table.csv: 2026 rows
local Pollice subset (project filter): 446 rows  [expected 446]
model_input_table parallel filter: 446 rows
canonical SMILES OK   = 446
canonical SMILES fail = 0
RDKit available       = True (version 2026.03.1)
```

| Metric | Value |
|---|---|
| Local subset row count | **446** |
| Expected row count | 446 |
| `N == 446`? | **YES** |
| Output CSV | `audit/pollice_446_local.csv` |
| Filter rule used | `source_domain == "pollice" AND adc2_dest_ev.notna()`<br>(verbatim from `scripts/diag_distance_to_source.py:81-89`) |
| Canonical SMILES parse failures | 0 |

---

## Internal pipeline consistency

### Comparison target
`data/processed/model_input_table.csv` — this is the file actually loaded
by `p0a_ablation_fixed.py` / `p0b_conformal_prediction.py` /
`retrain_after_round1.py` for source-domain training.

### Source-domain identification rule (in model_input_table)
Used in `p0a_ablation_fixed.py:95-96`:
```python
labeled = df[df["adc2_available"] == True].dropna(subset=["adc2_dest_ev"])
source = labeled[labeled["source_domain"] == "pollice"]
```
Equivalent (after `dropna`) to the audit filter.

### Set comparison
Output: `audit/pollice_vs_model_input_setdiff.csv` (one row per unique
canonical SMILES across the union of the two sets).

| Metric | Value |
|---|---|
| audit (446-local) set size | 446 |
| model_input source set size | 446 |
| intersection | 446 |
| only in audit | **0** |
| only in model_input | **0** |

### Internal status
**INTERNAL_SET_MATCH** — the audit-extracted 446 Pollice subset is
identical (by RDKit canonical SMILES) to the source-domain subset
actually consumed by the project's ML pipeline.

---

## External reference check

### Search performed (offline, no download)
1. Filename glob: `pollice*`, `matter2021*`, `matter_2021*`,
   `*supporting_information*`, `supplementary*`, `SI_*`, `*aspuru*`
   → 0 hits
2. Content grep for DOI `10.1016/j.matt.2021.02.017` and "Matter 2021" /
   "pollice.*supp" / "pollice.*si" / "matter4_1654" in `*.csv *.json
   *.xlsx *.tsv`
   → 3 hits, **all string mentions only**:
   - `figures/caption_data/diag_distance_to_source.json` — citation in
     caption text
   - `paper_overleaf/figures/caption_data/diag_distance_to_source.json` —
     same caption text
   - `audit/pollice_446_local.csv` — our own audit output (`method_basis_source`
     column documents the Pollice 2021 citation)
3. File-type sweep for `*.xlsx *.sdf *.sdf.gz *.tar *.zip` →
   only `INVEST_paper_overleaf_n13_v3.zip` (the manuscript bundle, not SI)
4. `audit/external_references/` directory: **does not exist**

### Result
**External reference file: NOT FOUND**

The Pollice 2021 supplementary information / source data file is not
present anywhere in the local repository. Per audit hard-constraint #5
(no network, no download), it cannot be fetched in this audit.

### STATUS: MISSING_EXTERNAL_REFERENCE

> Pollice 2021 SI data were not found in the local repository. Until the
> user provides the external SI file, the Pollice source labels are
> internally traceable only to local project files and cannot be
> externally verified in this audit.

### How the user can resolve MISSING_EXTERNAL_REFERENCE

User should obtain the supplementary dataset associated with:

> Pollice et al., *Matter* **2021**, 4, 1654–1682,
> DOI: 10.1016/j.matt.2021.02.017

Suggested places to check (audit does NOT visit these — user must):
1. Supplementary Information / Data Availability section of the
   *Matter* 2021 paper at the publisher's website.
2. Any Zenodo / Figshare / institutional data deposit linked from that
   paper.
3. Public GitHub release from the Aspuru-Guzik group or related INVEST
   dataset repository.

After obtaining the file, place it under:
```
audit/external_references/pollice_2021_si/
```

Then re-run **Phase 1 only** to perform the external cross-check via
`scripts/audit/02_compare_pollice_external.py` (not written this round,
because no external file is present to write a comparison against).

---

## Final Phase 1 status

**INTERNALLY_CONSISTENT**

Reasoning:
- Local Pollice subset extracted via the project's own filter (verbatim
  from `scripts/diag_distance_to_source.py:81-89`) has **N = 446** ✓
- 446-row subset is set-identical (by RDKit canonical SMILES) to the
  source-domain training set actually consumed by the ML pipeline
  (`data/processed/model_input_table.csv` filtered identically) ✓
- All 446 rows produce valid RDKit canonical SMILES (0 parse failures) ✓
- No external Pollice 2021 SI reference file is present in the local
  repository, so external verification of (a) the molecule identities,
  (b) the ADC(2)/cc-pVDZ ΔE_ST values, and (c) the method/basis labelling
  could not be performed in this audit.

### What this status does and does not mean

**Can be said:** the 446-row Pollice subset cited throughout the
manuscript is reproducibly extracted by a single filter rule applied to
project-local data; the same 446 rows are what the ML pipeline trains on.

**Cannot be said:** the ADC(2)/cc-pVDZ ΔE_ST values in the
`adc2_dest_ev` column for Pollice rows are externally verified against
the published Pollice 2021 source data. They are accepted at face value
as project metadata pending the external SI file.

**Cannot be said:** the `method = "ADC(2)"` / `basis = "cc-pVDZ"` labels
attached to these 446 rows are independently verified by raw calculation
output. For the source-domain subset, raw output files belong to the
external Pollice 2021 campaign and are not present locally; this is
expected (the project re-uses Pollice's published labels, it does not
re-run them).

---

## Deliverables produced this Phase

```
audit/pollice_source_candidates.txt              24 lines
audit/pollice_filter_logic_candidates.txt        50 lines
audit/external_ref_filename_search.txt           0 lines
audit/external_ref_content_search.txt            3 lines
audit/pollice_446_local.csv                      446 rows + header
audit/pollice_vs_model_input_setdiff.csv         446 union rows + header
audit/01_extract_pollice_subset.log              extraction stdout
audit/01b_setdiff.log                            setdiff stdout
audit/phase1_pollice_external.md                 (this file)
scripts/audit/01_extract_pollice_subset.py       (audit script, written this phase)
```

`scripts/audit/02_compare_pollice_external.py` — **not written** because
no external reference file is present. Will be written in a future re-run
of Phase 1 if the user supplies the SI file under
`audit/external_references/pollice_2021_si/`.

---

## Hard-constraint compliance (Phase 1)

| Constraint | Status |
|---|---|
| No file under `paper/`, `results/`, `data/`, `figures/`, `scripts/` (non-`scripts/audit/`) modified | ✓ |
| All new files written under `audit/` and `scripts/audit/` | ✓ |
| No `git add`, `git commit`, `git push`, `git rebase`, no git config changes | ✓ |
| No ssh/rsync/scp/curl/wget; no network access | ✓ |
| Did not fabricate the 446 to make the count fit (verified by filter coming verbatim from project script) | ✓ |
| Did not treat `session.md` as evidence — only as keyword index | ✓ |
| MISSING_EXTERNAL_REFERENCE marked honestly; no recovery from session.md attempted | ✓ |

---

## Status & gate

**Phase 1: COMPLETE.**

Final status: **INTERNALLY_CONSISTENT** (446-row Pollice subset internally
reproducible and set-matched against ML pipeline input; external Pollice
2021 SI verification NOT performed because the SI file is absent from the
local repository — flagged MISSING_EXTERNAL_REFERENCE).

**Halting.** Waiting for user instruction "继续 Phase 2" before proceeding
to Phase 2 (canonical_metrics.json self-audit).
