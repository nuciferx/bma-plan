# Plan: Align Current UI to Mockup V3

## Context

**Why this is being done:** Current `proto/ui.html` (1708 บรรทัด) ค่อยๆ สะสมระบบเสริมหลายชั้น (UI Layout Options, Panel Layout Options, Widget/Menu Placement System, Inspection Panel, Workflow Card, ฯลฯ) จน UI ห่างจาก mockup ต้นแบบ V3 (`docs/design/bma-plan-mockup-v3.html`) ไปมาก ผู้ใช้สั่งให้ตัดส่วนที่เกินออก ให้เหลือเฉพาะที่จำเป็นและตรงกับ mockup

**Source of truth:** `F:\My Drive\01 project\ai\bma-plan\docs\design\bma-plan-mockup-v3.html` (1943 บรรทัด — title bar + menu bar + ribbon + 3-pane main + status bar + draggable summary widget 4 tabs)

**Outcome:** UI ที่เรียบ ตรง mockup, มีฟังก์ชั่นการวัดครบ และโค้ดเล็กลงอย่างมาก

---

## Assumptions (ไม่ได้รับคำตอบจาก /AskUserQuestion — โปรดยืนยันก่อน implement)

| ประเด็น | สมมุติฐาน |
|---|---|
| Branch | สร้าง **`feature/mockup-v3-alignment`** ใหม่จาก `main` (ไม่ต่อจาก feature/summary-widget-floating เพราะ scope ต่างกัน) |
| Menu bar | **Visual-only ก่อน** — แสดง 13 menu items, hover state, แต่ไม่มี dropdown functionality (รอ phase ถัดไปถ้าต้องการ) |
| Removed systems | **Hard remove** — ลบโค้ดทิ้ง และลบ assertions ใน e2e_ui_test.py ที่เกี่ยวข้อง |
| Summary widget | **อัปเดตเป็น 4 tabs ตาม mockup** (พื้นที่/รายชั้น/ที่ดิน/แจ้งเตือน) + เพิ่ม drag |

---

## Hard Forbidden (ห้ามแตะ)

- `proto/server.py`
- Export logic, save/load logic, `.bmaplan` schema
- `polyMetrics()`, `polyAreaM2()`, `polySelfIntersects()`, `pdfToC()`, `cToPdf()`, scale math, coordinate conversion
- Snap algorithm
- ห้ามเพิ่ม OCR / AI / Rule Engine / FAR/OSR/setback pass-fail / legal checker

---

## Mockup Structure (ต้องสร้าง)

```
.title-bar (22px)        — macOS-style window dots + filename label
.menu-bar (28px)         — app-logo "BMA" + 13 menu items + phase badge
.ribbon (44px)           — 6 groups: Quick / Scale / Page / Measure / Edit / Review-Export
.main (flex 1)
  .left-panel (220px)    — 3 tabs: Sheets/Objects/Properties + body
  .canvas-wrap           — canvas-top-bar + PDF canvas + summary widget overlay
  .right-panel (200px)   — Layers list + Selected Object footer
.status-bar (~28px)      — tool/scale/object count/warnings/layer/save state

#summaryWidget (floating, draggable, bottom-right by default)
  header (drag handle + page badge + collapse + close)
  4 tabs: พื้นที่ / รายชั้น / ที่ดิน / แจ้งเตือน
  footer: Review + Export XLSX buttons
#swShowBtn (hidden until widget hidden)
```

**CSS color tokens จาก mockup** (เปลี่ยน palette เล็กน้อย):
- `--bg:#1a1d21` (เดิม `#090b10` ใน app.css)
- `--surface:#22262c`, `--surface2:#2a2f37`, `--surface3:#32383f`
- `--border:#3a404a`, `--border2:#454c58`
- `--accent:#0a84ff`, `--green:#30d158`, `--yellow:#ffd60a`, `--red:#ff453a`
- `--ribbon-h:44px`, `--menu-h:28px`, `--left-w:220px`, `--right-w:200px`

