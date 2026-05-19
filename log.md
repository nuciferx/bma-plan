# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (includes 001a Zen Mode + Ribbon Cleanup + 001c FRICTION polish + 002a Zen top bar + INV-003b end-of-day bundle + BLOAT-1 + BLOAT-2)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — BLOAT-4 Extract annotation JS to proto/static/js/annotations.js — PASS (branch: main)

**What changed:** Created `proto/static/js/annotations.js` (205 lines, plain non-module classic script) containing 13 annotation helper functions extracted from `proto/ui.html` (L1680–1869): `ensureAnnotations`, `newAnnotationId`, `addAnnotation`, `renderStickyCards`, `_createStickyCard`, `clearAnnotations`, `annotationHitTest`, `deleteAnnotation`, `openAnnotationEditModal`, `closeAnnotationEditModal`, `saveAnnotationEdit`, `_annColor`, `drawAnnotations`. Added `<script src="/static/js/annotations.js">` after `export-save.js` in `proto/ui.html`. The 7 per-mode mousedown branches for annotation tool dispatch remain in `proto/ui.html` (tightly coupled to the unified pointer state; kept out of scope). Added E2E machinery in `proto/e2e_ui_test.py`: `annotationsJsLoaded` field in UI-load test + new `_test_bloat4_annotations_extracted` function (8 sub-checks: `fileLoad`, `fnsOk`, `addOk`, `hitMissOk`, `drawOk`, `stickyOk`, `colorOk`, `clearOk`) + new marker `PHASE_BLOAT4_OK`. Net: `proto/ui.html` −190 +2 (4,057→3,869 lines; −188 net); `proto/static/js/annotations.js` NEW 205 LOC; `proto/e2e_ui_test.py` +99 LOC. Session total: ui.html 4,231→3,869 (−362 lines across BLOAT-1..4).

**Why:** Annotations were the third-largest cohesive cluster in ui.html — 7 annotation types (comment/sticky/text/highlight/rect/circle/cloud/arrow) + sticky HTML overlay + HT-11 edit modal + hit-test + canvas render dispatcher. Extracting them removes 188 LOC and isolates a self-contained domain from the measurement core. The recipe is now 4-for-4 (status-bar / export-save / annotations + the older semantic-meta / opening-parent). Pattern validation: cross-script binding access for state (`curPage` / `pageStore` / `zoom` / `ctx`), DOM-builder helpers, and event wiring (sticky drag) all work cleanly across the script boundary.

