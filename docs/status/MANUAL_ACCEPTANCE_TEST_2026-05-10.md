# MANUAL_ACCEPTANCE_TEST_2026-05-10.md

Date: 2026-05-10  
Tester: Claude Sonnet 4.6 (automated Playwright probe + code review)  
Baseline: py_compile PASS · smoke PASS · full PASS

## Scope

Acceptance test for the 8-phase batch completed 2026-05-10:
- Panel Scroll + Page-Scoped Layer UI
- Mockup V3 App Shell Theme
- Save / Save As / Overwrite
- Open / Recent Project
- Export Current-Page + All-Pages Annotated PDF

## Evidence Method

| Label | Meaning |
|-------|---------|
| AUTO | Verified by Playwright probe or E2E suite result |
| CODE | Verified by code review (logic/DOM/CSS) |
| HUMAN | Requires a human with a real browser for visual confirmation |

---

## Test Results

### TC-01 — Open real multi-page PDF
**Expected:** 45-page PDF loads, page label shows "1 / 45", canvas renders.  
**Evidence:** REAL_OK `page_label: '1 / 45'`, PERSIST_OK polygons drawn on pages 1 and 2. [AUTO]  
**Result: PASS**

---

### TC-02 — Set Scale
**Expected:** Calibration tool sets scale; badge updates; area recalculates.  
**Evidence:** RECAL_OK `scale: '★ 1:4 (สอบเทียบ)'`, summary area changed from 380.96 → 0.73 ตร.ม. [AUTO]  
**Result: PASS**

---

### TC-03 — Set Page Type and Floor
**Expected:** Page Setup overlay lets user tag pages (site/plan/elev/etc.) and name them; right panel context updates.  
**Evidence:** SETUP_OK `auto_tag: 'site'`, `auto_name: 'ผังบริเวณ'`. Right panel header shows `rp_page_ctx_text: "หน้า 1"` after load. [AUTO]  
Visual: floor name visible in rp-page-ctx. [HUMAN — requires visual confirmation in browser]  
**Result: PASS (automated); visual confirms pending**

---

### TC-04 — Right Panel Page-Scoped Layers Change Per Page
**Expected:** Right panel layer list reflects the current page's layer set; navigating pages updates the list.  
**Evidence:**  
- Probe `rp_layer_rows`: 5 layer rows rendered (พื้นที่หลัก, พื้นที่ย่อย[ACTIVE], ช่องว่าง, เส้นอ้างอิง, ป้าย)  
- MAIN_UI_OK `layerRows`: 5 site-preset rows (ที่ดิน/แนวเขต, กรอบอาคาร/แนวอาคาร, ที่ว่าง, เส้นอ้างอิง, ป้าย/หมายเหตุ)  
- `rightPanelHeaderShowsPageContext: true` — `.rp-page-ctx` rendered in `#rp-header` [AUTO]  
- Active layer row highlighted with `.active-layer` class: `v3ActiveLayerRowClass: true` [AUTO]  
**Result: PASS**

---

### TC-05 — Hide/Lock Layer on Page 1, Verify Page 2 Unaffected
**Expected:** Toggling layer visibility on page 1 has no effect on page 2 (page-scoped model).  
**Evidence:** Probe `layer_isolation`:  
- `p1_vis_before: true` → toggle → `p1_vis_after: false` (layer hidden on page 1)  
- `p2_vis: true` (same layer still visible on page 2) [AUTO]  
**Result: PASS**

---

### TC-06 — Draw Area
**Expected:** Area tool draws a polygon; area appears in page summary.  
**Evidence:** VECTOR_OK `summary: 'อาคาร/ห้อง 380.96 · สุทธิ 380.96 ตร.ม.'`, `measure: '⬡ 380.96 ตร.ม.'` [AUTO]  
**Result: PASS**

---

### TC-07 — Draw Opening
**Expected:** Opening tool draws a deduction polygon; appears in summary with negative sign.  
**Evidence:** SELECT_OK `hit: {type: 'opening'}`, XLSX_OK summary includes `(-)ช่องว่าง 0.10 ตร.ม.` [AUTO]  
**Result: PASS**

---

### TC-08 — Link Opening to Area
**Expected:** Opening can be reassigned a parent polygon; warnings cleared when linked.  
**Evidence:** SELECT_OK `parentLinked: true`, `parentReassigned: true`, `structuredWarnings: true`, `unlinkedWarnings: 1` (one intentionally left unlinked for test) [AUTO]  
**Result: PASS**

---

### TC-09 — Left Inspection Status Panel
**Expected:** Collapsible panel in left sidebar shows workflow steps, per-page stats, measurement summary, warnings, next action.  
**Evidence:**  
- `inspectionPanelVisible: true` [AUTO]  
- `inspectionPanelInSidebar: true`, `inspectionPanelNotInCanvas: true` [AUTO]  
- `inspectionPanelWorkflowVisible: true` (`.isp-wf-row` rows present) [AUTO]  
- `inspectionPanelContextVisible: true` (`.isp-section-title` present) [AUTO]  
- `inspectionPanelToggleWorks: true` (collapse/expand cycle confirmed) [AUTO]  
**Result: PASS**

