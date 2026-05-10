# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-10

### [session] Manual Acceptance Test — 20/20 PASS

**Scope:** 8-phase batch (Panel Scroll, Mockup V3 Theme, Save/Save As/Overwrite, Open/Recent Project, Annotated PDF Export Current+All).

**Method:** Playwright acceptance probe (`proto/acceptance_probe.py`) + code review. Evidence labels: AUTO / CODE / HUMAN.

**Results:** 20 TCs — all PASS. No BLOCKER. No MAJOR.

**Bug found:**
- TC-12-B1 (MINOR): `lbl-save-state` stays "Manual save required" after `pushUndo()` before first save. Guard `if(ss.textContent !== "Manual save required")` in `_setDirty()` blocks transition. Cosmetic — save/load unaffected. Severity: MINOR.

**Baseline re-confirmed:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

**Output:** `docs/status/MANUAL_ACCEPTANCE_TEST_2026-05-10.md`

**Root commit:** (docs-only — see next commit)

---

### [session] UI Layout Options — PASS

**Sprint:** RUN_UI_LAYOUT_OPTIONS_MOCKUP_V3

**What changed:**
- `proto/ui.html`: Added `#btn-ui-layout` button in topbar zone-a (after Page Setup). Added `#ui-layout-panel` floating panel with sections A–D (Top/Left/Right/Widgets), 5 presets (Current Stable / Mockup V3 / Inspection Focus / Layer Focus / Compact), Reset row. Added JS: `loadUiLayout()`, `saveUiLayout()`, `applyUiLayout()`, `setUiLayoutOption()`, `applyUiLayoutPreset()`, `toggleUiLayoutPanel()`, `closeUiLayoutPanel()`. localStorage key: `bmaPlan.uiLayoutOptions.v1`. Outside-click auto-close.
- `proto/static/css/app.css`: Added panel styles, v3 mode CSS classes (`body.ui-top-v3`, `body.ui-left-v3`, `body.ui-right-v3`, `body.ui-widgets-v3`). v3 modes are CSS-only visual overrides — no elements hidden, no DOM restructuring.
- `proto/e2e_ui_test.py`: 11 new JS assertions (optionsBtnVisible, optionsPanelExists, currentStablePresetExists, mockupV3PresetExists, optionsPanelOpens, topModeSwitchNoCrash, leftModeSwitchNoCrash, rightModeSwitchNoCrash, widgetsModeSwitchNoCrash, localStorageKeyWritten, resetRestoresCurrentStable) + 11 Python assertions.

**Proto commit:** `087c769`

**Tests:** py_compile PASS · smoke PASS · full PASS. All 11 new assertions True.

---

### [session] Page-Scoped Layer Implementation Batch — PASS (6 sprints)

**Sprints completed (all full E2E PASS):**
- RUN_LAYER_SCOPE_AUDIT (docs-only): audited all `layerVis`/`layerLock`/`activeLayer` usage; confirmed export is layer-name-free.
- RUN_PAGE_LAYER_INSTANCE_MODEL `ed9944d`: added `DEFAULT_LAYER_PRESETS`, `ensurePageLayers()`, `_syncPageLayersToGlobals()`, and all helper functions. Global `layerVis`/`layerLock` kept as backward-compat bridge.
- RUN_PAGE_TYPE_LAYER_PRESETS `eefab31`: `buildRightPanel()` layer rows now driven by `getCurrentPageLayers()`. E2E assertion updated for site-preset labels.
- RUN_OBJECT_LAYER_VALIDATION `94db3d9`: `validateObjectLayerScope()` assigns `pageIndex`/`layerSlug`/`layerId` to all existing objects on `restorePage()`.
- RUN_LAYER_TOOL_AWARENESS `a6c67e7`: `updateActiveLayerControl()` syncs active slug to `setActiveLayerForPage()`; `finishCurrentArea()` and `finishPathLike()` call `assignDefaultObjectLayer()` on new objects.
- RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR (docs-only): confirmed export groups by `semanticTag`/`reportTarget` — no layer name in any calculation or export key.

