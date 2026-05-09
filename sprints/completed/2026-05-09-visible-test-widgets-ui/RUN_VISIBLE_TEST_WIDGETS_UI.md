# RUN_VISIBLE_TEST_WIDGETS_UI.md

## 0. Sprint Identity

Sprint Name: Visible Test Widgets UI
Sprint Type: Fast Guarded UI Sprint
Status: IN PROGRESS
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: e4124d8 (root) / 9fa57a0 (proto)
py_compile PASS · smoke PASS · full PASS (confirmed at sprint start)

Source file sizes at baseline:
- proto/ui.html: 1111 lines
- proto/static/css/app.css: 307 lines
- proto/e2e_ui_test.py: 1525 lines

---

## 2. Goal

Make the designed/mockup widgets visible in the UI for real user testing,
using existing state only. This is a bridge sprint before full mockup visual implementation.

---

## 3. Widget Audit

| Widget | Status | Notes |
|--------|--------|-------|
| Workflow Widget | ✅ Already working | #workflow-card + setWorkflowState() + updateWorkspaceState() |
| Scale Status Widget | ✅ Already working | #scale-badge + #scale-notice + updateAnalyseUI() |
| Page Info Widget | ✅ Already working | #lp-page-info + updateWorkspaceState() |
| Review Warning Widget | ❌ Missing | Only #lbl-warnings (number) in bottombar — no visible widget |
| Export Ready Widget | 🔶 Partial | #export-readiness only visible inside export panel (requires click) |

---

## 4. Scope

### In Scope
- Add `#widget-review-warnings` div in sidebar (after workflow-card)
- Add `#widget-export-ready` div in sidebar (after warnings widget)
- Add `updateWidgets()` function (uses existing currentWarningCount, currentObjectCount, getScaleForPage)
- Call `updateWidgets()` from `updateBottomBar()`
- CSS for `.widget-card`, `.widget-title`, `.widget-body`, `.widget-link`, `.widget-badge`
- E2E test assertions for all 5 widgets' visibility

### Not Scope
- Full mockup visual layout
- Draggable/resizable widgets
- Widget configuration panel
- New drawing tools
- Backend changes
- Export logic changes
- Legal/OCR/AI/Rule Engine

---

## 5. Files Allowed

Source:
- proto/ui.html
- proto/static/css/app.css
- proto/e2e_ui_test.py (minimal assertions only)

Docs:
- CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md
- docs/status/
- sprints/active/ → sprints/completed/

## 6. Files Forbidden

- proto/server.py
- proto/export/*
- proto/static/js/semantic-meta.js
- proto/static/js/opening-parent.js
- proto/requirements.txt

---

## 7. UI Contract

- Widgets must be visible without opening hidden menus.
- Widgets use only existing state (totalPages, currentObjectCount, currentWarningCount, getScaleForPage, scaleLabel).
- If state unavailable, show neutral text ("เปิด PDF เพื่อดู...").
- No fake state. No legal/OCR/AI strings.
- Existing workflows (Open PDF, Set Scale, Export) must continue to work unchanged.
- Existing export buttons must continue to work.

## 8. State Contract

- Widget 4 (warnings): uses `currentWarningCount()` — cheap, safe, already tested
- Widget 5 (export ready): uses `totalPages`, `currentObjectCount()`, `getScaleForPage(curPage)`, `scaleLabel()` — all existing

## 9. Test Plan

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py   # PASS
python proto/e2e_ui_test.py smoke                            # PASS (+ new assertions)
python proto/e2e_ui_test.py full                             # PASS
```

New assertions added to MAIN_UI_OK:
- scaleStatusWidgetVisible (#scale-badge)
- pageInfoWidgetVisible (#lp-page-info)
- reviewWarningWidgetVisible (#widget-review-warnings)
- exportReadyWidgetVisible (#widget-export-ready)

## 10. Acceptance Criteria

- `#widget-review-warnings` visible in left sidebar without any click
- `#widget-export-ready` visible in left sidebar without any click
- `updateWidgets()` called from `updateBottomBar()` (no side effects)
- All 4 new MAIN_UI_OK assertions pass
- No existing assertions broken
- No forbidden Phase 1 strings introduced

## 11. Stop Conditions

- Open PDF breaks
- Set Scale breaks
- Area/Opening drawing breaks
- Properties panel breaks
- Opening parent reassignment breaks
- Layers panel breaks
- Export panel breaks
- Any existing test assertion fails
- Implementation touches server.py or export logic
- Legal/OCR/AI/Rule Engine strings appear in UI

---

## 12. Checklist

### Part A — HTML (ui.html)
- [x] Add #widget-review-warnings div after workflow-card
- [x] Add #widget-export-ready div after warnings widget
- [x] Add updateWidgets() function call in updateBottomBar()
- [x] Add updateWidgets() function definition

### Part B — CSS (app.css)
- [x] Add .widget-card, .widget-title, .widget-body, .widget-link, .widget-badge styles

### Part C — Tests (e2e_ui_test.py)
- [x] Add 4 new keys to JS evaluate return dict
- [x] Add 4 new Python assertion checks

### Part D — Testing
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

### Part E — Doc Update and Commit
- [x] Update status docs
- [x] Commit proto: ui: add visible workflow test widgets
- [x] Move sprint card to sprints/completed/
- [x] Commit root: docs: record visible test widgets sprint

---

## 13. Before/After

| File | Before | After |
|------|--------|-------|
| proto/ui.html | 1111 | ~1122 |
| proto/static/css/app.css | 307 | ~315 |
| proto/e2e_ui_test.py | 1525 | ~1533 |
