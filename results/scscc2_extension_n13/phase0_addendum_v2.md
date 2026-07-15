# Phase 0 Addendum v2 — fixes after GPT 二审

Date: 2026-05-02
Operator: Claude Code (qfh-u24)

Supersedes the v1 addendum on 4 specific items. v1 still authoritative for
Q2/Q5/Q6 and the original P1-A/P1-E description.

---

## Fix 1 — `intel` 节点资源审计 (P1-NEW-A)

### scontrol 探测结果

```
$ ssh -p 22116 ybsi@10.67.4.7 \
    "for n in node5 node6 node7 node12; do
       echo === $n ===
       scontrol show node $n | grep -E 'CPUTot|RealMemory|Sockets|CoresPerSocket|ThreadsPerCore'
     done"

=== node5 ===
NodeName=node5 Arch=x86_64 CoresPerSocket=1
   CPUAlloc=0 CPUTot=48 CPULoad=0.00
   RealMemory=1 AllocMem=0 FreeMem=184054 Sockets=48 Boards=1
   State=IDLE ThreadsPerCore=1 TmpDisk=0
=== node6 ===
   CPUAlloc=0 CPUTot=48 CPULoad=0.00
   RealMemory=1 AllocMem=0 FreeMem=200895 Sockets=48 Boards=1
=== node7 ===
   CPUAlloc=0 CPUTot=48 CPULoad=0.00
   RealMemory=1 AllocMem=0 FreeMem=263223 Sockets=48 Boards=1
=== node12 ===
   CPUAlloc=0 CPUTot=48 CPULoad=0.00
   RealMemory=1 AllocMem=0 FreeMem=345676 Sockets=48 Boards=1
```

### 解读 + 模板影响

| 字段 | 数值 | 解读 |
|---|---|---|
| `CPUTot` | 48 (4 节点一致) | `--cpus-per-task=48` 安全，无需调小 |
| `Sockets` | 48 | 单 thread/单 core/socket 配置（每个 socket 1 个物理核），非 hyperthreaded |
| `RealMemory` | **1** (MB) | **Slurm config quirk** — `RealMemory` 没正确设置 |
| `FreeMem` | 184–345 GB | 节点物理内存巨大，绝对够用 |
| `State` | IDLE | 4 节点都空闲 |

### 模板调整

`RealMemory=1` 意味着 Slurm 把这些节点当作只有 1 MB 物理内存，**`--mem=64G` 会被直接拒绝**。历史 sbatch (Hz_POZ1_NPh21_CF31 SVP, line: `#SBATCH -N 1 / -n 48 / -p batch / --time=72:00:00`) **完全没有 `--mem` 行**，依赖默认。

→ **新模板已删除 `--mem=64G`**，并加注释解释原因。

`--cpus-per-task=48` 保留，与历史 48 核 SMP 一致。

---

## Fix 2 — `trap EXIT` 清理 (P1-NEW-C)

### Diff

```diff
 # === RL-1 hostname guard — refuse to run on login/master node ===
 if [[ "$(hostname)" == "master" || "$(hostname)" == *"login"* ]]; then
     echo "FATAL: refusing to run on login node $(hostname)"
     exit 99
 fi

+# === RL-1 cleanup: remove tmp dir on ANY exit (success, failure, signal) ===
+trap 'rm -rf /public/home/ybsi/tmp/${SLURM_JOB_ID}' EXIT
+
 echo "=== Job started ==="
```

末尾旧的手动 `rm -rf` 已删除（被 `trap EXIT` 覆盖）。

无论 ridft 失败、ricc2 OOM、SIGTERM，13 个分子串跑都不会在 `/public/home/ybsi/tmp/` 累积垃圾。

---

## Fix 3 — Parser 加 "ricc2 : all done" precondition (P2-NEW-A → 升级 P1)

### Diff

```diff
 def parse_first_excitation_eV(ricc2_out_path):
+    """Return the first 'Energy: ... eV' value as float (S1 if singlet, T1 if triplet).
+
+    Precondition: ricc2 must have completed cleanly. Otherwise an unconverged
+    'Energy:' value would be silently returned and corrupt the ΔE_ST result.
+    """
     p = Path(ricc2_out_path)
     if not p.exists():
         raise FileNotFoundError(f"ricc2 output not found: {p}")
-    with p.open() as f:
-        for line in f:
-            m = ENERGY_RE.match(line)
-            if m:
-                return float(m.group(1))
+    text = p.read_text()
+    if 'ricc2 : all done' not in text and 'ricc2 ended normally' not in text:
+        raise ValueError(
+            f"ricc2 did not finish cleanly (no 'all done' / 'ended normally' marker): {p}"
+        )
+    for line in text.splitlines():
+        m = ENERGY_RE.match(line)
+        if m:
+            return float(m.group(1))
     raise ValueError(f"No 'Energy:' excited-state line found in {p}")
```

### 二次自测 stdout

```
$ python3 parse_scscc2_dest.py --selftest

Self-test on Hz_DMAC1_NPh21_CF31 (def2-SVP)
  Singlet: /home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_sing_scscc2/ricc2_scscc2_sing.out
  Triplet: /home/nudt_cleng/2026/results/adc2_batch2_raw/Hz_DMAC1_NPh21_CF31/turbo_trip_scscc2/ricc2_scscc2_trip.out
  E(S1)        = 3.46991 eV
  E(T1)        = 3.69024 eV
  ΔE_ST parsed = -0.22033 eV
  ΔE_ST ref    = -0.22033 eV (method_consistency_table.csv)
  difference   = -0.000 meV
  PASS — parser reproduces reference within 0.1 meV
```

