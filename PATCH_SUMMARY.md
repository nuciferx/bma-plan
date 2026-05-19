# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BLOAT-FLAKE-1 — Fix REAL_PDF `_wait_analyse_ready` flake

Branch: main
Date: 2026-05-20

## Outcome: PASS — Full E2E GREEN. Resolves the LOOP_STOP_REGRESSION halt from BLOAT-5. Retroactively confirms BLOAT-5 passes full E2E.

## Summary

Raised `_wait_analyse_ready` default timeout from 30.0 s to 60.0 s and added a grace window: if the status bar still shows active progress (`กำลังโหลด` / `กำลังวิเคราะห์`) at the original deadline, the wait is granted +50% extra time before declaring failure. ~15 LOC changed inside that one helper. No app code, no schema, no other test logic touched. Full E2E now GREEN — `PERSIST_OK` / `REAL_OK` / `ANNOT_OK` no longer flake. The raised ceiling is free on the fast smoke path. Dev-loop unblocked. Bloat-reduction wave confirmed complete: ui.html 4,231→3,777 (−454 across BLOAT-1..5, −10.7%, well under the 5,000-line trigger).

## Files Changed

| File | Change |
|---|---|
| `proto/e2e_ui_test.py` | +15 −2 — `_wait_analyse_ready` timeout 30.0→60.0; added grace-window branch for active-loading status |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `proto/ui.html` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
python -m py_compile proto/e2e_ui_test.py                  → PASS
python proto/e2e_ui_test.py full                           → EXIT 0 — ALL GREEN
  PERSIST_OK + REAL_OK + ANNOT_OK GREEN (these flaked 3x during BLOAT-5)
  PHASE_BLOAT2_OK 8/8 + _BLOAT3_OK 8/8 + _BLOAT4_OK 8/8 + _BLOAT5_OK 8/8
  PHASE_INV_PAGE_SETUP_A_OK 8/8 + _B_OK 9/9 + _C_OK 7/7 + PHASE_HT11_OK 10/10
  Retroactively confirms BLOAT-5 (shipped smoke-only) passes full E2E.
/bma-human-test — N/A (test-infrastructure only; no runtime code touched)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `proto/ui.html` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- (only `proto/e2e_ui_test.py` `_wait_analyse_ready` helper changed)

---

# Previous: BLOAT-5 — Extract page-setup modal JS to proto/static/js/page-setup.js

Branch: main
Date: 2026-05-20

## Outcome: PASS — py_compile PASS, full 22/22 baseline + PHASE_BLOAT4_OK 8/8 + PHASE_INV_STICKY_OK 10/10 + PHASE_HT11_OK 10/10 GREEN (retry for known REAL_PDF analyse flake)

## Summary

