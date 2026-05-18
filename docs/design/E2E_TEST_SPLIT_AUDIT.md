# E2E_TEST_SPLIT_AUDIT.md — BMA-Plan E2E Test Split Audit

Date: 2026-05-09
Source: proto/e2e_ui_test.py
Decision: **AUDIT_ONLY_STOP**

---

## 1. Total Line Count

**1525 lines**

---

## 2. Imports and Constants (lines 0–33)

```
Imports: socket, sys, threading, time, tempfile, io, zipfile, xml.etree.ElementTree,
         pathlib, fitz, requests, uvicorn, PIL.Image, playwright.sync_api, server
Constants: ROOT, VECTOR_PDF, RASTER_PDF, REAL_PDF, BASE_URL,
           VECTOR_POLY_NAME, VECTOR_OPENING_NAME
```

---

## 3. CLI Entrypoints

```
python proto/e2e_ui_test.py smoke   → 14 assertions (CACHE_OK through EXT_MEASURE_OK)
python proto/e2e_ui_test.py full    → 17 assertions (smoke + ANNOT_OK, PERSIST_OK, REAL_OK)
```

Entrypoint: `main()` at line 1464. Mode validated at line 1466.

---

## 4. Infrastructure / Helper Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `_xlsx_sheet_xml(zf, sheet_name)` | 35–58 | Parse XLSX XML to find named sheet content |
| `_wait_port(host, port, timeout)` | 61–73 | Poll TCP port until server ready |
| `_make_raster_pdf(src_pdf, out_pdf)` | 76–90 | Convert vector PDF to raster PNG→PDF |
| `_start_server()` | 93–101 | Launch uvicorn in daemon thread |
| `_upload_and_start(page, pdf_path)` | 104–117 | Upload PDF, click Start Measuring, wait |
| `_canvas_box(page)` | 576–580 | Get canvas bounding box or raise |
| `_wait_analyse_ready(page, timeout)` | 583–600 | Poll snap count until analysis done |
| `_draw_area_points(page, points, …)` | 1137–1149 | Click polygon points on canvas |
| `_draw_polygon(page, points)` | 1414–1416 | Thin wrapper over _draw_area_points |

**Total helper lines: ~114**

These are pure utilities with no cross-test state dependencies. They are safe to extract.

---

## 5. Test Functions and State Map

| Test Function | Lines | Assertion | Requires state from |
|---------------|-------|-----------|---------------------|
| `_test_backend_cache_limits()` | 489–573 | CACHE_OK | None (API-only) |
| `_test_project_setup_screen(page)` | 120–155 | SETUP_OK | None (fresh page) |
| `_test_main_measurement_ui_cleanup(page)` | 158–486 | MAIN_UI_OK | SETUP_OK: page must be in measurement UI |
| `_test_vector_area(page)` | 603–627 | VECTOR_OK | MAIN_UI_OK: page in measurement mode |
| `_test_recalibrate_and_exports(page, …)` | 1091–1134 | RECAL_OK | VECTOR_OK: polygon already drawn |
| `_test_site_sides_orientation_ui(page)` | 1152–1241 | SITE_UI_OK | RECAL_OK: calibrated scale in place |
| `_test_opening_and_xlsx_export(page, …)` | 1244–1292 | XLSX_OK | SITE_UI_OK: site poly + orientation stored |
| `_test_project_save_load(page, …)` | 1295–1330 | PROJECT_OK | XLSX_OK: opening + site poly in state |
| `_test_raster_mode(page)` | 1356–1366 | RASTER_OK | None (uploads new PDF) |
| `_test_mouse_wheel_zoom(page)` | 630–639 | WHEEL_OK | Raster page loaded |
| `_test_snap_helpers(page)` | 642–706 | SNAP_OK | Page with snap index; uses JS evaluate |
| `_test_selection_and_area_type_helpers(page)` | 767–1004 | SELECT_OK | Page; sets own state via JS evaluate |
| `_test_setback_helpers(page)` | 709–764 | SETBACK_OK | Page; sets own state via JS evaluate |
| `_test_extended_measurement_helpers(page)` | 1007–1088 | EXT_MEASURE_OK | Page; sets own state via JS evaluate |
| `_test_pdf_annotations_export(page, …)` | 1333–1353 | ANNOT_OK (full) | PROJECT_OK: annotated data in state |
| `_test_real_pdf_multipage_persistence(page)` | 1418–1461 | PERSIST_OK (full) | None (uploads REAL_PDF) |
| `_test_real_pdf_navigation_rotate_export(page, …)` | 1369–1411 | REAL_OK (full) | None (uploads REAL_PDF) |

---

## 6. State Dependency Chain

The `main()` function runs all tests **sequentially on one shared page object**:

