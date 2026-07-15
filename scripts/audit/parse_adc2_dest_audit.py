#!/usr/bin/env python3
"""
Phase 4 — independent audit parser for ADC(2) ricc2 outputs.

Method-banner priority enforced:
- Requires "ADC(2)     - Algebraic Diagrammatic Construction" in the
  wavefunction-models block.
- Rejects if "Spin-Component Scaling will be applied" appears (that would
  mean SCS-CC2, not ADC(2)).
- Requires normal termination ("ricc2 ended normally" or
  "ricc2 : all done") before trusting any number.
- Extracts S1 from singlet output, T1 from triplet output, using the
  ^\\s*Energy:\\s+...\\s+H\\s+(<eV>)\\s+eV pattern.

Usage:
    python3 parse_adc2_dest_audit.py SINGLET_RICC2.out TRIPLET_RICC2.out

Returns dict with keys: method, basis_in_output (None — basis lives in
control), E_S1_eV, E_T1_eV, dE_ST_eV, normal_termination_singlet,
normal_termination_triplet, raised_value_warnings.
"""
import re
import sys
from pathlib import Path

ENERGY_RE = re.compile(
    r'^\s*Energy:\s+[-+]?\d+\.\d+\s+H\s+([-+]?\d+\.\d+)\s+eV\s+'
)
ADC2_DECL_RE = re.compile(
    r"ADC\(2\)\s+-\s+Algebraic Diagrammatic Construction",
    re.IGNORECASE,
)
CC2_DECL_RE = re.compile(
    r"CC2\s+-\s+Approximate CC Singles and Doubles",
    re.IGNORECASE,
)
SCS_BANNER_RE = re.compile(
    r"Spin-Component Scaling will be applied",
    re.IGNORECASE,
)
NORMAL_TERM_RE = re.compile(
    r"ricc2 ended normally|ricc2\s*:\s*all done",
    re.IGNORECASE,
)
HOSTNAME_BANNER_RE = re.compile(
    r"ricc2\s*\(\s*(\S+?)\s*\)\s*:\s*TURBOMOLE",
)


def parse_one(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{p}")
    text = p.read_text()

    # method banner enforcement
    has_adc2 = bool(ADC2_DECL_RE.search(text))
    has_cc2 = bool(CC2_DECL_RE.search(text))
    has_scs = bool(SCS_BANNER_RE.search(text))

    if has_scs:
        raise ValueError(
            f"{p}: SCS banner present — this is SCS-CC2, not ADC(2). "
            f"Refusing to parse with ADC(2) parser."
        )
    if has_cc2 and not has_adc2:
        raise ValueError(
            f"{p}: model declared as CC2 (not ADC(2)). Refusing to parse "
            f"with ADC(2) parser."
        )
    if not has_adc2:
        raise ValueError(
            f"{p}: no ADC(2) wavefunction-model declaration found."
        )

    # normal termination
    if not NORMAL_TERM_RE.search(text):
        raise ValueError(
            f"{p}: no normal termination marker ('ricc2 ended normally' "
            f"or 'ricc2 : all done')."
        )

    # first Energy: line
    energy_eV = None
    for line in text.splitlines():
        m = ENERGY_RE.match(line)
        if m:
            energy_eV = float(m.group(1))
            break
    if energy_eV is None:
        raise ValueError(f"{p}: no 'Energy:' excited-state line found.")

    # hostname inference
    m_host = HOSTNAME_BANNER_RE.search(text)
    hostname = m_host.group(1) if m_host else None

    return {
        "path": str(p),
        "method_banner": "ADC(2)",
        "scs_present": False,
        "normal_termination": True,
        "first_excitation_eV": energy_eV,
        "hostname_in_output": hostname,
    }


def compute_dest(sing_path, trip_path):
    s = parse_one(sing_path)
    t = parse_one(trip_path)
    return {
        "method": "ADC(2)",
        "sing": s,
        "trip": t,
        "E_S1_eV": s["first_excitation_eV"],
        "E_T1_eV": t["first_excitation_eV"],
        "dE_ST_eV": s["first_excitation_eV"] - t["first_excitation_eV"],
    }


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    r = compute_dest(sys.argv[1], sys.argv[2])
    print(f"method   = {r['method']}")
    print(f"S1 host  = {r['sing']['hostname_in_output']}")
    print(f"T1 host  = {r['trip']['hostname_in_output']}")
    print(f"E(S1)    = {r['E_S1_eV']:.5f} eV")
    print(f"E(T1)    = {r['E_T1_eV']:.5f} eV")
    print(f"ΔE_ST    = {r['dE_ST_eV']:+.5f} eV ({r['dE_ST_eV']*1000:+.2f} meV)")


if __name__ == "__main__":
    main()