---

## Implementation Phases

### Phase A — Subtractive Removal

ลบโค้ดและ DOM ของระบบที่เกินจาก mockup

**1. `proto/ui.html` — ลบ DOM:**
- `#ui-layout-panel` modal (lines ~294-390) — UI Layout Options popup
- `#btn-ui-layout` button ใน topbar (line 27)
- `#inspection-panel` ใน sidebar (and `.isp-*` controls)
- `#workflow-card` ใน sidebar
- `#widget-review-warnings`, `#widget-export-ready` (เนื้อหาย้ายลง Summary Widget)
- `#wp-left-zone`, `#wp-right-zone` (widget placement zones)
- `#quick-tag-bar` (รวมเข้า menu bar / ribbon)
- `#tool-row` + `#float-toolbar` (replace ด้วย `.ribbon`)
- Multi-zone topbar `.topbar-zone-a/b/c` (replace ด้วย title-bar + menu-bar)

**2. `proto/ui.html` — ลบ JS systems (ทั้งบล็อก):**
- UI Layout Options system: `loadUiLayout`, `saveUiLayout`, `applyUiLayout`, `setUiLayoutOption`, `applyUiLayoutPreset`, `toggleUiLayoutPanel`, `closeUiLayoutPanel`, `UI_LAYOUT_KEY`, `uiLayout` state (~lines 1388-1430)
- Panel Layout Options: `loadPanelLayout`, `savePanelLayout`, `applyPanelLayout`, `setPanelLayoutOption`, `resetPanelLayout`, `_updatePanelLayoutPanelState`, `PANEL_LAYOUT_KEY` (~lines 1445-1495)
- Widget/Menu Placement: `WIDGET_MENU_REGISTRY`, `getDefaultWidgetPlacement`, `loadWidgetPlacement`, `saveWidgetPlacement`, `normalizeWidgetPlacement`, `resetWidgetPlacement`, `setWidgetPlacementOption`, `applyWidgetPlacement`, `renderWidgetPlacementOptions`, `filterWidgetPlacementList`, `_captureWidgetOriginalParents`, `WIDGET_PLACEMENT_KEY` (~lines 1498-1665)
- Inspection panel: `updateInspectionPanel()`, `toggleInspectionPanel()`, `inspPanelCollapsed`, badges/state (~line 615-617)
- `updateWidgets()` (lines 618) — เนื้อหาย้ายไป refreshSummaryWidget
- Init calls: ลบ `loadUiLayout(); loadPanelLayout(); loadWidgetPlacement();` (line 1666-1668)

**3. `proto/static/css/app.css` — ลบ CSS:**
- `.wp-zone`, `#wp-left-zone`, `#wp-right-zone`
- `.widget-hidden`, `.widget-size-collapsed/small/medium/large/full`
- `.ulp-*`, `#ui-layout-panel`, `.ulp-section-*`, `.ulp-opt`, `.ulp-wp-*`, `.wp-row`
- `.isp-*` (inspection panel)
- `#float-toolbar`, `.ft-btn`, `.ft-group`, `.ft-sep`, `#tool-row`, etc. (เปลี่ยนเป็น .ribbon)
- `#widget-review-warnings`, `#widget-export-ready` styles (ถ้ามี)
- `.topbar-zone-*` (จะถูกแทนที่)

