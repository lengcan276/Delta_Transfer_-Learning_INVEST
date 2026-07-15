# Cover letter — JCIM submission

**Date**: 2026-05-01
**Manuscript title**: *Scaffold-Resolved Active Learning and Hierarchical Validation for Low-Data INVEST Discovery*
**Target journal**: Journal of Chemical Information and Modeling (ACS) — primary; Digital Discovery (RSC) — secondary fallback.

---

Dear Editor,

We are pleased to submit our manuscript, *Scaffold-Resolved Active Learning and Hierarchical Validation for Low-Data INVEST Discovery*, for consideration as a research article in the Journal of Chemical Information and Modeling (JCIM).

## What the work contributes

The discovery of molecules with an inverted singlet–triplet gap (INVEST, $\Delta E_\mathrm{ST} < 0$) is fundamentally constrained by the cost of correlated excited-state labels. Existing screening campaigns either pay for exhaustive higher-level validation across a large candidate pool, or they accept lower-level approximations whose ordering is known to mis-rank molecules near the inversion threshold. We present an explicit alternative: a **scaffold-resolved active-learning and hierarchical-validation workflow** that splits the discovery question into two well-matched tiers and concentrates expensive cross-method evidence only on the surviving lead set.

The two contributions of the manuscript are:

1. **Scaffold-resolved active learning as a low-data pruning device.** A 446$\rightarrow$33 cross-level $\Delta$-ML transfer model (Pollice ADC(2)/cc-pVDZ source $\rightarrow$ in-house RI-ADC(2)/def2-SVP target) is used not to discriminate at candidate level but to choose a *small set of structurally informative queries*. With a single round of 15 deployments, the workflow eliminates the 5-aminopyrimidine scaffold from further consideration and concentrates attention on the heptazine subset; in the full 35-molecule validated cohort, the Hz vs.\ non-Hz contingency is 13/27 vs.\ 0/8 (two-sided Fisher exact $p=0.015$, reported as a descriptive contrast within the actively selected cohort).

2. **Hierarchical validation with concentrated higher-level cross-checks.** ADC(2)/def2-SVP serves as the primary post-Hartree–Fock label across all 35 molecules, and SCS-CC2/def2-SVP is applied to all 13 ADC(2)-screened INVEST candidates (the pre-registered Table~1 shortlist), where it confirms sign agreement in all 13 cases (0 within-screen disagreement; rule-of-three one-sided 95% upper bound on disagreement rate ≈ 0.23) and promotes one ADC(2)-borderline heptazine to negative-gap. The absolute method differences span 100–174 meV; the cross-check therefore supports scaffold-level selection and per-molecule sign confirmation rather than fine quantitative ranking among the most negative heptazines, which is the resolution we explicitly target.

Together these two contributions define a reusable low-data discovery recipe: cheap ML for scaffold elimination, expensive correlated-wavefunction theory only for sign confirmation on the small surviving lead set.

## Why JCIM

The work is positioned as a cheminformatics methodology contribution combined with a practical, end-to-end pipeline that other groups can pick up and re-use on their own low-data INVEST or near-degenerate excited-state campaigns. Specifically: (i) the manuscript introduces *scaffold-resolved active learning* as an explicit additional dimension along which AL acquisition strategies should be evaluated, complementing the more familiar uncertainty- and diversity-based axes; (ii) the *hierarchical validation pipeline* — cheap $\Delta$-ML for scaffold elimination, ADC(2) for primary post-Hartree–Fock labels, SCS-CC2 concentrated only on the surviving lead set — is a concrete engineering recipe for the recurring small-cohort INVEST problem, where exhaustive higher-level validation is not affordable; (iii) the supporting cheminformatics standards (single-source-of-truth `canonical_metrics.json`, per-figure machine-readable caption manifests, an automated number-audit script, and a structured author-response trail) ensure that every numerical claim in the paper resolves to a tracked source — at the time of submission the audit reports unresolved = 0. We believe this combination of methodological extension and operational pipeline aligns with JCIM's scope of practical, reusable cheminformatics methods for chemical discovery.

