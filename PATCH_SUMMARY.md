# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3

Branch: main

Date: 2026-05-20

## Outcome: PASS — Page-scoped layer is now the single authoritative source for render/hit/visibility/lock. Site-plan overlap bug fixed. Full E2E EXIT 0, 100 _OK markers. NEW INV_LAYER_L1/L2/L3_OK GREEN.

## Summary

Three-commit layer-model rebuild resolving a user-reported bug where objects on ผังบริเวณ (site plan) pages landed in the wrong layer and overlapped with no way to separate or toggle them. Root cause: two competing layer systems coexisted — page-scoped `pageStore[n].layers` (authoritative by design) vs. legacy global `areaTypeLayer`/`layerVis`/`layerLock` (still read by render/hit paths). Site objects with `areaType="room"` collapsed to slug `"sub_area"` which does not exist in the site preset, producing `layerId = undefined`. L1 establishes slug-guarantee + new render/hit helpers. L2 adds Bluebeam-style reassign-layer UI. L3 demotes global maps to a non-authoritative synced mirror — page-scoped authority proved by E2E (page locked + global unlocked → app follows page).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | Layer helpers (`validLayerSlugForPage`, `getObjectLayerSlug`, `_slugVisible`, `_slugLocked`, `_objLayerVisible`, `_objLayerLocked`); slug assignment at object creation; render/hit/label/lock-gate paths updated (L1); `reassignSelectedObjectLayer` + Layer `<select>` in properties panels (L2); global `layerVis`/`layerLock` demoted to mirror role (L3) |
| `proto/e2e_ui_test.py` | +3 test functions (`_test_inv_layer_l1/l2/l3`) + 3 markers + HT8D5A repointed |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `layerSlug`/`layerId` fields already existed; additive only

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py  → PASS
proto/e2e_ui_test.py full                         → EXIT 0
  100 _OK markers, 0 E2E_FAIL
  NEW: INV_LAYER_L1_OK GREEN
  NEW: INV_LAYER_L2_OK GREEN
  NEW: INV_LAYER_L3_OK GREEN (page locked + global unlocked → app follows page)
  HT8D5A all:True restored
  Pre-existing cosmetic all:False markers (HT8C/HT8D1/HT10/HT12H/PHASE_I_D) — unchanged
  Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`layerSlug`/`layerId` already existed; no renames; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: INV-2026-05-20-001 — Verify Scale tool

Branch: main

Date: 2026-05-20

## Outcome: PASS — Verify Scale tool implemented (approach A). verifyFinish() %dev band + Accept/Re-calibrate/Average modal. Full E2E GREEN. NEW INV_VERIFY_SCALE_OK 9/9.

## Summary

Replaced the `verifyScale()` stub with a real second-reference cross-check flow: Scale-menu "Verify Scale" reuses the existing 2-point calibration draw, then `verifyFinish()` computes `%dev = 100·|d_meas−d_enter|/d_enter` and shows a color-coded confidence band (green <0.5% / yellow <2% / red ≥2%) plus measured distance, entered distance, area-impact estimate (≈2×%dev), and three action buttons: Accept / Re-calibrate / Average. A `calibPanelOk()` router was added so the calib panel OK button routes to `verifyFinish()` in verify mode and to `finishCalib()` otherwise — `finishCalib()` itself is unchanged. Schema is additive: `calibScale.verifyResult{pct, action, verifyPts_per_m, ts}` round-trips through existing save/load automatically.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +82/−5 — calib panel h3 id + OK→`calibPanelOk`; `#verify-modal` HTML; 10 new fns (`verifyScale`, `verifyFinish`, `openVerifyModal`, `_verifyBand`, `_verifyWriteResult`, `_afterVerifyScaleChange`, `verifyAccept`, `verifyRecalibrate`, `verifyAverage`, `closeVerifyModal`); `cancelCalib` reset; `anyModal` guard extended |
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
  ANNOT_OK / PERSIST_OK / REAL_OK / PROJECT_OK / XLSX_OK / PATH_GEOMETRY_OK — GREEN
  Pre-existing 5 env-artifact markers unchanged. Zero regression.
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

<!-- Older entries archived to docs/archive/patch-history-2026-05-09.md -->
