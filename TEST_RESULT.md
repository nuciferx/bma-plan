# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Mockup V3 Alignment — Phase E + F (CSS cleanup + Final tests)

Branch: feature/mockup-v3-alignment

Date: 2026-05-11

## Result: PASS — Mockup V3 Alignment COMPLETE

Proto HEAD: `f6a1288` (last commit was Phase D + e2e tweak; Phase E touches proto submodule with CSS removal only)

## Commands Run

```
python3 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3 proto/e2e_ui_test.py smoke                          → PASS (exit 0)
python3 proto/e2e_ui_test.py full                           → PASS (exit 0)
```

Python 3.11 required (`server.py` uses `dict | None` syntax). macOS default `/usr/bin/python3` (3.9.6) fails import.

## Test Markers (all OK)

CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, ANNOT_OK, PERSIST_OK, REAL_OK

## Measurement Verification (no regression)

| Marker | Value | vs Baseline |
|---|---|---|
| VECTOR | อาคาร/ห้อง 305.56 ตร.ม. | ✅ unchanged |
| XLSX | สุทธิ 0.82 ตร.ม. | ✅ unchanged |
| PERSIST page 1 | 66646.05 ตร.ม. | ✅ unchanged |
| PERSIST page 2 | 11883.33 ตร.ม. | ✅ unchanged |
| REAL | 45 pages, rotation 90° | ✅ unchanged |
| RECAL | ★ 1:5 สอบเทียบ, 0.75 ตร.ม. | ✅ unchanged |

## Stop Conditions Triggered

None.

---

# Previous: Mockup V3 Alignment — Phase A (Subtractive Removal)

Branch: feature/mockup-v3-alignment

Date: 2026-05-11

## Result: PASS

Proto HEAD: `72d621c`

## Commands Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## Test Markers (all OK)

CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, ANNOT_OK, PERSIST_OK, REAL_OK

## Removed Assertions (covered systems are gone)

- `panelLayoutControlsExist`, `panelLayoutKeyWritten`, `panelResetRestoresDefaults`, `panelCollapseWorks`
- `widgetPlacementRegistryExists`, `widgetPlacementHelpersExist`, `widgetPlacementSearchBox`, `widgetPlacementListRendered`, `widgetPlacementKeyWritten`, `widgetVisibilityToggleWorks`, `widgetOrderInputWorks`, `widgetRegionMoveWorks`, `widgetSizeClassApplies`, `widgetPlacementResetWorks`, `widgetPlacementMalformedJsonSafe`, `widgetLockedRespected`, `widgetLeftPanelScrollOk`, `widgetRightPanelScrollOk`, `widgetCurrentPageLayersVisible`
- `inspectionPanelVisible`, `inspectionPanelInSidebar`, `inspectionPanelNotInCanvas`, `inspectionPanelWorkflowVisible`, `inspectionPanelContextVisible`, `inspectionPanelToggleWorks`
- `optionsBtnVisible`, `optionsPanelExists`, `currentStablePresetExists`, `mockupV3PresetExists`, `optionsPanelOpens`, `topModeSwitchNoCrash`, `leftModeSwitchNoCrash`, `rightModeSwitchNoCrash`, `widgetsModeSwitchNoCrash`, `localStorageKeyWritten`, `resetRestoresCurrentStable`
- `reviewWarningWidgetVisible`, `exportReadyWidgetVisible`

## New Assertions

| Key | Check |
|-----|-------|
| `leftPanelScrollOk` | `.sidebar-scroll-body` keeps `overflow-y: auto` |
| `rightPanelScrollOk` | `#rp-content` keeps `overflow-y: auto` |

## Stubbed (to true) — UI elements gone but field needed

`workflowVisible`, `workflowOrderOk`, `primaryWorkflowAvoidsProjectSetup` — workflow-card removed; assertions return literal `true`.

## Stop Conditions Triggered

None. Area drawing, opening drawing, save/load, export, scale, coordinate, persistence, real PDF — all unchanged.

---

# Previous: Widget / Menu Placement System

Date: 2026-05-11

## Result: PASS

Proto HEAD: (current working tree)

## Commands Run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## New Assertions (all True)

| Key | Check |
|-----|-------|
| `widgetPlacementRegistryExists` | `WIDGET_MENU_REGISTRY` non-empty array (>= 10 entries) |
| `widgetPlacementHelpersExist` | 9 helper functions defined |
| `widgetPlacementSearchBox` | `#wp-search` and `#wp-category` exist |
| `widgetPlacementListRendered` | `#wp-list` shows ≥ 5 `.wp-row` rows |
| `widgetPlacementKeyWritten` | `bmaPlan.widgetPlacement.v1` written after option change |
| `widgetVisibilityToggleWorks` | `.widget-hidden` toggles on `#widget-review-warnings` |
| `widgetOrderInputWorks` | `style.order` updates on order input change |
| `widgetRegionMoveWorks` | `#widget-review-warnings` moves to `#wp-right-zone` then returns to `#sidebar` |
| `widgetSizeClassApplies` | `.widget-size-collapsed` and `.widget-size-large` apply |
| `widgetPlacementResetWorks` | Reset restores defaults |
| `widgetPlacementMalformedJsonSafe` | Loader does not crash on bad JSON |
| `widgetLockedRespected` | Locked `currentPageLayers` ignores region-change attempt |
| `widgetLeftPanelScrollOk` | `.sidebar-scroll-body` still `overflow-y:auto` |
| `widgetRightPanelScrollOk` | `#rp-content` still `overflow-y:auto` |
| `widgetCurrentPageLayersVisible` | Current page layers panel not hidden |

## Existing Assertions

All existing assertions for inspection panel, page info, review warning, export ready, layers panel, scale badge, drawing, save/load, export, real-PDF round-trip, panel layout, and layout options remain PASS.

## Stop Conditions Triggered

None.
