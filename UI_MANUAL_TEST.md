# Latest: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3

Branch: main

Date: 2026-05-20

## Result

Automated PASS — py_compile PASS; full EXIT 0; INV_LAYER_L1_OK / INV_LAYER_L2_OK / INV_LAYER_L3_OK GREEN; HT8D5A all:True restored; 100 _OK markers. Manual verification required: headless Playwright confirms slug resolution and lock authority, but real-browser verification of the layer reassign dropdown UX, site-page layer rendering, and the absence of overlap must be confirmed in Chrome with a real multi-page permit PDF.

## Manual Checklist — Layer rebuild: site-plan page correctness

| Check | Expected | Result |
|-------|----------|--------|
| Open a PDF; tag a page as "ผังบริเวณ" in Page Setup; draw a building-coverage polygon | Object appears under a real site layer (not a phantom "sub_area" phantom slug); right-panel object count increments | — |
| Draw a land/boundary area on the same site page | Object lands in "ที่ดิน/แนวเขต" (site_boundary layer), not "sub_area" | — |
| Select an existing object on the site page; open Properties panel | Properties panel shows a "Layer" `<select>` dropdown listing the page's layer presets | — |
| Change the Layer dropdown to a different layer | Object moves to the new layer; summary and render update; object is no longer in old layer | — |
| In the Layers tab, hide a single layer (eye icon) | Only that layer's objects are hidden; objects on other layers remain visible; no overlap bleed across the 7 site area types | — |
| Lock the active layer (lock icon) | Drawing a new object or clicking an existing one in that layer is blocked; alert shown; other layers remain editable | — |
| Unlock the layer; toggle the layer off at the page-scoped level | App follows the page-scoped state even if the legacy global toggle was previously set differently | — |

---

# Previous: BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode

Branch: main

Date: 2026-05-20

## Result

