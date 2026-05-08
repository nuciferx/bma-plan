# RUN_ROLLBACK_UI_PACK1_TARGETED_FIX.md — Roll Back UI Pack 1 and Apply Targeted Fixes

## Goal

Roll back the recent UI Pack 1 header/toolbar changes because the previous toolbar/header workflow was more usable.

Restore the previous working toolbar/header behavior first, then apply only small targeted fixes.

This is a restoration sprint, not a redesign sprint.

## Current Problem

After UI Pack 1:
- Some toolbar functions became harder to use.
- Area / พื้นที่ controls are not working or not convenient.
- Land / ที่ดิน controls are not working or not convenient.
- The new grouped/open dropdown layout changed the user's workflow too much.
- The user prefers the older toolbar/header behavior and wants to fix UI problems point by point instead.

## Main Decision

Use the pre-UI-Pack-1 header/toolbar as the baseline.

Restore:
- old toolbar structure
- old button visibility
- old click behavior
- old menu behavior
- old tool access pattern

Then apply only minimal fixes:
- keep any harmless CSS improvement if it does not affect function
- keep overflow fixes only if they do not change tool access
- keep font readability only if safe
- do not redesign group/menu structure

## Required Reading

Read first:

1. `AGENTS.md`
2. latest `log.md`
3. `CURRENT_STATUS.md`
4. `index.md`
5. `FINAL_REPORT_FOR_CHATGPT.md`
6. `TEST_RESULT.md`
7. `UI_MANUAL_TEST.md`
8. `PATCH_SUMMARY.md`
9. `proto/ui.html`
10. `proto/e2e_ui_test.py`

Also inspect git diff / file history if available to identify the UI Pack 1 changes.

## Scope

Do only:

1. Roll back UI Pack 1 header/toolbar structural changes.
2. Restore old toolbar/header function and access.
3. Fix only the specific broken points:
   - Area / พื้นที่ clickability
   - Land / ที่ดิน clickability
   - Toolbar buttons not triggering original actions
4. Keep semanticTag/useCategory Sprint A unchanged.
5. Keep site sides/orientation functions unchanged.
6. Keep existing tests passing.
7. Produce before/after screenshots.

## Allowed

Allowed changes:
- `proto/ui.html` header/toolbar HTML/CSS/JS only as needed to restore previous behavior.
- `proto/e2e_ui_test.py` targeted tests for toolbar function.
- report files and log files.

Allowed restoration:
- revert Open PDF / Open Project / Sample from dropdown if old direct buttons worked better.
- restore old visible toolbar buttons if they were functional.
- restore old Area / Land menu/button wiring.
- restore old toolbar click handlers.
- restore old active-state behavior.

Allowed small fixes:
- CSS spacing
- button hit area
- z-index / pointer-events bug
- overflow prevention that does not change tool access
- tooltip / label clarity

## Forbidden

Do not:
- add new drawing tools
- redesign the whole UI
- create a new toolbar concept
- change measurement geometry
- change hit testing, except if absolutely required to restore toolbar dispatch
- change canvas drawing logic
- change layer model
- change layer ordering
- change semanticTag/useCategory model
- change save/load
- change XLSX/PDF export logic
- add OCR
- add AI checker
- add legal rules
- add Rule Engine
- add FAR/OSR/setback validation
- add Project PDF Save/Load

## Restoration Target

The restored toolbar/header should behave like the version before UI Pack 1.

Expected:
- Area / พื้นที่ action is directly accessible and clickable.
- Land / ที่ดิน / parcel/site action is directly accessible and clickable.
- Existing tools remain visible or accessible as before.
- User does not need to dig through new dropdowns for primary workflow tools.
- Toolbar active state reflects selected tool.
- More menu may remain only for truly secondary controls if it already existed safely.

## Specific Checks

### Area / พื้นที่

Must confirm:
- button/menu exists
- click works
- correct mode activates
- area can be drawn
- active state updates

### Land / ที่ดิน

Must confirm:
- button/menu exists
- click works
- correct parcel/site mode activates
- parcel/site boundary can be drawn or selected
- side editor still works after selection

### Open File / Header

Prefer the older clearer workflow if the new `เปิด ▾` dropdown causes friction.

If old direct buttons were better, restore:
- Open PDF
- Open Project
- Sample / Example file

Do not hide essential actions inside a dropdown if it slows workflow.

## Before / After UI Evidence

Create artifact folder:

