# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Widget Placement Polish

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```

## Notes

- Full test initially caught a local regression from calling `collectAreas()` in live widget rendering; fixed by using current-page-only state reads.
- Existing non-fatal Windows `ConnectionResetError` appeared after successful full output.

---

# Previous: Static 404 Fix

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## HTTP Verification (port 8001)

```
GET /static/css/app.css       → 200 OK
GET /static/js/semantic-meta.js → 200 OK
GET /static/js/opening-parent.js → 200 OK
GET /                         → 200 OK
```

## Regression Coverage Maintained

- All 17 assertions PASS: CACHE through REAL_OK.
- `cssVarLoaded: True`, `cssLinkPresent: True` — CSS applies in browser.
- All widget visibility assertions PASS.
- Proto commit: a2099ec.

---

# Previous: CSS BOM Fix

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## Regression Coverage Maintained

- All 17 assertions PASS: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK,
  XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK,
  ANNOT_OK, PERSIST_OK, REAL_OK.
- `cssVarLoaded: True` — CSS custom properties active in browser.
- All widget visibility assertions PASS (scaleStatusWidgetVisible, pageInfoWidgetVisible,
  reviewWarningWidgetVisible, exportReadyWidgetVisible).
- Proto commit: 65f5a65.

---

# Previous: Mockup Layout Mapping (Docs Only)

Date: 2026-05-09

## Result: NO TEST RUN REQUIRED (docs only)

No source code changed. Baseline from Static Asset Healthcheck sprint (proto 797a4a2) remains valid.

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS (last run 2026-05-09)
python proto/e2e_ui_test.py smoke                           # PASS (last run 2026-05-09)
python proto/e2e_ui_test.py full                            # PASS (last run 2026-05-09)
```

---

# Previous: Static Asset Healthcheck

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## New Assertions Verified (all True)

- MAIN_UI_OK `cssLinkPresent: True` (`<link href="/static/css/app.css">` in DOM)
- MAIN_UI_OK `cssVarLoaded: True` (CSS custom property `--blue` non-empty)
- MAIN_UI_OK `semanticMetaJsLoaded: True` (`AREA_SEMANTIC_TAGS` defined in global scope)
- MAIN_UI_OK `openingParentJsLoaded: True` (`openingProbePoints` defined in global scope)

## Regression Coverage Maintained

- All previous assertions including widget visibility, leftPanelTabsOk,
  forbiddenPhase1StringsAbsent, rightPanelCompatibilityVisible — all PASS.
- Proto commit: 797a4a2.

---

# Previous: Visible Test Widgets UI

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## New Assertions Verified (all True)

- MAIN_UI_OK `scaleStatusWidgetVisible: True` (#scale-badge visible in sidebar)
- MAIN_UI_OK `pageInfoWidgetVisible: True` (#lp-page-info visible in sidebar)
- MAIN_UI_OK `reviewWarningWidgetVisible: True` (#widget-review-warnings visible in sidebar)
- MAIN_UI_OK `exportReadyWidgetVisible: True` (#widget-export-ready visible in sidebar)

## Regression Coverage Maintained

- All previous MAIN_UI_OK assertions including `leftPanelTabsOk`, `workflowVisible`,
  `forbiddenPhase1StringsAbsent`, `rightPanelCompatibilityVisible` still PASS.
- SELECT_OK, XLSX_OK, VECTOR_OK, RECAL_OK, SNAP_OK, PROJECT_OK, ANNOT_OK,
  PERSIST_OK, REAL_OK, all others — all PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect results.
- Proto commit: a2a6e81.

---

# Previous: E2E Test Split Audit

Date: 2026-05-09

## Result: NO TEST CHANGES (AUDIT_ONLY_STOP)

No source code changes. Baseline (proto 9fa57a0) remains valid. All 17 assertions PASS.

---

# Previous: Frontend UI HTML Split

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## Regression Coverage Maintained

- MAIN_UI_OK `toolbarFitsWorkspace: True`, `toolbarBelowHeader: True`, `topbarNoOverflow: True` — CSS external load works
- SELECT_OK `parentLinked: True`, `parentReassigned: True` — opening-parent functions intact in external JS
- SELECT_OK `semanticEdited: True`, `metaOk: True` — semantic-meta functions intact in external JS
- XLSX_OK — export still correct
- All 17 assertions: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, ANNOT_OK, PERSIST_OK, REAL_OK — all PASS

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect results.
- server.py reduced from 1451 to ~1290 lines; behavior unchanged via re-import.

---

# Previous: Left Properties Migration

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```

## New Assertions Verified

- MAIN_UI_OK — `leftPanelTabsOk: True` (Objects tab shows lp-objects-content, Properties tab shows lp-properties-content, Sheets tab restores sidebar-content).

## Regression Coverage Maintained

- MAIN_UI_OK `rightPanelCompatibilityVisible: True` — right panel properties section still present.
- All previous MAIN_UI_OK assertions including leftPanelLabelsOk, workflowVisible, workflowOrderOk still PASS.
- SELECT_OK (parentLinked, parentSelectVisible, parentReassigned, metaOk, metaPanelVisible, strippedMetaOk) still PASS.
- CACHE_OK, XLSX_OK, VECTOR_OK, RECAL_OK, SNAP_OK, PROJECT_OK, ANNOT_OK, PERSIST_OK, REAL_OK all PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect results.
- Full test detail and all assertions: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)
