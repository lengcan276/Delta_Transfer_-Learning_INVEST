# Phase 3 — 自我审视

**完成时间**：2026-05-01 18:42 CST
**调用 skills**：stats-rigor-reviewer (R1–R6) + comp-chem-method-reviewer (M1–M6) + adversarial-reviewer.
**目标**：冷峻地审视 Phase 2 的 4 个实验，回答四个核心问题。

---

## Q1. 我有没有过度解读结果？

### Phase 2A & 2B (negative results)

**审视**：
- A 的 Spearman ρ = +0.244, p = 0.40, n = 14 — point estimate 是正相关，但 95% CI 必然横跨 0；任何"distance 不影响 nonconformity"的因果断言都过强。
- B 的 Mann-Whitney p = 0.47, calib/test 中位距离 0.803/0.799 — 这是一个 **near-zero effect size**，不是 "underpowered"；结论"no measurable shift"是诚实且适当的。

**风险**：A 的"假设不成立"措辞略强；改为"在 n=14 上没有观察到该相关性"更准确。
**修正**：在论文 Discussion 中用 "we did not detect a Tanimoto-distance dependence (Spearman ρ = +0.24, p = 0.40, n = 14)" 而不是 "distance does not predict nonconformity"。

### Phase 2C (Mondrian)

**审视**：
- 14.3% Mondrian 聚合 vs 35.7% global — 表面上 Mondrian "更差"，但根本原因是 5AP n_calib = 1 退化。
- 这不是 Mondrian 方法的失败，是 calibration 集设计的产物；我已在 phase2 log 中明确说明。
**风险**：低。
**修正**：论文写作时要避免"Mondrian fails"，改用"With this calibration sample (n_calib(5AP) = 1), Mondrian recalibration is infeasible for the 5AP bucket — a design-level rather than method-level failure".

### Phase 2D (locally-weighted CP)

**审视**：**这是过度解读的最大风险点。**
- 在 α=0.80 上 21.4% → 35.7% 的 coverage 上升是 monotonic 的 point estimate，但 Wilson 95% CI:
  - 3/14: [7.6, 47.6]
  - 4/14: [11.7, 54.6]
  - 5/14: [16.3, 61.2]
  - 这些 CI **完全重叠**。形式上无法拒绝 "β 不影响 coverage" 的零假设。
- "α=0.80 上 locally-weighted CP outperforms global" 这种说法不能 carry significance 含义。

**修正**：
- Phase 4 集成进 main.tex 时必须写：
  > "Empirical coverage at α = 0.80 rose monotonically from 3/14 (β = 0) to 5/14 (β = 4); given the small test set (Wilson 95% CIs span ≥ 30 percentage points and overlap), this trend is descriptive."
- 不允许写 "improves coverage" 而不带 "descriptive" 限定。

### "Structural pinning at α = 0.95" 的发现

**审视**：
- 数学事实：ceil((19+1) × 0.95) = ceil(19.0) = 19 = n_calib，所以 split-conformal 的 q̂ = 第 19 阶 = max calibration nonconformity score。这是 *确定性* 的，不是"经验观察"。
- 但这个 "pin" 是 split conformal 的标准教科书内容（Vovk, Algorithmic Learning in a Random World, 2005, Sec 2.4）；CP 理论家都知道。

**风险**：把这件事描述为"我们发现"会显得 naive 给 CP 专家审稿人。
**修正**：
- 论文里写"As is well known in conformal prediction theory (Vovk 2005, §2.4), the finite-sample quantile rank ceil((n+1)α) at α = 0.95 with n_calib = 19 equals n = 19, so q̂ is structurally pinned to the maximum calibration nonconformity score regardless of weighting. We surface this constraint here because, in cheminformatics deployment papers with n_calib < 30, it is the binding factor on attainable empirical coverage and is rarely reported alongside the coverage point estimate."

---

## Q2. 假如我是 Digital Discovery 审稿人，最尖锐的 3 个问题？

### Q2.1 — 为何只测 Morgan FP r=2，没有 sensitivity to FP choice？

**审稿人原话推测**：
> "The negative result on Tanimoto-distance-based mechanism may be FP-dependent. Morgan radius 2 captures only local atomic environments; a larger radius or a topological/pharmacophore FP could produce a different conclusion. Repeating the analysis with one alternative descriptor would strengthen the negative claim."