**Files touched:**
- `proto/ui.html`: −190 +2 — replaced extracted annotation block with 1 placeholder comment; added `<script src="/static/js/annotations.js">` tag; net −188 LOC (4,057→3,869)
- `proto/static/js/annotations.js`: NEW 205 LOC — 13 annotation functions (ensureAnnotations + newAnnotationId + addAnnotation + renderStickyCards + _createStickyCard + clearAnnotations + annotationHitTest + deleteAnnotation + openAnnotationEditModal + closeAnnotationEditModal + saveAnnotationEdit + _annColor + drawAnnotations)
- `proto/e2e_ui_test.py`: +99 LOC — `annotationsJsLoaded` field + `_test_bloat4_annotations_extracted` (8 sub-checks) + `PHASE_BLOAT4_OK` marker print

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py full                           → first run FAILED (intermittent REAL_PDF analyse flake on page 1/45 — known, unrelated to BLOAT-4); retry GREEN
  All 22 baseline markers GREEN: CACHE_OK / UPLOAD_CAP_OK / SETUP_OK / MAIN_UI_OK (annotationsJsLoaded: True) / VECTOR_OK / RECAL_OK / SITE_UI_OK / XLSX_OK / PROJECT_OK / RASTER_OK / WHEEL_OK / SNAP_OK / SELECT_OK / SETBACK_OK / EXT_MEASURE_OK / MENU_OK / PATH_GEOMETRY_OK / ANNOT_OK / PERSIST_OK / REAL_OK
  PHASE_INV_STICKY_OK 10/10 (J_roundTrip ✓ — sticky-note schema round-trip survives extraction)
  PHASE_HT11_OK 10/10 (annotation edit + delete modal still functional)
  PHASE_BLOAT2_OK 8/8 + PHASE_BLOAT3_OK 8/8 + PHASE_BLOAT4_OK 8/8
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PHASE_INV_STICKY_OK + PHASE_HT11_OK on real fixtures cover annotation create/edit/delete/round-trip; PHASE_BLOAT4_OK verifies all 13 fns + canvas-render + sticky-overlay-render)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED (annotations READ pdfToC/cToPdf for coordinate conversion only; never edit)
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED (zero edits this sprint)
- ✅ `.bmaplan` schema — UNCHANGED (`pageStore[pg].annotations` field name, shape, items, and id format all preserved; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- BLOAT-5 (page-setup modal extraction: `_renderSetupDashboard` / `_renderSetupPageCard` / `_openRenumberDialog` / `_executeRenumberDelete` / `_reindexPageDicts` / floor-kind helpers → `proto/static/js/page-setup.js`, est. ~300 LOC) — next queued sprint; depends-on BLOAT-2 (now satisfied).
- The 7 per-mode mousedown branches stay in ui.html — they call extracted helpers via global scope. A future BLOAT-4b could extract the entire pointer-event handler into `/static/js/pointer.js`, but that unified handler does mPts/measurement/annotation/drag in one switch — out of scope here.

---

## 2026-05-20 — BLOAT-3 Extract export/save JS to proto/static/js/export-save.js — PASS (branch: main)

**What changed:** Created `proto/static/js/export-save.js` (188 lines, classic non-module script) containing 14 functions and 13 constants extracted from `proto/ui.html`. Added `<script src="/static/js/export-save.js">` after `status-bar.js` in `proto/ui.html`. Functions extracted: `rowBase`, `buildRows`, `dlBlob`, `exportJSON`, `exportCSV`, `exportSummaryXLSX`, `exportXLSX`, `exportAllPagesAnnotatedPDF`, `exportCurrentPageAnnotatedPDF`, `exportPngZip`, `_makeProjBlob`, `_writeToHandle`, `_fallbackDownload`, `saveProjectAs`, `saveProject`, `saveSourcePdfInPlace`. Constants extracted: `COL_PAGE`, `COL_TYPE`, `COL_NAME`, `COL_VALUE`, `COL_UNIT`, `COL_RNW`, `TYPE_DISTANCE`, `TYPE_PATH`, `TYPE_REF`, `TYPE_PARKING`, `TYPE_AREA`, `TYPE_OPENING`, `TYPE_REF_DISTANCE`. Added E2E machinery in `proto/e2e_ui_test.py`: `exportSaveJsLoaded` field in UI-load test + new `_test_bloat3_export_save_extracted` function (8 sub-checks: `fileLoad`, `fnsOk`, `constsOk`, `dlBlobOk`, `buildRowsOk`, `blobIsBlob`, `schemaOk`, `asyncOk`) + new marker `PHASE_BLOAT3_OK`. Net: `proto/ui.html` −161 +6 (4,208→4,057 lines, −151 net); `proto/static/js/export-save.js` NEW 188 LOC; `proto/e2e_ui_test.py` +111 LOC.

**Why:** BLOAT-2 proved the no-bundler extraction recipe on a small module (status bar). BLOAT-3 scales it to the largest cohesive cluster: export + save = 14 fns + 13 consts, including the sensitive `.bmaplan` schema serialization (`_makeProjBlob`) and FSA file-handle persistence (`saveProject` / `saveSourcePdfInPlace` that mutate `currentProjectHandle` / `currentSourcePdfHandle` declared in `ui.html`). With the recipe now proven on the biggest and most complex piece — verified by `XLSX_OK`, `PROJECT_OK`, `PERSIST_OK`, and `ANNOT_OK` all GREEN on the real 45-page permit — BLOAT-4 (annotations) and BLOAT-5 (page-setup) become formulaic.

**Files touched:**
- `proto/ui.html`: −161 +6 — extracted 14 fns + 13 consts; added `<script src="/static/js/export-save.js">` tag; 3 one-line comment placeholders remain; net −155 LOC (4,208→4,057)
- `proto/static/js/export-save.js`: NEW 188 LOC — 6 column consts + 7 type consts + `rowBase` + `buildRows` + `dlBlob` + JSON/CSV/XLSX/PDF/PNG export fns + save fns (`_makeProjBlob`, `_writeToHandle`, `_fallbackDownload`, `saveProjectAs`, `saveProject`, `saveSourcePdfInPlace`)
- `proto/e2e_ui_test.py`: +111 LOC — `exportSaveJsLoaded` field + `_test_bloat3_export_save_extracted` (8 sub-checks) + `PHASE_BLOAT3_OK` marker print

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0, 18/18 baseline + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN
python proto/e2e_ui_test.py full                           → EXIT 0, 21/21 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN
  XLSX_OK (calls extracted exportXLSX) — GREEN
  PROJECT_OK (calls extracted saveProject + applyLoadedProject round-trip) — GREEN
  PERSIST_OK (save+reload multi-page on real 45-page permit) — GREEN
  ANNOT_OK (calls extracted exportCurrentPageAnnotatedPDF) — GREEN
  REAL_OK (real-PDF flow) — GREEN
  PHASE_BLOAT3_OK 8/8 sub-checks — GREEN (incl. schemaOk: all 12 v1 fields present; asyncOk: 3 async fns confirmed)
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PROJECT_OK + PERSIST_OK + ANNOT_OK on real permit cover most sensitive surfaces; schemaOk sub-check explicitly verifies 12-field v1 schema integrity post-extraction)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED (extracted client functions still POST to `/export-pdf` / `/export-xlsx` / `/export-xlsx-summary` / `/export-png`; server side untouched)
- ✅ `.bmaplan` schema — UNCHANGED (`_makeProjBlob` still emits `version: 1` with same 12 fields; verified by `schemaOk` sub-check)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- BLOAT-4 (annotation extraction, ~300 LOC, 7 annotation tool handlers + render + hit-test → `proto/static/js/annotations.js`) — next queued sprint.
- BLOAT-5 (page-setup modal extraction) — after BLOAT-4.
- Optional BLOAT-3b: extract print cluster (`printCurrentPage` / `printSelectedPages` / `_captureCanvasDataURL` / `_buildPrintDoc` / `_escForHtml` / `_waitForRedraw`) to `proto/static/js/print-canvas.js` (~50–60 LOC delta). Low-risk; self-contained. Not in scope of BLOAT-3.
- Optional BLOAT-6: shared helpers (`collectAreas` / `phase1Warnings` / `collectSummaryData` / `syncProjectInfoFromForm` / `normalizeAllObjects`) — high coupling (summary widget + layer + measurement); NOT for export-save.js; separate sprint if desired.