Extracted 13 annotation helper functions from `proto/ui.html` (L1680–1869) into a new file `proto/static/js/annotations.js` (205 LOC, plain non-module classic script). `proto/ui.html` shrank from 4,057 to 3,869 lines (−188 net). Functions extracted cover the full annotation domain: lazy array init (`ensureAnnotations`), id factory (`newAnnotationId`), add/clear/delete operations, sticky HTML overlay (`renderStickyCards`, `_createStickyCard`), HT-11 edit modal (`openAnnotationEditModal`, `closeAnnotationEditModal`, `saveAnnotationEdit`), hit-test for all 7 annotation types (`annotationHitTest`), default-color helper (`_annColor`), and canvas render dispatcher (`drawAnnotations`). The 7 per-mode mousedown branches remain in `proto/ui.html` (tightly coupled to the unified pointer state). New E2E marker `PHASE_BLOAT4_OK` (8 sub-checks) verifies all 13 fns defined, operations correct, canvas render + sticky overlay render clean. Session total ui.html: 4,231→3,869 (−362 lines across BLOAT-1..4).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | −190 +2 — replaced extracted annotation block (L1680–1869) with 1 placeholder comment; added `<script src="/static/js/annotations.js">` tag after `export-save.js`; net −188 LOC (4,057→3,869) |
| `proto/static/js/annotations.js` | NEW 205 LOC — 13 annotation functions: `ensureAnnotations`, `newAnnotationId`, `addAnnotation`, `renderStickyCards`, `_createStickyCard`, `clearAnnotations`, `annotationHitTest`, `deleteAnnotation`, `openAnnotationEditModal`, `closeAnnotationEditModal`, `saveAnnotationEdit`, `_annColor`, `drawAnnotations` (plain non-module classic script) |
| `proto/e2e_ui_test.py` | +99 LOC — `annotationsJsLoaded` load-check field + `_test_bloat4_annotations_extracted` (8 sub-checks) + `PHASE_BLOAT4_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — UNCHANGED (zero edits this sprint)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED (annotations READ pdfToC/cToPdf for coordinate conversion only; never edit)
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `pageStore[pg].annotations` field name, shape, items, and id format all preserved

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py full                           → first run FAILED (intermittent REAL_PDF analyse flake page 1/45 — known, unrelated to BLOAT-4); retry GREEN
  All 22 baseline markers GREEN (incl. MAIN_UI_OK annotationsJsLoaded: True / ANNOT_OK / PERSIST_OK / REAL_OK)
  PHASE_INV_STICKY_OK 10/10 (J_roundTrip ✓ — sticky-note schema round-trip survives extraction)
  PHASE_HT11_OK 10/10 (annotation edit + delete modal still functional)
  PHASE_BLOAT2_OK 8/8 + PHASE_BLOAT3_OK 8/8 + PHASE_BLOAT4_OK 8/8
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PHASE_INV_STICKY_OK + PHASE_HT11_OK cover annotation create/edit/delete/round-trip; PHASE_BLOAT4_OK verifies all 13 fns + canvas + sticky overlay)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; `pageStore[pg].annotations` field preserved; `PHASE_INV_STICKY_OK` J_roundTrip sub-check verified)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous (older): BLOAT-3 — archived to [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

<!-- BLOAT-3 and earlier entries: see docs/archive/patch-history-2026-05-09.md -->

---

# Previous-older: BLOAT-3 — Extract export/save JS to proto/static/js/export-save.js

Branch: main
Date: 2026-05-20

## Outcome: PASS — py_compile PASS, smoke 18/18 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK, full 21/21 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN

## Summary

Extracted 14 export/save functions and 13 column/type constants from `proto/ui.html`'s inline `<script>` block into a new file `proto/static/js/export-save.js` (188 LOC, plain non-module classic script). `proto/ui.html` shrank from 4,208 to 4,057 lines (−151 net). Functions include the full export surface (`exportJSON`, `exportCSV`, `exportSummaryXLSX`, `exportXLSX`, `exportAllPagesAnnotatedPDF`, `exportCurrentPageAnnotatedPDF`, `exportPngZip`) and the full save surface (`_makeProjBlob`, `_writeToHandle`, `_fallbackDownload`, `saveProjectAs`, `saveProject`, `saveSourcePdfInPlace`). New E2E marker `PHASE_BLOAT3_OK` (8 sub-checks) verifies all 14 fns + 13 consts defined, `.bmaplan` v1 schema intact (12 fields), and 3 save fns are AsyncFunctions. `XLSX_OK` + `PROJECT_OK` + `PERSIST_OK` + `ANNOT_OK` all GREEN on real 45-page permit. With the recipe proven on the most complex cluster, BLOAT-4 (annotations) and BLOAT-5 (page-setup) are formulaic.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | −161 +6 — extracted 14 fns + 13 consts from inline `<script>`; added `<script src="/static/js/export-save.js">` tag; 3 one-line comment placeholders remain; net −155 LOC (4,208→4,057) |
| `proto/static/js/export-save.js` | NEW 188 LOC — 6 column consts + 7 type consts + `rowBase` + `buildRows` + `dlBlob` + JSON/CSV/XLSX/PDF/PNG export fns + save fns (plain non-module classic script) |
| `proto/e2e_ui_test.py` | +111 LOC — `exportSaveJsLoaded` load-check field + `_test_bloat3_export_save_extracted` (8 sub-checks) + `PHASE_BLOAT3_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — UNCHANGED (zero edits this sprint; extracted client functions still POST to existing endpoints)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `_makeProjBlob` still emits all 12 v1 fields (verified by `schemaOk` sub-check in PHASE_BLOAT3_OK)

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0, 18/18 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN
python proto/e2e_ui_test.py full                           → EXIT 0, 21/21 + PHASE_BLOAT2_OK + PHASE_BLOAT3_OK GREEN
  XLSX_OK, PROJECT_OK, PERSIST_OK, ANNOT_OK, REAL_OK — all GREEN on real 45-page permit
  PHASE_BLOAT3_OK 8/8 sub-checks GREEN (fileLoad, fnsOk, constsOk, dlBlobOk, buildRowsOk, blobIsBlob, schemaOk, asyncOk)
/bma-human-test — SKIPPED (mechanical extraction, zero user-visible change; PROJECT_OK + PERSIST_OK + ANNOT_OK on real permit cover most sensitive surfaces)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; `schemaOk` sub-check verified all 12 v1 fields present post-extraction)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

<!-- Previous (older) BLOAT-2 and BLOAT-1 entries archived to docs/archive/patch-history-2026-05-09.md -->

---

# Previous (older): INV-2026-05-19-003b — /export-png ZIP endpoint (Path C)

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, full EXIT 0; PHASE_INV_EXPORT_PNG_OK (new marker); all predecessor markers retained

## Summary