Automated PASS — py_compile PASS; full EXIT 0; BUG_20260520_SEL_MIDPAN_OK GREEN (canvas #cc transform +70x/+45y; mode stayed 'sel' throughout). Manual verification required: headless Playwright drives middle-button events via `mouse.down({button:'middle'})` which is spec-correct, but real cursor grab behavior (cursor icon switch + smooth pan feel) must be verified in a real browser.

## Manual Checklist — BUG-20260520-sel-midpan: Select mode pan

| Check | Expected | Result |
|-------|----------|--------|
| Activate the Select tool (S key or ribbon button); load any PDF | Tool label shows "Select" in status bar | — |
| Hold middle mouse button + drag on canvas | Canvas pans smoothly; cursor changes to grabbing hand during drag | — |
| Release middle mouse button | Cursor reverts to default (not grabbing); mode remains 'sel' (not 'pan') | — |
| Hold Space + drag on canvas (Select tool still active) | Canvas pans smoothly; cursor changes to grabbing hand | — |
| Release Space | Cursor reverts; mode remains 'sel' | — |
| Single left-click on an existing object (Select tool active) | Object becomes selected normally; pan did NOT hijack click | — |
| Double-check: activate Pan tool explicitly (P key), then middle-drag | Still pans as before (no regression on pan tool's own path) | — |

---

# Previous (older): Mockup Alignment Bundle — Structure (HT-18..21) + Visual Polish (HT-22..26)

Branch: main

Date: 2026-05-18

## Result

Automated PASS for both sub-bundles — py_compile clean, smoke 18/18 markers green across both runs (CACHE_OK, SETUP_OK, MAIN_UI_OK with `leftPanelLabelsOk: True` and `statusBarText` containing "Save: Manual save required" + "Page: ผังบริเวณ", VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK). Forbidden-surface scan clean — polyAreaM2 / polyMetrics / polySelfIntersects / pdfToC / cToPdf / RS / buildSnapIndex / snap / .bmaplan schema fields / server.py core endpoints all untouched across all 9 sprints. Manual verification **PENDING** — headless Chromium cannot detect dropdown click-outside, visual hover/active states, gradient/shadow rendering, density transitions, or modal stacking; the checklists below must be run in real Chrome before this bundle is considered closed.

## Sub-bundle B: Visual Polish (HT-22..26) — 2026-05-18 evening

5 region-scoped sprints that align live UI with the mockup at `proto/sandbox/mockup-top-menu-redesign.html` after positioning/structure was already correct (HT-18..21). Each sprint was scoped via `/bma-ui-scope`, delegated to its region-specialist subagent for a patch plan, applied by the main agent, then verified by `bma-ui-regression-guardian`. CSS-first — `proto/static/css/app.css` carries 95% of the visual change; `proto/ui.html` carries minimal DOM rewrap (`rsection` + `rlbl` headers for ribbon, `panel-head` + count badge for right panel).

- **HT-22 (Ribbon visual polish):** Added 7 uppercase section labels (`🔍 TOOL / 📐 SCALE / 🟩 พื้นที่ / 📏 LINES / 📍 MARKER / 🛠 HELPERS / ↩ EDIT`) above each ribbon-group; introduced 8 new CSS variables (`--btn-h:60px / --btn-icon-font:22px / --btn-font:11px / --btn-min-w:60px / --hero-w:88px / --hero-icon:28px / --mini-size:28px / --mini-font:14px`) and bumped `--ribbon-h` 44→78; density-compact/comfortable/spacious now drive the variables instead of hard-coded values; hero buttons (Set Scale, Polygon) styled as 88×60 blue-gradient pills with bigger icon + label below.
- **HT-23 (Status bar separator):** Added `.bb-sep` divider rule, `.bb-save-dirty` (yellow) + `.bb-save-clean` (green) classes; `_setDirty`/`_markSaved` now toggle classes instead of inline `style.color`; `#snap-bar` + `#color-bar` visually demoted to auxiliary zone with smaller font + `border-left` + subtle background — visually reads as `[prefix + core 7] │ [snap aux] │ [color aux]`.
- **HT-24 (Right panel header + count badge):** `#rp-header` converted from plain h2 to `.panel-head` flex container with `<span class="count" id="rp-header-count">N</span>` green badge; new helpers `_sumAllPagesObjectCount()` + `_sumAllPagesCommentCount()`; `switchRightTab` updates the badge per active tab (List=page objects, Layers=page layer count + `(P.N)` suffix on h2, Props=0|1, Summary=cross-page object total, Notes=cross-page comment total).
- **HT-25 (Left panel polish):** `.panel-tab.active` switched from `var(--accent)` (blue) to `var(--cyan)` with `margin-bottom:-1px` overlay trick; `.sheet-item` font/padding bumped from `11px / 6px 12px` to `12px / 6px 14px` to match mockup.
- **HT-26 (Summary widget hide-when-empty + canvas-top-bar polish):** `swState.visible` default `false`; added `_manuallyHidden` field; `hideSummaryWidget` sets `_manuallyHidden=true`; `updateSummaryWidget` auto-hides widget when `!hasPdf` and auto-shows on first PDF load (only if user hasn't explicitly closed it). Canvas-top-bar CSS reworked from per-span pills to a single unified rounded pill with `rgba(20,20,25,.88)` + backdrop-blur + cyan `<b>` highlights per mockup. Sidebar widths bumped 220→240 / 200→240 to match mockup `--lpanel-w` / `--panel-w`.

## Sub-bundle A: Structure Alignment (HT-18..21) — 2026-05-18 daytime

## Why sub-bundle A (HT-18..21)

User flagged "live program doesn't match `proto/sandbox/mockup-top-menu-redesign.html` yet." Comparison showed 4 critical gaps that previous HT-12..HT-15 cycle missed because the mockup was updated AFTER those sprints landed.

- **HT-18 (Menu Gap Fix):** Edit menu had no dropdown (bare `<div>Edit</div>` — fake button per anti-fake-button rule). Review/Export/Workspace menu-items were leftover bare labels that did nothing on click. Help had no dropdown. Fix: added Edit dropdown (Undo/Redo/Rename/Delete wired to existing functions); added Help dropdown (User Manual / Shortcuts / Dev Log / Report Issue / About) linked to `/static/docs/`; removed bare Review/Export/Workspace items (commented with rationale); wired previously-missing `Ctrl+Y → redo()` global shortcut.
- **HT-19 (Status Bar Save+Page):** `lbl-save-state` + `bb-page-name` already existed but rendered AFTER snap-bar + color-bar, so users saw a mess instead of the clean 7-field mockup order. Fix: reordered to mockup spec (prefix / Tool / Scale / Objects / Warnings / Layer / Save / Page) with snap-bar + color-bar as auxiliary AFTER the 7 core fields; enhanced `_markSaved` (✓ green) and `_setDirty` (● yellow) to color the save state per mockup.
- **HT-20 (Right Notes Tab):** Right panel only had 4 tabs; mockup wants 5 (List / Layers / Props / Summary / Notes) plus a panel-footer (⬇ CSV / 📤 ส่งกลับ). Fix: added 5th Notes tab; new `_renderNotesInPanel` aggregates `ann_comment` annotations across all pages with click-to-jump; `rpAddNote` allows quick comment entry; panel-footer wired (CSV → `exportCSV()`, ส่งกลับ → workflow-Phase-2 placeholder).
- **HT-21 (Left Sheets Tab):** Left panel had 3 tabs (หน้า / รายการบนหน้า / Properties); mockup wants 4 with a separate "Sheets" tab grouped by discipline (A-/S-/M-/E-). Fix: added 4th Sheets tab with `buildLeftDisciplines` — parses leading code from `pageNames[n]`, falls back to `pageTags`; renamed Objects → "Tree" and Properties → "Props" to match mockup; updated `_test_main_measurement_ui_cleanup` backward-compat to accept both old and new tab labels.

## Manual Checklist — Edit + Help Dropdowns (HT-18)

| Check | Expected | Result |
|-------|----------|--------|
| Click "Edit" in menu bar | Dropdown opens with Undo / Redo / Rename / Delete | — |
| Click Edit › Undo when nothing undoable | Status bar shows "ไม่มีอะไรให้ Undo", no crash | — |
| Press Ctrl+Y (no draft in progress) | Calls `redo()` — status bar says "↪ Redo" or "ไม่มีอะไรให้ Redo" | — |
| Press F2 with object selected | Rename modal opens with current name | — |
| Click "Help" in menu bar | Dropdown opens with 5 items | — |
| Click Help › User Manual | New tab opens `/static/docs/index.html` | — |
| Click Help › Report Issue | Alert with stub message (Phase 2 placeholder) | — |
| Verify "Review" / "Export" / "Workspace" no longer appear as bare menu items | Only File / Edit / View / Project / Scale / Page / Measure / Object / Layer / Annotate / Help visible (+ density picker + Phase badge) | — |

## Manual Checklist — Status Bar Save+Page Order (HT-19)

| Check | Expected | Result |
|-------|----------|--------|
| Open a PDF; look at status bar field order | `📐 วัด → Tool → Scale → Objects → Warnings → Layer → Save → Page → │ → Snap toggles → Color picker` | — |
| Save field initially | Yellow text "Manual save required" | — |
| Draw an area, observe Save | Turns yellow with `● Unsaved changes` | — |
| Press Ctrl+S then Save As | Save field turns green "✓ Saved" or "✓ Downloaded" | — |
| Page field after PDF load | Shows page name (e.g. "ผังบริเวณ") in cyan, not "—" | — |

## Manual Checklist — Right Panel Notes + Footer (HT-20)

| Check | Expected | Result |
|-------|----------|--------|
| Open right panel, look at tab strip | 5 tabs: 📋 รายการ / 🗂 Layers (active) / 🔧 Props / 📊 สรุป / 💬 Notes | — |
| Click 💬 Notes | Header changes to "💬 Notes & Comments"; shows empty state or comment cards | — |
| Type in input "ทดสอบ comment" and press Enter | New comment card appears with current timestamp; canvas shows 💬 at center | — |
| Click a comment card | Loads the page where the comment lives | — |
| Look at bottom of right panel | Footer with `⬇ CSV` + `📤 ส่งกลับ` (green primary) | — |
| Click ⬇ CSV | Browser downloads `measurements.csv` | — |
| Click 📤 ส่งกลับ | Alert with workflow-Phase-2 placeholder message | — |
| Collapse right panel (▶) | Footer hides along with body | — |

## Manual Checklist — Left Panel Sheets by Discipline (HT-21)

| Check | Expected | Result |
|-------|----------|--------|
| Open left panel, look at tab strip | 4 tabs: 📑 หน้า (active) / 📚 Sheets / 🌳 Tree / 🔧 Props | — |
| Click 📚 Sheets with real 45-page permit PDF open | Sheets grouped by discipline; if pages have no leading code, fallback grouping by tag (📍 Site Plan / 🏢 Floor Plan / etc.) | — |
| Click a group header | Toggles open/closed; ▾ / ▸ caret reflects state | — |
| Click a sheet item | Calls `loadPage(n)` and navigates | — |
| Sheet with manual scale shows ★ | ★ next to page number | — |
| Click 🌳 Tree | Same content as old "รายการบนหน้า" — list of objects on current page | — |
| Click 🔧 Props | Same content as old "Properties" — object detail | — |

## Manual Checklist — Forbidden Surface Sanity

| Check | Expected | Result |
|-------|----------|--------|
| Draw a polygon (Polygon tool), close it | Area in `ตร.ม.` matches scale (polyAreaM2 unchanged) | — |
| Recalibrate scale | All measurements re-derive instantly (raw-geometry contract unchanged) | — |
| Save .bmaplan, close, reopen | All measurements + comments restored (schema additive only) | — |
| Export XLSX | Excel opens; sheet sums match summary widget | — |

---

## Manual Checklist — HT-22 Ribbon Section Labels + Hero Buttons

| Check | Expected | Result |
|-------|----------|--------|
| Open app, look at ribbon (Measure tab) | 7 section labels visible: 🔍 TOOL / 📐 SCALE / 🟩 พื้นที่ / 📏 LINES / 📍 MARKER / 🛠 HELPERS / ↩ EDIT | — |
| Look at Set Scale + พื้นที่ (Polygon) buttons | Large blue-gradient hero buttons, ~88px wide × 60px tall, icon ~28px, label below | — |
| Switch density via menu (Compact / Comfortable / Spacious) | Buttons resize smoothly; labels remain readable; ribbon doesn't overflow | — |
| Helpers section 2×2 grid | Loupe/Ortho/Perp/Snap-off as 4 small square buttons | — |
| Vertical dividers (`.rdiv`) | 1px lines between section groups | — |

## Manual Checklist — HT-23 Status Bar Aux Zone Separation

| Check | Expected | Result |
|-------|----------|--------|
| Status bar after `Page:` field | `│` divider, then snap-bar with subtle border-left + slightly darker bg | — |
| Snap toggle buttons (EP/MP/CT/NL/IX/—) | Smaller font, dimmer than core 7 fields — reads as "aux tools" | — |
| Color picker + opacity slider | Same demoted treatment, sits after snap bar | — |
| Draw an object (any tool) | `Save:` field turns yellow with `● Unsaved changes` (class `.bb-save-dirty`) | — |
| Ctrl+S → Save | `Save:` turns green `✓ Saved` (class `.bb-save-clean`) | — |

## Manual Checklist — HT-24 Right Panel Header Count Badge

| Check | Expected | Result |
|-------|----------|--------|
| Open right panel, look at h2 + badge | "Layers" h2 with green count badge to the right | — |
| Click Layers tab with a PDF open | Header reads "🗂 Layers (P.{n})", badge shows layer count | — |
| Click List tab | Header changes to "📋 รายการ object", badge shows objects on current page | — |
| Click Summary tab | Badge shows total objects across all pages | — |
| Click Notes tab | Badge shows total comments across all pages | — |
| Click Props tab with object selected | Badge shows `1`; with no selection shows `0` (gray) | — |

## Manual Checklist — HT-25 Left Panel Tab + Sheet Polish

| Check | Expected | Result |
|-------|----------|--------|
| Click any left-panel tab | Active state = cyan text + cyan border-bottom (not blue) | — |
| Hover non-active tab | Background brightens, text turns lighter | — |
| Click 📚 Sheets tab | Sheet group cards with cleaner padding (12px font, 6×14 padding) | — |
| Click a sheet item | Background tint + cyan text on active item; bold weight | — |

## Manual Checklist — HT-26 Summary Widget + Canvas Top Bar

| Check | Expected | Result |
|-------|----------|--------|
| Open app fresh (no PDF) | Summary widget HIDDEN, no floating overlay on empty state | — |
| Open a PDF | Summary widget auto-appears in saved position | — |
| Click ✕ on widget | Widget hides; `📊 สรุปผลการวัด` show-button appears | — |
| Open another PDF | Widget stays hidden (respect manual close) | — |
| Click show-button | Widget reappears, `_manuallyHidden` cleared | — |
| Canvas top bar | Single unified pill (rounded, dark rgba bg, backdrop blur), 7 spans inline with cyan `<b>` highlights | — |
| Zoom to 50% / 100% / 200% / 400% | Top bar pill stays visible, doesn't break layout, doesn't clip | — |

---

# Previous: Menu Bar / Canvas Overlay Z-Index Fix

Branch: main

Date: 2026-05-14

## Result

Automated PASS (py_compile + smoke 16/16, `MENU_OK` + `MAIN_UI_OK` green; `MAIN_UI_OK.workspaceRect.top = 94`). Manual verification **PENDING** — headless Chromium cannot detect z-index paint/stacking bugs, so the checklist below must be run in real Chrome before this sprint is considered closed.

## Why this sprint

User report: top menu bar was being overlapped by canvas overlays. Two root causes — `.menu-bar` had `z-index:100` but no `position` (so z-index never applied), and `#check-panel` started at `top:var(--topbar-h)` (22px) covering the menu + ribbon. Fix re-layered: canvas overlays (≤700) < loupe / recent-dropdown (8998–8999) < menu-bar + dropdowns (9000) < `#setup-overlay` (9001) < modals `.panel` / `#export-panel` / `#pgmgr-overlay` / `#scale-mgr-overlay` (9002).

## Manual Checklist — Z-Index / Stacking (the core fix)

| Check | Expected | Result |
|-------|----------|--------|
| Open any top-level menu dropdown while Summary Widget is visible | Dropdown paints **above** the widget | — |
| Open a menu dropdown while Draw Bar is up (start drawing an area, leave bar visible) | Dropdown above draw bar | — |
| Open a menu dropdown while a canvas context menu / object picker is open | Dropdown above ctx-menu / obj-picker | — |
| Enable Loupe (🔍), hover canvas near top edge, then open a menu dropdown | Dropdown wins — loupe does not paint over it | — |
| Open recent-project dropdown (📁 Project button) | Shows below ribbon button, not clipped, sits below menu-bar dropdowns | — |
| Open Review panel (`#check-panel`) | Starts **below** menu bar + ribbon (top ≈ 94px) — does not cover them | — |
| Open Scale Manager overlay | Full-screen modal covers menu bar; its buttons clickable | — |
| Open Page Manager overlay | Same — menu bar covered by modal backdrop, interactive | — |
| Open Page Setup (`#setup-overlay`) | Full-screen above menu bar; buttons clickable | — |
| Open Export panel | Centered card above menu bar | — |

## Manual Checklist — Dropdown Close Behavior (regression — not touched this sprint)

| Check | Expected | Result |
|-------|----------|--------|
| Click outside an open menu dropdown | Closes | — |
| Press `Escape` with a dropdown open | Closes (not covered by smoke marker — verify) | — |
| Select an item in a dropdown | Closes + action runs | — |
| Open a different top-level menu while one is open | First closes, second opens | — |

## Manual Checklist — Workflow Regression (CSS change → confirm layout intact)

| Check | Expected | Result |
|-------|----------|--------|
| Open PDF | Page renders, no layout shift | — |
| Draw Area + name panel | Works | — |
| Save .bmaplan + reload | Round-trip restores | — |
| Export XLSX | File generates | — |

---

# Previous: Phase G — Menu Wiring + Measure/Layer Power-up

Branch: feature/menu-power-up

Date: 2026-05-11

## Result

Automated PASS (smoke, 15 OK markers including MENU_OK). Per-page layer memory bug fixed. 6 functional dropdown menus wired.

## Manual Checklist — UI structure tracks mockup v3

| Check | Expected | Result |
|-------|----------|--------|
| Title bar (22px) with 3 win-btn dots + filename label | Visible | — |
| Menu bar (28px) with `BMA` logo + 13 menu items + phase badge | Visible | — |
| Ribbon (44px) with 6 groups (Quick / Scale / Page / Measure / Edit / Review-Export) | Visible | — |
| Left panel — 3 tabs (Sheets / Objects / Properties) | Tabs toggle | — |
| Canvas top bar | Visible inside workspace | — |
| Right panel — Layers + Selected Object | Visible | — |
| Status bar — Tool / Scale / Objects / Warnings / Layer / Save / Page | Visible | — |
| Summary Widget — 4 tabs (พื้นที่ / รายชั้น / ที่ดิน / แจ้งเตือน) | Tabs switch, drag works | — |
| Palette matches mockup (#1a1d21 bg, #22262c surface, #0a84ff accent) | Looks consistent | — |
| No dead Layout Options popup, no Workflow card, no Quick Tag bar | Gone | — |

## Manual Checklist — Workflow Regression

| Check | Expected | Result |
|-------|----------|--------|
| Open PDF | Page renders | — |
| Set Scale | Calib mode → polygon → area shown | — |
| Page Setup | Overlay opens | — |
| Draw Area (`btn-area`) | Polygon drawn, name panel opens | — |
| Draw Opening (`btn-opening`) | Linked to parent | — |
| Right panel layers list | Layers visible per page type | — |
| Save .bmaplan + reload | Round-trip restores | — |
| Export XLSX | File generates | — |
| Real 45-page PDF | Loads, rotation works | — |

---

# Previous: Mockup V3 Alignment — Phase A (Subtractive Removal)

Branch: feature/mockup-v3-alignment

Date: 2026-05-11

## Result

Automated PASS (py_compile + smoke + full). Visual UI looks similar to before — just less clutter in sidebar.

## Manual Checklist — Removed Elements (must be GONE)

| Check | Expected | Result |
|-------|----------|--------|
| `⚙ Layout` button in topbar | Gone | — |
| Layout Options modal popup | Gone | — |
| Inspection panel in left sidebar | Gone (no "สถานะการตรวจ" card) | — |
| Workflow card in left sidebar | Gone (no "Workflow" with 6 steps) | — |
| Review Warnings widget | Gone | — |
| Export Ready widget | Gone | — |
| Quick Tag bar (🏗 / 📐 / 📏 / 🔍 / 🚫) | Gone | — |

## Manual Checklist — No Regressions

| Check | Expected | Result |
|-------|----------|--------|
| Open PDF | Works, page renders | — |
| Set Scale (Set Scale button in topbar) | Calib mode activates, polygon drawn, area shown | — |
| Page Setup (Page Setup button) | Overlay opens, tag grid renders | — |
| Area drawing (tool-row Area button) | Polygon drawn, name panel opens, area in measure-result | — |
| Opening drawing | Opening drawn, linked to parent | — |
| Right panel layers | Layers list visible per page type | — |
| Save .bmaplan | File saves, reload restores all data | — |
| Export XLSX | File generates, summary matches UI | — |
| Real PDF (45 pages) | Loads, can navigate, rotation works | — |

---

# Previous: Widget / Menu Placement System

Date: 2026-05-11

## Result

Automated PASS (py_compile + smoke + full). Manual viewport check below.

## Manual Checklist — Widget / Menu Placement Section

| Check | Expected | Result |
|-------|----------|--------|
| Open Layout Options panel | Panel appears, "G. Widget / Menu Placement" section visible | — |
| Search box filters list | Typing e.g. `review` filters list to Review Warnings | — |
| Category filter | Changing category to "Layer" leaves only Layer-category rows | — |
| Visibility toggle for Review Warnings | Widget hides/shows in left panel | — |
| Region select moves Review Warnings to right | Widget appears in right panel under Layers | — |
| Region select returns Review Warnings to left | Widget returns to left panel above Sheets | — |
| Order input changes display order in left zone | Higher order moves widget visually lower | — |
| Size = `collapsed` for Review Warnings | Body collapses to title only; state preserved | — |
| Size = `full` for Review Warnings | Widget body shows again | — |
| Reset button | All widgets restored to defaults; locked widgets re-snap to original parents | — |
| Reload page after changes | Custom placement persists from localStorage | — |
| Locked widget region select is disabled | Sheets / Objects / Properties / Layer Context / Current Page Layers / Page Info / Inspection Status / Scale Status cannot be moved by region select | — |

## Workflow Regression Checklist

| Check | Expected | Result |
|-------|----------|--------|
| Left panel scroll (Sheets / Objects / Properties) | Scrolls smoothly | — |
| Right panel scroll (Layers) | Scrolls smoothly | — |
| Current Page Layers still visible | All page-tag layers listed | — |
| Active Layer dropdown still works | Switching layer applies | — |
| Sidebar tabs (Sheets / Objects / Properties) | Toggling tabs works as before | — |
| Set Scale → Calibrate → Confirm | Still works, no regression | — |
| Draw Area | Polygon drawn, area shown, summary updated | — |
| Draw Opening | Opening drawn and linked, summary updated | — |
| Export Excel | XLSX file downloads | — |
| Export Current Page + Annotations | PDF file downloads | — |
| Save Project / Load Project | Round-trip works | — |
| Layout Options → Reset to Current Stable | Removes v3 body classes; widget placement unaffected | — |
| Layout Options → Reset Panel Layout | Restores 236/300 widths and docked modes | — |

## Notes

- Hidden widgets via placement use `.widget-hidden { display:none !important; }`; state is preserved.
- Collapsed size hides body details (`.widget-body`, `.widget-link`, `.widget-links-row`, `.wf-row`) but keeps DOM and titles.
- Movable widgets default to left (their original region). They are re-parented to `#wp-right-zone` only when explicitly placed in right.
