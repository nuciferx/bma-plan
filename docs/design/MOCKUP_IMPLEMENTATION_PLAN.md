# MOCKUP_IMPLEMENTATION_PLAN.md

Date: 2026-05-09
Based on: MOCKUP_LAYOUT_MAPPING.md
Baseline: proto 797a4a2

---

## Sequencing Principle

Each sprint must:
1. Have a single clear goal
2. Not break existing test assertions
3. Stay within Phase 1 scope (no legal/OCR/AI/Rule Engine)
4. Pass py_compile + smoke + full before commit

Ordering: lowest risk first, highest value per risk second.

---

## Sprint 1 — Widget Placement Polish

**Goal:** Polish the 5 sidebar widgets to match mockup visual quality: better typography,
color-coded status, and compact row format. No new state, no new logic — CSS and innerHTML
refinements only.

**Target elements:**
- `#widget-review-warnings` — add color-coded severity (error/warning/info badge)
- `#widget-export-ready` — add per-item status line (Pages, Objects, Scale, QA)
- `#lp-page-info` — align with mockup sheet-item style
- `#workflow-card` — match mockup panel-section header style

**Allowed files:**
- `proto/ui.html` (updateWidgets() function, widget HTML)
- `proto/static/css/app.css` (widget-card, widget-badge refinements)

**Forbidden files:**
- `proto/server.py`, `proto/e2e_ui_test.py`, `proto/export/*`

**Risk level:** LOW
- Only touches CSS and one JS function (updateWidgets)
- Existing E2E assertions check visibility not inner style
- No behavior change

**Test requirements:**
- py_compile PASS
- smoke PASS (all widget assertions still True)
- full PASS

**Stop conditions:**
- Export breaks
- Open PDF breaks
- Any existing E2E assertion fails

---

## Sprint 2 — Canvas Top Info Bar

**Goal:** Add a thin overlay bar (`.canvas-top`) above the canvas area showing:
page name, current page/total, zoom%, scale badge, coordinates (read from mouse events).
This replaces the need to look at the topbar for scale/page context while drawing.

**Target elements (new HTML inside `#workspace`):**
- `<div id="canvas-top-bar">` — position: absolute, top:0, left:0, right:0, height:28px
  - Page nav info: `หน้า {curPage} / {totalPages}`
  - Zoom: `{zoom}%`
  - Scale: `{scaleLabel()}` (live from existing function)
  - Coordinates: `x: {px} y: {py}` (from mousemove on canvas)