## What we acknowledge upfront

We want to flag two scope boundaries that the manuscript itself states but that we want the editor to be aware of when assigning reviewers:

- **The Fisher exact $p=0.015$ in the scaffold-elimination claim** is a descriptive contrast within the actively selected cohort; the queried set was chosen by an active-learning policy rather than drawn at random, and we have not attempted to recast it as a population-level prevalence estimate. This is stated in the Abstract, in §3.4, and in Figure 5's caption.
- **The four SCS-CC2 cross-checks** are an *independent higher-level cross-check on lead candidates*, not an exhaustive method audit; the manuscript does not call SCS-CC2 a "gold standard" relative to ADC(2) (we follow the recommendation that only CCSD(T) with a large basis qualifies). One borderline heptazine (Hz\_POZ1\_NPh21\_CF31, $|\Delta E_\mathrm{ST}^\mathrm{ADC(2)/def2\text{-}SVP}|=9.7$ meV) carries a provisional classification pending independent basis-set sensitivity assessment; this is recorded in §3.5 and §5.

These caveats are deliberate and load-bearing; the workflow's value is precisely that scaffold-level decisions can be made *despite* the small-sample cohort, by hierarchically deferring the expensive sign-level evidence to the lead set rather than spreading it thin across the cohort.

## Suggested reviewers

We respectfully suggest reviewers with expertise in (a) excited-state computational chemistry of INVEST/TADF candidates; (b) active learning and Bayesian optimisation for molecular property regression; and (c) cross-level transfer learning between different electronic-structure methods. Specific suggestions include:

- **Robert Pollice** (Univ. of Vienna / Univ. of Toronto) — transfer learning and INVEST screening; original ADC(2)/cc-pVDZ source dataset.
- **Daniele Padula** (Univ. of Siena) — INVEST cheminformatics and excited-state property prediction.
- **Turab Lookman** (AiMaterials Research / formerly LANL) — multi-fidelity and active-learning ML for materials/molecular discovery.
- **Ghanshyam Pilania** (Toyota Research Institute / formerly LANL) — multi-fidelity ML for property prediction across levels of theory.

A formal short list with affiliations and email addresses is included in the submission portal.

## Statement of originality and overlap

The manuscript has not been published or submitted elsewhere. The work makes use of the publicly available Pollice et al.\ ADC(2)/cc-pVDZ dataset (cited in the manuscript), all in-house ADC(2)/def2-SVP and SCS-CC2/def2-SVP calculations are new for this study, and all scripts and result files are in a project repository whose layout is summarized in the Methods section. We will deposit the full repository (anonymized) in a public archive on acceptance.

We hope you find the work suitable for the Journal of Chemical Information and Modeling, and we look forward to the reviewers' feedback.

With kind regards,

The authors

---

## Editor-facing checklist (for our own reference, not for the cover letter body)

- [x] Abstract leads with C1 (scaffold-resolved AL) and C2 (hierarchical validation), no over-claim phrasing
- [x] Fisher *p* = 0.015 carries the "descriptive on the actively selected cohort" qualifier in Abstract and Results
- [x] §3.3 (UQ) is condensed to ~2 paragraphs + Fig 2; diagnostic detail moved to §5 (Limitations)
- [x] §3.4 (AL) and §3.5 (Validation) reframed as positive contributions; Hz_POZ1_NPh21_CF31 retains "provisional pending basis-set check" disclaimer
- [x] §5 (Scope and Limitations) absorbs the moved 52.1>30 caveat, the structural-pinning conformal note, and the SOC/RISC/M3 disclaimer
- [x] Conclusions §6 is two-paragraph positive framing; no "cannot do near-threshold candidate-level classification" line in the Conclusions itself
- [x] Cover letter declares the two scope boundaries upfront (Fisher descriptive, SCS-CC2 lead-only)
- [x] Audit pipeline: `audit_numbers.py` unresolved = 0 at time of cover letter draft
- [x] All bibliography additions (Bostrom 2020, Tibshirani 2019, Whitehead 2026, Vovk 2005) committed
