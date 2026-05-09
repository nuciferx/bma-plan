# E2E_SPLIT_PLAN.md — E2E Test Reorganization Plan

Date: 2026-05-09
Status: PLAN ONLY — not implemented

## Current State

`proto/e2e_ui_test.py` — 1525 lines, single file.
CLI: `python proto/e2e_ui_test.py smoke` / `python proto/e2e_ui_test.py full`
All tests share a single Playwright browser/context/page instance, run sequentially.

## Why Not Split Yet

Shared state is load-bearing:
- `smoke` tests run first, leave page in state that `full` tests depend on.
- CACHE_OK, SETUP_OK establish browser state; MAIN_UI_OK, VECTOR_OK etc. build on it.
- Splitting requires a state handoff mechanism between files.
- Risk: test ordering breaks → false failures → stop condition.

## Proposed Split (future sprint)

```
proto/
  e2e_ui_test.py          # CLI entry point + shared fixtures only
  tests/
    __init__.py
    test_smoke.py          # CACHE_OK, SETUP_OK, MAIN_UI_OK
    test_vector.py         # VECTOR_OK, RECAL_OK, SITE_UI_OK
    test_export.py         # XLSX_OK, PROJECT_OK
    test_drawing.py        # RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK
    test_measure.py        # SETBACK_OK, EXT_MEASURE_OK
    test_persist.py        # ANNOT_OK, PERSIST_OK, REAL_OK
```

## Implementation Requirements

1. Shared browser/context/page must be passed between test modules (or re-created per module).
2. `python proto/e2e_ui_test.py smoke` CLI must keep working.
3. `python proto/e2e_ui_test.py full` must run all modules in order.
4. Each module must be independently runnable for debugging (option, not required).
5. All assertions must remain — no reduction in coverage.

## Stop Conditions for This Sprint (when executed)

- Any test module fails that passed before the split.
- Assertion count drops.
- Test ordering changes break state assumptions.
- Fix requires broad rewrite of test runner logic.
