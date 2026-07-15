# Phase 0 — 全局数据地图

**完成时间**：2026-05-01 18:16 CST
**耗时**：约 30 分钟
**结论**：数据充足，**可以直接进入 Phase 1**，无需停下等指令。

---

## 1. 数据地图表

| 我需要的数据 | 状态 | 路径（绝对） |
|---|---|---|
| Per-molecule conformal nonconformity scores（33 mol） | ✅ 找到 | `~/2026/github_upload/results/round1_eval/p0b_conformal_calibration.csv` |
| Per-molecule bootstrap mean + std（33 mol） | ✅ 找到 | 同上（列 `boot_mean`, `boot_std`） |
| Per-molecule true gap + point prediction（33 mol） | ✅ 找到 | 同上（列 `y_true`, `pred`） |
| 33 mol calibration vs test 标签 | ✅ 找到 | 同上（列 `set` ∈ {calibration, test}） |
| 14 deployment mol SMILES + scaffold | ✅ 找到 | `~/2026/github_upload/data/processed/master_molecule_table.csv`（mol_id 全部匹配） |
| 33 mol（19 calib + 14 test）SMILES + scaffold | ✅ 找到 | 同上（33/33 mol_id 匹配） |
| 446 Pollice source SMILES + ADC(2) 标签 | ✅ 找到 | 同上（filter `source_domain == "pollice"` ∧ `adc2_dest_ev.notna()`） |
| Conformal multi-level coverage（6 nominal levels） | ✅ 找到 | `~/2026/github_upload/results/round1_eval/p0b_conformal_calibration.json` |
| Per-member bootstrap predictions | ❌ **未保存** | 当前脚本 `p0b_conformal_prediction.py` 只存 mean/std |
| Per-molecule predicted residuals（round1 deployment） | ✅ 找到 | `~/2026/github_upload/results/round1_eval/task1_deployment_detail.csv`、`p03_sigma_vs_residual.csv` |
| 已训练模型（avoid retrain） | ⚠️ 不需要 | 复跑 conformal 流水线只要 ~1 分钟（XGBoost），重训成本可忽略 |
| RDKit / Tanimoto / Morgan FP | ✅ 可用 | `from rdkit import Chem, AllChem, DataStructs` 验证通过 |

## 2. 已有 / 缺失数据 → 可行性判断

| 候选诊断方向 | 数据基础 | 可行性 | 说明 |
|---|---|---|---|
| **A. Tanimoto distance-to-calibration vs conformal nonconformity 相关分析** | ✅ 全有 | **直接可做** | Morgan FP r=2 from RDKit + 19 calib SMILES + 14 test SMILES + nonconf scores |
| **B. Tanimoto distance-to-source（446 Pollice）vs |residual|** | ✅ 全有 | **直接可做** | 446 Pollice SMILES + 33 target |residual| |
| **C. Scaffold-conditional (Mondrian) conformal coverage** | ✅ 全有 | **直接可做** | scaffold_family 列已有；按 Hz / 5AP / others 分桶重算 q_hat |
| **D. Locally-weighted conformal（Tanimoto-weighted quantile）** | ✅ 全有 | **直接可做** | 同 A + 加权位数 |
| **E. Bootstrap ensemble 成员多样性** | ⚠️ 部分 | **需 1 次 ~1min 重跑** | 现有脚本只存 mean/std；要 per-member preds 必须改脚本（在 github_upload/scripts/ 下做副本，输出 per-member matrix） |
| **F. Bootstrap σ vs |residual| 相关 / sharpness 分析** | ✅ 全有 | **直接可做** | boot_std 已经在 CSV 里 |
| **G. Epistemic vs aleatoric 分解（Deep Ensemble + MVE）** | ❌ 缺数据 | **不做** | 需要 mean-variance estimation 模型（双输出 head），当前 XGBoost regressor 只输出点；引入新架构超出本 session 时间 |

## 3. 选定优先级（写在 Phase 1 报告里详细论证）

候选优先排序（基于"对论文 contribution 的杠杆 × 实现难度 × 数据完整度"）：

1. **A + C + D 组合** — 一条完整的 "Diagnose → Mechanism → Recalibration" 故事链：
   - **A** = 诊断（为什么 conformal 失效）→ 距离-不一致性相关
   - **C** = 机制（哪类样本失效最厉害）→ Hz vs 5AP 子集 coverage
   - **D** = 修正方案（locally-weighted conformal 是否能恢复 nominal coverage）
2. **B** — 强化 A 的 mechanism 部分（distance-to-source 比 distance-to-calibration 更通用）
3. **F** — 现有 boot_std 数据快速做一个 sharpness/calibration 散点图，补充 bootstrap 章节
4. **E** — 时间允许再做（per-member 多样性是 nice-to-have，不是 critical-path）

## 4. 数据完整性 sanity check

```
conformal_calibration.csv:    34 rows (header + 33 mol)
  calibration set:            19 mol（pre-Round-1 labelled target）
  test set:                   14 mol（Round-1 deployment, excl. Hz_NH23）

mol_id ↔ master_molecule_table SMILES match:    33/33

Pollice source ADC(2)-labelled training set:    446 mol
  → 这是论文 abstract 引用的 "446 source-domain ADC(2)/cc-pVDZ labels"
  → 已在 canonical_metrics.library.n_invest_labeled_pollice_source 暴露
```

## 5. 红线检查

- ✅ 所有计划写入路径都在 `~/2026/github_upload/` 下
- ✅ 旧脚本 `~/2026/project/scripts/p0b_conformal_prediction.py` 不会原地用；如需复跑会在 `~/2026/github_upload/scripts/` 下做副本（实际上 github_upload/scripts/p0b_conformal_prediction.py 已是副本，可以直接派生 `diag_*.py`）
- ✅ Pollice 源 SMILES 来自 `~/2026/github_upload/data/processed/master_molecule_table.csv`（在工作区内）；不会读 `~/2026/data/invest_core/` 的原始文件做写入
- ✅ `paper/main.tex`、`results/validated_candidates_master.csv`、`results/canonical_metrics.json` 在 Phase 4 之前不动

## 6. 进入 Phase 1 的决策

**直接进入 Phase 1**。理由：

- 关键数据全部就位（A, B, C, D, F 五条诊断路线无任何缺口）
- 不需要新 ORCA / SCS-CC2 计算（红线 = 不动 orca_jobs/）
- 一次性可写入的脚本 ≤ 6 个，每个 < 200 行
- Bootstrap per-member preds 是 nice-to-have，不阻塞主线

**不需要等用户决策** — 数据完整度满足任务设计要求。