**回应策略（在论文里前置防御）**：
- 在 Methods 加一句："We use Morgan FP (radius = 2, 2048 bits) as the standard cheminformatics distance metric; sensitivity to alternative descriptors (e.g., MACCS, ECFP6) is left to future work but expected to behave similarly given the strong scaffold separation in our library."
- 在 Phase 4 之前如果时间允许，可加一个 5 分钟的 robustness check：用 r=3 (~ECFP6) 重跑 A/B，看 conclusion 是否稳定。**Phase 2 缓冲时间充足，应做。**

### Q2.2 — Calibration 集的设计选择

**审稿人原话推测**：
> "The conformal calibration set is the chronologically pre-Round-1 labelled subset (n = 19), which is heavily Hz-biased (16/19 Hz, 1/19 5AP). The Mondrian failure on 5AP is therefore a calibration-design artifact, not a CP property. A scaffold-stratified calibration choice (e.g., re-split the 33 mols 18/15 ensuring each scaffold has n ≥ 3 in calib) would resolve the Mondrian degeneracy."

**回应策略**：
- 这是有 force 的 critique。我们的 calibration set 不是按 statistical optimality 选的，而是按 "what was labelled before Round-1 actively went out". 这是真实部署设定。
- Phase 4 写作里诚实交代：
  > "The calibration set used here is the temporally pre-Round-1 labelled subset, which is heavily Hz-skewed by accident of acquisition order. A re-design using scaffold-stratified split would relax the Mondrian degeneracy on 5AP but would forfeit the pre-Round-1 / Round-1 temporal split that defines our deployment-shift evaluation. We therefore report Mondrian's degeneracy as a *design-coupled* limitation, not a methodological one."

### Q2.3 — Lei-Wasserman 2014 weighted CP 的 validity 假设

**审稿人原话推测**：
> "The Tanimoto-weighted CP requires either (a) calibration-test exchangeability under the weight (Tibshirani et al. 2019) or (b) a covariate-shift-aware weighting that uses the source/target density ratio (Tibshirani 2019). The authors' Tanimoto similarity weights are test-molecule-dependent and have no formal validity guarantee in the framework cited; the empirical coverage is descriptive, not certified valid. The current presentation may mislead readers as to the inferential force of the result."

**回应策略**：
- 这是一个真审稿点，需要严格回应。
- 写作时明确：
  > "Locally-weighted CP as applied here uses Tanimoto-similarity weights for adaptive q̂; this is a heuristic adaptation rather than a formally certified weighted-CP procedure (cf. Tibshirani et al. 2019 for the density-ratio formalism). We therefore present the per-mol q̂ values and the empirical coverage as descriptive recalibration outcomes; formal coverage guarantees would require either calibration-test exchangeability under the chosen weights or an explicit density-ratio estimate beyond the scope of this demonstration."
- This caveats prevents the audit-style reading "we proved local CP works". Important.

---

## Q3. 这些新结果加进 paper 是真提升 contribution，还是包装？

### 真提升

1. **"distance-OOD 解释被诊断证伪"** — 这是新的负面知识，在 cheminformatics CP 文献里没有人为 excited-state ML 报告过。Whitehead 2026 ACS Omega 在 QSAR 上证明 nUNC 能识别 conformal 不可靠样本；我们在 excited-state 上 *不能复现*。这是 cross-domain replication failure 的真正贡献。
2. **"finite-sample structural pinning at α=0.95"** — 数学是已知的，但 cheminformatics deployment 论文从不报告（否则就不会有那么多 n_calib=20 + α=0.95 的 over-claims）。Surfacing this constraint 是真贡献。
3. **"locally-weighted CP 在 α=0.80 上有 directional improvement"** — 即使是描述性的 trend，也是一个 actionable proof-of-concept：当 nominal level 选择允许的时候，local CP 比 global CP 更可能给出非平凡的 individualized intervals。这能 reframe Recommendations。

### 真"包装"风险

- 任何把 Phase 2 包装成"本工作提出新方法"的写作都是 overclaim。我们 *应用* 了 Mondrian/Lei-Wasserman/Whitehead 的已有方法，目的是诊断，不是创新方法学。
- Mitigation：在 §3.3 / Methods 明确"we apply locally-weighted CP (Lei & Wasserman 2014; cf. Bostrom & Johansson 2020 for Mondrian) as a diagnostic tool"，避免"we propose locally-weighted CP for chemistry"这种说法。

---

## Q4. 有没有结果反而*削弱*了原论点？

### 削弱（must address）

**原论文（main.tex line 131）**：
> "The two UQ formalisms therefore diagnose different failure modes. Conformal prediction is underconservative because **the exchangeability assumption linking the pre-round calibration set and the round-1 deployment set is visibly violated by the acquisition-induced shift**."

