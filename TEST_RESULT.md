# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: BLOAT-2 — Extract status-bar JS to proto/static/js/status-bar.js

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS, smoke 18/18 + PHASE_BLOAT2_OK, full 21/21 + PHASE_BLOAT2_OK GREEN

## Commands

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # EXIT 0 — 18/18 + PHASE_BLOAT2_OK
python proto/e2e_ui_test.py full                           # EXIT 0 — 21/21 + PHASE_BLOAT2_OK
```

## New Marker — PHASE_BLOAT2_OK (8 sub-checks)

| Sub-check | Result |
|---|---|
| fileLoad (HTTP 200 + file contains expected fn defs) | PASS |
| fnsOk (all 8 functions defined as typeof === "function") | PASS |
| constsOk (both consts defined + values correct) | PASS |
| modeLabelOk (`updateModeLabel("area")` → writes `'วัดพื้นที่ ⬡'` to `#lbl-mode`) | PASS |
| bottomBarOk (`updateBottomBar()` → writes 4 fields) | PASS |
| setDirtyOk (`_setDirty()` → flips `isDirty=true` + writes label) | PASS |
| markSavedOk (`_markSaved()` → flips `isDirty=false` + writes label) | PASS |
| crossScriptOk (inline ui.html script can read moved `MODE_BASE_LABELS` const) | PASS |

## Baseline Markers Retained (no regression)

All 21 core markers GREEN: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK, ANNOT_OK, PERSIST_OK, REAL_OK.

PERSIST_OK on real 45-page permit confirms `_setDirty`/`_markSaved` extraction is safe across a full save/reload cycle.

`/bma-human-test` — SKIPPED. Rationale: mechanical extraction with zero user-visible change; PERSIST_OK on real permit covers the most sensitive surface (_setDirty/_markSaved round-trip).

---

# Previous: BLOAT-1 — CLAUDE.md LOC drift fix + consolidation trigger rule (docs-only)

Branch: main
Date: 2026-05-19

## Result: PASS (no-test, docs-only sprint)

## No-Test Rationale

Per AGENTS.md §1, docs-only sprints record a no-test rationale instead of running tests.
This sprint changed only: `CLAUDE.md` (+21 −2 LOC corrections + Size discipline paragraph) and `docs/status/PHASE_INDEX.md` (+26 −0 queue rows). No source code, UI, test code, or schema changed. Therefore `/bma-e2e` (py_compile + smoke + full) and `/bma-human-test` were not run.

Sanity baseline: `python -m py_compile proto/server.py` → PASS.

## Reference Baseline (from previous sprint: INV-2026-05-19-003b end-of-day bundle)

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py full                           → EXIT 0
  PHASE_INV_EXPORT_PNG_OK: PASS (new in 003b)
  PHASE_INV_PRINT_CANVAS_OK: PASS — 8 sub-checks (new in 003a)
  PHASE_HT18B_OK: 13/13 GREEN (fixed in HT-18c)
  PHASE_HT18_OK: 36/36 GREEN (from HT-18a-ext)
  All 21 core markers GREEN (smoke 18 + PHASE_I_A_OK + PHASE_I_B1_OK + ANNOT_OK + PERSIST_OK + REAL_OK)
```

Markers: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK, ANNOT_OK, PERSIST_OK, REAL_OK (smoke 18 + full adds 3).

---

# Previous (older): INV-2026-05-19-003b — /export-png ZIP endpoint (end-of-day bundle)

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, full EXIT 0; PHASE_INV_EXPORT_PNG_OK (new); PHASE_INV_PRINT_CANVAS_OK (new); PHASE_HT18B_OK 13/13 GREEN

## Commands

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PY_COMPILE_OK (all 3 sprints)
python proto/e2e_ui_test.py full                           # EXIT 0 — INV-003b
python proto/e2e_ui_test.py smoke                          # EXIT 0 — HT-18c
python proto/e2e_ui_test.py full                           # EXIT 0 — INV-003a
```

