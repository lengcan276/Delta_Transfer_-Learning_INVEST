# Patch D Step 2 — Source-label mislabel diagnosis + fix

## Classification: **LABEL_ONLY_MISREFERENCE**

## Diagnosis evidence

Pre-fix state of `scripts/99_emit_canonical.py` (lines 956–960):

```python
incon(
    "scs_cc2_extended_n13.rule_of_three_upper_bound",
    upstream_rule, "results/stats_n13.json",      # ← stale label
    rule_of_three_upper_bound, "recomputed from n_total in 99_emit_canonical.py",
)
```

Actual read site (lines 891–893):
```python
upstream_dir = RESULTS / "scscc2_extension_n13"
csv_path = upstream_dir / "cross_check_n13.csv"
stats_path = upstream_dir / "stats_n13.json"      # ← actual upstream
```

The string at line 958 is the **source-name label** passed to the
`incon()` helper. It is never used as a path to open or read the
file; it appears in the audit-time report only if a drift between
the upstream value and the recomputed value is detected.

The `incon()` for this key is currently DORMANT (upstream and
recomputed `rule_of_three_upper_bound` agree to floating-point
precision; no inconsistency record produced).

Confirmed: the legacy root path `results/stats_n13.json` is NOT
opened or read anywhere in the canonical pipeline. The label is
purely a stale display string.

## Fix applied (label-only)

```python
incon(
    "scs_cc2_extended_n13.rule_of_three_upper_bound",
    upstream_rule, "results/scscc2_extension_n13/stats_n13.json",  # ← fixed
    rule_of_three_upper_bound, "recomputed from n_total in 99_emit_canonical.py",
)
```

One-line string change. No read logic, no write logic, no numeric
logic, no schema change.

## Post-fix validation

| step | exitcode | result |
|---|---|---|
| `python3 scripts/99_emit_canonical.py` | **0** | regeneration succeeded |
| `python3 scripts/audit_numbers.py` | **0** | unresolved = **0**, Major = **0 / 7** |

Both validation targets remain met after the fix. No restore from
backup needed.

## Backups (kept for audit trail)

- `audit/revision_patchD_before_source_label_99_emit_canonical.py`
- `audit/revision_patchD_before_source_label_canonical_metrics.json`

## Verdict

LABEL_ONLY_MISREFERENCE fixed. Pipeline validation unchanged.
Proceed to Step 3.