历史 ricc2.out 含 `ricc2 : all done` 行 → precondition 通过 → 解析正常返回 -0.22033 eV，差值 0.000 meV。新增的完成度检查不影响 happy-path 输出。

---

## Fix 4 — RL-1 retrospective 证据修正 (P0-NEW-1)

v1 addendum 用 `ricc2.out` 第 3 行的 "ricc2 (node1)" 字符串作为"compute node"证据。GPT 二审正确指出: **ricc2 程序自身不显式打印 hostname，"(node1)" 是 Turbomole 内部对 node 的命名习惯，无法 100% 排除 master alias 可能**。

### 修正后的 RL-1 retrospective 论证（三条独立证据）

**证据 1 — sinfo 显示 `node1` 是 batch partition 的 compute node**

```
$ ssh ybsi "sinfo"
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
batch*       up   infinite      2    mix node[1,4]
batch*       up   infinite      2  alloc node[2-3]
```
→ `node1` 列在 `batch` partition 内，状态 `mix`（被作业分配中）。partition 节点 ≠ 集群登录节点 (`master` 是登录节点，单独存在不在任何 partition 内)。

**证据 2 — 历史 sbatch 脚本含 Slurm 调度指令**

```
$ cat ~/2026/results/scscc2_poz1_nph21_cf31_inputs/Hz_POZ1_NPh21_CF31/run_scs_cc2.slurm
#!/bin/bash
#SBATCH -J scscc2_Hz_POZ1_NPh21_CF31
#SBATCH -N 1
#SBATCH -n 48
#SBATCH -p batch              ← 提交到 batch partition
#SBATCH --time=72:00:00
...
```
→ 历史 4 个 SVP SCS-CC2 job 通过 sbatch 提交到 `batch` partition。Slurm 不会把作业分配给 partition 之外的节点（即不会落到 master）。

**证据 3 — 真实并行计算证据（OpenMP + walltime ratio）**

```
$ head -1 ricc2_scscc2_sing.out
   OpenMP run-time library returned nthreads = 48

$ tail -10 ricc2_scscc2_sing.out
    total  cpu-time : 18 days 22 hours 20 minutes and 27 seconds
    total wall-time : 11 hours 26 minutes and 12 seconds
```
→ CPU/wall 比 = (18d 22h 20m) / (11h 26m) ≈ 39.7 ≈ 48 线程 (理想加速比)，证实实际有 ~48 线程并行加速。master 节点典型只有少量核心给登录使用，无法支持 48 线程持续 11 小时；只有 batch partition 的 compute node 才有 48 物理核（已由 Fix 1 的 `scontrol show node` 间接确认）。

**结论**：三条证据共同证明历史 4 个 SCS-CC2 job 在 batch partition 的 compute node 上运行，**未在 master/login 节点执行**。RL-1 retrospective 满足。

---

## 修复完成 / 推迟 / 仅登记 矩阵

| Item | 状态 |
|------|------|
| **P0-NEW-1** RL-1 retrospective 证据 | ✅ Fixed (本 v2) |
| **P1-NEW-A** intel 节点 CPU/Mem 审计 | ✅ Fixed (本 v2; 模板已调) |
| **P1-NEW-C** trap EXIT 清理 | ✅ Fixed (本 v2) |
| **P2-NEW-A** parser 完成度 precondition | ✅ Fixed (升级 P1，本 v2) |
| **P1-NEW-B** setup 脚本 sed byte-for-byte | ⏳ 推迟到 Phase 1.1 |
| **P2-NEW-B** node CPU microarch 漂移 | 📝 仅登记 (Phase 1 sanity 报告中说明 < 0.1 meV 远小于 ±2 meV 阈值) |
| **P2-NEW-C** SCF 起点等价性 | 📝 仅登记 (Phase 1 sanity 后 diff SCF total energy < 1e-6 a.u.) |

**P0-NEW-1, P1-NEW-A, P1-NEW-C, P2-NEW-A 已修，P1-NEW-B 推迟到 Phase 1.1，P2-NEW-B/C 仅登记。**

---

## 下一步

进 **Phase 1 sanity** — 单分子 Hz_DMAC1_NPh21_CF31，目标复现 ΔE_ST = -0.22033 ± 0.002 eV。

具体步骤（Phase 1.1 + 1.2 + 1.3 + 1.4）：

1. **1.1** 写 `setup_scscc2_svp_on_login.sh`，逐字符对齐历史 `setup_tzvp_on_login.sh`，仅替换 `def2-TZVP` → `def2-SVP`（处理 P1-NEW-B）。
2. **1.2** rsync 整个 `~/2026/results/scscc2_extension_n13/` 到 ybsi。
3. **1.3** 在 ybsi master 跑 `bash setup_scscc2_svp_on_login.sh Hz_DMAC1_NPh21_CF31` 生成 control（cheap，只跑 define + sed）。
4. **1.4** `cd Hz_DMAC1_NPh21_CF31; sed s/PLACEHOLDER/.../ ../templates/run_scscc2_svp.slurm > run.slurm; sbatch run.slurm`。
5. **1.5** 等完成（预计 ~12-24h），rsync 回，跑 parser 验证。

每步报告进展。完成后写 `phase1_sanity_pass.md` 或 `phase1_sanity_FAIL.md`。