```
_test_backend_cache_limits()         ← API-only, no page
 ↓ browser started
_test_project_setup_screen(page)     ← fresh page
 ↓ measurement page open
_test_main_measurement_ui_cleanup(page)
 ↓ UI verified
_test_vector_area(page)              ← draws polygon E2E_ROOM_A
 ↓ polygon in mPolys
_test_recalibrate_and_exports(page)  ← uses existing polygon
 ↓ calibrated scale set
_test_site_sides_orientation_ui(page) ← adds site poly + north
 ↓ site polygon + orientation in state
_test_opening_and_xlsx_export(page)  ← draws opening E2E_VOID_A, exports XLSX
 ↓ opening in mOpenings, XLSX verified
_test_project_save_load(page)        ← saves/loads entire state
 ↓ project file verified
...
_test_pdf_annotations_export(page)   ← (full only) requires annotated data
```

Later tests that use `page.evaluate()` to inject state (`_test_snap_helpers`,
`_test_selection_and_area_type_helpers`, `_test_setback_helpers`,
`_test_extended_measurement_helpers`) can technically run on any measurement page.
However, they still share the page object and depend on being within the same
browser session.

---

## 7. Token Reduction by Section

| Section | Lines | Extractable? |
|---------|-------|-------------|
| Helpers (_xlsx_sheet_xml, _wait_port, etc.) | ~114 | YES — pure utilities, no state |
| _test_backend_cache_limits | ~85 | Marginally (needs server imports) |
| _test_main_measurement_ui_cleanup | ~329 | NO — stateful, must run in sequence |
| _test_selection_and_area_type_helpers | ~238 | NO — stateful pipeline |
| _test_site_sides_orientation_ui | ~90 | NO — requires prior calibration |
| All other test functions | ~669 | NO — pipeline dependencies |

**Maximum safe extraction: ~114 lines (7.5%)**

---

## 8. Proposed Split Structure — Feasibility

Proposed:
```
proto/tests/
  __init__.py
  e2e_helpers.py         ← safe
  test_smoke_flow.py     ← NOT SAFE (stateful pipeline)
  test_ui_contract.py    ← NOT SAFE (stateful pipeline)
  test_xlsx_export.py    ← NOT SAFE (depends on prior state)
  test_metadata.py       ← NOT SAFE (depends on prior state)
  test_page_scales.py    ← NOT SAFE (depends on prior state)
  test_opening_parent.py ← NOT SAFE (depends on prior state)
```

`e2e_helpers.py` alone is safe. All test modules are NOT safe because:

1. **Stateful pipeline**: Test functions consume browser state produced by previous functions.
   To isolate a test module, each would need to recreate all prior state — massive code
   duplication that weakens test isolation guarantees and risks skipping coverage.

2. **Shared page object**: A single `page` object threads through all tests. Splitting
   requires passing it (or a factory) across module boundaries, adding fragile coupling.

3. **Token benefit is negligible if pipeline preserved**: If the wrapper imports all 17
   test functions to run them in sequence, the total token load at runtime is unchanged.

4. **No functional problem**: Tests are passing, clean, well-structured. No regression
   risk justifies a refactor that yields ≤7.5% line reduction in the main file.

---

## 9. Risk Assessment

| Risk | Level | Notes |
|------|-------|-------|
| Breaking CLI smoke/full | HIGH (if split) | Pipeline ordering must be exact |
| Dropping assertions | HIGH (if split) | State-dependent assertions could be silently skipped |
| Import complexity | MEDIUM (if split) | Cross-module server/page imports add fragility |
| Helper extraction only | LOW | Pure functions, no state |
| Doing nothing | NONE | Tests pass, no active defect |

---

## 10. Decision

**AUDIT_ONLY_STOP**

Rationale:
- The test suite is a stateful pipeline. Splitting test functions into independent modules
  is NOT safe without duplicating state setup or weakening coverage.
- Only helper extraction (~114 lines) is safe, providing ~7.5% reduction — insufficient
  to justify the split overhead.
- No test is failing; no stop condition requires a fix.
- Token load from this file can be managed by reading it in sections rather than splitting.

**Follow-on recommendation**: If future token reduction is needed, the safer approach is
to shrink individual test functions by factoring out large `page.evaluate()` JS strings
into separate `.js` files served statically — similar to the CSS/JS split done in
RUN_FRONTEND_UI_HTML_SPLIT.md. This would not affect the Python structure.

---

## 11. What Was NOT Changed

- proto/e2e_ui_test.py: unchanged (1525 lines)
- proto/ui.html: unchanged
- proto/server.py: unchanged
- All CLI commands remain: `python proto/e2e_ui_test.py smoke` and `full`