---

<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->

---

## 2026-05-19 — End-of-day bundle: INV-003b /export-png ZIP + HT-18c round-trip 13/13 + INV-003a Print canvas — PASS (branch: main)

**What changed:** Three committed sprints shipped in this session. (1) **INV-2026-05-19-003b** (`612de96` feat + `7f0300f` docs): NEW `/export-png` ZIP endpoint in `proto/server.py` — accepts `case_id + selected_pages[] + dpi_scale`, renders each page via PyMuPDF at requested scale, bundles PNGs into a ZIP archive returned as `application/zip`. Export menu in `proto/ui.html` wired with "Export PNG (ZIP)" option. New E2E test `_test_inv_export_png` + marker `PHASE_INV_EXPORT_PNG_OK`. (2) **HT-18c** (`f1b4331` fix + `9297ed4` docs): Fixed `_test_ht18b_save_load_round_trip` — replaced over-strict deep `eq()` comparison (fails after `normalizeAllObjects` mutates pre-snapshot) with field-by-field checks on the 13 round-trip properties. Also fixed a bug in `applyLoadedProject` (HT-18d-equivalent): `_projInfoSnap` was not fully restored from blob; fix ensures `projectInfo` round-trip is symmetric. `PHASE_HT18B_OK` now 13/13 GREEN. (3) **INV-2026-05-19-003a** (`b4f7235` feat + `8200ef6` docs): "Print Current Page" + "Print Selected Pages" in File menu — client-side `canvas.toDataURL("image/png")` → synthetic print window + `window.print()` trigger (Path B). New E2E test `_test_inv_print_canvas` (8 sub-checks) + marker `PHASE_INV_PRINT_CANVAS_OK`. In addition, a ~10 LOC uncommitted test refinement for `_test_ht18b_save_load_round_trip` (HT-18b `_projInfoSnap` direct global check) is pending fold into next commit.