**4. `proto/e2e_ui_test.py` — ลบ assertions:**
- `panelLayoutControlsExist`, `panelLayoutKeyWritten`, `panelResetRestoresDefaults`, `panelCollapseWorks`
- `widgetPlacementRegistryExists`, `widgetPlacementHelpersExist`, `widgetPlacementSearchBox`, `widgetPlacementListRendered`, `widgetPlacementKeyWritten`, `widgetVisibilityToggleWorks`, `widgetOrderInputWorks`, `widgetRegionMoveWorks`, `widgetSizeClassApplies`, `widgetPlacementResetWorks`, `widgetPlacementMalformedJsonSafe`, `widgetLockedRespected`, `widgetLeftPanelScrollOk`, `widgetRightPanelScrollOk`, `widgetCurrentPageLayersVisible`
- `inspectionPanelVisible`, `inspectionPanelInSidebar`, `inspectionPanelNotInCanvas`, `inspectionPanelWorkflowVisible`, `inspectionPanelContextVisible`, `inspectionPanelToggleWorks`
- `optionsBtnVisible`, `optionsPanelExists`, `currentStablePresetExists`, `mockupV3PresetExists`, `optionsPanelOpens`, `topModeSwitchNoCrash`, `leftModeSwitchNoCrash`, `rightModeSwitchNoCrash`, `widgetsModeSwitchNoCrash`, `localStorageKeyWritten`, `resetRestoresCurrentStable`
- `reviewWarningWidgetVisible`, `exportReadyWidgetVisible` (ย้ายไปทดสอบ Summary Widget tabs แทน)
- `toolbarInToolRow`, `toolRowAboveWorkspace` (ทำแทนด้วย `ribbonAboveMain`)

**5. `proto/e2e_ui_test.py` — เพิ่ม assertions ใหม่:**
- `titleBarVisible` — `.title-bar` element + filename label
- `menuBarHasItems` — `.menu-bar` มี ≥10 menu items
- `ribbonHasGroups` — `.ribbon .ribbon-group` ≥5 groups
- `ribbonContainsMeasureTools` — Area/Opening/Land/Dimension buttons ปรากฏใน ribbon
- `leftPanelTabsThree` — 3 tabs (Sheets/Objects/Properties)
- `rightPanelHasLayersAndProperties` — Layer list + selected-object footer
- Summary Widget assertions (ปรับเป็น 4 tabs)

### Phase B — Structural Rebuild (Header)

ใน `proto/ui.html` หลังลบเสร็จ ใส่โครงสร้างใหม่ตามลำดับ:

```html
<div class="title-bar">
  <div class="win-btn close"></div>
  <div class="win-btn min"></div>
  <div class="win-btn max"></div>
  <div class="title-bar-label" id="title-bar-label">BMA-Plan — <ชื่อไฟล์></div>
</div>

<div class="menu-bar" id="menuBar">
  <div class="app-logo">BMA</div>
  <div class="menu-item" data-menu="file">File</div>
  ... <!-- 13 items: File, Edit, View, Project, Scale, Page, Measure, Object, Layer, Review, Export, Workspace, Tools, Help -->
  <div class="phase-badge">Phase 1 · Measurement Only</div>
</div>

<div class="ribbon">
  <div class="ribbon-group"> <!-- Quick: Open PDF / Save / Recover --> </div>
  <div class="ribbon-group"> <!-- Scale: Set Scale / Scale Mgr / scale-badge --> </div>
  <div class="ribbon-group"> <!-- Page: Page Mgr / Set Floor --> </div>
  <div class="ribbon-group"> <!-- Measure: Select/Pan/Area/Opening/Land/Dimension/North/Label --> </div>
  <div class="ribbon-group"> <!-- Edit: Undo/Redo/Delete --> </div>
  <div class="ribbon-group"> <!-- Review/Export: Review / Export XLSX --> </div>
</div>
```

**ทุก ribbon button ต้องชี้ไปยังฟังก์ชั่นเดิม:**
- "เปิด PDF" → reuse `#upload-btn` logic
- "Save" → `saveProject()`
- "Set Scale" → `setMode('calib')` (ผ่าน guard `if(totalPages)`)
- "Page Setup" → `openSetup()`
- "Select" → `setMode('sel')`, "Pan" → `setMode('pan')`
- "Area" → `activateAreaTool('room')`, "Opening" → `toggleOpening()`, "Land" → `activateAreaTool('land')`
- "Dimension" → `setMode('dist')`
- "North" → `setMode('north')`
- "Undo" → `undo()`, "Redo" → `redo()`, "Delete" → `deleteSelectedObject()`
- "Review" → `openCheckPanel()`, "Export XLSX" → `openExportPanel()`

