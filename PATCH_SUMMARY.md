# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite

Branch: main

Date: 2026-05-21

## Outcome: PASS — Spacebar/middle-mouse pan in any mode + H pan-tool + smooth clamped zoom + fit/actual-size/zoom shortcuts forked from proto into lite. BUG_20260521_LITE_PAN_OK GREEN (13/13). ZERO proto/ edits. MEASURE_PARITY_OK unchanged.

## Summary

Lite's view/navigation controls were impoverished vs proto: pan only worked in select/empty mode (draw tools blocked mousedown early), no spacebar or middle-mouse pan, no zoom clamp (runaway zoom), no fit/actual-size/zoom keyboard shortcuts. This sprint adapted proto's entire view-control BEHAVIOR onto lite's `V={k,ox,oy,rot}` single-canvas model (proto uses CSS-transform + per-page server rotation, so functions could not be copied verbatim). New Playwright regression guard `test_pan_controls.py` validates all 13 control paths. MEASURE_PARITY_OK confirms ptToScreen/screenToPt/RS untouched.

## Files Changed

| File | Change |
|---|---|
| `lite/ui-lite.html` | mousedown/mousemove/mouseup/wheel/keydown/keyup handlers + setTool; new zoomCenter/actualSize/setCursor helpers; hint text; state.panTool default (~39 insertions / 12 deletions) |
| `lite/tests/test_pan_controls.py` | NEW — Playwright regression guard (13 checks: midPan, spaceArmed, spacePanMidDraw, panToolOn/Drag/Off, selectPan, clampMax, clampMin, wheelZoomIn, actualSize, fit, ctrlZoomIn) |
| `docs/status/PHASE_INDEX.md` | bug filed at top of Active queue then marked done |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (lite vendors in measure-engine.js — untouched)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED (lite ptToScreen/screenToPt/RS untouched)
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only (not touched)

## Tests Run

```
py -3 -m py_compile lite/server_lite.py lite/tests/test_pan_controls.py lite/tests/test_menu_clickable.py
  -> PYCOMPILE_OK
lite/tests/test_pan_controls.py  -> BUG_20260521_LITE_PAN_OK GREEN (13/13 checks)
lite/tests/test_menu_clickable.py  -> BUG_20260521_LITE_MENU_CLIP_OK GREEN (no regression)
lite/tests/test_measure_parity.py  -> MEASURE_PARITY_OK GREEN (ptToScreen/screenToPt/RS untouched)

No-test rationale for proto full E2E: zero edits to any file under proto/; lite tree is isolated.
Reference baseline: proto full E2E = 102 _OK markers (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (lite vendors them in measure-engine.js — untouched)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED (lite ptToScreen/screenToPt/RS untouched)
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only; version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: LITE-0 — scaffold standalone /lite/ tree (sub-sprint 1 of epic INV-2026-05-21-001)

Branch: main

Date: 2026-05-21

## Outcome: PASS — /lite/ sibling tree scaffolded; measurement engine vendored byte-identical from proto/ui.html + anti-drift parity gate; proto/ untouched; MEASURE_PARITY_OK; py_compile PASS both trees; Playwright self-test 0 errors.

## Summary

LITE-0 scaffolds a standalone `/lite/` sibling tree (own FastAPI server, launcher, and UI shell) as the foundation of BMA-Plan Lite (Approach A: vendored-copy + contract-test). The measurement engine is vendored verbatim from `proto/ui.html` — `RS`, `pdfToC`, `cToPdf`, `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pathAreaM2`, and 6 path helpers — with a new lite-only `objectAreaM2Lite` wrapper. An anti-drift parity gate verifies both source byte-identity (10 fns + 2 consts) and numeric parity on 5 polys, 2 paths, and 4 coordinate pairs. Zero edits to any file under `proto/`.

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/measure-engine.js` | NEW — vendored verbatim measure engine + lite-only `objectAreaM2Lite` |
| `lite/tests/test_measure_parity.py` | NEW — anti-drift gate: byte-identity + numeric parity via Node |
| `lite/tests/fixtures/measure_parity_v1.json` | NEW — 5 polys / 2 paths / 4 coords test vectors |
| `lite/server_lite.py` | NEW — skeleton FastAPI (static mount + /health + /); endpoints deferred to LITE-1 |
| `lite/launch_lite.py` | NEW — free-port (8100+) launcher |
| `lite/ui-lite.html` | NEW — LITE-0 shell: host globals + engine load + self-test (unit square = 25.00 m2) |
| `lite/README.md` | NEW — vendoring contract + version-sync policy |
| `docs/invent/bma-plan-lite-standalone.md` | NEW — invent research + approach decision record |
| `proto/sandbox/invent-bma-plan-lite-standalone.html` | NEW — invention spike |
| `docs/status/PHASE_INDEX.md` | MODIFIED — sprint card LITE-0 added + status flipped to done |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (LITE-0 has its own `lite/server_lite.py`)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED in proto (vendored copy byte-identical, enforced by parity gate)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED in proto
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
python lite/tests/test_measure_parity.py
  -> MEASURE_PARITY_OK (10 fns + 2 consts byte-identical; 5 polys/2 paths/4 coords numeric parity; unit square = 25.00 m2 verified)
python3.11 -m py_compile lite/server_lite.py lite/launch_lite.py  -> PASS
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py     -> PASS (proto regression guard)
Playwright render lite/ui-lite.html -> self-test "engine wired", 0 console errors

No-test rationale for proto full E2E: LITE-0 is purely additive in /lite/ tree; ZERO proto/ changes.
Reference baseline: proto full E2E = 21 markers / 102 _OK (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (vendored copy byte-identical, enforced by parity gate)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only; version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- HT-ACC series and earlier entries archived to docs/archive/patch-history-2026-05-09.md -->