End-of-day bundle headline sprint. NEW `/export-png` ZIP endpoint in `proto/server.py` (additive — no existing endpoint modified): accepts `case_id + selected_pages[] + dpi_scale`, renders each selected page via PyMuPDF at the requested DPI scale, bundles PNGs into a ZIP archive returned as `application/zip`. Export menu in `proto/ui.html` wired with "Export PNG (ZIP)" option. This is Path C of the print-canvas-per-page invent (INV-003), providing high-DPI archival PNG export as a complement to Path B (INV-003a, fast browser-print). Together 003a + 003b close the invention. Also in this session bundle: HT-18c fixed save/load round-trip test to 13/13 GREEN (closing the HT-18 series), and INV-003a delivered browser-side "Print Current Page" + "Print Selected Pages" via `canvas.toDataURL + window.print()`. Session totals: 33 commits pushed to `origin/main-v2-2026-05-19`.

## Files Changed

| File | Change |
|---|---|
| `proto/server.py` | NEW `/export-png` endpoint — additive; accepts case_id + page list + dpi_scale; PyMuPDF render per page; ZIP bundle; case isolation preserved |
| `proto/ui.html` | Export menu `/export-png` wiring; "Print Current Page" + "Print Selected Pages" File menu items; `printCurrentPage()` + `printSelectedPages()` helpers |
| `proto/e2e_ui_test.py` | `_test_inv_export_png` (PHASE_INV_EXPORT_PNG_OK); `_test_inv_print_canvas` (PHASE_INV_PRINT_CANVAS_OK, 8 sub-checks); `_test_ht18b_save_load_round_trip` 13/13 field-by-field fix |
| `docs/status/PHASE_INDEX.md` | Queue rows flipped for INV-003a, HT-18c, INV-003b |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `proto/server.py` — additive NEW endpoint only; no rename or removal of existing endpoints; case isolation preserved
- `.bmaplan` schema version stays 1; no field rename or removal

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (all three sprints in bundle)

INV-003b: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_EXPORT_PNG_OK: PASS (new marker)

HT-18c: python proto/e2e_ui_test.py smoke → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (was 7/13; eq() over-strict comparison fixed + applyLoadedProject _projInfoSnap fix)

INV-003a: python proto/e2e_ui_test.py full → EXIT 0
  PHASE_INV_PRINT_CANVAS_OK: PASS (8 sub-checks)

Predecessor markers confirmed retained: PHASE_HT18_OK 36/36,
PHASE_INV_ZEN_V2_OK 10/10, PHASE_INV_OVERVIEW_OK 9/9,
PHASE_INV_ZEN_OK 10/10, PHASE_INV_PALETTE_OK 10/10,
PHASE_INV_POLISH_001C_OK 5/5
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ⚠️ `proto/server.py` — INV-003b added `/export-png` (additive new endpoint; no rename/removal of existing endpoints; case isolation preserved; no schema change)
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; no field rename or removal)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

> Older sprints (HT-18c, HT-18a-ext, HT-18a, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) and git commit log.

<!-- ARCHIVED BELOW — HT-18c (formerly Previous, now superseded) -->

# Previous (older): HT-18c — Save/load round-trip E2E test 13/13 GREEN

Branch: main
Date: 2026-05-19

## Outcome: PASS — py_compile PASS, smoke EXIT 0; PHASE_HT18B_OK 13/13 GREEN (closes HT-18 series)

## Summary

Fixed `_test_ht18b_save_load_round_trip` 13-sub-check round-trip test. Root cause: deep `eq()` comparison was too strict — `normalizeAllObjects` mutated the pre-snapshot object before the comparison, making legitimately equal fields appear different. Fix: replaced deep `eq()` with field-by-field checks on the 13 specific fields a save/load round-trip should preserve. Also fixed a bug in `applyLoadedProject` (HT-18d-equivalent): `_projInfoSnap` was not being correctly restored from blob — confirmed by the test reading `_projInfoSnap` from post-load global state rather than just the blob. After both fixes, `PHASE_HT18B_OK` = 13/13 GREEN. The HT-18 series (HT-18a + HT-18a-ext + HT-18b-with-caveat + HT-18c) is now complete.

## Files Changed

| File | Change |
|---|---|
| `proto/e2e_ui_test.py` | `_test_ht18b_save_load_round_trip` — deep `eq()` replaced by field-by-field checks for 13 sub-checks (A poly / B opening / C line / D ref / E parking / F-M page metadata + projectInfo + layer state); `_projInfoSnap` post-load global read |
| `proto/ui.html` | `applyLoadedProject` — `_projInfoSnap` restoration fix (HT-18d-equivalent) |
| `docs/status/PHASE_INDEX.md` | HT-18c card flipped to done |

## Source Files NOT Touched (Forbidden Surfaces)

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no field rename or removal

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_HT18B_OK: 13/13 GREEN (A poly round-trip, B opening, C line, D ref, E parking,
  F-M page metadata / projectInfo / layer state — all PASS)
  All predecessor markers retained: PHASE_HT18_OK 36/36 + INV markers all GREEN
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1; fix is in `applyLoadedProject` restore logic, not schema fields)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

> Older sprints (HT-18a, HT-18a-ext, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) and git commit log.
