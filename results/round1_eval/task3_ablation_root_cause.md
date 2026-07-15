# Task3 Ablation Root Cause

## Verdict

- `results/round1_eval/task3_ablation_results.csv` is a stale legacy output.
- Its generator script is the older `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py` workflow, not the current `github_upload` script set.
- The file is exactly reproducible from the current data by a legacy logic that re-filters every ablation config against source-domain coverage, which removes all physics descriptors and leaves the same 54 RDKit features for all six configs.

## Source Code Origin

- Tracked current script: `scripts/p0a_ablation_fixed.py`
- Legacy generator script: `/home/nudt_cleng/2026/project/scripts/task3_ablation_study.py`
- Exact legacy code pattern: `run_loo_delta()` inside `task3_ablation_study.py` applies a shared `usable_features` filter of the form `source[c].notna().mean() >= 0.1 and target[c].notna().mean() >= 0.1` before both the source and delta models are built.

## Data Files Driving the Bug

- `data/processed/model_input_table.csv`
- `data/processed/master_molecule_table_round1_updated.csv`

## Coverage Pattern That Triggers the Collapse

- `stda_s1_ev`: source coverage = 0.0%, target coverage = 0.0%
- `stda_t1_ev`: source coverage = 0.0%, target coverage = 0.0%
- `stda_dest_ev`: source coverage = 0.0%, target coverage = 0.0%
- `stda_fosc`: source coverage = 0.0%, target coverage = 0.0%
- `homo_spacing`: source coverage = 0.0%, target coverage = 57.6%
- `lumo_spacing`: source coverage = 0.0%, target coverage = 57.6%
- `od_index`: source coverage = 0.0%, target coverage = 57.6%
- `dft_dest_raw_ev`: source coverage = 0.0%, target coverage = 100.0%
- `dft_dest_calibrated_ev`: source coverage = 0.0%, target coverage = 100.0%
- `fosc_dft`: source coverage = 0.0%, target coverage = 100.0%
- `homo_ev`: source coverage = 0.0%, target coverage = 57.6%
- `lumo_ev`: source coverage = 0.0%, target coverage = 57.6%
- `hl_gap_ev`: source coverage = 0.0%, target coverage = 57.6%
- `homo_m1_ev`: source coverage = 0.0%, target coverage = 57.6%
- `lumo_p1_ev`: source coverage = 0.0%, target coverage = 57.6%

## Reconstruction

| Config | Nominal count | Usable after legacy filter | Reconstructed MAE | task3 MAE | Match |
|---|---:|---:|---:|---:|---|
| `full` | 69 | 54 | 0.052086959787 | 0.052086959787 | Yes |
| `no_stda` | 65 | 54 | 0.052086959787 | 0.052086959787 | Yes |
| `no_ksod` | 66 | 54 | 0.052086959787 | 0.052086959787 | Yes |
| `no_stda_no_ksod` | 62 | 54 | 0.052086959787 | 0.052086959787 | Yes |
| `no_dft` | 61 | 54 | 0.052086959787 | 0.052086959787 | Yes |
| `rdkit_only` | 54 | 54 | 0.052086959787 | 0.052086959787 | Yes |

## Why p0a Differs

- `scripts/p0a_ablation_fixed.py` keeps the source model on shared RDKit features but lets the delta model use target-domain physics features directly.
- Therefore `p0a` does not discard KS-OD and DFT features just because source rows lack them.
- That is why `p0a_ablation_multiseed.csv` shows real differences across configs while `task3_ablation_results.csv` does not.
