# Phase 1 — 方法选定 + 文献调研

**完成时间**：2026-05-01 18:35 CST
**耗时**：约 20 分钟
**结论**：选定 **A + B + C + D 四条诊断**，构成 "Diagnose → Mechanism → Recalibration" 故事链。

---

## 1. 选定方向 + rationale

### 主线（Diagnose → Mechanism → Recalibration）

**A. Distance-to-calibration vs conformal nonconformity correlation (Diagnose)**
- 输入：19 calibration mol + 14 test mol 的 Morgan FP（r=2, 2048 bits）
- 计算：每个 test mol 到 calib set 的 1-Tanimoto 最近邻距离 d₁(test→calib)
- 相关：Spearman ρ between d₁ and |residual|（test set 14 mol）
- **目的**：把"为什么 35.7% << 95%"从一句话升级为定量机制
- **预期结果**：正相关；相关强度决定后续 mechanism 的力度

**B. Distance-to-source-training vs |residual| (Mechanism)**
- 输入：446 Pollice source SMILES + 33 target mol（19 calib + 14 test）
- 计算：每个 target mol 到最近 Pollice mol 的 1-Tanimoto 距离
- 相关：Spearman ρ between distance-to-source and |y_true − pred|
- **目的**：证明 OOD shift 不是"整批 14 mol 都远"，而是 calib 离 source 近、test 离 source 更远
- **预期结果**：test set 距离分布显著大于 calib set；如果是这样，conformal 失败有可解释的几何根源

**C. Scaffold-conditional / Mondrian conformal coverage (Mechanism)**
- 输入：33 mol 的 nonconformity scores + scaffold_family
- 计算：把 calibration set 按 scaffold（Hz vs non-Hz）分桶，对每桶单独算 q̂₀.₉₅；apply to 同 scaffold 的 test 子集
- **目的**：检查"是否所有 scaffold 都失败了，还是只有某个子集失败"
- **预期结果**：如果 Hz 子集 coverage 比 5AP 子集好得多，说明 conformal 失败被特定 scaffold（5AP, 完全 OOD）放大；这是 Mondrian/scaffold-aware CP 的经典适用场景

**D. Tanimoto-weighted locally-adaptive conformal (Recalibration)**
- 输入：calibration 19 mol nonconformity scores + 14 test mol Morgan FP
- 计算：对每个 test mol，用 Tanimoto 相似度作为权重，从 calib set 提取**加权** quantile (Beran-style local conformal)
- 输出：每个 test mol 一个 individualized q̂ → 个体化 coverage
- **目的**：演示 recalibration —— locally-weighted CP 是否能比 global CP 提供更接近 nominal 的 coverage（即使是在 14-mol 小样本上）
- **预期结果**：locally-weighted 提供更宽 / 更窄 intervals（而不是恒定 53 meV），且 coverage 应高于 global CP；不一定能恢复到 nominal 95%（小样本限制），但能证明方法朝正确方向走

### 不做（已评估并放弃）

- **Bootstrap per-member 多样性 (E)**：原 `p0b_conformal_prediction.py` 只存 mean/std。需要复跑保存 per-member preds（成本约 1 分钟）但只能给出"成员高度相关 → ensemble 是 pseudo-uncertainty"的弱叙事，不像 D 一样是可操作的修复。**不做**，节省时间留给主线。
- **Epistemic / aleatoric 分解 (G)**：需要新的 mean-variance estimation 模型架构，超出 session 时间。**不做**。

## 2. 关键文献（按相关度）