**Why:** INV-003a/003b deliver the "print-canvas-per-page" invention (originally a raw `/idea` entry, promoted via `/bma-invent` 7-phase pipeline, GO verdict MATURE). Path B (003a) gives fast single-page print via browser's native print dialog. Path C (003b) provides high-DPI archival PNG export bundled as ZIP — useful for sending annotated plans by email or attaching to permit submissions. HT-18c was the final item in the HT-18 series: the save/load round-trip test was gated on fixing the `eq()` comparison that was too strict after `normalizeAllObjects` transformed the pre-snapshot object; with that fix plus the `applyLoadedProject` `_projInfoSnap` restoration, the full 13-sub-check round-trip is now GREEN and the HT-18 series is complete.

**Files touched:**
- `proto/server.py`: NEW `/export-png` endpoint (additive — no rename or removal of existing endpoints; case isolation preserved) [INV-003b]
- `proto/ui.html`: Export menu `/export-png` wiring + "Print Current Page" / "Print Selected Pages" File menu items + `printCurrentPage()` / `printSelectedPages()` helpers [INV-003a + INV-003b]
- `proto/e2e_ui_test.py`: `_test_inv_export_png` (PHASE_INV_EXPORT_PNG_OK) + `_test_inv_print_canvas` (PHASE_INV_PRINT_CANVAS_OK) + `_test_ht18b_save_load_round_trip` 13/13 field-by-field fix [INV-003b + INV-003a + HT-18c]
- `docs/status/PHASE_INDEX.md`: queue rows flipped for INV-003a, HT-18c, INV-003b [all three]

**Tests:**
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (all three sprints)

INV-003b: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_EXPORT_PNG_OK: PASS (new marker)
  All prior markers retained (no regression)

HT-18c: python proto/e2e_ui_test.py smoke → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (was 7/13 — test design issue now fixed)

INV-003a: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_PRINT_CANVAS_OK: PASS (8 sub-checks)
  All prior markers retained (no regression)

Predecessor markers confirmed retained: PHASE_HT18_OK 36/36,
PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9,
PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10,
PHASE_INV_POLISH_001C_OK 5/5
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ⚠️ `proto/server.py` — INV-003b added `/export-png` endpoint (additive new endpoint; no rename or removal of existing endpoints; case isolation preserved; no schema change)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- ~10 LOC uncommitted HT-18b test refinement (`_projInfoSnap` direct global check) pending fold into next commit
- Zen Mode user manual docs sprint still uncommitted (`proto/manual/zen-mode.md` NEW ~80 LOC + keyboard-shortcuts.md +2 LOC + getting-started.md +1 LOC + content.json rebuild) — pending user finalize
- INV-2026-05-19-002c (F12 Overview mockup-port) still queued — next after docs sprint
- Session totals: 33 local commits pushed to `origin/main-v2-2026-05-19` (local `main` tracking that branch)

---

<!-- sessions before the current top-2 are archived to docs/archive/log-2026-05-19.md (HT-18a-ext + earlier 2026-05-19 entries: 001a Zen Mode + Ribbon Cleanup + 001b Command Palette + 001c FRICTION polish + 002a Zen top bar + 002b F12 Overview + HT-18a + INV-003b end-of-day bundle) and docs/archive/log-2026-05-18.md (earlier) -->
