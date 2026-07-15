# INVEST Discovery via Delta Transfer Learning and Active Learning

Code and data for the paper: *Delta transfer learning with active learning discovers INVEST molecules from a 155-candidate focused library — and reveals when the approach fails*

---

## Five Innovation Points

### 1. Delta Transfer Learning for Small-Sample INVEST Prediction

Transfer residual correction from a large source domain (446 Pollice molecules, ADC(2)/cc-pVDZ) to a small target domain (33 molecules, mixed methods) via XGBoost. LOO-CV MAE = 0.052 eV on the target domain.

- **Script:** `scripts/p0a_ablation_fixed.py`, `scripts/train_source_target_transfer.py`
- **Result:** `results/round1_eval/p0a_ablation_paired_tests.json`

### 2. Negative Transfer from Physics Descriptors

Counter-intuitive finding: adding physics-based features (DFT orbital energies, KS-OD descriptors, sTDA) to the delta correction model **worsens** prediction. RDKit-only achieves the best MAE (0.052 eV) vs full feature set (0.055 eV). All results are deterministic under LOO-CV (std = 0 across 10 seeds is expected, not a bug).

- **Script:** `scripts/p0a_ablation_fixed.py`
- **Result:** `results/round1_eval/p0a_ablation_multiseed.csv`
- **Key finding:** Physics descriptors contribute noise > signal in small-sample cross-domain transfer

### 3. UQ Failure Mode Taxonomy Under OOD

Split conformal prediction (Vovk 2005) vs bootstrap ensemble uncertainty quantification both fail under out-of-distribution deployment, but via **different mechanisms**:
- Conformal: miscalibrated (35.7% coverage at 95% nominal, intervals too narrow)
- Bootstrap: calibrated but uninformative (width 0.324 eV ~ naive fixed baseline 0.320 eV)

- **Script:** `scripts/p0b_conformal_prediction.py`
- **Result:** `results/round1_eval/p0b_conformal_calibration.json`
- **Key finding:** Neither UQ method provides actionable guidance for INVEST classification under OOD

### 4. Active Learning Value Reframing

AL does NOT beat random sampling on INVEST hit rate (7/15 vs expected 13.2/15, all p-values ~ 1.0). Its value lies in:
- **Subspace elimination:** Fisher exact test confirms Hz vs 5AP INVEST rate difference (p = 0.031)
- **Scaffold diversity:** AL explored 5AP subspace (0% INVEST), which Hz-greedy would never visit
- **Information gain:** 13.5% entropy reduction, CSRF = 3.27 molecules eliminated per query

- **Script:** `scripts/task2_baseline_significance.py`, `scripts/stats_validation.py`
- **Result:** `results/round1_eval/task2_hz_prior_defense.json`, `results/round1_eval/stats_validation_results.json`

### 5. Hierarchical Cross-Fidelity Validation (n=13 SCS-CC2 audit)

35 molecules classified via pre-registered evidence-grade rubric with three confidence levels:
- **high:** >= 2 independent methods agree on sign AND |DDEST| < 0.05 eV
- **medium:** single method or sign-confirmed but |DDEST| > 0.05 eV
- **low:** borderline, pending, or contradictory

Final tally: 10 negative_gap + 3 dark_negative_gap + 1 borderline + 21 positive_gap (0 pending, 0 unverified).

**SCS-CC2/def2-SVP cross-check extended from n=4 (original) to all n=13 ADC(2)-screened INVEST candidates** (the pre-registered Table 1 shortlist). 0 sign disagreement; one-sided 95% rule-of-three upper bound on within-screen sign-disagreement rate ≈ 3/13 = 0.23. All 13 SCS-CC2 ΔEST values are systematically more negative than ADC(2) (range −10 to −194 meV, mean −110 meV); framed as **method-family consistency within ADC(2)/CC2 rather than method-independent confirmation** (independent CCSD/CC3/NEVPT2 triangulation is identified as future work).

- **Scripts:** `scripts/scscc2_extension/build_cross_check_n13.py` (assemble + Clopper–Pearson/rule-of-three stats), `scripts/scscc2_extension/plot_fig4_n13.py` (regenerate Fig 4), `scripts/scscc2_extension/parsers/parse_scscc2_dest.py` (robust ricc2 parser w/ self-test), `scripts/scscc2_extension/templates/run_scscc2_svp_v2.slurm` (stage-skip restart + zombie defense + auto-cleanup)
- **Results:** `results/scscc2_extension_n13/cross_check_n13.csv`, `results/scscc2_extension_n13/stats_n13.json`
- **Phase reports:** `results/scscc2_extension_n13/phase{0,1,2}_*.md` — geometry source decision, sanity reproduction (bit-identical), mini-batch checkpoint, Phase 2.4 plan + submission record
- **Master table:** `results/validated_candidates_master.csv`

---

## Repository Structure

