# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-20-001 — Verify Scale tool

Branch: main

Date: 2026-05-20

## Outcome: PASS — Verify Scale tool implemented (approach A). verifyFinish() %dev band + Accept/Re-calibrate/Average modal. Full E2E GREEN. NEW INV_VERIFY_SCALE_OK 9/9.

## Summary

Replaced the `verifyScale()` stub with a real second-reference cross-check flow: Scale-menu "Verify Scale" reuses the existing 2-point calibration draw, then `verifyFinish()` computes `%dev = 100·|d_meas−d_enter|/d_enter` and shows a color-coded confidence band (green <0.5% / yellow <2% / red ≥2%) plus measured distance, entered distance, area-impact estimate (≈2×%dev), and three action buttons: Accept / Re-calibrate / Average. A `calibPanelOk()` router was added so the calib panel OK button routes to `verifyFinish()` in verify mode and to `finishCalib()` otherwise — `finishCalib()` itself is unchanged. Schema is additive: `calibScale.verifyResult{pct, action, verifyPts_per_m, ts}` round-trips through existing save/load automatically.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +82/−5 — calib panel h3 id + OK→`calibPanelOk`; `#verify-modal` HTML; 10 new fns (`verifyScale`, `verifyFinish`, `openVerifyModal`, `_verifyBand`, `_verifyWriteResult`, `_afterVerifyScaleChange`, `verifyAccept`, `verifyRecalibrate`, `verifyAverage`, `closeVerifyModal`); `cancelCalib` reset; `anyModal` guard |
| `proto/e2e_ui_test.py` | +124 lines — `_test_verify_scale` (9 sub-checks) + `INV_VERIFY_SCALE_OK` marker wired into `main()` |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `finishCalib()` — UNCHANGED (`calibPanelOk` wrapper routes to it)
- `.bmaplan` schema version stays 1; `calibScale.verifyResult` is additive optional field

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py            → PASS
proto/e2e_ui_test.py full                                   → EXIT 0 — ALL GREEN
  NEW: INV_VERIFY_SCALE_OK 9/9 all:True
    (domAndHelpers, guardWhenNoScale, greenBandZeroDev, acceptWritesResult,
     redBandHighDev, recalibrateSetsPpm, averageSetsPpm, finishCalibIntact,
     roundTripSaveLoad)
  ANNOT_OK / PERSIST_OK / REAL_OK / PROJECT_OK / XLSX_OK / PATH_GEOMETRY_OK — GREEN
  Pre-existing 5 env-artifact markers unchanged (PHASE_HT8C, HT8D1, HT10, HT12H, I_D).
  Zero regression introduced by this sprint.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `finishCalib()` — UNCHANGED
- ✅ `.bmaplan` schema — additive only (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode

Branch: main

Date: 2026-05-20

## Outcome: PASS — Select-mode middle-mouse-button and Space pan now work. Full E2E GREEN. New marker BUG_20260520_SEL_MIDPAN_OK. Total markers: 22.

## Summary

The `ws` mousedown handler's `mode==="sel"` branch had an unconditional `redraw();return` that fired before the pan-intent check, silently discarding middle-mouse (button===1) and Space pan while the Select tool was active. Fixed by inserting a one-line guard at the top of the `sel` branch that mirrors the identical pan guard already in the non-`sel` path. A new E2E test `_test_bug_sel_midpan` verifies that a Playwright middle-button drag moves the canvas transform by the expected delta while keeping `mode==='sel'` throughout. All 21 prior baseline markers remain GREEN.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +1 line — pan guard at top of `mode==="sel"` mousedown branch (~L2064): `if(e.button===1\|\|spaceDown){isPan=true;...return;}` |
| `proto/e2e_ui_test.py` | +34 lines — `_test_bug_sel_midpan` + call wiring + `BUG_20260520_SEL_MIDPAN_OK` marker |
| `docs/status/PHASE_INDEX.md` | +1 row — BUG-20260520-sel-midpan filed and marked done |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py full                           → EXIT 0 — ALL GREEN
  NEW: BUG_20260520_SEL_MIDPAN_OK GREEN (canvas #cc transform +70x/+45y; mode stayed 'sel')
  21 baseline markers intact incl. PATH_GEOMETRY_OK, ANNOT_OK, PERSIST_OK, REAL_OK
  Total markers: 22
/bma-measure-ux → MEASURE_UX_PASS
/bma-measure-regression → MEASURE_REGRESSION_PASS
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- Older entries archived to docs/archive/patch-history-2026-05-09.md -->