1. **Whitehead et al., ACS Omega 2026** — "Explicit Applicability Domain Calculations Can Help Determine When Uncertainty Estimates Are Less Reliable" — k-NN 距离 (nUNC) 作为 AD 指标，证明 conformal/Venn-ABERS 在 OOD 上不可靠且 nUNC 能识别这种不可靠。**这是和我们直接对应的工作**；本论文必须 cite 并明确"我们的诊断在小样本/excited-state 场景重现并扩展了他们的发现"。
2. **Boström & Johansson, PMLR 2020** — "Mondrian Conformal Regressors" — Mondrian CP 的 regression 形式，把 calib 按特征/类别分桶。本论文 C 部分的方法学根。
3. **Arvidsson McShane et al., J. Cheminform. 2024 (CPSign)** — Mondrian CP 的 cheminformatics 实现；为 D 提供 reference implementation 选型依据（虽然我们不用 CPSign 包，会用纯 Python + RDKit 自己实现以保持依赖最小）。
4. **Hopkins et al. (Bayer), JCIM 2024** — adaptive local ML with Tanimoto-selected training；同 D 用 Tanimoto weighting 的思想，但他们做 model selection 我们做 calibration weighting。
5. **Bostrom-Johansson-Lofstrom, PMLR 2021** — Mondrian Conformal Predictive Distributions — 提供 Mondrian 在小样本上的统计行为参考。
6. **Norinder et al., J. Chem. Inf. Model. 2014** — Introducing CP for AD determination —— 历史背景，证明"CP-as-AD"有十年传统。
7. **Wessels & Krestel, ScienceDirect 2025** — review of CP in cheminformatics —— 现状综述，用于 Methods/Discussion 引用。

## 3. 方法定位（必须诚实）

**(c) 我新提出的方法 — 否**
**(b) 我改进了已有方法 — 否**
**(a) 我把已有方法应用到新问题 — 是**

具体地：A、B、C、D 都是 2014–2025 文献中已有的工具（distance-based AD、Mondrian CP、locally-weighted CP）。**本论文的新意不是方法学，而是把它们组合成一个针对 excited-state ML 在 OOD 14-mol deployment 上的失效诊断 + 修复 demo**。

写作时必须明确：
- "We apply locally-weighted conformal prediction (Lei & Wasserman 2014; cf. Bostrom 2020 for Mondrian) to diagnose…" —— **不是**说"We propose a new method"
- 论文 contribution 升级表述：从 "we report conformal under-coverage" → "we diagnose the failure mechanism (distance-to-calibration drives nonconformity), localise it to specific scaffold subsets (5AP), and show that scaffold-aware Mondrian / locally-weighted recalibration partially recovers coverage even on a 14-molecule deployment set."

## 4. 详细实验设计

### 实验 A — distance vs nonconformity

**输入路径**：
- `~/2026/github_upload/results/round1_eval/p0b_conformal_calibration.csv`（mol_id, set, nonconf_score for 33 mol）
- `~/2026/github_upload/data/processed/master_molecule_table.csv`（mol_id ↔ smiles）

**计算步骤**（写入 `~/2026/github_upload/scripts/diag_distance_nonconformity.py`）：
1. 读 33 mol 的 mol_id, set, nonconf_score
2. merge SMILES from master_molecule_table.csv
3. RDKit Morgan FP r=2, 2048 bits（standard MFP cheminformatics setting）
4. 对每个 test mol 计算 Tanimoto 最近邻距离 d₁(test → calib)
5. Spearman ρ(d₁, nonconf_score) for test set
6. 输出 JSON + CSV + scatter PDF

**输出 path**：
- `results/diagnostics/distance_nonconformity.{json,csv}`
- `figures/diag_distance_nonconformity.pdf`
- `figures/caption_data/diag_distance_nonconformity.json`

**Success 标准**：
- Spearman ρ ≥ 0.4 with two-sided p < 0.1 → 强信号，进 paper
- 0.2 ≤ ρ < 0.4 → 中等信号，进 paper 但 caveated
- |ρ| < 0.2 → 弱信号，写在 supplement，不强调

### 实验 B — distance to Pollice source

**输入路径**：同上 + `master_molecule_table.csv` 的 `source_domain == "pollice"` 子集（446 mol）

**计算步骤**（写入 `~/2026/github_upload/scripts/diag_distance_to_source.py`）：
1. 读 446 Pollice SMILES
2. 读 33 target mol SMILES + |y_true − pred|（from p0b_conformal_calibration.csv）
3. 对每个 target 计算到 Pollice 集的最近邻 Tanimoto 距离
4. Spearman ρ(d_to_source, |residual|) for 33 mol（calib + test 一起，因为这是诊断 pre-existing OOD 性质）
5. 还要计算 calib vs test 的 d_to_source 分布是否显著不同（Mann-Whitney U）

**输出**：
- `results/diagnostics/distance_to_source.{json,csv}`
- `figures/diag_distance_to_source.pdf`（split violinplot calib vs test）