### Phase C — Structural Rebuild (Main + Panels)

```html
<div class="main">
  <div class="left-panel">
    <div class="panel-tabs">
      <div class="panel-tab active" data-mode="sheets">Sheets</div>
      <div class="panel-tab" data-mode="objects">Objects</div>
      <div class="panel-tab" data-mode="properties">Properties</div>
    </div>
    <div class="panel-body">
      <div id="sidebar-content"> <!-- pages list (existing logic) --> </div>
      <div id="lp-objects-content" hidden> <!-- objects per page (existing) --> </div>
      <div id="lp-properties-content" hidden> <!-- properties (existing) --> </div>
    </div>
  </div>

  <div class="canvas-wrap">
    <div class="canvas-top-bar" id="canvas-top-bar"><!-- page/zoom/scale info --></div>
    <canvas id="cv"></canvas>
    <!-- summary widget overlay (positioned absolute inside canvas-wrap or fixed) -->
  </div>

  <div class="right-panel">
    <div class="right-panel-header">Layers <button id="add-layer-btn">+</button></div>
    <div id="rp-content"><!-- layer rows (existing buildRightPanel logic) --></div>
    <div class="selected-object-footer" id="selected-object-footer">
      <!-- name / category / tag / floor / use / area for selected object -->
    </div>
  </div>
</div>

<div class="status-bar">
  <div class="status-bar-left">
    <span id="lbl-mode">Pan</span> · <span id="lbl-scale">—</span> ·
    <span>Objects: <span id="lbl-objects">0</span></span> ·
    <span>Warnings: <span id="lbl-warnings">0</span></span> ·
    <span>Layer: <span id="lbl-layer">—</span></span>
  </div>
  <div class="status-bar-right">
    <span id="lbl-save-state">—</span> · <span id="bb-page-name">—</span>
  </div>
</div>
```

**ID ที่ใช้ฟังก์ชั่นเดิมต้องเก็บไว้:** `#cv`, `#sidebar-content`, `#lp-objects-content`, `#lp-properties-content`, `#rp-content`, `#canvas-top-bar`, `#lbl-mode/scale/objects/warnings/layer/save-state`, `#bb-page-name`, `#scale-badge`, `#zoom-val`, `#page-lbl`, `#status`, `#measure-result`, `#snap-cur`, `#snap-lbl`, modals ทั้งหมด (calib-panel, name-panel, land-edge-panel, setup-overlay, check-panel, export-panel, scale-mgr-overlay, pgmgr-overlay, obj-picker, ctx-menu, loupe)

### Phase D — Summary Widget Update (4 tabs)

อัปเดต `#summary-widget` จาก 3 tabs เป็น 4 tabs ตาม mockup:

| Tab | Content |
|---|---|
| **พื้นที่** (area) | Total gross + breakdown by use category (ใช้เกษตร/พาณิชย์/ผังเมือง ฯลฯ) + deductions + net + measured-objects chips |
| **รายชั้น** (floor) | สรุป area per page/floor — measured pages list + unmeasured pages chips + total |
| **ที่ดิน** (site) | ที่ดิน area + ด้านที่ดิน (front/left/right/back from `polyEdgeTags`) + setbacks + north angle |
| **แจ้งเตือน** (warn) | Required-before-export warnings + object issues + passed checks |

เพิ่ม:
- Drag handle ใน header (mousedown → mousemove → mouseup → save position)
- Page badge ใน header (`หน้า ${curPage} / ${totalPages}`)
- Footer 2 buttons: "Review (${warnCount})" + "Export XLSX"
- Hide → แสดงปุ่ม `#sw-show-btn` (ปุ่มลอย 📊 สรุปผลการวัด)

ปุ่ม Review เรียก `openCheckPanel()`, Export XLSX เรียก `openExportPanel()` (reuse).

State key: เปลี่ยนเป็น `bmaPlan.summaryWidget.v2` (รวม drag position) — fallback safe สำหรับ v1

