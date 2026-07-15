#!/bin/bash
#SBATCH --job-name=scscc2_PLACEHOLDER
#SBATCH --partition=batch,intel
#SBATCH --exclude=node8,node9
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --time=168:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --no-requeue
# v2 wrapper:
#   - stage-skip via "ended normally" / "all done" markers in per-stage outputs
#   - --no-requeue prevents Slurm auto-restart from scratch on node fault
#   - clean_actual removes stale $actual / $last step before each run
#   - Stage 2 clone+patch is idempotent (skip if control already patched)
#   - re-submit safely continues from the first non-finished stage

# === RL-1 hostname guard ===
if [[ "$(hostname)" == "master" || "$(hostname)" == *"login"* ]]; then
    echo "FATAL: refusing to run on login node $(hostname)"
    exit 99
fi

# === RL-1 cleanup ===
trap 'rm -rf /public/home/ybsi/tmp/${SLURM_JOB_ID}' EXIT

echo "=== Job started ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo "Slurm Job ID: $SLURM_JOB_ID"
echo "Working directory: $SLURM_SUBMIT_DIR"
cd "$SLURM_SUBMIT_DIR" || exit 1

# === Turbomole + Intel oneAPI env ===
export PARA_ARCH=SMP
source /public/home/ybsi/software/TURBOMOLE/Config_turbo_env
source /public/apps/oneapi/setvars.sh intel64 2>/dev/null
export TURBODIR=/public/home/ybsi/software/TURBOMOLE
export PARNODES=$SLURM_CPUS_PER_TASK
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

mkdir -p /public/home/ybsi/tmp/${SLURM_JOB_ID}
export TMPDIR=/public/home/ybsi/tmp/${SLURM_JOB_ID}

# === Helper functions ===
done_marker() {
    local out="$1"
    [ -f "$out" ] || return 1
    grep -q "ended normally\|ricc2 : all done" "$out" && return 0
    return 1
}

clean_actual() {
    sed -i '/^\$actual/d; /^\$last step/d' control
}

run_ridft_or_skip() {
    local out="$1" tag="$2"
    if done_marker "$out"; then
        echo "  [skip] $tag (output ended normally)"
        return 0
    fi
    echo "--- $tag: $(date) ---"
    clean_actual
    ridft > "$out" 2>&1
    if ! grep -q "ridft ended normally" "$out"; then
        echo "FAIL: ridft $tag"; tail -20 "$out"; exit 1
    fi
}

run_ricc2_or_skip() {
    local out="$1" tag="$2"
    if done_marker "$out"; then
        echo "  [skip] $tag (output ended normally)"
        return 0
    fi
    echo "--- $tag: $(date) ---"
    clean_actual
    ricc2 > "$out" 2>&1
    if ! (grep -q 'ricc2 : all done' "$out" || grep -q 'ricc2 ended normally' "$out"); then
        echo "FAIL: ricc2 $tag"; tail -20 "$out"; exit 1
    fi
}

# === Stage 1: ADC(2) sing ===
SING_DIR=turbo_sing_svp_round2
TRIP_DIR=turbo_trip_svp_round2

cd "$SING_DIR" || { echo "FATAL: $SING_DIR missing"; exit 1; }
run_ridft_or_skip ridft_sing.out "SCF (ridft) Singlet"
run_ricc2_or_skip ricc2_adc2_sing.out "ADC(2) Singlet"
cd ..

# === Stage 1: ADC(2) trip ===
if ! done_marker "$TRIP_DIR/ridft_trip.out"; then
    cp "$SING_DIR/mos" "$TRIP_DIR/mos"
fi
cd "$TRIP_DIR" || { echo "FATAL: $TRIP_DIR missing"; exit 1; }
run_ridft_or_skip ridft_trip.out "SCF (ridft) Triplet"
run_ricc2_or_skip ricc2_adc2_trip.out "ADC(2) Triplet"
cd ..

# === Stage 2 setup: clone + patch (idempotent) ===
setup_scscc2_dir() {
    local mult=$1
    local SRC="turbo_${mult}_svp_round2"
    local DST="turbo_${mult}_scscc2_svp"
    # Skip if already patched
    if [ -f "$DST/control" ] && grep -q "scs" "$DST/control"; then
        echo "  [skip] $DST setup (control already patched)"
        return 0
    fi
    rm -rf "$DST"; mkdir -p "$DST"
    for f in coord basis auxbasis mos control; do cp "$SRC/$f" "$DST/"; done
    python3 - "$DST/control" <<'PYEOF'
import sys
p = sys.argv[1]
t = open(p).read()
old = "$ricc2\n  adc(2)\n  maxiter 150"
new = "$ricc2\n  cc2\n  scs\n  maxiter 150"
if old not in t:
    raise SystemExit(f"ERROR: ricc2 block not found in {p}")
open(p, 'w').write(t.replace(old, new))
PYEOF
    rm -f "$DST/CC"* || true
    echo "  patched $DST/control: adc(2) -> cc2 + scs"
}

setup_scscc2_dir sing
setup_scscc2_dir trip

# === Stage 2: SCS-CC2 sing ===
SING_SCSCC2=turbo_sing_scscc2_svp
TRIP_SCSCC2=turbo_trip_scscc2_svp

cd "$SING_SCSCC2" || { echo "FATAL: $SING_SCSCC2 missing"; exit 1; }
run_ricc2_or_skip ricc2_scscc2_sing.out "SCS-CC2 Singlet"
cd ..

# === Stage 2: SCS-CC2 trip ===
if ! done_marker "$TRIP_SCSCC2/ricc2_scscc2_trip.out"; then
    cp "$SING_SCSCC2/mos" "$TRIP_SCSCC2/mos"
fi
cd "$TRIP_SCSCC2" || { echo "FATAL: $TRIP_SCSCC2 missing"; exit 1; }
run_ricc2_or_skip ricc2_scscc2_trip.out "SCS-CC2 Triplet"
cd ..

# === Auto-cleanup: delete Turbomole CC* intermediate scratch files ===
# Only runs if all 4 stages have "ended normally" / "all done" markers.
# Keeps: ricc2_*.out, ridft_*.out, control, basis, auxbasis, mos, coord, energy
echo "=== Auto-cleanup: removing Turbomole scratch intermediates ==="
all_done=true
for f in turbo_sing_svp_round2/ricc2_adc2_sing.out \
         turbo_trip_svp_round2/ricc2_adc2_trip.out \
         turbo_sing_scscc2_svp/ricc2_scscc2_sing.out \
         turbo_trip_scscc2_svp/ricc2_scscc2_trip.out; do
    if ! grep -q "ended normally\|ricc2 : all done" "$f" 2>/dev/null; then
        echo "  ABORT cleanup: $f not finished"
        all_done=false
        break
    fi
done
if [ "$all_done" = "true" ]; then
    BEFORE=$(du -sh . | awk '{print $1}')
    for d in turbo_sing_svp_round2 turbo_trip_svp_round2 turbo_sing_scscc2_svp turbo_trip_scscc2_svp; do
        find "$d" -type f \
            \( -name "CC*" -o -name "RE0*" -o -name "LE0*" \
               -o -name "*INTM*" -o -name "exstates" -o -name "restart.cc" \
               -o -name "tmp.*" -o -name "*.tmp" \) \
            -delete 2>/dev/null
    done
    AFTER=$(du -sh . | awk '{print $1}')
    echo "  cleanup OK: $BEFORE -> $AFTER"
fi

echo "=== Job finished cleanly ==="
echo "Date: $(date)"
