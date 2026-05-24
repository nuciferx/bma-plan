# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Centerline Snap arc (invent → INV-002a proto → INV-002b lite → 2 post-ship bugfixes)

Branch: main
Date: 2026-05-25

## Result: PASS

Proto full E2E PASS (21/21 + NEW PHASE_CENTERLINE_SNAP_OK 10/10). Lite LITE_CENTERLINE_SNAP_OK 8/8 PASS. MEASURE_PARITY_OK GREEN. All prior baseline markers retained. Commits: `0208314` `6db0461` `ad920c6` `916d379` `ff3f9fe` `5783df4`.

## Commands

```bash
# Proto
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

# Lite
python lite/tests/test_centerline_snap.py
python lite/tests/test_measure_parity.py
```

## Proto — Smoke (18 baseline markers)

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

## Proto — Full (3 additional markers + NEW centerline marker)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| **PHASE_CENTERLINE_SNAP_OK (10/10 sub-checks)** | **PASS — NEW** |

Sub-checks for PHASE_CENTERLINE_SNAP_OK:
- fnsExist, versionExists, toggleExists, stateExists, buttonExists, prefDefault: all PASS
- sanity: PASS (skeleton pixels found on synthetic dashed canvas)
- accuracy: PASS (maxDelta=0.140%, target ≤0.5%)
- subFnsExist: PASS (CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton)
- refineHookInFinish: PASS (finishCurrentArea calls refine for poly branch)

Note: PROJECT_OK + PERSIST_OK confirm `obj.traceMode = "centerline-roi"` additive field round-trips through save/load without breaking existing .bmaplan files.

## Lite — LITE_CENTERLINE_SNAP_OK (8/8 sub-checks)

| Sub-check | Result |
|---|---|
| jsFnsExist | PASS (CL_snapCanvasToCenterline + CL_litePolyClick + CL_litePolyFinish present) |
| toggleBtnInstalled | PASS (floating toggle button self-installs on page load) |
| localStoragePersist | PASS (centerlineSnapOn state persists across page reload) |
| accuracy | PASS (maxDelta=0.1778% ≤0.5% on synthetic dashed pentagon) |
| skeletonFound | PASS (algorithm finds dark pixels on synthetic canvas) |
| refineHookInFinish | PASS (finishDraft calls CL_litePolyFinish for poly branch) |
| dprBridge | PASS (source scan confirms both glue functions reference `dpr` for coord conversion) |
| activeCssRule | PASS (.active CSS rule present: green background + glow when toggle ON) |

## Lite — MEASURE_PARITY_OK

```bash
python lite/tests/test_measure_parity.py  → GREEN
```

16 functions + 2 constants in `lite/static/js/measure-engine.js` are byte-identical to proto.
`centerline-snap.js` Section A is byte-identical to `proto/static/js/centerline-snap.js` per drift-locked vendoring contract.

## TEST-H Rationale (Skipped)

Per AGENTS.md: feature defaults OFF; user must opt-in via "⊙ CL" Helpers ribbon button (proto) or floating toggle (lite). The existing `bma-human-journey-tester` does not toggle Helpers ribbon options. The full E2E with 10/8 sub-check synthetic proof (including accuracy gate, hook wiring, DPR bridge, and active CSS verification) constitutes sufficient verification. TEST-H will be relevant when the feature is promoted to default-ON.

---

# Previous: SIM-2 — /bma-simulate regression-probe hardening (permanent regression probes)

Branch: main
Date: 2026-05-24

## Result: PASS (no-test rationale for proto/lite — zero source changes; probe verifier is the relevant smoke test)

## No-Test Rationale

Per AGENTS.md §1, sprints that make ZERO changes to proto/ or lite/ source record a no-test rationale instead of running proto E2E. This sprint changed only files under `.claude/` (SKILL.md, bma-sim-driver.md, regression_probes.json) and added a sprint card under `sprints/`. The `regression_probes.json` mechanism is a READ-ONLY observer of the running lite app — it does not modify lite or proto code. Therefore proto `py_compile + smoke + full` and lite tests were not re-run (would only re-verify unchanged baseline). The probe verifier below IS the relevant smoke test for this sprint.

## Tests Run

```bash
python -c "import json; json.load(open('.claude/skills/bma-simulate/regression_probes.json', encoding='utf-8'))"
  → PASS (2 probes registered, both schema-valid)

artifacts/sim/lite/regression-probes-verify-20260524T200000/probe_executor.py
  (loads regression_probes.json; runs each probe against current lite build using
   the exact bma-sim-driver recipe: setup_js → trigger → assertion_js → cleanup_js)

  === LITE-BUG-MODAL-NEST ===
    type: evaluate
    result: PASS  (860ms)
    assertion: #setupModal has non-zero rect, parent=#stage, select.offsetParent exists

  === LITE-BUG-DBLCLICK-OVER-POP ===
    type: mouse_sequence (4 clicks + 1 dblclick at last-click position)
    result: PASS  (2919ms)
    assertion: PS[1].objects[0].pts.length === 4

  2 PASS · 0 FAIL
```

Evidence trail:
- Probe JSON: `.claude/skills/bma-simulate/regression_probes.json`
- Verifier results: `artifacts/sim/lite/regression-probes-verify-20260524T200000/verify_result.json`
- Screenshots: `artifacts/sim/lite/regression-probes-verify-20260524T200000/screenshots/probe_*.png`
- Closed bugs protected: commit `2dae5c0` (LITE-BUG-2-OPUS47-FINDINGS)

## Reference Baseline (from previous sprint LITE-BUG-2-OPUS47-FINDINGS 2026-05-24)

```
python -c "open('lite/ui-lite.html', encoding='utf-8').read()"    → parseable PASS
wc -l lite/ui-lite.html                                            → 1197 (≤1200 cap) PASS
<div> vs </div> balance: delta=0 PASS
cd lite && python -m py_compile server_lite.py                     → PASS
cd lite && python tests/test_pan_controls.py                       → BUG_20260521_LITE_PAN_OK PASS

proto baseline (unchanged):
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → PASS (18 baseline markers)
python3.11 proto/e2e_ui_test.py full                           → PASS (21 markers)
```

---

<!-- LITE-BUG-2-OPUS47-FINDINGS and older test results archived to docs/archive/test-history-2026-05-09.md -->
