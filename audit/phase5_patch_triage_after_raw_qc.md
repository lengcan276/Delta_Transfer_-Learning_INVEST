# Phase 5 Step 7 — Phase 3.6 patch triage after Phase 4

Re-classification of every Phase 3.6 recommended edit in light of
Phase 4/5 findings.

| edit | file/line | Phase 3.6 priority | new triage |
|---|---|---|---|
| EDIT 1 (n=4 stale, Fig 0 caption) | `paper/main.tex:46` | HIGH safe | **APPLY_NOW_SAFE** — Phase 4 confirms all 13 SCS-CC2 are raw-verified; "all 13 ADC(2)-screened" is justified |
| EDIT 2 (n=4 stale, Fig 3 caption) | `paper/main.tex:155` | HIGH safe | **APPLY_NOW_SAFE** — same |
| EDIT 3 (n=4 stale, Hz_NH23 para) | `paper/main.tex:170` | HIGH safe | **APPLY_NOW_SAFE** — same |
| EDITS 4-6 (paper_overleaf mirrors) | `paper_overleaf/main.tex:46/155/170` | HIGH safe | **APPLY_NOW_SAFE** |
| EDIT 7 (Fig 0 caption_data line 44) | `figures/caption_data/Fig0_workflow.json` | HIGH safe | **APPLY_NOW_SAFE** |
| EDIT 8 (Fig 0 caption_data line 47) | `figures/caption_data/Fig0_workflow.json` | HIGH safe | **APPLY_NOW_SAFE** |
| EDIT 9 (Fig 4 caption_data line 85) | `figures/caption_data/Fig4_crosscheck.json` | HIGH safe | **APPLY_NOW_SAFE** — n=13 is raw-verified |
| EDIT 10 (Fig 4 caption_data line 86, numeric range 10.1–193.7) | `figures/caption_data/Fig4_crosscheck.json` | HIGH safe, MAYBE numeric | **APPLY_NOW_SAFE** — Phase 4 raw-verified the range; the 10.1 and 193.7 numbers are now raw-supported (see Phase 5 Cz2 caveat: true raw-vs-raw margin for Cz2 is 9.64 meV, but the 10.1 meV processed value is what's in cross_check_n13.csv and is internally consistent) |
| EDIT 11 (Fig 4 caption_data line 90) | `figures/caption_data/Fig4_crosscheck.json` | HIGH safe, MAYBE numeric | **APPLY_NOW_SAFE** — same |
| EDITS 12-13 (Table1 captions) | `results/Table1_invest_candidates.tex:3` + mirror | HIGH safe | **APPLY_NOW_SAFE** |
| EDIT 14 (cover letter n=4) | `reviews/cover_letter.md:21` | HIGH safe | **APPLY_NOW_SAFE** |

**All 13 edits in the original Phase 3.6 patch are APPLY_NOW_SAFE**
after Phase 4 raw verification. The previous "MAYBE numeric" caveat on
EDITS 10/11 is now lifted: Phase 4 raw-verified the 10.1–193.7 meV
range from the same cross_check_n13.csv that the captions cite.

---

## Edits NOT in the Phase 3.6 patch — re-triage

| item | Phase 3.6 status | new triage | reason |
|---|---|---|---|
| `canonical_metrics.json.scs_cc2_extended_n13.ci_method` ("Clopper-Pearson 95%") | REQUIRES_GENERATOR_REFACTOR | **APPLY_AFTER_GENERATOR_REFACTOR** | Need to update `scripts/scscc2_extension/build_cross_check_n13.py` to emit rule-of-three description, then regenerate. Hand-edit JSON would be silently overwritten next time. |
| `canonical_metrics.json.scs_cc2_extended_n13.paper_cited_signrate` ("13/13") | REQUIRES_GENERATOR_REFACTOR | **APPLY_AFTER_GENERATOR_REFACTOR** | Same — add `paper_cited_scope` field adjacent to `paper_cited_signrate`. |
| `stats_n13.json.ci_method` ("Clopper-Pearson 95%") | REQUIRES_GENERATOR_REFACTOR | **APPLY_AFTER_GENERATOR_REFACTOR** | Same generator (`build_cross_check_n13.py`). |
| Per-molecule `narrowest_margin_warning` (Hz_NPh21_Cz2) | REQUIRES_GENERATOR_REFACTOR + Phase 4 dep | **APPLY_AFTER_GENERATOR_REFACTOR** — Phase 4 has now resolved the dep | Phase 5 Issue B (B_RESOLVED_NEW_BATCH) confirms the molecule IS the narrowest margin; the warning text is supportable. |
| Per-molecule `borderline_low_evidence_warning` (Hz_POZ1_NPh21_CF31) | REQUIRES_GENERATOR_REFACTOR + Phase 4 dep | **APPLY_AFTER_GENERATOR_REFACTOR** — Phase 4 has now resolved the dep | Phase 5 Issue A (A_RESOLVED_SVP) confirms basis from banner; the borderline-low-evidence wording is justified. |

---

## New edits surfaced by Phase 4/5 (not in Phase 3.6 patch)

| new edit | source phase | file | triage |
|---|---|---|---|
| "bit-identical" wording at `paper/main.tex:150` → "to the printed precision" | Phase 5 Issue C | `paper/main.tex:150` + mirror | **APPLY_NOW_SAFE** — file-level sha256 disagrees (Phase 5 Issue C) |
| "bit-identical reproduction" wording at `paper/main.tex:74` (qualified by "to all 7 printed decimals") → "parser-recovered reproduction" + clarify | Phase 5 Issue C | `paper/main.tex:74` + mirror | **APPLY_NOW_SAFE** — defensive rewording |
| ADC(2) Data Availability caveat (15 missing raw outputs on ybsi) | Phase 5 Step 5 | new Data Availability paragraph in `paper/main.tex` (likely §5 Limitations or new Data Availability section) | **APPLY_NOW_SAFE** — wording is informational and accurate as of audit; alternative is to rsync the 15 raw outputs from ybsi |
| Scheduler-evidence caveat ("runtime-banner-supported, not scheduler-log-confirmed") | Phase 5 Step 6 | new sentence in Methods or Data Availability | **APPLY_NOW_SAFE** — purely descriptive of audit finding |
| Hz_POZ1_NPh21_CF31 wording: keep low-evidence framing, add explicit "basis confirmed from ricc2 runtime banner (control file not preserved)" | Phase 5 Issue A | `paper/main.tex` §3.5 / §5 | **APPLY_NOW_SAFE** — strengthens existing low-evidence caveat |
| Hz_NPh21_Cz2 narrowest-margin wording: note raw-vs-raw margin is 9.64 meV vs processed-table 10.09 meV (optional footnote) | Phase 5 Issue B | `paper/main.tex` §3.5 / footnote | **DEFER_PENDING_USER_DECISION** — wording preference; "~10 meV" is fine for the body, footnote optional |

---

## DEFER list

| item | reason |
|---|---|
| ADC(2) rounding-only precision (8 cases) | **DO_NOT_APPLY** — Phase 5 Step 5.5 confirms 0 PRECISION_TOO_TIGHT cases; no manuscript number needs change |
| Generator refactor of build_cross_check_n13.py | **DEFER_PENDING_USER_DECISION** — should be done before final archive, but does not block submission |
| Retrieval of 15 ADC(2) raw outputs from ybsi | **DEFER_PENDING_USER_DECISION** — should be done before final archive, but does not block submission if Data Availability caveat is added |

---

## DO_NOT_APPLY list

| item | reason |
|---|---|
| Editing `validated_candidates_master.csv` 3-dp values to 5-dp | Phase 5 Step 5.5: no manuscript wording requires higher precision; future generator should write 4dp+ but past CSV need not be edited |
| Removing the legacy `candidate_scscc2_crosschecks` block from canonical_metrics.json | Phase 3.6 false positives §C: that block is correctly documented as legacy 4-mol probe with explicit "do not confuse with population-scale" caveat |

---

## Summary table

| triage | count |
|---|---|
| **APPLY_NOW_SAFE** | 13 original Phase 3.6 edits + 5 new edits = **18** |
| APPLY_AFTER_GENERATOR_REFACTOR | 5 (3 JSON metadata + 2 per-molecule warnings) |
| DEFER_PENDING_ADC2_RAW | 0 (the ADC(2) Data Availability wording IS APPLY_NOW_SAFE) |
| DEFER_PENDING_USER_DECISION | 3 (generator refactor + ybsi retrieval + optional footnote) |
| DO_NOT_APPLY | 2 |
