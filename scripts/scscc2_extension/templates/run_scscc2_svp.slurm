#!/bin/bash
#SBATCH --job-name=scscc2_PLACEHOLDER
#SBATCH --partition=batch,intel
#SBATCH --exclude=node8,node9
# Allows scheduler to pick batch (faster) or intel (more idle nodes); skip down* nodes
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --time=168:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
# NOTE: --mem omitted intentionally. Slurm RealMemory=1 MB on node5-7,12
# (config quirk; nodes physically have 180-345 GB free). Historical SCS-CC2
# sbatch also omits --mem and runs fine. Setting --mem=64G would be rejected.

# === RL-1 hostname guard — refuse to run on login/master node ===
if [[ "$(hostname)" == "master" || "$(hostname)" == *"login"* ]]; then
    echo "FATAL: refusing to run on login node $(hostname)"
    exit 99
fi

# === RL-1 cleanup: remove tmp dir on ANY exit (success, failure, signal) ===
trap 'rm -rf /public/home/ybsi/tmp/${SLURM_JOB_ID}' EXIT

echo "=== Job started ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "Slurm Job ID: $SLURM_JOB_ID"
echo "Slurm Nodelist: $SLURM_NODELIST"
echo "Working directory: $SLURM_SUBMIT_DIR"
cd "$SLURM_SUBMIT_DIR" || exit 1

# === Turbomole + Intel oneAPI env (matches historical 4-job sbatch) ===
export PARA_ARCH=SMP
source /public/home/ybsi/software/TURBOMOLE/Config_turbo_env
source /public/apps/oneapi/setvars.sh intel64 2>/dev/null
export TURBODIR=/public/home/ybsi/software/TURBOMOLE
export PARNODES=$SLURM_CPUS_PER_TASK
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

mkdir -p /public/home/ybsi/tmp/${SLURM_JOB_ID}
export TMPDIR=/public/home/ybsi/tmp/${SLURM_JOB_ID}

# === Stage 1: ADC(2)/def2-SVP — produces converged MOs in turbo_{sing,trip}_svp_round2 ===
SING_DIR=turbo_sing_svp_round2
TRIP_DIR=turbo_trip_svp_round2

if [ ! -f ${SING_DIR}/control ] || [ ! -f ${TRIP_DIR}/control ]; then
    echo "FATAL: control files missing in $SING_DIR or $TRIP_DIR — run setup_scscc2_svp_on_login.sh first"
    exit 1
fi

# Singlet ridft (RI-DFT/SCF) → ricc2 (ADC(2)) — needed to converge MOs for SCS-CC2 step
cd ${SING_DIR}
echo "--- SCF (ridft) Singlet: $(date) ---"
sed -i '/^\$actual/d; /^\$last step/d' control  # defensive: remove stale state from any prior aborted run
ridft > ridft_sing.out 2>&1
if ! grep -q "ridft ended normally" ridft_sing.out; then
    echo "SCF Singlet FAILED"; tail -20 ridft_sing.out; exit 1
fi

echo "--- ADC(2) Singlet: $(date) ---"
ricc2 > ricc2_adc2_sing.out 2>&1
if ! (grep -q 'ricc2 : all done' ricc2_adc2_sing.out || grep -q 'ricc2 ended normally' ricc2_adc2_sing.out); then
    echo "ADC(2) Singlet FAILED"; tail -20 ricc2_adc2_sing.out; exit 1
fi
cd ..

# Triplet — reuse converged MOs from singlet then ridft + ricc2
cp ${SING_DIR}/mos ${TRIP_DIR}/mos
cd ${TRIP_DIR}
echo "--- SCF (ridft) Triplet: $(date) ---"
sed -i '/^\$actual/d; /^\$last step/d' control  # defensive: remove stale state from any prior aborted run
ridft > ridft_trip.out 2>&1
if ! grep -q "ridft ended normally" ridft_trip.out; then
    echo "SCF Triplet FAILED"; tail -20 ridft_trip.out; exit 1
fi

echo "--- ADC(2) Triplet: $(date) ---"
ricc2 > ricc2_adc2_trip.out 2>&1
if ! (grep -q 'ricc2 : all done' ricc2_adc2_trip.out || grep -q 'ricc2 ended normally' ricc2_adc2_trip.out); then
    echo "ADC(2) Triplet FAILED"; tail -20 ricc2_adc2_trip.out; exit 1
fi
cd ..

# === Stage 2: clone *_svp_round2 → *_scscc2_svp, patch adc(2) → cc2+scs, run ricc2 ===
for mult in sing trip; do
    SRC=turbo_${mult}_svp_round2
    DST=turbo_${mult}_scscc2_svp
    rm -rf "$DST"; mkdir -p "$DST"
    for f in coord basis auxbasis mos control; do
        cp "$SRC/$f" "$DST/"
    done
    python3 - "$DST/control" <<'PYEOF'
import sys
p = sys.argv[1]
with open(p) as f:
    txt = f.read()
old = "$ricc2\n  adc(2)\n  maxiter 150"
new = "$ricc2\n  cc2\n  scs\n  maxiter 150"
if old not in txt:
    raise SystemExit(f"ERROR: expected ricc2 block not found in {p}")
with open(p, 'w') as f:
    f.write(txt.replace(old, new))
print(f"Patched {p}: adc(2) -> cc2 + scs")
PYEOF
    rm -f "$DST/CC"* || true
done

# Run SCS-CC2 — singlet first
cd turbo_sing_scscc2_svp
echo "--- SCS-CC2 Singlet: $(date) ---"
sed -i '/^\$actual/d; /^\$last step/d' control  # defensive: remove stale state from any prior aborted run
ricc2 > ricc2_scscc2_sing.out 2>&1
if ! (grep -q 'ricc2 : all done' ricc2_scscc2_sing.out || grep -q 'ricc2 ended normally' ricc2_scscc2_sing.out); then
    echo "SCS-CC2 Singlet FAILED"; tail -20 ricc2_scscc2_sing.out; exit 1
fi
cd ..

# Triplet SCS-CC2 — reuse converged singlet MOs
cp turbo_sing_scscc2_svp/mos turbo_trip_scscc2_svp/mos
cd turbo_trip_scscc2_svp
echo "--- SCS-CC2 Triplet: $(date) ---"
sed -i '/^\$actual/d; /^\$last step/d' control  # defensive: remove stale state from any prior aborted run
ricc2 > ricc2_scscc2_trip.out 2>&1
if ! (grep -q 'ricc2 : all done' ricc2_scscc2_trip.out || grep -q 'ricc2 ended normally' ricc2_scscc2_trip.out); then
    echo "SCS-CC2 Triplet FAILED"; tail -20 ricc2_scscc2_trip.out; exit 1
fi
cd ..

echo "=== Job finished cleanly ==="
echo "Date: $(date)"
# (tmp cleanup handled by trap EXIT at top of script)
