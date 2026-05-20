# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; NEW marker BUG_20260520_SEL_MIDPAN_OK GREEN; total 22 markers; all 21 prior baselines intact.

## Commands

```bash
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
py -3.12 proto/e2e_ui_test.py full                           # EXIT 0 — ALL GREEN
```

## Full Results — All Markers GREEN

| Marker | Result |
|---|---|
| CACHE_OK | PASS |
| SETUP_OK | PASS |
| MAIN_UI_OK | PASS |
| VECTOR_OK | PASS |
| RECAL_OK | PASS |
| SITE_UI_OK | PASS |
| XLSX_OK | PASS |
| PROJECT_OK | PASS |
| RASTER_OK | PASS |
| WHEEL_OK | PASS |
| SNAP_OK | PASS |
| SELECT_OK | PASS |
| SETBACK_OK | PASS |
| EXT_MEASURE_OK | PASS |
| MENU_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| PHASE_I_A_OK | PASS |
| PHASE_I_B1_OK | PASS |
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| **BUG_20260520_SEL_MIDPAN_OK** | **PASS** (NEW — canvas #cc transform moved +70x/+45y under Playwright middle-button drag; mode stayed 'sel') |

Scope skills: `/bma-measure-ux` → `MEASURE_UX_PASS`. Regression: `/bma-measure-regression` → `MEASURE_REGRESSION_PASS`.

## Fix Summary

`proto/ui.html` mousedown handler `mode==="sel"` branch: added pan guard `if(e.button===1||spaceDown){isPan=true;lastMx=e.clientX;lastMy=e.clientY;ws.style.cursor="grabbing";return;}` at the very top of the branch. 1 line inserted. mouseup already clears `isPan` + resets cursor — no change needed there.

---

# Previous: BLOAT-FLAKE-1 — Fix REAL_PDF `_wait_analyse_ready` flake

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0 — PERSIST_OK / REAL_OK / ANNOT_OK GREEN; all BLOAT and INV_PAGE_SETUP markers GREEN. LOOP_STOP_REGRESSION halt cleared. BLOAT-5 retroactively full-validated.

## Commands

```bash
python -m py_compile proto/e2e_ui_test.py                  # PASS
python proto/e2e_ui_test.py full                           # EXIT 0 — ALL GREEN
```

## Full Results — All Markers GREEN

| Marker | Result |
|---|---|
| CACHE_OK | PASS |
| SETUP_OK | PASS |
| MAIN_UI_OK (incl. pageSetupJsLoaded: True) | PASS |
| VECTOR_OK | PASS |
| RECAL_OK | PASS |
| SITE_UI_OK | PASS |
| XLSX_OK | PASS |
| PROJECT_OK | PASS |
| RASTER_OK | PASS |
| WHEEL_OK | PASS |
| SNAP_OK | PASS |
| SELECT_OK | PASS |
| SETBACK_OK | PASS |
| EXT_MEASURE_OK | PASS |
| MENU_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| PHASE_I_A_OK | PASS |
| PHASE_I_B1_OK | PASS |
| **ANNOT_OK** | **PASS** (flaked 3x during BLOAT-5; now stable) |
| **PERSIST_OK** | **PASS** (flaked 3x during BLOAT-5; now stable) |
| **REAL_OK** | **PASS** (flaked 3x during BLOAT-5; now stable) |
| PHASE_BLOAT2_OK 8/8 | PASS |
| PHASE_BLOAT3_OK 8/8 | PASS |
| PHASE_BLOAT4_OK 8/8 | PASS |
| PHASE_BLOAT5_OK 8/8 | PASS (retroactively full-validated) |
| PHASE_INV_PAGE_SETUP_A_OK 8/8 | PASS |
| PHASE_INV_PAGE_SETUP_B_OK 9/9 | PASS |
| PHASE_INV_PAGE_SETUP_C_OK 7/7 | PASS |
| PHASE_HT11_OK 10/10 | PASS |

`/bma-human-test` — N/A (test-infrastructure change only; no app runtime code touched).

## Fix Summary

`_wait_analyse_ready` in `proto/e2e_ui_test.py`: default timeout raised 30.0 s → 60.0 s; grace window added (+50% time if status bar still shows active progress at deadline). ~15 LOC changed. No app code touched.

---

<!-- Older results archived to docs/archive/test-history-2026-05-09.md -->