---

### TC-10 — Right Panel Current Page Layers
**Expected:** 5+ layer rows visible with object counts, visibility 👁 and lock 🔓 controls.  
**Evidence:**  
- `rightPanelLayerCountsVisible: true` (≥5 `.rp-layer-count` elements) [AUTO]  
- `rightPanelLayerControlsVisible: true` (≥9 `.rp-layer-row .rp-icon-btn` elements) [AUTO]  
- `rightPanelLayersFirst: true` — layers section is the first section [AUTO]  
- Probe `rp_layer_rows`: 5 rows confirmed [AUTO]  
**Result: PASS**

---

### TC-11 — Layout Options: Current Stable, Mockup V3, Layer Focus, Compact
**Expected:** Each preset applies correct body classes; reset to Current Stable removes all v3 classes.  
**Evidence:** Probe `layout_presets`:  
- `current_stable_classes: ""` — no v3 classes [AUTO]  
- `mockup_v3_classes: "ui-top-v3 ui-left-v3 ui-right-v3 ui-widgets-v3"` — all 4 [AUTO]  
- `layer_focus_classes: "ui-right-v3"` — only right panel [AUTO]  
- `reset_classes: ""` — clean reset [AUTO]  
- `resetRestoresCurrentStable: true` (E2E assertion) [AUTO]  
Visual appearance of v3 theme (darker cards, cyan tabs, compact layout): [HUMAN — browser visual check]  
**Result: PASS (logic); visual pending**

---

### TC-12 — Save As
**Expected:** "Save As" button triggers `saveProjectAs()`. FSAPI unavailable in headless → fallback to `.bmaplan` download. `isDirty` cleared after save.  
**Evidence:**  
- `save_as_btn_present: true` [AUTO]  
- `saveSystemFunctionsExist: true` — all 7 helper functions present [AUTO]  
- `after_fallbackDownload_lbl: "Downloaded"` confirmed by `_markSaved("download")` logic [CODE]  
- PROJECT_OK: `_fallbackDownload()` produces valid roundtrip `.bmaplan` [AUTO]  

**⚠ MINOR BUG found (TC-12-B1):**  
`lbl-save-state` stays at `"Manual save required"` after `pushUndo()` because `_setDirty()` guards against updating the initial label string:  
```js
if(ss && ss.textContent !== "Manual save required") ss.textContent = "Unsaved changes";
```  
After the FIRST successful save (`_markSaved` → "Downloaded" or "Saved"), subsequent dirty actions correctly show "Unsaved changes". Impact: user sees no "Unsaved changes" indicator until after first save. Does NOT affect save/load functionality.  
**Severity: MINOR**  
**Result: PASS (functionality); MINOR label UX bug noted**

---

### TC-13 — Save Overwrite Existing Project
**Expected:** If `currentProjectHandle` is set (FSAPI), save overwrites in-place. Handle set to null after FSAPI failure → falls back to Save As.  
**Evidence:**  
- `_writeToHandle` function exists [AUTO]  
- `currentProjectHandle` state variable initializes to `null` [CODE]  
- `isDirtyClearedByApplyLoaded: true` — load resets handle [AUTO]  
- Logic review: async try/catch with `currentProjectHandle = null` on failure [CODE]  
**Result: PASS**

---

### TC-14 — Close / Reopen Project
**Expected:** Load `.bmaplan` via "เปิด Project" restores all measurements, site orientation, and page tags.  
**Evidence:** PROJECT_OK:  
- `project_file: 'roundtrip.bmaplan'`  
- `restored: 'อาคาร/ห้อง 0.73 · ที่ดิน 0.13 · (-)ช่องว่าง 0.10 · สุทธิ 0.76 ตร.ม.'` (matches saved)  
- `site_meta: {north: true, sideNote: 'ถนนหน้าโครงการ', sideRole: 'front_road'}` [AUTO]  
- `isDirtyClearedByApplyLoaded: true` — isDirty and handle reset on load [AUTO]  
**Result: PASS**

---

### TC-15 — Recent Project List
**Expected:** Loading a `.bmaplan` adds it to recent list. Dropdown appears on "เปิด Project" click if list non-empty. Broken localStorage entry handled safely.  
**Evidence:** Probe `recent_projects`:  
- `fn_exists: true` — `addRecentProject`, `getRecentProjects` defined [AUTO]  
- `storage_key_writable: true` — `localStorage['bmaPlan.recentProjects.v1']` writable [AUTO]  
- `add_then_get: "test.bmaplan"` — deduplication and ordering correct [AUTO]  
- `dropdown_in_dom: true` — `#recent-proj-dropdown` in DOM [AUTO]  
- `openBrokenRecentNoCrash: true` — broken JSON in localStorage handled with try/catch, no crash [AUTO]  
**Result: PASS**

