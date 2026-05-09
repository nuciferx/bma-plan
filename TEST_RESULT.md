# TEST_RESULT.md - Opening Parent Reassignment

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## New Assertions Verified

- SELECT_OK — `parentSelectVisible: True` (select #rp-opening-parent appears for unlinked opening).
- SELECT_OK — `parentReassigned: True` (rpSetOpeningParent sets parentId and parentStatus="linked").

## Regression Coverage Maintained

- All previous SELECT_OK assertions including parentLinked, semanticDefaults, metaOk, strippedMetaOk still PASS.
- CACHE_OK, XLSX_OK, MAIN_UI_OK, and all other assertions still PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue.

---

# Previous: Page Scales Audit

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## New Assertions Verified

- CACHE_OK — `_test_cache` now reads `xl/sharedStrings.xml` from the Page Scales audit XLSX and asserts `scale_state`, `object_count`, `needs_attention` headers are present.

## Regression Coverage Maintained

- All previous CACHE_OK assertions still pass (row count ≥ 4, cache size, bad_scale rejection).
- All XLSX_OK, SELECT_OK, MAIN_UI_OK, and other assertions still PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue.

---

# Previous: Report Target Summary XLSX

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## New Assertions Verified

- XLSX_OK — sheet name assertion now includes `สรุปตาม Report Target` — present in XLSX workbook XML.

## Regression Coverage Maintained

- All previous XLSX_OK assertions still pass (all sheet names, text content, project info, metadata column headers).
- MAIN_UI_OK, VECTOR_OK, RECAL_OK, SNAP_OK, PROJECT_OK, ANNOT_OK, PERSIST_OK, REAL_OK all PASS.
- SELECT_OK (metaOk, metaPanelVisible, strippedMetaOk) still PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect tests.

---

# Previous: Export Metadata Columns XLSX

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## New Assertions Verified

- XLSX_OK — `_test_opening_and_xlsx_export` now checks that all 5 new column headers (`measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`) appear in the XLSX sharedStrings XML.
- The column headers are present in sheets: สรุปพื้นที่, ความยาวเส้น Polygon, ที่จอดรถ, ระยะอ้างอิง.

## Regression Coverage Maintained

- All previous XLSX_OK assertions still pass (sheet names, text content, project info).
- MAIN_UI_OK, VECTOR_OK, RECAL_OK, SNAP_OK, PROJECT_OK, ANNOT_OK, PERSIST_OK, REAL_OK all PASS.
- SELECT_OK (metaOk, metaPanelVisible, strippedMetaOk) still PASS.

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect tests.

---

# Previous: Measurement Profile Metadata Foundation

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## New Assertions Verified

- `metaOk: True` — `mPolys[0]` after `rpSetSemanticTag("gross_floor_area")` has `measurementProfile="legal_building_area"`, `objectCategory="area"`, `reportTarget="Building Area Summary"`, `countingRule="included"`, `lawBasis="พื้นที่อาคาร"`
- `metaPanelVisible: True` — Properties panel shows `.rp-meta-value` read-only labels
- `strippedMetaOk: True` — after stripping and re-normalizing, `measurementProfile="use_area"`, `objectCategory="area"`, `countingRule="classified"` are re-derived correctly

## Regression Coverage Maintained

- All existing SELECT_OK assertions still pass (semantic defaults, semantic editing, use category, label hidden, layer lock, ref hit, structured warnings)
- MAIN_UI_OK, VECTOR_OK, RECAL_OK, SNAP_OK, PROJECT_OK, XLSX_OK, ANNOT_OK, PERSIST_OK, REAL_OK all PASS

## Notes

- Non-fatal WinError 10054 on uvicorn shutdown remains — known issue, does not affect tests.

---

# Previous: Post-Baseline Workspace Housekeeping

Date: 2026-05-09

## Result

PASS (housekeeping only — no source changed, no tests re-run)

## Last Known Test State

Tests were run against baseline commit d4dce83 (root) / c92f1d8 (proto):

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## Notes

- No source files were changed in this housekeeping sprint.
- Test results carry over from the previous baseline commit.

---

# Previous: Right Panel Organization After Mockup V3

Date: 2026-05-09

## Result

PASS

## Commands Run

- `python -m py_compile proto/server.py proto/e2e_ui_test.py` - PASS
- `python proto/e2e_ui_test.py smoke` - PASS
- `python proto/e2e_ui_test.py full` - PASS

## Additional Verification

- Manual viewport check with Chromium:
  - `1440 x 900` - PASS
  - `1512 x 982` - PASS
  - `1366 x 768` - PASS

## Coverage Added

- Right panel `Layers` section is visible and appears before compatibility `Properties` and `Object Tree`.
- Right panel layer rows expose layer counts and existing visibility/lock controls.
- Existing Properties/Object Tree remain accessible below Layers.
- Workflow order remains `Open PDF -> Set Scale -> Page Setup -> Measure -> Review -> Export`.
- `Set Scale` remains before `Page Setup`.
- Left panel labels remain `Sheets`, `Objects`, `Properties`.
- Status bar still includes `Scale`, `Objects`, `Warnings`, `Layer`, `Tool`, and `Save`.
- Forbidden Phase 1 feature wording is not visible in active UI.

## Notes

- No backend/export/save-load/data-model files were edited.
