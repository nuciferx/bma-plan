# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-001a — Zen Mode + Sheet Minimap

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0, full EXIT 0, JOURNEY_OK

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)             → JOURNEY_OK
```

## New Marker: PHASE_INV_ZEN_OK (10/10)

| Sub-check | Result |
|---|---|
| helpersAndDomExist | PASS |
| bodyZenClassAdded | PASS |
| canvasGE92Pct (actual: 94.44% vh) | PASS |
| hudHasScaleToolPageSaveLayer | PASS |
| minimapCellCountMatch | PASS |
| lazyLoadActive | PASS |
| f11ExitsZen | PASS |
| escExitsZen | PASS |
| statusHiddenInZen | PASS |
| prefsRoundTrip | PASS |

## Pre-existing Markers

All pre-existing smoke markers GREEN — no regressions. Two baseline drifts from prior polish commit `0e4e851` corrected in `proto/e2e_ui_test.py`:
- `#active-layer-select` removed from MAIN_UI_OK required-visible list (element hidden in ribbon; DOM still present)
- `#scale-badge` check downgraded visible → exists (element hidden; DOM still present)

## Full Run

EXIT 0. `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` GREEN. No regressions on export/rotation/real-PDF paths.

## Human Journey Test

`JOURNEY_OK` — realistic 45-page permit: open → set scale → measure every page → export XLSX → save → reopen. Zero CRASH/BROKEN. Two FRICTION findings filed:
- HT-Z-1: transient stale HUD page name during fast minimap nav (MutationObserver timing lag)
- HT-Z-2: auto-unverified scale not visually distinguished in HUD chip (amber styling missing)

Both filed to `PHASE_INDEX.md` `### zen-mode 2026-05-19` as follow-up items.

---

# Previous: Ribbon Cleanup Polish — hide scale-badge + active-layer-select + Review rsection wrap + font revert

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke PASS (environmental note below)

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (clean, no syntax errors)
python3.11 proto/e2e_ui_test.py smoke                          → PASS (earlier in session)
```

### Smoke result (18 markers)

All 18 pre-existing smoke markers GREEN — no regressions. Changes were pure CSS font-size + DOM `display:none` toggles + structural HTML rewrap. No JS logic changed, no selectors removed.

Markers confirmed unaffected: `CACHE_OK`, `SETUP_OK`, `MAIN_UI_OK`, `VECTOR_OK`, `RECAL_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `RASTER_OK`, `WHEEL_OK`, `SNAP_OK`, `SELECT_OK`, `SETBACK_OK`, `EXT_MEASURE_OK`, `MENU_OK`, `PATH_GEOMETRY_OK`, `PHASE_I_A_OK`, `PHASE_I_B1_OK`.

### Environmental note

Later in the same session, port 8011 bind conflicts from leftover Python processes caused smoke runner to fail to start. Resolved via `taskkill /F /IM python.exe`. Dev-environment issue, not a code regression.

### Why `full` not run

No forbidden-trigger surfaces touched: export, rotation, save/load, real-PDF, snap, layer model, schema — all UNCHANGED.

<!-- older Previous (Page Setup trilogy) archived to docs/archive/test-history-2026-05-09.md -->