**Allowed files:**
- `proto/ui.html` (add #canvas-top-bar div + updateCanvasTop() function)
- `proto/static/css/app.css` (add .canvas-top-bar styles)
- `proto/e2e_ui_test.py` (add canvasTopBarVisible assertion)

**Forbidden files:**
- `proto/server.py`, `proto/export/*`

**Risk level:** LOW-MEDIUM
- New overlay div inside workspace (no change to layout flow)
- mousemove handler is additive (no existing handlers removed)
- scale badge remains in topbar too (dual display, consistent data)

**Test requirements:**
- py_compile PASS
- smoke PASS (+ canvasTopBarVisible assertion)
- full PASS

**Stop conditions:**
- Canvas click/draw breaks
- Scale calibration breaks
- Any existing assertion fails

---

## Sprint 3 — Scale Manager Foundation

**Goal:** Add an in-app Scale Manager overlay showing per-page scale status table.
Uses existing pageData, getScaleForPage(), pageNames — no new backend calls.
Accessible via a "Scale Manager" button in the topbar or via Set Scale button long-action.

**Target elements (new overlay):**
- `<div id="scale-manager-overlay">` — modal, shows table
- Table columns: Page# | Page Name | Tag | Scale | Status | Action (Set Scale)
- Data from: `pageNames`, `getScaleForPage(n)` for n in 1..totalPages

**Allowed files:**
- `proto/ui.html` (new overlay + openScaleManager() function + button in topbar)
- `proto/static/css/app.css` (overlay styles)
- `proto/e2e_ui_test.py` (add scaleManagerButtonVisible assertion)

**Forbidden files:**
- `proto/server.py`, `proto/export/*`

**Risk level:** MEDIUM
- New overlay (modal pattern already used for setup-overlay)
- No backend changes
- Closes without side effects

**Test requirements:**
- py_compile PASS
- smoke PASS (+ scaleManagerButtonVisible assertion)
- full PASS

**Stop conditions:**
- Export breaks
- Set Scale calibration breaks
- Overlay does not close correctly
- Any existing assertion fails

---

## Sprint 4 — Page Setup Table

**Goal:** Enhance the Sheets tab in the left panel to show per-page setup status inline:
warning icon when scale not set, page type tag, floor label. Aligns with mockup sheet-item
`.sheet-warn` indicator.

**Target elements:**
- `buildSidebar()` function in proto/ui.html: add per-page scale status + warn icon to
  each page row in `#sidebar-content`
- Each page row gets: page number badge, name, tag, scale-missing ⚠ icon (if applicable)

**Allowed files:**
- `proto/ui.html` (buildSidebar() function only)
- `proto/static/css/app.css` (sheet-item, sheet-warn, sheet-num styles)

**Forbidden files:**
- `proto/server.py`, `proto/e2e_ui_test.py`, `proto/export/*`

**Risk level:** LOW
- buildSidebar() is a render function; data sources already exist
- No logic change to scale/measurement engine
- E2E smoke test does not assert per-page sidebar content details

**Test requirements:**
- py_compile PASS
- smoke PASS
- full PASS (page list renders for REAL_OK test)

**Stop conditions:**
- Page switching breaks
- Any existing sidebar assertion fails

---

## Sprint 5 — Export Review Preview

**Goal:** Expand `#widget-export-ready` to show a richer pre-export checklist:
per-page status (scale set / objects / warnings) in a scrollable table.
Add an inline "Export XLSX" button to the widget.

**Target elements:**
- `updateWidgets()` in proto/ui.html: expand export widget body
- Export button in widget: `onclick="exportXlsx()"` (function already exists)
- Per-page rows: `totalPages` loop, `getScaleForPage(n)`, `pageNames[n]`

**Allowed files:**
- `proto/ui.html` (updateWidgets() function)
- `proto/static/css/app.css` (widget table row styles)
- `proto/e2e_ui_test.py` (update exportReadyWidgetVisible assertion if needed)

**Forbidden files:**
- `proto/server.py`, `proto/export/*`

**Risk level:** LOW
- No new state
- Export button calls existing exportXlsx() with no changes
- Only widget innerHTML changes

**Test requirements:**
- py_compile PASS
- smoke PASS (exportReadyWidgetVisible still True)
- full PASS

**Stop conditions:**
- Export breaks
- Any existing E2E assertion fails

---

## Sprint 6 — Mockup Visual Implementation Phase 1

**Goal:** Restructure the topbar from 48px single-bar to two-zone layout matching mockup:
- Zone 1 (28px): Menu-bar style with app logo + key menu items as clickable labels
  (File, Scale, Page, Review, Export as flat nav — no full dropdown menus yet)
- Zone 2 (44px): Ribbon-style with icon+label button groups (same tools as current toolbar)

The float-toolbar becomes the ribbon (anchored, not floating).
The 3 workflow zone-b buttons move to ribbon groups.

**Allowed files:**
- `proto/ui.html` (topbar HTML, float-toolbar layout, CSS vars)
- `proto/static/css/app.css` (new .menu-bar, .ribbon, .rbtn, .ribbon-group styles)
- `proto/e2e_ui_test.py` (update toolbar assertions for new IDs/positions)

**Forbidden files:**
- `proto/server.py`, `proto/export/*`

**Risk level:** HIGH
- Major HTML structure change — #topbar and #float-toolbar both change
- All toolbar E2E assertions (toolbarFitsWorkspace, toolbarBelowHeader, primaryToolsVisible,
  primaryToolCount, activeHighlightOk, toolbarHasDividers, etc.) need verification
- Test suite must pass with new structure before commit

**Test requirements:**
- py_compile PASS
- smoke PASS (all toolbar assertions verified — may need assertion updates)
- full PASS (all 17 tests)

**Pre-conditions:**
- Sprints 1–5 must be complete
- All existing assertions must be documented before starting
- Start with a git branch: `feat/mockup-visual-phase1`

**Stop conditions:**
- Open PDF breaks
- Set Scale breaks
- Any measurement tool breaks
- Export breaks
- Test count drops below 17 assertions in MAIN_UI_OK

---

## Implementation Priority Matrix

| Sprint | Value | Risk | Effort | Recommended Order |
|--------|-------|------|--------|-------------------|
| 1 — Widget Polish | HIGH | LOW | S | 1st |
| 2 — Canvas Top Bar | HIGH | LOW | S | 2nd |
| 3 — Scale Manager | HIGH | MEDIUM | M | 3rd |
| 4 — Page Setup Table | MEDIUM | LOW | S | 4th |
| 5 — Export Review | MEDIUM | LOW | S | 5th |
| 6 — Visual Phase 1 | HIGH | HIGH | L | 6th (requires 1–5 done) |

---

## What Stays Forbidden (All Sprints)

| Feature | Reason |
|---------|--------|
| Draggable summary widget | Draggable workspace — Phase 1 scope lock |
| Custom workspace save | Phase 1 scope lock |
| Full autosave engine | Phase 1 scope lock |
| Legal checker | Phase 1 scope lock |
| OCR | Phase 1 scope lock |
| AI checker | Phase 1 scope lock |
| Rule Engine / FAR/OSR | Phase 1 scope lock |
| K.1 generator | Phase 1 scope lock |
| Auto boundary detection | Phase 1 scope lock |
| Summary widget Area/Floor/Site tabs | Depends on backend per-page summary API — deferred |

---

## Immediate Next Sprint

**Sprint 1 — Widget Placement Polish** is ready to start now.

Prerequisites:
- Baseline py_compile/smoke/full PASS confirmed (797a4a2) ✓
- No forbidden phase 1 strings in UI ✓
- CSS and JS static assets load correctly ✓

Sprint card: create `sprints/active/RUN_WIDGET_PLACEMENT_POLISH.md`