### Phase E — CSS Sync

**`proto/static/css/app.css`:**
- เปลี่ยน CSS variables (`:root`) ให้ใช้ palette mockup
- เพิ่ม styles: `.title-bar`, `.win-btn.*`, `.menu-bar`, `.menu-item`, `.app-logo`, `.phase-badge`
- เพิ่ม styles: `.ribbon`, `.ribbon-group`, `.ribbon-btn`, `.ribbon-sep`, `.ribbon-label`
- เพิ่ม styles: `.main`, `.left-panel`, `.right-panel`, `.canvas-wrap`, `.panel-tabs`, `.panel-tab`
- เพิ่ม styles: `.layer-row` (รูปแบบใหม่), `.selected-object-footer`
- ปรับ `.status-bar` ให้เป็น flex แบบ mockup
- **ปรับ Summary Widget** styles ให้ตรง mockup (header gradient, tab styling, footer buttons)
- Canvas grid pattern background (CSS gradient bg)

### Phase F — Tests + Docs

**Run:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

**Stop conditions (ห้าม PASS ถ้าเจอ):**
- Area drawing fails
- Opening drawing fails
- Save / load fails
- Export fails
- Right panel layers disappear
- Measurement result เปลี่ยน
- Scale calibration เปลี่ยน

**Docs ที่ต้องอัปเดต:**
- `PATCH_SUMMARY.md` — sprint "Mockup V3 Alignment"
- `TEST_RESULT.md` — assertions list ใหม่
- `UI_MANUAL_TEST.md` — manual checklist ตาม mockup
- `FINAL_REPORT_FOR_CHATGPT.md` — outcome
- `CURRENT_STATUS.md` — Phase 1 status update
- `log.md` — session record

---

## Critical Files to Modify

| File | Changes |
|---|---|
| `proto/ui.html` | ลบ ~700-900 บรรทัด (Layout/Panel/Widget systems + DOM), เพิ่ม ~400 บรรทัด (title-bar + menu-bar + ribbon + restructured panels), อัปเดต Summary Widget เป็น 4 tabs |
| `proto/static/css/app.css` | เปลี่ยน palette, ลบ `.ulp-*`/`.isp-*`/`.ft-*`/`.wp-*`, เพิ่ม `.ribbon-*`/`.menu-*`/`.title-bar`/`.panel-tabs`/`.layer-row` ใหม่ |
| `proto/e2e_ui_test.py` | ลบ ~35 assertions ของระบบที่ถูกตัด, เพิ่ม ~8 assertions ของโครงใหม่ |

---

## Reused Functions (ไม่แตะ)

| Function | File | Purpose |
|---|---|---|
| `loadPage(n)` | `proto/ui.html` | โหลด PDF + restore objects |
| `finishCurrentArea()` | `proto/ui.html` | จบ polygon/opening |
| `polyMetrics(poly, pg)` | `proto/ui.html` | คำนวณ area |
| `polyAreaM2(pts)` | `proto/ui.html` | area in m² |
| `pdfToC`, `cToPdf` | `proto/ui.html` | coord conversion |
| `getScaleForPage(pg)` | `proto/ui.html` | scale ของหน้า |
| `setMode(m)` | `proto/ui.html` | สลับ tool |
| `activateAreaTool(type)` | `proto/ui.html` | เริ่ม area/land |
| `toggleOpening()` | `proto/ui.html` | toggle opening mode |
| `saveProject`, `applyLoadedProject` | `proto/ui.html` | save/load .bmaplan |
| `openSetup`, `openExportPanel`, `openCheckPanel` | `proto/ui.html` | open modals |
| `buildSidebar()` | `proto/ui.html` | render pages |
| `buildRightPanel()` | `proto/ui.html` | render layers (เปลี่ยน wrapping แต่ logic เดิม) |
| `updateBottomBar()` | `proto/ui.html` | update status bar |
| `redraw()` | `proto/ui.html` | canvas redraw |
| `pushUndo`, `undo`, `redo` | `proto/ui.html` | undo/redo |
| `escHtml` | `proto/ui.html` | HTML escape |
| `fetchAnalyse(n)` | `proto/ui.html` | analyse PDF |

