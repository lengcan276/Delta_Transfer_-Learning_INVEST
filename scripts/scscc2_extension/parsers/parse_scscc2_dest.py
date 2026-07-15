#!/usr/bin/env python3
"""
parse_scscc2_dest.py — parse SCS-CC2 ΔE_ST from Turbomole ricc2 output.

The Turbomole ricc2 program with `cc2 + scs` writes excited-state energies in
"Energy:" blocks of the form:

       Energy:     0.1275169 H      3.46991 eV    27986.716 cm-1

These are the FINAL SCS-CC2 excitation energies (not CCS guesses, not Kohn-Sham
orbital energies). The first such line in a singlet ricc2.out is S1; in a
triplet ricc2.out it is T1.

Usage:
    python3 parse_scscc2_dest.py --singlet <sing.out> --triplet <trip.out>
    python3 parse_scscc2_dest.py -s <sing.out> -t <trip.out>
    python3 parse_scscc2_dest.py <sing.out> <trip.out>      # positional (legacy)
    python3 parse_scscc2_dest.py --selftest

Output: ΔE_ST = E(S1) - E(T1) in eV; negative = INVEST.
"""
import argparse
import re
import sys
from pathlib import Path


ENERGY_RE = re.compile(
    r'^\s*Energy:\s+[-+]?\d+\.\d+\s+H\s+([-+]?\d+\.\d+)\s+eV\s+'
)


def parse_first_excitation_eV(ricc2_out_path):
    """Return the first 'Energy: ... eV' value as float (S1 if singlet, T1 if triplet).

    Precondition: ricc2 must have completed cleanly. Otherwise an unconverged
    'Energy:' value would be silently returned and corrupt the ΔE_ST result.
    """
    p = Path(ricc2_out_path)
    if not p.exists():
        raise FileNotFoundError(f"ricc2 output not found: {p}")
    text = p.read_text()
    if 'ricc2 : all done' not in text and 'ricc2 ended normally' not in text:
        raise ValueError(
            f"ricc2 did not finish cleanly (no 'all done' / 'ended normally' marker): {p}"
        )
    for line in text.splitlines():
        m = ENERGY_RE.match(line)
        if m:
            return float(m.group(1))
    raise ValueError(f"No 'Energy:' excited-state line found in {p}")


def compute_dest(sing_path, trip_path):
    """Return dict with E_S1, E_T1, dE_ST in eV."""
    e_s1 = parse_first_excitation_eV(sing_path)
    e_t1 = parse_first_excitation_eV(trip_path)
    return {"E_S1_eV": e_s1, "E_T1_eV": e_t1, "dE_ST_eV": e_s1 - e_t1}


def selftest():
    """Reproduce the historical Hz_DMAC1_NPh21_CF31 reference value."""
    base = Path(__file__).parent.parent.parent / "adc2_batch2_raw" / "Hz_DMAC1_NPh21_CF31"
    sing = base / "turbo_sing_scscc2" / "ricc2_scscc2_sing.out"
    trip = base / "turbo_trip_scscc2" / "ricc2_scscc2_trip.out"
    expected = -0.22033  # eV, from method_consistency_table.csv col SCSCC2_SVP_eV

    print(f"Self-test on Hz_DMAC1_NPh21_CF31 (def2-SVP)")
    print(f"  Singlet: {sing}")
    print(f"  Triplet: {trip}")

    result = compute_dest(sing, trip)
    diff = result["dE_ST_eV"] - expected

    print(f"  E(S1)        = {result['E_S1_eV']:.5f} eV")
    print(f"  E(T1)        = {result['E_T1_eV']:.5f} eV")
    print(f"  ΔE_ST parsed = {result['dE_ST_eV']:+.5f} eV")
    print(f"  ΔE_ST ref    = {expected:+.5f} eV (method_consistency_table.csv)")
    print(f"  difference   = {diff*1000:+.3f} meV")

    tol_eV = 0.0001  # 0.1 meV — purely a parser-roundoff tolerance
    if abs(diff) <= tol_eV:
        print(f"  PASS — parser reproduces reference within {tol_eV*1000:.1f} meV")
        return 0
    else:
        print(f"  FAIL — parser differs from reference by more than {tol_eV*1000:.1f} meV")
        return 1


def main():
    # --selftest is a special mode (no other args)
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(selftest())

    parser = argparse.ArgumentParser(
        description="Parse SCS-CC2 ΔE_ST from Turbomole ricc2 outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-s", "--singlet", help="Path to singlet ricc2 output")
    parser.add_argument("-t", "--triplet", help="Path to triplet ricc2 output")
    parser.add_argument(
        "positional", nargs="*",
        help="Legacy positional form: <singlet.out> <triplet.out>",
    )
    args = parser.parse_args()

    # Resolve singlet/triplet from either flag form or positional form
    if args.singlet and args.triplet:
        sing, trip = args.singlet, args.triplet
    elif len(args.positional) == 2:
        sing, trip = args.positional[0], args.positional[1]
    else:
        parser.error(
            "Specify both --singlet/-s and --triplet/-t, "
            "OR pass two positional paths."
        )

    result = compute_dest(sing, trip)
    print(f"E(S1) = {result['E_S1_eV']:.5f} eV")
    print(f"E(T1) = {result['E_T1_eV']:.5f} eV")
    print(f"ΔE_ST = {result['dE_ST_eV']:+.5f} eV  ({result['dE_ST_eV']*1000:+.2f} meV)")
    print("INVEST candidate" if result['dE_ST_eV'] < 0 else "positive-gap molecule")


if __name__ == "__main__":
    main()
