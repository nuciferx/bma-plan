# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; 100 _OK markers, 0 E2E_FAIL; NEW INV_LAYER_L1/L2/L3_OK GREEN; HT8D5A restored; zero regression.

## Commands

```bash
py_compile proto/server.py proto/e2e_ui_test.py  # PASS
proto/e2e_ui_test.py full                         # EXIT 0 — 100 _OK markers
```

## New Markers

| Marker | Result | Description |
|---|---|---|
| **INV_LAYER_L1_OK** | PASS | Slug guarantee (`validLayerSlugForPage`) + render/hit/label paths read page-scoped layer via `_slugVisible`/`_slugLocked`/`_objLayerVisible`/`_objLayerLocked`; global `areaTypeLayer` no longer used for behaviour |
| **INV_LAYER_L2_OK** | PASS | `reassignSelectedObjectLayer()` present; Layer `<select>` dropdown in properties panels; `objLayerKey()` reports real slug |
| **INV_LAYER_L3_OK** | PASS | Page locked + global unlocked → app follows page-scoped lock (authority proven); `_layerLockGateBeforeMode` + `toggleLayerLock` repointed to `_slugLocked`/`getObjectLayerSlug` |

## HT8D5A Lock Test

| Test | Before sprint | After sprint |
|---|---|---|
| HT8D5A | all:False (repointed to page layers — test needed update) | **all:True RESTORED** |

## Key Baselines GREEN (100 total _OK markers)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| INV_VERIFY_SCALE_OK | PASS (9/9) |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing cosmetic all:False markers (HT8C_OK, HT8D1_OK, HT10_OK, HT12H_OK, PHASE_I_D_OK — left-panel/layout/compass, unrelated to layers) unchanged. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

---

# Previous: INV-2026-05-20-001 — Verify Scale tool

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
| domAndHelpers | PASS — `#verify-modal`, `verifyScale`, `verifyFinish`, `verifyAccept`, `verifyRecalibrate`, `verifyAverage`, `_verifyBand`, `calibPanelOk` all present |
| guardWhenNoScale | PASS — `verifyScale()` returns early (no modal) when no calibration exists |
| greenBandZeroDev | PASS — %dev=0 produces green band, Accept enabled |
| acceptWritesResult | PASS — `verifyAccept()` writes `calibScale.verifyResult{pct, action:"accept", verifyPts_per_m, ts}` |
| redBandHighDev | PASS — high %dev (≥2%) produces red band |
| recalibrateSetsPpm | PASS — `verifyRecalibrate()` discards verify result and re-enters calibration |
| averageSetsPpm | PASS — `verifyAverage()` sets pts_per_m to average of calib + verify |
| finishCalibIntact | PASS — `finishCalib()` body unchanged; `calibPanelOk` routes to it in normal mode |
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

Pre-existing 5 env-artifact markers (PHASE_HT8C_OK, PHASE_HT8D1_OK, PHASE_HT10_OK, PHASE_HT12H_OK, PHASE_I_D_OK) remain at same pre-sprint state. Zero regression.

---

<!-- Older results archived to docs/archive/test-history-2026-05-09.md -->
