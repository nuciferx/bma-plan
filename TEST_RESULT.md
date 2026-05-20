# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-20-001 — Verify Scale tool

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; NEW marker INV_VERIFY_SCALE_OK 9/9 all:True; all key baselines GREEN; zero regression.

## Commands

```bash
py_compile proto/server.py proto/e2e_ui_test.py  # PASS
proto/e2e_ui_test.py full                         # EXIT 0 — ALL GREEN
```

## New Marker: INV_VERIFY_SCALE_OK — 9/9 sub-checks

| Sub-check | Result |
|---|---|
| domAndHelpers | PASS — `#verify-modal`, `verifyScale`, `verifyFinish`, `verifyAccept`, `verifyRecalibrate`, `verifyAverage`, `_verifyBand`, `calibPanelOk` all present in DOM/JS |
| guardWhenNoScale | PASS — `verifyScale()` returns early (no modal) when no calibration exists |
| greenBandZeroDev | PASS — %dev=0 produces green band, Accept enabled, Re-calibrate/Average present |
| acceptWritesResult | PASS — `verifyAccept()` writes `calibScale.verifyResult{pct, action:"accept", verifyPts_per_m, ts}` |
| redBandHighDev | PASS — high %dev (≥2%) produces red band |
| recalibrateSetsPpm | PASS — `verifyRecalibrate()` discards verify result and re-enters calibration |
| averageSetsPpm | PASS — `verifyAverage()` sets pts_per_m to average of calib + verify measurements |
| finishCalibIntact | PASS — `finishCalib()` body unchanged; `calibPanelOk` routes to it in normal (non-verify) mode |
| roundTripSaveLoad | PASS — `calibScale.verifyResult` survives `_makeProjBlob()` → `applyLoadedProject()` round-trip |

## Key Baselines GREEN

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing 5 env-artifact markers (PHASE_HT8C_OK, PHASE_HT8D1_OK, PHASE_HT10_OK, PHASE_HT12H_OK, PHASE_I_D_OK) remain at same pre-sprint state — confirmed pre-existing (Python 3.14 + newer Chromium sandbox; canonical 3.11 env has them green). Zero regression introduced by this sprint.

---

# Previous: BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode

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

---

<!-- Older results archived to docs/archive/test-history-2026-05-09.md -->