**Root proto commit at batch end:** `a6c67e7`

**No forbidden items touched.** All 6 sprints committed. Full E2E green after each source sprint.

---

### [session] Page-Scoped Layer Model Lock — PASS (docs-only)

**Sprint:** RUN_PAGE_SCOPED_LAYER_MODEL_LOCK

**What changed (docs only — no source code touched):**
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` — created: canonical page-scoped layer spec
  (Project→Page→Layer→Object model, invariants, preset behaviour, calculation rules, forbidden patterns)
- `docs/design/LAYER_MODEL.md` — created: reference index, current status table, target model summary
- `docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md` — created: full audit of current implementation vs. target
  (page model, layer model, object fields, area summary, gap list G1–G8, risk table, implementation sequence)
- `docs/status/NEXT_ACTIONS.md` — updated: prepended 6 layer implementation sprints before UI polish sprints

**Audit findings:**
- Layers are currently **global** (`layerVis`, `layerLock` in JS) — not per-page
- Objects have no `layerId` or `pageId` field — layer derived from `areaType` at render time
- `pageStore[n]` has no `layers[]` array
- **Positive:** no calculation or export uses layer name — `semanticTag`/`reportTarget` correctly drive area summaries

**Tests:** Docs-only sprint — no source changed. Existing baseline remains valid.
- `proto/server.py` — not touched
- `proto/ui.html` — not touched

---

### [session] 8-Sprint UI/Measurement Usability Batch — PASS

**Sprints completed (all full E2E PASS):**
- Canvas Top Info Bar: `50d5d68` — non-blocking overlay with page/zoom/scale/tool/layer/coords
- Ribbon Toolbar Polish: `7461278` — .ft-group bg, .ft-btn.active glow + bottom border
- Right Layers Final Polish: `c947a2a` — ACTIVE badge on current layer row
- Page Floor Setup Panel: `9b8c505` — ⚠ warning badge on thumbnails with objects but no Scale
- Scale Manager Foundation: `adb412f` — audit modal showing per-page scale, trigger in export widget
- Review Warning Panel Polish: `c0b909e` — .cd-warn.error/.warning/.cd-severity-info CSS classes
- Export Ready Panel Polish: `56f06c2` — XLSX/Scale/Targets/Unlinked/Warnings checklist + Export/Scale links
- UI Visual Consistency Pass: `4a09693` — wf-row.current, layer hover, widget accent, workflow current state

**No forbidden items touched.** All 8 sprints committed with PASS. Full E2E green after each.

---

## 2026-05-09

### [session] Knowledge Capture — Static 404 Regression Lesson

**What changed (docs only — no source code):**
- `docs/process/TROUBLESHOOTING.md` — created: full diagnosis steps for static 404,
  WinError 10054, AUTO_MERGE.lock, correct server.py pattern with startup print.
- `docs/process/ANTI_PATTERNS.md` — created: 6 confirmed anti-patterns with root cause
  + correct alternative: guarded mount, CWD-relative paths, missing aiofiles, BOM in CSS,
  assuming E2E pass = browser renders correctly, not killing old server.
- `docs/status/KNOWN_ISSUES.md` — added Resolved Incidents table (3 incidents), pointer to TROUBLESHOOTING.md.
- `AGENTS.md` — added Section 8: Static Asset Verification: required server.py pattern,
  aiofiles dependency check, E2E assertion table, HTTP verification commands, BOM check.
- `docs/status/LATEST_STATUS.md` — updated sprint results table and latest commits.

**Tests:** No source changed. Baseline proto `a2099ec` remains valid.

---

### [session] Static 404 Fix (Critical Regression)

**Root causes:**
- `aiofiles` not installed — `StaticFiles` raises `RuntimeError` at init without it.
- `if _STATIC_DIR.exists(): app.mount(...)` guard — mount was attempted but the RuntimeError
  from missing `aiofiles` caused it to fail silently, leaving `/static/*` unregistered → 404.

**What changed:**
- `proto/server.py`: Removed `if _STATIC_DIR.exists()` guard. Mount now unconditional.
  Added `print(f"[static] serving from: {_STATIC_DIR}")` for startup confirmation.
- `proto/requirements.txt`: Added `aiofiles`.
- `proto/static/css/app.css`: Removed UTF-8 BOM.
- Installed `aiofiles==25.1.0` into active Python environment.

**HTTP verified (port 8001):**
```
/static/css/app.css         → 200 OK
/static/js/semantic-meta.js → 200 OK
/static/js/opening-parent.js → 200 OK
/                            → 200 OK
```

**Tests:** py_compile PASS · smoke PASS · full PASS (proto a2099ec)

---

### [session] Mockup Layout Mapping

**What changed (docs only — no source code):**
- Read `docs/design/bma-plan-mockup-v3.html` in full (title-bar, menu-bar, ribbon, left-panel,
  canvas-wrap, summary-widget, right-panel, status-bar).
- Read `proto/ui.html` for current structure map.
- Created `docs/design/MOCKUP_LAYOUT_MAPPING.md`:
  - Section A: existing UI structure (topbar, sidebar, workspace, right-panel, bottombar, float-toolbar)
  - Section B: mockup v3 intended structure
  - Section C: full mapping table (13 mockup areas mapped)
  - Section D: widget mapping (10 widgets: DONE / PARTIAL / MISSING)
  - Section E: gap classification (10 DONE, 9 SMALL POLISH, 4 MEDIUM IMPLEMENTATION, 2 LATER, 3 FORBIDDEN)
  - Section F: forbidden mockup areas (draggable widget, autosave, workspace save, legal/OCR/AI)
  - Section G/H: what is implemented vs. missing
- Created `docs/design/MOCKUP_IMPLEMENTATION_PLAN.md`:
  - 6 sequenced sprints with goal, files, risk, tests, stop conditions
  - Sprint 1 (Widget Polish, LOW), Sprint 2 (Canvas Top Bar, LOW-MEDIUM),
    Sprint 3 (Scale Manager, MEDIUM), Sprint 4 (Page Setup Table, LOW),
    Sprint 5 (Export Review, LOW), Sprint 6 (Visual Phase 1, HIGH)

**Tests:** No source changes — baseline 797a4a2 remains valid.

---

### [session] Static Asset Healthcheck

**What changed:**
- `proto/server.py`: Added `from pathlib import Path`. Changed `_STATIC_DIR` from
  `os.path.join(os.path.dirname(__file__), "static")` to
  `Path(__file__).resolve().parent / "static"` — always absolute, CWD-independent.
  Updated `os.path.exists` → `_STATIC_DIR.exists()`, mount → `directory=str(_STATIC_DIR)`.
- `proto/e2e_ui_test.py`: Added 4 JS evaluate keys + 4 Python assertions:
  `cssLinkPresent`, `cssVarLoaded`, `semanticMetaJsLoaded`, `openingParentJsLoaded`.

**Root cause:** `os.path.dirname("")` = `""`, so `os.path.join("", "static")` = `"static"`
(relative). Running `python server.py` from `proto/` with a bare `__file__` caused the
static mount guard (`os.path.exists`) to pass for the wrong CWD.

**Tests:** py_compile PASS · smoke PASS · full PASS (proto 797a4a2)

---

### [session] Visible Test Widgets UI

**What changed:**
- `proto/ui.html` (1111→1120 lines): Added `#widget-review-warnings` and `#widget-export-ready`
  divs in left sidebar after `#workflow-card`. Added `updateWidgets()` function (uses
  `currentWarningCount()`, `currentObjectCount()`, `getScaleForPage()`, `scaleLabel()`).
  Added `updateWidgets()` call at end of `updateBottomBar()`.
- `proto/static/css/app.css` (307→315 lines): Added `.widget-card`, `.widget-title`,
  `.widget-body`, `.widget-link`, `.widget-badge` classes with `.ok`, `.warn`, `.error` modifiers.
- `proto/e2e_ui_test.py`: Added 4 JS evaluate keys + 4 Python assertions:
  `scaleStatusWidgetVisible`, `pageInfoWidgetVisible`, `reviewWarningWidgetVisible`,
  `exportReadyWidgetVisible` — all confirmed True.

**Tests:** py_compile PASS · smoke PASS · full PASS (proto a2a6e81)

---

### [session] E2E Test Split Audit

**What changed:**
- Read proto/e2e_ui_test.py (1525 lines) in full.
- Mapped 17 test functions + 9 helper functions.
- Identified irreversible stateful pipeline: test functions share one page object; each
  depends on browser state produced by the previous test.
- Created `docs/design/E2E_TEST_SPLIT_AUDIT.md` with full structure map and risk analysis.
- Decision: AUDIT_ONLY_STOP — splitting test modules is not safe without weakening tests.
  Only helpers (~114 lines, 7.5%) are safely extractable, insufficient to justify refactor.

**Tests:** No code changes. Baseline from proto 9fa57a0 remains valid.

---

### [session] Frontend UI HTML Split

**What changed:**
- Extracted `<style>` block (307 lines) → `proto/static/css/app.css`.
- Extracted 6 semantic constants + 2 functions → `proto/static/js/semantic-meta.js`.
- Extracted 5 opening-parent functions → `proto/static/js/opening-parent.js`.
- Added StaticFiles mount to `proto/server.py` (guarded, 3 lines).
- `proto/ui.html`: 1437 → 1111 lines (-326 lines, -23%).

**Tests:** py_compile PASS · smoke PASS · full PASS (proto 9fa57a0)

---

### [session] Max Token Reduction / File Split

**What changed:**
- Created `proto/export/__init__.py`, `proto/export/semantic_metadata.py`, `proto/export/xlsx_helpers.py`.
- Moved SEMANTIC_*_MAPs, AREA_SEMANTIC_TAGS, _derive_measurement_meta, _get_meta → `export/semantic_metadata.py`.
- Moved _hex_to_rgb, _poly_area_pt2, _line_points, _line_length_pt, _nearest_on_segment, _object_points_for_ref_report, _distance_to_ref, _m2_to_rwu → `export/xlsx_helpers.py`.
- `proto/server.py` now imports all names back — behavior identical.
- Created `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md` (file size + risk analysis).
- Created `docs/design/E2E_SPLIT_PLAN.md` (e2e test split plan, implementation deferred).
- Created `docs/status/READ_ORDER.md` (agent reading guide).
- Updated all status docs (CURRENT_STATUS.md, LATEST_STATUS.md, NEXT_ACTIONS.md, COMMIT_HISTORY.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md).

**Tests:** py_compile PASS · smoke PASS · full PASS (proto fb89ecd)

---

### [session] Fast UI Testability Polish (Sprint B)

**What changed:**
- Sprint 1: Empty state card with action buttons + numbered workflow steps 1→6.
- Sprint 2: Topbar zone-a .sep separator between file group and workflow group.
- Sprint 3: Set Scale .scale-cta orange highlight when PDF open but scale not set.
- Sprint 4: `#lp-page-info` strip in sidebar showing page name · tag · scale state.
- Sprint 5: `aria-label` on toolbar groups for testability.
- Sprint 6: `buildLeftProperties()` grouped: Basic / Measurement / Metadata.
- Sprint 7: Right panel Layers title styled; compat note improved.
- Sprint 8: QA warnings grouped by severity: Error / Warning / Info.
- Sprint 9: `#export-readiness` summary bar in export panel.
- Sprint 10: `docs/process/QUICK_TEST_GUIDE.md` created.
- Added rightPanelCompatibilityVisible, rightPanelLayersFirst, leftPanelTabsOk assertions to E2E.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

### [session] Token Reduction / Status File Split

**What changed:**
- Archived full log.md (1624 lines) → `docs/archive/log-2026-05-09.md`.
- Archived PATCH_SUMMARY, TEST_RESULT, FINAL_REPORT history → `docs/archive/`.
- Created 5 new small status files in `docs/status/`: LATEST_STATUS.md, NEXT_ACTIONS.md, TEST_BASELINE.md, COMMIT_HISTORY.md, KNOWN_ISSUES.md.
- Reduced log.md, CURRENT_STATUS.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md to current-only.
- Updated index.md to prioritize small status files.
- Sprint card created at sprints/active/RUN_TOKEN_REDUCTION_FILE_SPLIT.md.

**Tests:** No source code changed — no tests required.

---

### [session] Left Properties Migration

**What changed:**
- `proto/ui.html`: added `data-mode` + `onclick="setSidebarMode('...')"` to 3 left-panel tab divs.
- `proto/ui.html`: added `#lp-objects-content` and `#lp-properties-content` hidden divs in HTML.
- `proto/ui.html`: added `lSidebarMode` global, `setSidebarMode(mode)`, `buildLeftObjects()`, `buildLeftProperties()` functions.
- `proto/ui.html`: `selectObjectFromTree`, `_initDrag`, `showObjPicker` row click — each now calls `setSidebarMode("properties")` to auto-switch on object selection.
- `proto/e2e_ui_test.py`: added `leftPanelTabsOk` IIFE to MAIN_UI_OK; added Python assertion.
- Sprint card moved to `sprints/completed/2026-05-09-left-properties-migration/`.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

### [session] Opening Parent Reassignment

**What changed:**
- `linkOpeningParent` in `proto/ui.html`: added `parentManual` guard so manual assignments survive `ensureStoreObjectIds` → `linkOpeningsInStore` cycles.
- `buildRightPanel()` opening case: shows `<select id="rp-opening-parent">` when parentStatus ≠ "linked".
- Added `rpSetOpeningParent(id)` to `proto/ui.html`.
- Extended SELECT_OK in `proto/e2e_ui_test.py` to assert parentSelectVisible and parentReassigned.
- Sprint card moved to `sprints/completed/2026-05-09-opening-parent-reassignment/`.

**Tests:** py_compile PASS · smoke PASS · full PASS

---

> Earlier sessions (Page Scales Audit, Report Target Summary, Export Metadata Columns,
> Measurement Profile Metadata, Right Panel Organization, Mockup V3 UI, etc.)
> are in [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md)

---

### [2026-05-09 23:12 +07:00] Widget Placement Polish

**What changed:**
- Created `sprints/active/RUN_WIDGET_PLACEMENT_POLISH.md` from the requested sprint scope.
- Polished the existing left-side workflow, page info, review warning, export-ready, and inspection widgets.
- Added compact status rows for current-page warnings/export readiness using existing state.
- Updated CSS for compact left-panel card style and page-info strip.
- Moved sprint card to completed after PASS.

**Why:**
- Sprint 2 required visual polish only, with no backend, export, save/load, or business logic changes.

**Files touched:**
- `proto/ui.html`
- `proto/static/css/app.css`
- `sprints/active/RUN_WIDGET_PLACEMENT_POLISH.md`
- `PATCH_SUMMARY.md`
- `TEST_RESULT.md`
- `UI_MANUAL_TEST.md`
- `FINAL_REPORT_FOR_CHATGPT.md`
- `CURRENT_STATUS.md`
- `docs/status/LATEST_STATUS.md`
- `docs/status/NEXT_ACTIONS.md`
- `log.md`

**Verification:**
- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

**Known issues:**
- Full test initially caught a local regression from calling `collectAreas()` in live widget rendering; fixed before PASS by using current-page-only reads.
- Existing non-fatal Windows `ConnectionResetError` appeared after successful full output.
