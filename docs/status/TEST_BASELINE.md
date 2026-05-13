# TEST_BASELINE.md — BMA-Plan Test Baseline

Date: 2026-05-13

## Commands

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full
```

## Latest Result: PASS (2026-05-13)

### Smoke Test Assertions

| Assertion | Status |
|-----------|--------|
| CACHE_OK | PASS |
| SETUP_OK | PASS |
| MAIN_UI_OK (incl. leftPanelTabsOk, rightPanelCompatibilityVisible) | PASS |
| VECTOR_OK | PASS |
| RECAL_OK | PASS |
| SITE_UI_OK | PASS |
| XLSX_OK | PASS |
| PROJECT_OK | PASS |
| RASTER_OK | PASS |
| WHEEL_OK | PASS |
| SNAP_OK | PASS |
| SELECT_OK (incl. metaOk, parentSelectVisible, parentReassigned) | PASS |
| SETBACK_OK | PASS |
| EXT_MEASURE_OK | PASS |
| MENU_OK (incl. curvesMath, rectTool, circleTool, ellipseTool, annotateMenu) | PASS |
| PATH_GEOMETRY_OK (tests A–E: rect/circle/mixed/legacy/roundtrip) | PASS |

### Full Test (additional)

| Assertion | Status |
|-----------|--------|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |

## Known Non-Fatal

- `WinError 10054` (ConnectionResetError) on uvicorn shutdown — does not affect test results.

## Key New Assertions Added (2026-05-09)

- `leftPanelTabsOk: True` — left panel Sheets/Objects/Properties tab switching
- `parentSelectVisible: True` — select shown for unlinked opening
- `parentReassigned: True` — rpSetOpeningParent links correctly
- `metaOk: True` — 5 measurement metadata fields present
- `metaPanelVisible: True` — properties panel shows metadata fields
- `strippedMetaOk: True` — re-normalization of metadata after strip
- scale_state, object_count, needs_attention — in XLSX Page Scales
- สรุปตาม Report Target — sheet present in XLSX workbook
