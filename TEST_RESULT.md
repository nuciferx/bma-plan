# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Max Token Reduction / File Split

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                           # PASS
python proto/e2e_ui_test.py full                            # PASS
```

## Regression Coverage Maintained

- MAIN_UI_OK `rightPanelCompatibilityVisible: True` — compat sections still present
- MAIN_UI_OK `rightPanelLayersFirst: True` — Layers section first in right panel
- MAIN_UI_OK `leftPanelTabsOk: True` — left panel tabs switch correctly
- XLSX_OK — export functions correctly (semantic metadata helpers now imported from export package)
- All previous assertions: CACHE_OK, SETUP_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, ANNOT_OK, PERSIST_OK, REAL_OK — all PASS

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
