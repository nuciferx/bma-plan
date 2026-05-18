# RUN_PHASE_I_C — Phase I-C: "ผังบริเวณ" 5th tab in Summary Widget

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `a490c1e`

## Goal

Add a 5th "ผังบริเวณ" tab to the Summary Widget that renders an in-app view of `collectSummaryData`
output — BCR / OSR / FAR / Permeable ratios + per-tag area breakdown + marker counts + front-setback
— with a Phase 1 footer note ("ไม่มีการพิจารณาผ่าน/ไม่ผ่านตามกฎหมาย"). Reuses `collectSummaryData`
(already exists from U2 sprint) so no new server logic is required.

Source: PHASE_INDEX.md row `I-C` (depends on I-B3 ✅).

## Scope — IN

- 5th tab `#tab-siteplan` added to Summary Widget tab bar (after Area / Floor / Site / Warnings).
- Tab content `#summary-siteplan`: renders `collectSummaryData()` inline — BCR/OSR/FAR/Permeable
  plain numbers, per-tag breakdown table, marker-count table, front-setback row.
- "Phase 1 footer note" at bottom: Thai text confirming facts-only, no legal verdict.
- `updateSiteplanTab()` function: called by existing `updateSummaryWidget()` when siteplan tab active.
- Tab visibility: always shown (not site-page-gated at tab level — user may navigate tabs freely).
- New E2E marker `PHASE_I_C_OK` with 10 sub-checks.

## Scope — OUT

- No new server endpoints (reuses `collectSummaryData` client-side aggregation from U2).
- No XLSX sheet addition in this sprint (I-C is in-app view only; additive XLSX deferred).
- No pass/fail verdict, no user-defined-limit comparison UI in this sprint.

## Implementation summary

### Functions added (`proto/ui.html`)

- `updateSiteplanTab()` — calls `collectSummaryData()`; renders ratio block (BCR/OSR/FAR/Permeable
  as `XX.X%`) + per-tag area table (tag label, area m², % of site) + marker-count rows + front-setback
  line + Phase 1 footer note. Called from `updateSummaryWidget()`.
- 5th tab button + `#summary-siteplan` content div added to Summary Widget DOM.

### Key design decisions

- Tab content computed entirely client-side from `collectSummaryData()` — same data as U2 XLSX export.
  This keeps the in-app view and the XLSX perfectly in sync without new server state.
- Phase 1 footer note is non-removable (hard-coded in the template) as a scope guardrail.
- Ratios are plain numbers (e.g. `BCR: 45.2%`). No colour-coded verdict band.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | 5th tab DOM; `updateSiteplanTab()` fn; hook in `updateSummaryWidget()` |
| `proto/e2e_ui_test.py` | NEW `_test_phase_i_c(page)` 10 sub-checks + marker `PHASE_I_C_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS GREEN
```

PHASE_I_C_OK: 10 sub-checks all PASS.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED (pure client rendering)
- `.bmaplan` schema — UNTOUCHED
- Phase 1 boundary — kept (facts only; Phase 1 footer note enforces scope)

## References

- PHASE_INDEX.md row `I-C`
- U2 sprint — `collectSummaryData()` + `/export-xlsx-summary` (client aggregation reused)
- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` — BCR/OSR/FAR/Permeable formula definitions