---

### TC-16 — Export XLSX
**Expected:** Excel report has all required sheets; includes area, warnings, scales, floor summaries.  
**Evidence:** XLSX_OK all 10 expected sheets present; shared strings include VECTOR_POLY_NAME, VECTOR_OPENING_NAME, "BMA-Plan Phase 1 Export", metadata column headers. [AUTO]  
**Result: PASS**

---

### TC-17 — Export Current-Page Annotated PDF
**Expected:** "Export หน้าปัจจุบัน + Annotations" button triggers `exportCurrentPageAnnotatedPDF()` → POST `/export-pdf` with `pages=[curPage]` + full `pageStore`.  
**Evidence:**  
- `exportCurrentPageFnExists: true` [AUTO]  
- `exportCurrentPageBtnExists: true` [AUTO]  
- `annotated_pdf_valid: true` — `/export-pdf` returns `application/pdf`, >500 bytes [AUTO]  
**Result: PASS**

---

### TC-18 — Export All-Pages Annotated PDF
**Expected:** "Export ทุกหน้า + Annotations" button triggers `exportAllPagesAnnotatedPDF()` → POST `/export-pdf` with all non-excluded pages + full `pageStore`.  
**Evidence:**  
- `exportAllPagesFnExists: true` [AUTO]  
- `exportAllPagesBtnExists: true` [AUTO]  
- `/export-pdf` endpoint tested with multi-page export in REAL_OK `export_pages: 2` [AUTO]  
**Result: PASS**

---

### TC-19 — Verify Annotated PDF Overlay Alignment
**Expected:** Polygon and line annotations drawn in the browser appear at the correct position on the exported PDF page.  
**Evidence:**  
- ANNOT_OK: `label: 'E2E_ROOM_A'` — label text found at correct centroid location in exported PDF [AUTO]  
- Coordinate system confirmed: stored coords = PDF points, drawn directly via `fitz.Point(x, y)` with no scale transform [CODE]  
- Rotation transform `_rot_pt()` applied before drawing [CODE]  
Visual: sub-pixel alignment on a real architectural PDF with zoom. [HUMAN — browser + PDF viewer check]  
**Result: PASS (coordinate logic); visual alignment pending human review**

---

### TC-20 — Viewport Responsiveness (1366×768, 1440×900, 1512×982)
**Expected:** No horizontal overflow at any viewport; topbar fits; toolbar stays within workspace.  
**Evidence:** Probe viewports:  
- 1440×900: `topbarNoOverflow: true`, `bodyNoHorizontalOverflow: true` [AUTO]  
- 1366×768: `topbarNoOverflow: true`, `bodyNoHorizontalOverflow: true` [AUTO]  
- 1512×982: `topbarNoOverflow: true`, `bodyNoHorizontalOverflow: true` [AUTO]  
- E2E: `toolbarFitsWorkspace: true`, `toolbarBelowHeader: true` at 1440×900 [AUTO]  
**Result: PASS**

---

## Forbidden-String Audit
**Expected:** No legal checker, OCR, AI, Rule Engine, FAR/OSR, autosave wording in active UI.  
**Evidence:** `forbiddenPhase1StringsAbsent: true`, `forbidden_absent: true` (probe) [AUTO]  
**Result: PASS**

---

## Bug Summary

| ID | TC | Severity | Description | Fix |
|----|----|----------|-------------|-----|
| TC-12-B1 | TC-12 | MINOR | `lbl-save-state` stays "Manual save required" instead of "Unsaved changes" after `pushUndo()` when no prior save has occurred. Guard in `_setDirty()` prevents update from initial label. | Remove guard or reset label to "" on `loadPage()`. |

No BLOCKER or MAJOR bugs found.

---

## Automated Test Summary (2026-05-10)

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

Full test covers: CACHE, SETUP, MAIN_UI, VECTOR, RECAL, SITE_UI, XLSX, PROJECT, RASTER, WHEEL, SNAP, SELECT, SETBACK, EXT_MEASURE, ANNOT, PERSIST, REAL — 17 test sections, all PASS.

---

## Next Sprint Recommendation

**Recommended sprint:** `RUN_SAVE_STATE_LABEL_FIX.md`  
- Scope: Fix TC-12-B1 — reset `lbl-save-state` to a neutral initial state (e.g., `""` or `"Not saved"`) when `loadPage()` succeeds so `_setDirty()` can transition it to "Unsaved changes" correctly.  
- Risk: Low (cosmetic label only, no logic change)  
- Hard rules apply: no save format change, no schema migration.

Or defer TC-12-B1 to the next UI polish sprint as a one-liner fix inside another save-related task.
