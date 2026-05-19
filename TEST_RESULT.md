# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-003b — /export-png ZIP endpoint (end-of-day bundle)

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

# Previous: HT-18a-ext — Extended pushUndo() coverage to 22 more mutation sites

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