---

## Verification (End-to-end Test Plan)

1. **Static compile check:**
   ```
   python -m py_compile proto/server.py proto/e2e_ui_test.py
   ```
   Expected: PASS

2. **Smoke test (manual + automated):**
   ```
   python proto/e2e_ui_test.py smoke
   ```
   Expected: PASS — รวมถึง assertions ใหม่ทั้งหมด

3. **Full test:**
   ```
   python proto/e2e_ui_test.py full
   ```
   Expected: PASS — รวม VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, ANNOT_OK, REAL_OK ครบ

4. **Manual browser test (`python proto/server.py` แล้วเปิด `http://localhost:8001`):**
   - [ ] Title bar แสดง filename ปัจจุบัน
   - [ ] Menu bar แสดง 13 items
   - [ ] Ribbon แสดง 6 groups, ทุกปุ่มกดได้
   - [ ] Left panel: 3 tabs สลับได้, Sheets แสดงรายการหน้า
   - [ ] Canvas top bar แสดง page/zoom/scale info
   - [ ] Right panel แสดง layers + selected-object footer
   - [ ] Status bar แสดงข้อมูลครบตามตำแหน่ง mockup
   - [ ] Summary Widget: 4 tabs (พื้นที่/รายชั้น/ที่ดิน/แจ้งเตือน), draggable, collapse, hide/show
   - [ ] Open PDF → drawn area → polygon shows in canvas และใน Summary Widget tabs
   - [ ] Save .bmaplan → reload → ทุกอย่างกลับมาเหมือนเดิม
   - [ ] Export XLSX → ไฟล์ออกถูกต้อง

5. **Regression check:**
   - [ ] เปิด `feature/summary-widget-floating` PDF เดิม → วัดได้ค่าเท่าเดิม
   - [ ] Scale calibration → ค่าตรงเดิม
   - [ ] Save/load roundtrip → ค่าเท่าเดิม

---

## Risk Assessment

| Risk | Mitigation |
|---|---|
| ลบโค้ดผิด ทำให้ฟังก์ชั่นวัดพัง | ทำ subtractive phase ก่อน แล้ว run smoke ทันที |
| ID ที่ฟังก์ชั่นเดิมใช้ถูกลบ | ตรวจ grep ก่อนลบทุก ID ที่อยู่ใน List "ID ที่ใช้ฟังก์ชั่นเดิมต้องเก็บ" |
| CSS palette เปลี่ยน อาจกระทบ readability | ใช้ palette จาก mockup โดยตรง (ผ่านการออกแบบมาแล้ว) |
| Summary Widget v1→v2 state ใช้คีย์เก่า | เก็บ fallback อ่าน v1 ได้ ถ้าไม่มี v2 |
| E2E test fail เพราะ assertions เก่า | ลบ/แทนที่ assertion ทันทีในขั้นเดียวกับการลบ DOM |
| Time/size | คาดว่าใหญ่ — ควรแบ่ง commit เป็น phase A/B/C/D/E/F แต่ละ commit รัน smoke ผ่าน |

---

## Implementation Order (recommended)

1. Branch off main: `git checkout -b feature/mockup-v3-alignment`
2. **Phase A** — subtractive (ลบทั้งระบบที่เกิน) → commit + smoke
3. **Phase B** — title bar + menu bar + ribbon → commit + smoke
4. **Phase C** — restructure left/right panels + status bar → commit + smoke + full
5. **Phase D** — Summary Widget 4 tabs + drag → commit + smoke
6. **Phase E** — CSS sync (palette + new styles) → commit + smoke
7. **Phase F** — update tests + docs → commit + smoke + full → ready to evaluate

แต่ละ commit ห้าม push ออก main จนกว่าจะได้รับอนุมัติ