**Success 标准**：
- Mann-Whitney U test 显示 test 的 d_to_source 显著大于 calib（p < 0.05）→ 解释了 conformal 失效
- Spearman ρ(d_to_source, |residual|) > 0.3 → 加分

### 实验 C — Scaffold-conditional (Mondrian) coverage

**输入路径**：`p0b_conformal_calibration.csv` + scaffold_family from master_molecule_table.csv

**计算步骤**（`~/2026/github_upload/scripts/diag_mondrian_coverage.py`）：
1. 把 19 calib + 14 test 都按 scaffold 分桶。预期分布：calib = {Hz: ~14, 5AP: ~3, BN: ~2}; test = {Hz: ~9, 5AP: ~5}
2. 对每个 scaffold 桶：
   - 取该 scaffold 在 calib 的 nonconf scores → 算 q̂₀.₉₅
   - 取该 scaffold 在 test 的 nonconf scores → empirical coverage
3. 比较 Mondrian coverage vs 全局 coverage (35.7%) at 95% nominal level
4. 记录每桶 n（Hz n=?, 5AP n=?）+ coverage CI（Wilson）

**输出**：
- `results/diagnostics/mondrian_coverage.{json,csv}`
- `figures/diag_mondrian_coverage.pdf`（bar chart by scaffold + global comparison）

**Success 标准**：
- 至少有 1 个 scaffold 桶 Hz coverage 比全局 35.7% 显著高 OR 5AP coverage 显著低 → 强 mechanism 信号
- 如果 Mondrian 桶都太小（n<3 per bucket）→ 报告"不可执行"，回到主诊断 A+B

### 实验 D — Locally-weighted conformal recalibration

**输入路径**：同 A

**计算步骤**（`~/2026/github_upload/scripts/diag_local_conformal.py`）：
1. 对每个 test mol t:
   - 计算到所有 19 calib mol 的 Tanimoto 相似度 s_i = T(t, c_i)
   - 加权 quantile：用权重 w_i ∝ s_i / Σ_j s_j 在 nonconf scores {α_i} 上取 α=0.95 加权 quantile（weighted empirical CDF inversion）
   - 个体化 q̂_t
2. coverage = mean over test set of [|y_true − pred| ≤ q̂_t]
3. 比较 vs global conformal (q̂ 固定 = 0.0267, coverage 35.7%)
4. 也要报告区间宽度分布（每个 test mol 一个 q̂_t）→ 是否有"远的样本得到更宽区间"的预期行为

**输出**：
- `results/diagnostics/local_conformal.{json,csv}`
- `figures/diag_local_conformal.pdf`（comparison: global vs local q̂ per test mol + coverage bars）

**Success 标准**：
- Local coverage > global 35.7% by ≥ 5 pp（5/14 → 6/14 或更高）→ 进 paper
- Local coverage 不变或下降 → 说明 calib n=19 太小，locally-weighted 也救不了 → 诚实报告（这本身是有价值的负面结果）

## 5. 时间预算

| 实验 | 预估耗时 |
|---|---|
| A (distance vs nonconf) | 25 分钟 |
| B (distance to source) | 30 分钟（446 vs 33 距离矩阵稍大） |
| C (Mondrian) | 25 分钟 |
| D (locally-weighted CP) | 35 分钟 |
| 中间 review + 调试 | 30 分钟 |
| **合计** | **2 小时 25 分钟** |

留约 30 分钟缓冲在 Phase 2 总硬上限 (3 小时) 内。

## 6. 风险 + mitigation

| 风险 | 概率 | mitigation |
|---|---|---|
| Mondrian 桶太小（5AP n<3） | 中 | 桶合并或退回 D；C 报告"insufficient n per bucket" |
| Locally-weighted CP coverage 没改善 | 中 | 诚实报告负面结果；这本身证明 "n=19 calib 是硬上限" |
| Tanimoto 相关 ρ 太弱 | 低 | 已知 chemistry-MFP 在 INVEST scaffold 下区分度高（Hz vs 5AP MFP overlap < 30%） |
| 旧 SMILES vs new RDKit canonicalisation 不一致 | 低 | 直接用 master_molecule_table.csv 里的 SMILES，不重 canonicalise |

---

进入 Phase 2，按 A → B → C → D 顺序执行。