## New Markers — INV-003b

`PHASE_INV_EXPORT_PNG_OK`: PASS — verifies `/export-png` endpoint returns `application/zip`, contains correct PNG count for selected pages, file size reasonable.

## New Markers — INV-003a

`PHASE_INV_PRINT_CANVAS_OK` (8 sub-checks):

| Sub-check | Result |
|---|---|
| printCurrentPageFnExists | PASS |
| printSelectedPagesFnExists | PASS |
| printMenuItemsPresent | PASS |
| printCurrentPageTriggersWindow | PASS |
| canvasToDataURLCalled | PASS |
| printWindowCreated | PASS |
| printSelectedPagesFiltersPages | PASS |
| noPrintRegressionOnMeasure | PASS |

## HT-18c — PHASE_HT18B_OK 13/13

Save/load round-trip now fully GREEN. Fixed by replacing deep `eq()` (too strict after `normalizeAllObjects` mutates pre-snapshot) with field-by-field checks + fixing `applyLoadedProject` `_projInfoSnap` restoration.

| Sub-check group | Result |
|---|---|
| A poly round-trip | PASS |
| B opening round-trip | PASS |
| C line round-trip | PASS |
| D ref round-trip | PASS |
| E parking round-trip | PASS |
| F-M page metadata + projectInfo + layer state (8 checks) | PASS |

All 13/13 PASS. HT-18 series complete.

## Predecessor Markers Retained (no regression)

`PHASE_HT18_OK` 36/36. `PHASE_INV_ZEN_V2_OK` 10/10. `PHASE_INV_OVERVIEW_OK` 9/9. `PHASE_INV_ZEN_OK` 10/10. `PHASE_INV_PALETTE_OK` 10/10. `PHASE_INV_POLISH_001C_OK` 5/5. All 21 core markers GREEN.

## Pre-existing Non-regressions

`PHASE_HT8C_OK` 3/5, `PHASE_HT8D1_OK` 8/9, `PHASE_HT10_OK` 8/10, `PHASE_HT12H_OK` 4/5 — all pre-existing before this session, unrelated to any sprint in this bundle.

---

> Older entries (HT-18a-ext, HT-18a, INV-002b, INV-002a, INV-001a/b/c, and earlier) archived to [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md).

<!-- ARCHIVED BELOW — HT-18a-ext (formerly Previous, now superseded) -->

# Previous (older): HT-18a-ext — Extended pushUndo() coverage to 22 more mutation sites

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, full EXIT 0; PHASE_HT18_OK 36/36; HUMAN_TEST_PASS

## Commands

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PY_COMPILE_OK
python proto/e2e_ui_test.py full                           # EXIT 0 — 21/21 core markers GREEN
```

## PHASE_HT18_OK (36/36)

- 22 source-presence checks: `moveLayerUp`, `moveLayerDown`, `renameLayer`, `setLayerColor`, `toggleLayerLock`, `setAllLayersVisible`, `hideOtherLayers`, `lockOtherLayers`, `setAllLayersLocked`, `toggleLayer`, `layerHideOthers`, `layerShowAll`, `setQuickTag`, `setPageTag`, `setPageFloorKind`, `setPageFloorNum`, `applyAutoNames`, `excludePage`, `restorePage2`, `hideSelectedPages`, `rotatePage`, `resetPageScale`
- 7 runtime isDirty-flip checks — all PASS
- 7 original HT-18a checks — all PASS

All 36 PASS. `{'all': True}`. HUMAN_TEST_PASS (3 inline fixes: `toggleLayer`, `layerHideOthers`, `layerShowAll`).

> Older entries (HT-18a, INV-002b, INV-002a, and earlier) archived to [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md).

<!-- INV-002b, INV-002a, INV-001a/b/c, HT-18a and earlier archived to docs/archive/test-history-2026-05-09.md -->
