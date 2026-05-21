# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: LITE-0 — scaffold standalone /lite/ tree (sub-sprint 1 of epic INV-2026-05-21-001)

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
- `.bmaplan` schema version stays 1; additive fields only (count objects deferred to LITE-5 as additive `store.counts`)

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

# Previous: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX

Branch: main

Date: 2026-05-20

## Outcome: PASS — Calibration workflow accuracy fixed; area math proven exact (0.08% error); silent wrong-line snap now surfaced as orange warning; Verify Scale promoted to ribbon; tooltip shows exact pts_per_m. Full E2E EXIT 0, 102 _OK markers. NEW HT_ACC_OK GREEN.

## Summary

/bma-human-test on real Downloads PDFs (SCR_Permit_Layout, raster ข.4) returned JOURNEY_OK. The user then reported measuring a 4,000 m² title-deed lot ~1% smaller than deeded. Investigation confirmed the area math is exact (shoelace formula, precise pts_per_m float, 0.08% geometric error). Root cause: snap silently captured a longer nearby vector line instead of the user's intended reference, driving pts_per_m too high and making all derived areas proportionally smaller. HT-ACC-1 surfaces this failure mode with an orange warning the moment it occurs. HT-ACC-2 promotes the Verify Scale button and adds calibration UX nudges. HT-ACC-3 adds an exact pts_per_m tooltip to the scale status fields (no measurement change). HT-NAV-1 required no code fix.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | `calibRaw[]` captures pre-snap click coords; snap-deviation >5% triggers orange warning in calib panel; `#btn-scale-verify` ribbon button added beside Set Scale; longest-baseline tip in calib panel; `finishCalib` nudges to Verify; `activateAreaTool('land')` hints to use arc edges |
| `proto/static/js/status-bar.js` | `updateAnalyseUI` sets tooltip on `#lbl-scale` and `#scale-badge` showing exact `pts_per_m` and precise `1:N.x` (visible label stays rounded; area float unchanged) |
| `proto/e2e_ui_test.py` | `_test_ht_acc_calibration` (5 sub-checks) + `HT_ACC_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (area math proven exact; this series fixes calibration UX, not the formula)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` internals — UNCHANGED (`calibRaw` captures raw clicks before snap; snap logic not modified)
- `.bmaplan` schema version stays 1; `calibRaw` is in-memory only, not persisted

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py            → PASS
proto/e2e_ui_test.py full                                   → EXIT 0
  102 _OK markers, 0 E2E_FAIL
  NEW: HT_ACC_OK GREEN (5 sub-checks:
       verifyBtnExists, verifyBtnWired, longestTip,
       calibRawExists, devWarnsWrongLine, devQuietWhenClose)
  CACHE_OK, MAIN_UI_OK (cssLinkPresent/statusBarJsLoaded true) confirm assets serve
  Static-asset safety: NO_BOM on app.css + status-bar.js
  All prior 101 markers retained. Zero regression.
  UI_REGRESSION_PASS. Forbidden-surface diff scan CLEAN.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibRaw` in-memory only; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- BUG-20260520-zen-exit-rp-restore and earlier entries archived to docs/archive/patch-history-2026-05-09.md -->
