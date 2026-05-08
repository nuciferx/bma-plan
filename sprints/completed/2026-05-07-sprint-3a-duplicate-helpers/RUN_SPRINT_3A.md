# RUN_SPRINT_3A.md — BMA-Plan Sprint 3A Cleanup Duplicate Helpers

## Goal

Clean up duplicate legacy helper declarations in `proto/ui.html` without changing current behavior.

This sprint is a cleanup-only sprint.

## Background

Previous sprint passed:
- automated tests passed
- manual UI picker test passed
- overlapping picker lifecycle was fixed
- layer lock remained working
- properties panel worked
- export audit sheets worked

But `FINAL_REPORT_FOR_CHATGPT.md` reported remaining technical debt:

- `proto/ui.html` still contains duplicate legacy declarations for:
  - `buildRows`
  - `collectAreas`
  - `phase1Warnings`

Newer definitions currently override older ones and tests pass, but this is risky because future agents may edit the wrong declaration.

## Required Reading

Read these files first:

1. `AGENTS.md`
2. latest entry in `log.md`
3. `FINAL_REPORT_FOR_CHATGPT.md`
4. `PATCH_SUMMARY.md`
5. `TEST_RESULT.md`
6. `UI_MANUAL_TEST.md`
7. `proto/ui.html`
8. `proto/e2e_ui_test.py`

## Scope

Do only this:

1. Inspect `proto/ui.html`.
2. Identify duplicate legacy declarations for:
   - `buildRows`
   - `collectAreas`
   - `phase1Warnings`
3. Keep only the active/current definitions used by report/export/QA behavior.
4. Remove or rename obsolete duplicate definitions only if safe.
5. Preserve behavior exactly.
6. Add or adjust focused regression checks only if needed.
7. Update `log.md`.

## Forbidden

Do not add:
- legal rules
- OCR
- AI checker
- Rule Engine
- FAR / OSR / setback logic
- K.1 generation
- Project PDF Save/Load
- new UI features
- UI redesign
- large refactor
- curved path
- iPad/touch UI

Do not change:
- object ID normalization behavior
- opening parent auto-link behavior
- overlapping picker lifecycle fix
- layer lock behavior
- properties panel behavior
- XLSX export sheets
- warnings structure
- measurement geometry
- backend case handling

## Acceptance Criteria

This sprint is done only if:

1. `proto/ui.html` no longer has duplicate active declarations for:
   - `buildRows`
   - `collectAreas`
   - `phase1Warnings`
2. Existing behavior remains unchanged.
3. Overlapping picker remains fixed.
4. Layer lock remains fixed.
5. Properties panel still works.
6. XLSX export still contains:
   - `Cover`
   - `Warnings`
   - `Page Scales`
   - `Audit Log`
   - existing summary sheets
7. No law/OCR/AI/Rule Engine strings are introduced.
8. `py_compile`, `smoke`, and `full` tests pass.

## Suggested Work Method

1. Search in `proto/ui.html`:

```bash
rg -n "function buildRows|const buildRows|let buildRows|var buildRows|buildRows\s*=" proto/ui.html
rg -n "function collectAreas|const collectAreas|let collectAreas|var collectAreas|collectAreas\s*=" proto/ui.html
rg -n "function phase1Warnings|const phase1Warnings|let phase1Warnings|var phase1Warnings|phase1Warnings\s*=" proto/ui.html