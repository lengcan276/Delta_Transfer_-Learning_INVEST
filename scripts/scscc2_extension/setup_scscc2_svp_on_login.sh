#!/usr/bin/env bash
# setup_scscc2_svp_on_login.sh — Run on ybsi LOGIN NODE (not via sbatch!)
#
# PURPOSE: SCS-CC2/def2-SVP extension input preparation for the n=13
# INVEST cohort (round 2). Creates control files for ADC(2)/def2-SVP
# (the SCS-CC2 patch is applied inside Stage 2 of run_scscc2_svp.slurm).
#
# This script is byte-for-byte aligned with setup_tzvp_on_login.sh except:
#   1. "def2-TZVP" -> "def2-SVP"  (one-electron + jbas + cbas basis)
#   2. "tzvp" -> "svp_round2"     (directory and function names)
#   3. BASEDIR -> scscc2_extension_n13
#   4. MOL accepts a CLI argument (default: Hz_DMAC1_NPh21_CF31 for sanity)
# All sed patterns and the $excitations / $ricc2 block are unchanged so
# that the resulting control files have identical byte layout to the
# historical TZVP run (modulo basis name), which keeps the slurm Stage 2
# patch ("$ricc2\n  adc(2)\n  maxiter 150" -> cc2 + scs) reliable.
#
# INPUT: xtbopt.xyz for ${MOL} (must be rsynced to ${BASEDIR}/${MOL}/ first)
# OUTPUT: turbo_sing_svp_round2/ + turbo_trip_svp_round2/ containing control
#         files with def2-SVP one-electron basis + def2-SVP auxiliary
#         (jbas + cbas). Excitations block identical to historical SVP batch.
# USAGE:
#   1. rsync ~/2026/results/scscc2_extension_n13/ to ybsi under
#      /public/home/ybsi/nudt_cleng/2026/orca_jobs/scscc2_extension_n13/
#   2. ssh to ybsi login node
#   3. bash setup_scscc2_svp_on_login.sh <MOLECULE_ID>
#   4. cd <MOLECULE_ID> ; sbatch run.slurm   (prepared from templates/)
set -e

source /public/home/ybsi/software/TURBOMOLE/Config_turbo_env
export TURBODIR=/public/home/ybsi/software/TURBOMOLE

BASEDIR=/public/home/ybsi/nudt_cleng/2026/orca_jobs/scscc2_extension_n13
MOL=${1:-Hz_DMAC1_NPh21_CF31}

setup_turbo_svp_dir() {
  local WORKDIR=$1
  local XYZFILE=$2
  local EXCTYPE=$3

  mkdir -p ${WORKDIR}
  cd ${WORKDIR}

  rm -f coord control basis mos alpha auxbasis energy gradient *.out

  # xyz -> coord
  ${TURBODIR}/scripts/x2t ${XYZFILE} > coord

  # define: HF/def2-SVP basis (one-electron) + def2-SVP auxiliary
  define << 'DEFINE_EOF'


a coord
*
no
b all def2-SVP
*
eht


*
DEFINE_EOF

  if [ ! -f control ]; then
    echo "  ERROR: define failed to create control file"
    return 1
  fi

  # Clean optimization blocks from control
  sed -i '/$optimize/,/basis      off/d' control
  sed -i '/$drvopt/,/nuclear polarizability/d' control
  sed -i '/$interconversion/,/maxiter=25/d' control
  sed -i '/$coordinateupdate/,/statistics    5/d' control
  sed -i '/$forceupdate/,/damping=0.0/d' control
  sed -i '/$forceinit/,/diag=default/d' control
  sed -i '/$energy/d' control
  sed -i '/$grad    file=gradient/d' control
  sed -i '/$forceapprox/d' control

  # SCF parameters (8000 MiB per_core is comfortable for SVP)
  sed -i 's|$maxcor.*|$maxcor    8000 MiB  per_core|' control
  sed -i 's|$scfiterlimit.*|$scfiterlimit      200|' control

  # Add jbas and cbas for each element at def2-SVP level
  for elem in b c f h n o s; do
    sed -i "/basis =${elem} def2-SVP/a\\   jbas  =${elem} def2-SVP\n   cbas  =${elem} def2-SVP" control
  done

  # Build excitations block (identical nexc/npre/nstart to historical SVP batch)
  if [ "$EXCTYPE" = "singlet" ]; then
    EXCBLOCK='$excitations\n  irrep=a  multiplicity=1  nexc=5  npre=15  nstart=30\n  spectrum  states=all'
  else
    EXCBLOCK='$excitations\n  irrep=a  multiplicity=3  nexc=3  npre=9  nstart=15'
  fi

  # Insert RI and ricc2 settings before $end — default is adc(2);
  # run_scscc2_svp.slurm Stage 2 will later clone turbo_*_svp_round2 to
  # turbo_*_scscc2_svp and patch "adc(2)" -> "cc2\n  scs".
  sed -i "s|\$end|\$rij\n\$ricore    8000\n\$denconv   1d-7\n\$ricc2\n  adc(2)\n  maxiter 150\n${EXCBLOCK}\n\$end|" control

  echo "  OK: $(grep -c '^\$' control) sections in control (def2-SVP)"
}

echo "============================================="
echo "SCS-CC2 extension (n=13): def2-SVP — ${MOL}"
echo "============================================="

MOLDIR=${BASEDIR}/${MOL}
XYZ=${MOLDIR}/xtbopt.xyz

if [ ! -f "$XYZ" ]; then
  echo "FATAL: ${XYZ} missing. rsync from local first."
  exit 1
fi

echo "  Singlet SVP..."
setup_turbo_svp_dir "${MOLDIR}/turbo_sing_svp_round2" "${XYZ}" "singlet"

echo "  Triplet SVP..."
setup_turbo_svp_dir "${MOLDIR}/turbo_trip_svp_round2" "${XYZ}" "triplet"

if [ -f "${MOLDIR}/turbo_sing_svp_round2/control" ] && [ -f "${MOLDIR}/turbo_trip_svp_round2/control" ]; then
  echo "  DONE"
else
  echo "  FAILED"
  exit 1
fi

echo ""
echo "Next: cd ${MOLDIR} ; sed s/PLACEHOLDER/${MOL}/ \$BASEDIR/templates/run_scscc2_svp.slurm > run.slurm ; sbatch run.slurm"
