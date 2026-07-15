# INVEST-n13

Code, data, and audited provenance for the manuscript
*Delta transfer learning with active learning discovers INVEST
molecules from a 155-candidate focused library — and reveals when
the approach fails*.

**Canonical repository:**
[https://github.com/lengcan276/INVEST-n13](https://github.com/lengcan276/INVEST-n13)

---

## Scope

Low-data INVEST screening on a 155-candidate focused library, with
a hierarchical post-Hartree–Fock validation pipeline:

- 446-molecule Pollice ADC(2)/cc-pVDZ source set → 33-molecule
  target-domain RI-ADC(2)/def2-SVP labels (delta transfer learning)
- 14-molecule round-1 deployment (15 deployed, Hz_NH23 excluded
  from the conformal / Fisher subset by design)
- 35-molecule final validation table, with SCS-CC2/def2-SVP
  cross-checks on **all 13 ADC(2)-screened INVEST candidates**
  (negative-gap + dark-negative-gap shortlist)

---

## Reproducibility chain

The canonical pipeline has a single canonical writer for the
top-level metadata file `results/canonical_metrics.json`:

```
scripts/scscc2_extension/build_cross_check_n13.py
    └─ writes results/scscc2_extension_n13/cross_check_n13.csv
    └─ writes results/scscc2_extension_n13/stats_n13.json

scripts/99_emit_canonical.py
    └─ reads the two files above (+ all other processed tables)
    └─ writes results/canonical_metrics.json
       (sole writer of canonical_metrics.json; build_cross_check_n13.py
       does NOT write canonical_metrics.json)

scripts/audit_numbers.py
    └─ checks paper/main.tex numbers against canonical_metrics.json
       + figures/caption_data/*.json + results/Table1*.tex
    └─ target: unresolved = 0, Major checks = 0 / 7
```

### Regenerating from a fresh checkout

```bash
python3 scripts/scscc2_extension/build_cross_check_n13.py
python3 scripts/99_emit_canonical.py
python3 scripts/audit_numbers.py
```

Expected validation output from `audit_numbers.py`:

```
unresolved = 0
Major issue checks triggered = 0 / 7
```

If these targets are not met, the regeneration did not match the
reference state. Please open an issue at
[https://github.com/lengcan276/INVEST-n13/issues](https://github.com/lengcan276/INVEST-n13/issues).

---

## Key status

- **SCS-CC2 n=13 raw-output provenance:** locally verified
  end-to-end via independent parser, with sha256 manifest at
  `audit/revision_patchC_raw_provenance_manifest.tsv` (26 files,
  ~1.16 MB; all banner-confirmed CC2 + Spin-Component Scaling
  with def2-SVP basis; compute-node hostnames recorded on all 26;
  no login-node red flags).
- **ADC(2) raw provenance:** partial. 20 / 35 raw outputs are
  locally verified (12 fully, 8 to within sub-meV rounding-level
  differences attributable to processed-table rounding); the
  remaining 15 R1-deploy raw outputs are unavailable locally and
  are documented as `ybsi` cluster pending in the Data Availability
  section and in `DATA_AVAILABILITY.md`.
- **Single-writer canonical pipeline:** `scripts/99_emit_canonical.py`
  is the sole writer of `results/canonical_metrics.json`; verified
  by `scripts/audit/15_validate_patchB_single_writer.py` (15/15
  checks pass).
- **Number-consistency audit:** `audit_numbers.py` currently
  reports `unresolved = 0` and `Major checks = 0 / 7`.

---

## Repository layout

```
.
├── data/
│   ├── processed/                          # ML-ready feature tables
│   └── source/                             # source-domain datasets
├── results/
│   ├── canonical_metrics.json              # canonical numerical leaf store
│   │                                       # (single writer: scripts/99_emit_canonical.py)
│   ├── validated_candidates_master.csv     # 35-molecule master table
│   ├── scscc2_extension_n13/
│   │   ├── cross_check_n13.csv             # 13-molecule SCS-CC2 cross-check
│   │   ├── stats_n13.json                  # screened-cohort statistics
│   │   │                                   # (rule-of-three primary;
│   │   │                                   # Clopper-Pearson kept transparency-only)
│   │   └── phase{0,1,2}_*.md               # historical phase reports
│   ├── round1_eval/                        # round-1 statistical evaluation
│   └── diagnostics/                        # UQ diagnostic JSONs
├── scripts/
│   ├── 99_emit_canonical.py                # canonical-metrics writer
│   ├── audit_numbers.py                    # paper-vs-canonical audit
│   ├── scscc2_extension/                   # SCS-CC2 n=13 pipeline
│   │   ├── build_cross_check_n13.py        # upstream writer
│   │   ├── plot_fig4_n13.py                # Fig 4 regenerator
│   │   ├── parsers/parse_scscc2_dest.py    # robust ricc2 parser
│   │   └── templates/run_scscc2_svp_v2.slurm
│   └── audit/                              # audit-checker scripts
├── paper/                                  # primary manuscript tree
├── paper_overleaf/                         # Overleaf-style mirror
├── figures/                                # publication-quality figures
│   └── caption_data/                       # per-figure metadata JSONs
├── reviews/                                # cover letter etc.
├── audit/                                  # phase audit reports + manifests
├── DATA_AVAILABILITY.md                    # public-facing data statement
├── README.md
└── requirements.txt
```

---

## Computational methods (summary)

- **L1 screen:** GFN2-xTB optimization; TDA-TDDFT/PBE0/def2-SVP
  singlet; UKS ΔSCF/PBE0/def2-SVP triplet; linear ΔE_ST
  calibration anchored on a small (N=5) anchor set
- **L2 post-HF:** RI-ADC(2)/def2-SVP via Turbomole 7.5.1 `ricc2`
  module
- **L3 post-HF:** SCS-CC2/def2-SVP via Turbomole 7.5.1 `ricc2`
  with `cc2 + scs` (Grimme factors C_os = 1.2, C_ss = 0.333),
  deployed across all 13 ADC(2)-screened INVEST candidates
- **ML:** delta transfer learning with XGBoost, 446 Pollice source
  → 33 target labels, RDKit + Morgan-FP-PCA features

The manuscript and the auxiliary manifests describe SCS-CC2 sign
agreement with ADC(2) as **method-family consistency within the
ADC(2)/CC2 hierarchy** rather than method-independent confirmation
against an unrelated theory level; an independent CCSD / CC3 /
NEVPT2 triangulation tier is identified in the manuscript as
future work.

---

## Data availability

See `DATA_AVAILABILITY.md` for the formal public-facing data
statement, including:

- processed validation tables (included in this repository)
- canonical metrics file (`results/canonical_metrics.json`)
- raw-output provenance manifest
  (`audit/revision_patchC_raw_provenance_manifest.tsv`)
- raw archive plan (external GitHub Release asset / Zenodo)
- ADC(2) ybsi-pending honest disclosure

---

## Provenance audit history (brief)

The audit trail lives under `audit/`. Key entry points:

- `audit/phase5_residual_issues.md` — read-only audit completion
  summary
- `audit/revision_patchB_review_fix.md` — single-writer canonical
  refactor (closes the prior reproducibility gap on the
  `scs_cc2_extended_n13` block of `canonical_metrics.json`)
- `audit/revision_patchB_tail_summary.md` — closes
  `audit_numbers.py` unresolved values to 0
- `audit/revision_patchC_raw_provenance_manifest.md` — sha256
  manifest for the SCS-CC2 n=13 raw outputs

---

## License

MIT

## Citation

[Will be added upon publication]