**Phase 2 证据**：
- Tanimoto distance to calib: no shift detected (p = 0.20)
- Tanimoto distance to source: no shift detected (p = 0.47)
- → The "visibly violated by acquisition-induced shift" claim is **NOT supported by chemistry-distance evidence**.

**修正**：必须在 Phase 4 改写 §3.3 这句话。新版本：
> "The two UQ formalisms therefore diagnose different failure modes. Conformal prediction's empirical coverage of 5/14 = 35.7% at the 95% nominal level is, however, structurally bounded by the finite calibration sample: with n_calib = 19, the conformal quantile rank ceil((n+1) × 0.95) = 19 pins q̂ to the maximum calibration nonconformity score irrespective of weighting (Vovk 2005, §2.4; see Methods §X for diagnostic details). Tanimoto-distance-based applicability metrics on Morgan fingerprints did not separate calibration from deployment in this setting (Spearman ρ = +0.24, p = 0.40, n = 14; Mann–Whitney p = 0.47), so the under-coverage cannot be attributed to a chemistry-distance OOD shift; the binding constraint is calibration sample size."

This correction is more nuanced than the original and will appear *more* careful, not less. Net effect on the paper's force: positive.

### 加强

- The structural-pinning finding tightens the claim about UQ's role: it is no longer "conformal looks bad because of unspecified shift"; it's "conformal cannot reach nominal coverage with n_calib = 19, period". This is more decisive.
- The Mondrian-failure note adds a positive recommendation: "do not deploy Mondrian on under-represented scaffolds; use locally-weighted CP at lower α instead".

### 不变

- Bootstrap intervals being ~baseline-width is unchanged (no Phase 2 work touched bootstrap).
- The §3.4 active-learning section is unaffected.

---

## 决定 / Action items for Phase 4

1. **Run a 5-minute robustness check** (Phase 2 buffer): repeat A with Morgan radius 3 to defuse Q2.1.
2. **Phase 4 writing rules**:
   - Replace §3.3 line 131 sentence (above corrected version).
   - Add Methods subsection "Uncertainty Diagnostics" describing diag_A/B/C/D briefly.
   - Insert 1 paragraph in §3.3 referencing all four diag figures + canonical metrics.
   - Update Conclusions (line 190) sentence about UQ to mention the structural-pinning finding and the locally-weighted CP being a partial-recovery option at α < 0.95.
   - Update Abstract sentence (~line 26) about UQ to reflect the calibration-sample binding constraint, **conservatively** — one short clause, no overclaim.
3. **Forbidden phrases**:
   - Do NOT write "we propose locally-weighted CP for chemistry" — use "we apply".
   - Do NOT claim "significant improvement" for D's α=0.80 trend — write "descriptive trend".
   - Do NOT claim Mondrian "fails as a method" — say "is infeasible at this calibration set design".
4. **Forced citations** to add:
   - Vovk 2005 (already in refs as Vovk2005)
   - Tibshirani 2019 (covariate shift weighted CP) — NEW BibTeX entry needed
   - Lei & Wasserman 2014 — NEW
   - Bostrom & Johansson PMLR 2020 — NEW
   - Whitehead 2026 ACS Omega (nUNC AD) — NEW

---

## Phase 3 总结

- **Phase 2 results 是可靠的，但 D 的 trend 必须以 descriptive 措辞写**。
- **Phase 2 的发现削弱了原论文 §3.3 的"acquisition shift causes under-coverage"措辞**；必须 Phase 4 修正。
- **Phase 2 的发现强化了 §3.3 整体的 honesty profile**：把模糊的"shift"诊断升级为具体的 finite-sample structural pinning + recalibration scope statement。
- **3 个新引用 + 1 段 Methods 子章节 + 1 段 Results 增补 + 1 句 Abstract 修订** 即可吸收 Phase 2 的全部成果。

进入 Phase 4 之前先做 Robustness Check (Q2.1)。

---

## Robustness check (post-Phase-3, pre-Phase-4)

**Q2.1 critique addressed: re-ran Phase 2A with Morgan FP r = 3 (~ECFP6).**

| FP setting | Spearman ρ (test n = 14) | p (two-sided) |
|---|---|---|
| Morgan r = 2 (Phase 2A canonical) | +0.244 | 0.400 |
| Morgan r = 3 (this robustness check) | +0.218 | 0.455 |

**Conclusion**: the negative result is robust to FP radius. The
Tanimoto-distance-based mechanism diagnosis stands. The check was a
one-off probe; results are recorded here only and not committed as a
separate figure (the conclusion does not change).

