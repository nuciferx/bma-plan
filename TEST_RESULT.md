# TEST_RESULT.md - Post-Baseline Workspace Housekeeping

Date: 2026-05-09

## Result

PASS (housekeeping only — no source changed, no tests re-run)

## Last Known Test State

Tests were run against baseline commit d4dce83 (root) / c92f1d8 (proto):

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## Notes

- No source files were changed in this housekeeping sprint.
- Test results carry over from the previous baseline commit.

---

# Previous: Right Panel Organization After Mockup V3

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## Additional Verification

- Manual viewport check with Chromium:
  - `1440 x 900` - PASS
  - `1512 x 982` - PASS
  - `1366 x 768` - PASS

## Coverage Added

- Right panel `Layers` section is visible and appears before compatibility `Properties` and `Object Tree`.
- Right panel layer rows expose layer counts and existing visibility/lock controls.
- Existing Properties/Object Tree remain accessible below Layers.
- Workflow order remains `Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export`.
- `Set Scale` remains before `Page Setup`.
- Left panel labels remain `Sheets`, `Objects`, `Properties`.
- Status bar still includes `Scale`, `Objects`, `Warnings`, `Layer`, `Tool`, and `Save`.
- Forbidden Phase 1 feature wording is not visible in active UI.

## Notes

- No backend/export/save-load/data-model files were edited.
