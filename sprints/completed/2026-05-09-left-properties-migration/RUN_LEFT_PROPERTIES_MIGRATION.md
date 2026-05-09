# RUN_LEFT_PROPERTIES_MIGRATION.md

## 0. Sprint Identity

Sprint Name: Left Properties Migration
Sprint Type: Implementation / UI Feature
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commits 754f436 (proto) / a6d9f43 (root).

Left panel has 3 static tabs (Sheets, Objects, Properties) — none have click handlers.
Clicking them does nothing. Only Sheets content (page thumbnails) is visible.
The property editor lives in right panel "Legacy / Compatibility - Properties" section.

---

## 2. Goal

Wire up the 3 left panel tabs so they actually switch content:
- Sheets (default): current page thumbnails and tag bar (existing behavior)
- Objects: flat list of all objects on current page, click to select
- Properties: selected object property editor (mirrors right panel properties section)

When an object is selected via canvas or tree, auto-switch left panel to Properties tab.

Right panel properties section stays in place (backwards compatible).

---

## 3. Approach

- Add `data-mode` attributes to the 3 `.sidebar-mode-tab` divs and a `setSidebarMode(mode)` function.
- Add 2 new hidden content divs: `#lp-objects-content` and `#lp-properties-content`.
- `setSidebarMode("sheets")`: show #sidebar-content, #quick-tag-bar, #search-input; hide others.
- `setSidebarMode("objects")`: hide #sidebar-content, #quick-tag-bar, #search-input; show #lp-objects-content with object list.
- `setSidebarMode("properties")`: hide others; show #lp-properties-content with property editor.
- `buildLeftProperties()`: render property editor HTML into #lp-properties-content (same data as right panel properties section).
- Wire all rpSet* functions and canvas selection to call `buildLeftProperties()` when left panel is in "properties" mode.
- Auto-switch to "properties" mode when selItem is set (in setMode("sel") flows and selectObjectFromTree).
- E2E: add leftPanelTabsOk assertion to MAIN_UI_OK (tabs switch; Properties content appears after selection).

---

## 4. Files Allowed

- `proto/ui.html` — add tab handlers, new divs, buildLeftProperties, wiring
- `proto/e2e_ui_test.py` — extend MAIN_UI_OK or SELECT_OK

## 5. Files Forbidden

- `proto/server.py`
- `proto/requirements.txt`
- Legal/OCR/AI/Rule Engine logic
- No removal of right panel properties section

---

## 6. Acceptance Criteria

- [x] Clicking "Sheets" tab shows page thumbnails (existing behavior)
- [x] Clicking "Objects" tab shows a list of objects on the current page
- [x] Clicking "Properties" tab shows property editor (or "select an object" placeholder)
- [x] Selecting an object auto-switches left panel to Properties tab
- [x] `leftPanelTabsOk: True` in E2E test
- [x] Right panel properties section still present (rightPanelCompatibilityVisible still PASS)
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

---

## 7. Stop Conditions

- Requires moving/removing right panel content
- Left panel becomes too wide for the viewport
- Tab switching breaks existing keyboard shortcuts or selection flow
- Tests fail outside tab switching
