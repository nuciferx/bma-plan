# UI_MANUAL_TEST.md - Rollback UI Pack 1 + Targeted Toolbar Fix

Date: 2026-05-08 00:45 +07:00

## Result

PASS via automated Chromium E2E plus focused screenshot checks.

## UI Scope Checked

| Item | Result | Detail |
|---|---|---|
| App opens | PASS | Chromium opened the app and uploaded `proto/test_plan_A1.pdf`. |
| Header direct actions | PASS | `Open PDF`, `Open Project`, and sample PDF are direct header controls again. |
| Open dropdown neutralized | PASS | `#top-open-btn` is absent and no primary file action is hidden behind it. |
| Export | PASS | Export remains visible and unchanged. |
| Toolbar primary row | PASS | Primary measurement controls remain visible and fit the workspace at 1440x900. |
| Area direct access | PASS | Clicking Area after Opening resets `openingMode=false`, `curAType=room`, active layer `sub_area`. |
| Land direct access | PASS | Clicking Land after Opening resets `openingMode=false`, `curAType=land`, active layer `base_area`. |
| Opening | PASS | Opening remains direct and is used without clicking Area afterward. |
| Side editor | PASS | `SITE_UI_OK` confirms parcel side editor still works. |
| North/orientation | PASS | `SITE_UI_OK` confirms north/orientation still works. |
| Save/load/export | PASS | `PROJECT_OK`, `XLSX_OK`, `ANNOT_OK`, `PERSIST_OK`, and `REAL_OK` pass. |

## Screenshots

- `manual_test_artifacts/rollback_ui_pack1_targeted_fix_20260508/before_ui_pack1_problem.png`
- `manual_test_artifacts/rollback_ui_pack1_targeted_fix_20260508/after_restored_toolbar.png`
- `manual_test_artifacts/rollback_ui_pack1_targeted_fix_20260508/after_area_tool_active.png`
- `manual_test_artifacts/rollback_ui_pack1_targeted_fix_20260508/after_land_tool_active.png`

## Manual Notes

- This was a restoration sprint, not a redesign sprint.
- The canvas, measurement geometry, hit testing, layer model, semantic metadata model, Project Setup, save/load, and export code were not changed.
- Advanced land-edge/setback helpers remain hidden by default.
