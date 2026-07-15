#!/usr/bin/env python3
"""
Phase 4 — independent audit parser for SCS-CC2 ricc2 outputs.

Stricter than the project's parser. Method-banner priority enforced:
- Requires "CC2 - Approximate CC Singles and Doubles" wavefunction-model
  declaration.
- Requires "Spin-Component Scaling will be applied" runtime banner.
- Reads scaling factors (C_os, C_ss) if present.
- Rejects if "ADC(2) - Algebraic Diagrammatic Construction" appears.
- Requires normal termination.

Usage:
    python3 parse_scscc2_dest_audit.py SINGLET_RICC2.out TRIPLET_RICC2.out
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
SCS_FACTORS_RE = re.compile(
    r"C_os\s*=\s*([\d.]+)\s+C_ss\s*=\s*([\d.]+)",
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

    has_adc2 = bool(ADC2_DECL_RE.search(text))
    has_cc2 = bool(CC2_DECL_RE.search(text))
    has_scs = bool(SCS_BANNER_RE.search(text))

    if has_adc2 and not has_cc2:
        raise ValueError(
            f"{p}: model declared as ADC(2) (not CC2). Refusing to parse "
            f"with SCS-CC2 parser."
        )
    if not has_cc2:
        raise ValueError(
            f"{p}: no CC2 wavefunction-model declaration found."
        )
    if not has_scs:
        raise ValueError(
            f"{p}: CC2 declaration found but no 'Spin-Component Scaling "
            f"will be applied' banner — this is plain CC2, not SCS-CC2."
        )

    if not NORMAL_TERM_RE.search(text):
        raise ValueError(f"{p}: no normal termination marker.")

    # parse SCS factors
    m_fac = SCS_FACTORS_RE.search(text)
    c_os = float(m_fac.group(1)) if m_fac else None
    c_ss = float(m_fac.group(2)) if m_fac else None

    # first Energy: line
    energy_eV = None
    for line in text.splitlines():
        m = ENERGY_RE.match(line)
        if m:
            energy_eV = float(m.group(1))
            break
    if energy_eV is None:
        raise ValueError(f"{p}: no 'Energy:' excited-state line found.")

    m_host = HOSTNAME_BANNER_RE.search(text)
    hostname = m_host.group(1) if m_host else None

    return {
        "path": str(p),
        "method_banner": "SCS-CC2",
        "scs_c_os": c_os,
        "scs_c_ss": c_ss,
        "normal_termination": True,
        "first_excitation_eV": energy_eV,
        "hostname_in_output": hostname,
    }


def compute_dest(sing_path, trip_path):
    s = parse_one(sing_path)
    t = parse_one(trip_path)
    return {
        "method": "SCS-CC2",
        "scs_c_os": s["scs_c_os"],
        "scs_c_ss": s["scs_c_ss"],
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
    print(f"method   = {r['method']} (C_os={r['scs_c_os']}, C_ss={r['scs_c_ss']})")
    print(f"S1 host  = {r['sing']['hostname_in_output']}")
    print(f"T1 host  = {r['trip']['hostname_in_output']}")
    print(f"E(S1)    = {r['E_S1_eV']:.5f} eV")
    print(f"E(T1)    = {r['E_T1_eV']:.5f} eV")
    print(f"ΔE_ST    = {r['dE_ST_eV']:+.5f} eV ({r['dE_ST_eV']*1000:+.2f} meV)")


if __name__ == "__main__":
    main()