```text
manual_test_artifacts/rollback_ui_pack1_targeted_fix_YYYYMMDD/

Save screenshots:

before_ui_pack1_problem.png
after_restored_toolbar.png
after_area_tool_active.png
after_land_tool_active.png

If true pre-patch screenshot cannot be captured, document it clearly.

Acceptance Criteria

This sprint passes only if:

UI Pack 1 header/toolbar structural changes are rolled back or neutralized.
Area / พื้นที่ is clickable and works.
Land / ที่ดิน is clickable and works.
Existing toolbar functions are restored.
No new drawing tools are added.
No measurement geometry changes.
No layer model changes.
No semanticTag/useCategory changes.
No save/load changes.
No export changes.
Site side editor still works.
North/orientation still works.
Project Setup still works.
MAIN_UI_OK is updated to reflect restored toolbar behavior, not UI Pack 1 behavior.
SITE_UI_OK, SELECT_OK, XLSX_OK, PROJECT_OK, ANNOT_OK, PERSIST_OK, REAL_OK still pass.
py_compile, smoke, and full pass.
Forbidden scope grep passes.
Before/after screenshots are produced.
Tests

Run:

python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

Allow python3 fallback if needed.

Run forbidden grep:

rg -n "ZONE_RULES|runCheck|FAR|OSR|Rule Engine|OCR|AI checker|Project PDF Save/Load" proto/ui.html proto/server.py proto/e2e_ui_test.py

Expected:

no matches

Run targeted no-new-tool grep:

rg -n "btn-(arc|rect|rectangle|circle|callout|leader|dimension-arrow)|setMode\('(arc|rect|rectangle|circle|callout|leader)'\)|function .*Arc|function .*Circle|function .*Rectangle|function .*Callout" proto/ui.html proto/e2e_ui_test.py

Expected:

no matches
Test Additions

Add/update E2E checks:

Area toolbar control exists.
Area toolbar click activates area mode.
Land toolbar control exists.
Land toolbar click activates parcel/site mode.
Old primary tool access pattern is restored.
More/dropdown does not hide Area/Land primary tools.
Header essential actions are directly accessible if restored.
Existing semanticTag/useCategory tests still pass.
Manual UI Check

Check:

Open app.
Confirm header/toolbar looks closer to old usable version.
Open PDF.
Start Measuring.
Click Area / พื้นที่.
Draw area.
Click Land / ที่ดิน.
Draw/select parcel boundary.
Confirm side editor opens.
Click Select.
Click North/orientation.
Confirm More menu only contains secondary controls if present.
Confirm toolbar functions are not blocked.
Export XLSX.
Save/reload .bmaplan.

Update:

UI_MANUAL_TEST.md
Output Files

Update:

PATCH_SUMMARY.md
TEST_RESULT.md
UI_MANUAL_TEST.md
FINAL_REPORT_FOR_CHATGPT.md
CURRENT_STATUS.md
index.md
log.md

Optional:

PATCH.diff
PATCH_SUMMARY.md Format
# PATCH_SUMMARY.md — Rollback UI Pack 1 + Targeted Toolbar Fix

## Goal
Restore the older working header/toolbar behavior and fix Area/Land toolbar clickability.

## Files Changed
- ...

## What Changed
- Rolled back/neutralized UI Pack 1 header/toolbar structural changes
- Restored direct toolbar access for Area / Land
- Fixed click handlers / disabled state / pointer-events issues
- Preserved semanticTag/useCategory and site/orientation behavior

## What Did Not Change
- measurement geometry
- hit testing
- layer model
- semanticTag/useCategory model
- save/load
- export
- legal/OCR/AI/Rule Engine
- Project PDF Save/Load

## Tests Run
- py_compile:
- smoke:
- full:
- forbidden grep:
- no-new-tool grep:
- manual UI:
FINAL_REPORT_FOR_CHATGPT.md Format
# FINAL_REPORT_FOR_CHATGPT.md — Rollback UI Pack 1 + Targeted Toolbar Fix

## Goal
Restore older working toolbar/header behavior and fix Area/Land controls.

## Outcome
PASS/FAIL/STOP

## Files Changed
- ...

## Restoration Result
- Header:
- Toolbar:
- Area / พื้นที่:
- Land / ที่ดิน:
- Click wiring:
- Active state:
- Before/after screenshots:

## Tests
- py_compile:
- smoke:
- full:
- forbidden grep:
- no-new-tool grep:
- manual UI:

## Regression Status
- Project Setup:
- MAIN_UI_OK:
- SITE_UI_OK:
- SELECT_OK:
- semanticTag/useCategory:
- parcel side editor:
- north/orientation:
- XLSX_OK:
- PROJECT_OK:
- ANNOT_OK:
- PERSIST_OK:
- REAL_OK:

## Known Remaining Gaps
- UI should now be improved point-by-point only.
Stop Conditions

Stop immediately if:

reverting UI Pack 1 risks breaking core workflow
area/land controls require geometry rewrite
semanticTag/useCategory model must be touched
save/load must be touched
layer model must be touched
full test fails
forbidden scope appears

If stopped, write STOP report instead of forcing a patch.

Final Instruction

Function first.

Restore the old working header/toolbar behavior.

Do not redesign.

After restoration, only fix specific broken toolbar points.