```
.
├── scripts/                              # Reproducible analysis scripts
│   ├── p0a_ablation_fixed.py             # Innovation 1+2: ablation study
│   ├── p0b_conformal_prediction.py       # Innovation 3: UQ failure taxonomy
│   ├── task2_baseline_significance.py    # Innovation 4: AL vs baselines
│   ├── stats_validation.py              # Innovation 4: statistical tests
│   ├── build_validated_master.py         # Innovation 5: master table builder
│   ├── train_source_target_transfer.py   # Delta transfer learning training
│   ├── build_master_table.py             # Data preparation
│   ├── compute_rdkit_features.py         # RDKit feature engineering
│   ├── compute_physics_features.py       # Physics descriptors (DFT, KS-OD)
│   ├── merge_feature_blocks.py           # Feature assembly
│   ├── run_active_learning_round1.py     # Active learning loop
│   ├── evaluate_round1_hits.py           # Round-1 evaluation
│   ├── ingest_round1_adc2_results.py     # ADC(2) result ingestion
│   ├── retrain_after_round1.py           # Post-round-1 retraining
│   ├── audit_numbers.py                  # Consistency audit: paper vs canonical_metrics.json
│   ├── 99_emit_canonical.py              # Regenerate canonical_metrics.json from raw data
│   └── scscc2_extension/                 # Innovation 5: n=13 SCS-CC2 cross-check
│       ├── build_cross_check_n13.py      # Assemble 13-row table + Clopper–Pearson/rule-of-three
│       ├── plot_fig4_n13.py              # Regenerate Fig 4 with 13 markers (TNR, 300 DPI)
│       ├── setup_scscc2_svp_on_login.sh  # Turbomole control file generator (def2-SVP)
│       ├── parsers/parse_scscc2_dest.py  # ricc2.out parser w/ all-done precondition + selftest
│       └── templates/run_scscc2_svp_v2.slurm  # Hardened wrapper: stage-skip, no-requeue, auto-cleanup
├── data/
│   ├── processed/                        # ML-ready feature tables
│   │   ├── model_input_table.csv         # 2026 molecules, 85 features
│   │   ├── rdkit_features.csv            # Morgan FP PCA + RDKit descriptors
│   │   ├── physics_features.csv          # DFT orbital energies, KS-OD
│   │   └── master_molecule_table_round1_updated.csv
│   └── source/
│       └── invest_master_dataset.csv     # 3444 source molecules (Pollice + Omar)
├── results/
│   ├── validated_candidates_master.csv   # Final 35-molecule master table
│   ├── adc2_batch2_summary.csv           # RI-ADC(2)/def2-SVP raw results (10 molecules)
│   ├── scscc2_batch2_summary.csv         # SCS-CC2/def2-SVP results (4 molecules, historical)
│   ├── scscc2_extension_n13/             # Innovation 5: n=13 cross-check extension
│   │   ├── cross_check_n13.csv           # 13-molecule cross-check table
│   │   ├── stats_n13.json                # Clopper–Pearson + rule-of-three (0.7529/0.23)
│   │   └── phase{0,1,2}_*.md             # Phase reports (geometry/sanity/checkpoint/plan)
│   ├── invest_labeled_layered.csv        # L1+L2+L3 merged evidence labels
│   ├── stgabs27_all_methods_benchmark.csv # External benchmark (STGABS27)
│   ├── method_consistency_table.csv      # Multi-method consistency
│   └── round1_eval/                      # Statistical evaluation outputs
│       ├── p0a_ablation_paired_tests.json
│       ├── p0a_ablation_multiseed.csv
│       ├── p0b_conformal_calibration.json
│       ├── p0b_conformal_calibration.csv
│       ├── task2_hz_prior_defense.json
│       ├── task2_baseline_significance.csv
│       └── stats_validation_results.json
├── figures/                              # Publication-quality figures
├── requirements.txt
└── README.md
```

---

## Computational Methods

### L1 Screen: Delta-DFT Linear Calibration
- Geometry: GFN2-xTB optimization
- S1: TDA-TDDFT/PBE0/def2-SVP (ORCA 6.1.0)
- T1: UKS delta-SCF/PBE0/def2-SVP
- Linear correction: DEST_corr = 0.5501 * raw - 0.2127 (R^2 = 0.97, n = 5 anchors)

### L2 Post-HF: RI-ADC(2)/def2-SVP
- Turbomole 7.5.1 ricc2 module, SMP 48 cores
- 5 singlet + 3 triplet roots

### L3 Post-HF: SCS-CC2/def2-SVP
- Turbomole 7.5.1 ricc2 with `cc2 + scs`
- Independent second-level verification

### ML: Delta Transfer Learning (XGBoost)
- Source: 446 Pollice molecules (ADC(2)/cc-pVDZ)
- Target: 33 molecules (mixed methods)
- Features: 54 shared RDKit descriptors + Morgan FP PCA
- LOO-CV MAE: 0.052 eV, sign accuracy: 78.8%

---

## Reproduction

```bash
pip install -r requirements.txt

# Innovation 1+2: Ablation study (deterministic, ~30s)
python3 scripts/p0a_ablation_fixed.py

# Innovation 3: UQ failure taxonomy (~30s)
python3 scripts/p0b_conformal_prediction.py

# Innovation 4: AL baseline significance (~10s)
python3 scripts/task2_baseline_significance.py
python3 scripts/stats_validation.py

# Innovation 5: Master validation table (~5s)
python3 scripts/build_validated_master.py
```

---

## Data Authenticity

All quantum chemistry results were parsed from raw Turbomole ricc2 output files with 5-decimal precision. Key cross-checks:

| Molecule | ADC(2) DEST (eV) | SCS-CC2 DEST (eV) | Sign Agree | DDEST (eV) |
|----------|-------------------|---------------------|------------|------------|
| Hz_DMAC1_NPh21_CF31 | -0.12034 | -0.22033 | Yes | 0.100 |
| Hz_NPh22_SO2Ph1 | -0.09532 | -0.21444 | Yes | 0.119 |
| Hz_POZ1_NPh21_CF31 | -0.00971 | -0.16557 | Yes | 0.156 |
| Hz_NH23 | -0.38346 | -0.55787 | Yes | 0.174 |

Raw ricc2 output files are available upon request.

---

## License

MIT

## Citation

[Will be added upon publication]
