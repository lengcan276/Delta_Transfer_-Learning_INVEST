# Data availability

**Canonical repository:**
[https://github.com/lengcan276/INVEST-n13](https://github.com/lengcan276/INVEST-n13)

This statement describes what is included in the release directly,
what is held in an external archive, and what is honestly disclosed
as pending.

## Included in this repository

- **Processed validation tables** — the post-Hartree–Fock
  electronic-structure results in machine-readable form:
  - `results/validated_candidates_master.csv` — 35-molecule master
    table, with ADC(2)/def2-SVP `DEST_adc2_eV`,
    SCS-CC2/def2-SVP `DEST_scscc2_eV`, fosc, and classification
    columns
  - `results/scscc2_extension_n13/cross_check_n13.csv` —
    13-row SCS-CC2 cross-check table used as the upstream input
    for the canonical pipeline
  - `results/scscc2_extension_n13/stats_n13.json` — screened-cohort
    sign-retention statistics (rule-of-three primary;
    Clopper-Pearson kept as transparency-only)
- **Canonical metrics file** — `results/canonical_metrics.json`,
  the single numerical-leaf source of truth referenced by the
  manuscript; regenerated from upstream files by
  `scripts/99_emit_canonical.py`
- **Figure caption metadata** — `figures/caption_data/*.json`,
  per-figure numeric metadata used to verify Figures 0 through 4
  against `canonical_metrics.json`
- **Raw-output provenance manifest** —
  `audit/revision_patchC_raw_provenance_manifest.tsv` and the
  companion markdown notes, providing sha256 + size + banner-
  derived basis/method/hostname/scheduler diagnostics for each
  raw output

## External archive (recommended placement: GitHub Release)

- **SCS-CC2 n=13 raw-output archive** — 26 files
  (13 singlet + 13 triplet) of `ricc2_scscc2_*.out` Turbomole
  outputs, ~1.16 MB total uncompressed. The release plan
  (`audit/revision_patchC_raw_archive_release_plan.md`) packages
  these into a single tarball
  `INVEST_n13_scscc2_raw_provenance.tar.gz` to be published as a
  GitHub Release asset at
  [https://github.com/lengcan276/INVEST-n13/releases](https://github.com/lengcan276/INVEST-n13/releases)
  (Zenodo deposit optional, for DOI citation).

  Each file in the tarball has a sha256 entry in the provenance
  manifest; the tarball itself will carry a top-level sha256
  recorded in the manifest's accompanying notes once the user
  uploads it.

## Honest disclosure: ybsi-pending ADC(2) raw outputs

- **20 / 35** ADC(2)/def2-SVP raw outputs are locally verified
  (12 verified to the precision of the reported digits; 8 verified
  to within sub-meV rounding-level differences attributable
  entirely to processed-table rounding to 3 decimals in eV).
- **15 / 35** ADC(2) raw outputs were computed on the `ybsi`
  compute cluster and **were not rsynced into the local audit
  snapshot at the time of this release.** They will be added to
  the external raw-archive tarball in a subsequent point release.

The absence of these 15 raw outputs does not affect any manuscript
numeric claim: the post-processed values in
`results/validated_candidates_master.csv` are the authoritative
source, and the SCS-CC2 sign-retention result (the headline 13/13
within-screen agreement) is established entirely from the n=13
SCS-CC2 cohort that **is** fully raw-verified locally.

## Reproducibility

The canonical pipeline is documented in `README.md` under
"Reproducibility chain". A fresh checkout can regenerate
`results/canonical_metrics.json` from the upstream files in three
commands; `scripts/audit_numbers.py` then verifies that every
non-trivial number in the manuscript resolves to a canonical
source (target: `unresolved = 0`, `Major checks = 0 / 7`).

## Contact

For questions about data and code, or to request raw outputs
not yet in the release tarball, please open an issue at
[https://github.com/lengcan276/INVEST-n13/issues](https://github.com/lengcan276/INVEST-n13/issues)
or contact the corresponding author.
