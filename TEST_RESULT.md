# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: UI Layout Options — Mockup V3 Mode Support

Date: 2026-05-10

## Result: PASS

Proto HEAD: `087c769`

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## New Assertions (all True)

| Key | Check |
|-----|-------|
| `optionsBtnVisible` | `#btn-ui-layout` visible in topbar |
| `optionsPanelExists` | `#ui-layout-panel` in DOM |
| `currentStablePresetExists` | `#ulp-preset-current` in DOM |
| `mockupV3PresetExists` | `#ulp-preset-v3` in DOM |
| `optionsPanelOpens` | toggle opens to `flex`, close sets `none` |
| `topModeSwitchNoCrash` | `setUiLayoutOption('top','v3')` + reset — no throw |
| `leftModeSwitchNoCrash` | same for left |
| `rightModeSwitchNoCrash` | same for right |
| `widgetsModeSwitchNoCrash` | same for widgets |
| `localStorageKeyWritten` | `localStorage.getItem('bmaPlan.uiLayoutOptions.v1')` truthy after switch |
| `resetRestoresCurrentStable` | after mockup_v3 preset + current reset, no v3 body classes |

## Regression Coverage Maintained

All prior assertions PASS. Export green check, topbar height, toolbar position, layer rows, left tabs, widget visibility — all unaffected.

---

# Previous: Page-Scoped Layer Implementation Batch (6 Sprints)

Date: 2026-05-10

## Result: PASS

Proto HEAD at batch end: `a6c67e7`

## Commands Run (after each source sprint)

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## Sprint Results

| Sprint | Type | Result | Proto HEAD |
|--------|------|--------|------------|
| RUN_LAYER_SCOPE_AUDIT | docs-only | PASS (no test run) | — |
| RUN_PAGE_LAYER_INSTANCE_MODEL | source | PASS | `ed9944d` |
| RUN_PAGE_TYPE_LAYER_PRESETS | source + e2e fix | PASS | `eefab31` |
| RUN_OBJECT_LAYER_VALIDATION | source | PASS | `94db3d9` |
| RUN_LAYER_TOOL_AWARENESS | source | PASS | `a6c67e7` |
| RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR | docs-only | PASS (no test run) | — |

## E2E Fix in Sprint 3

Old assertion checked for Thai plan-preset labels ("พื้นที่หลัก" etc.) which are absent on
the site-preset page used by the test PDF. New assertion: `len(layerRows) >= 4` and
presence of "เส้นอ้างอิง" and "ป้าย" (common to both plan and site presets).

## Regression Coverage Maintained

All prior assertions PASS. Key layer-specific invariants:
- `layerVis.deduction === true && layerLock.deduction === true` after `toggleLayerLock("deduction")` — PASS
- `layerVis.reference_geometry === true && layerLock.reference_geometry === true` after toggle — PASS
- Layer rows show ≥ 4 entries, include "เส้นอ้างอิง" and "ป้าย" — PASS

---

# Previous: 8-Sprint UI Batch

Date: 2026-05-10

## Result: PASS

Proto HEAD: `4a09693`

All sprints (Ribbon Toolbar, Layers Badge, Page Warn, Scale Manager, Warning CSS,
Export Checklist, Visual Consistency) passed full E2E after each commit.
No assertions added in this batch — all existing assertions remain green.

---

# Previous: Canvas Top Info Bar

Date: 2026-05-09

## Result: PASS

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```

## Added Coverage

- Canvas top bar visible inside workspace.
- Canvas top bar uses `pointer-events: none`.
- Canvas top bar shows page, scale, tool, layer, zoom, and coordinates.
- Existing drawing/export/save-load/full workflow still PASS.

---

# Previous: Widget Placement Polish

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
