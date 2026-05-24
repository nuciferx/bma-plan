# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: SIM-2 — /bma-simulate regression-probe hardening (permanent regression probes)

Branch: main

Date: 2026-05-24

## Outcome: PASS — /bma-simulate gains a permanent hard-probe channel: regression_probes.json (tracked, curated per sprint) holds mandatory steps prepended to every SCENARIO_PLAN. Two probes registered (LITE-BUG-MODAL-NEST + LITE-BUG-DBLCLICK-OVER-POP) and verified PASS against current build. False assertion = REGRESSION severity (above CRASH). Zero runtime changes to lite/ or proto/.

## Summary

Added a permanent regression-probe mechanism to Pack J `/bma-simulate`. Two memory channels now coexist: the existing soft channel (`artifacts/sim/lite/history.jsonl`, rolling, gitignored, few-shot context) and a new hard channel (`.claude/skills/bma-simulate/regression_probes.json`, tracked, permanent). Phase A reads the hard channel and prepends one `regression_probe` step per entry to the SCENARIO_PLAN right after `open_pdf`. `bma-sim-driver` supports the new step type with setup_js → trigger → assertion_js → cleanup_js recipe. A false assertion returns REGRESSION severity — a new tier above CRASH — and triggers the new `SIM_REGRESSION` stop condition. Two initial probes verify PASS against the current build: LITE-BUG-MODAL-NEST (evaluate-type, 860 ms) and LITE-BUG-DBLCLICK-OVER-POP (mouse_sequence-type, 2919 ms).

## Files Changed

| File | Change |
|---|---|
| `.claude/skills/bma-simulate/regression_probes.json` | NEW — 2 active probes + `_schema` docs block (~50 lines) |
| `.claude/skills/bma-simulate/SKILL.md` | Phase A reads probes; prepends probe steps to SCENARIO_PLAN; REGRESSION severity added (highest); SIM_REGRESSION + SIM_PROBES_MALFORMED stop conditions; soft/hard memory table (~+30 lines) |
| `.claude/agents/bma-sim-driver.md` | `regression_probe` step type added to step types table; "How to execute regression_probe" sub-section (~+45 lines) |
| `sprints/active/SIM-2-REGRESSION-PROBES-2026-05-24.md` | NEW sprint card (to be moved to `sprints/completed/2026-05-24-sim-2-regression-probes/`) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; untouched (probes read PS in-memory, ephemeral)
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `lite/ui-lite.html` — NOT TOUCHED (zero lite/ runtime edits)

## Tests Run

```
python -c "import json; json.load(open('.claude/skills/bma-simulate/regression_probes.json', encoding='utf-8'))"
  → PASS (2 probes registered, both schema-valid)

artifacts/sim/lite/regression-probes-verify-20260524T200000/probe_executor.py
  → LITE-BUG-MODAL-NEST:       PASS (860ms)
  → LITE-BUG-DBLCLICK-OVER-POP: PASS (2919ms)
  → 2 PASS · 0 FAIL

No proto/lite source changes → proto py_compile + E2E not re-run.
Reference baseline: proto full E2E = 102 _OK markers (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; probes read in-memory PS only)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Size cap honored (no lite/ runtime files touched)

---

# Previous: LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop)

Branch: main

Date: 2026-05-24

## Outcome: PASS — Fixed LITE-BUG-MODAL-NEST (BROKEN: #setupModal nested inside hidden #modal, invisible regardless of openSetup()) and LITE-BUG-DBLCLICK-OVER-POP (FRICTION: unbounded while loop ate intentional vertices, saved polygon as triangle). Both surfaced by Opus-4.7 multi-model simulator (Pack J). Zero net lines. lite/ui-lite.html stays at 1197 ≤ 1200. All live Playwright verify checks PASS.

## Summary

Two silent bugs in `lite/ui-lite.html` fixed — both found by the multi-model simulator (Pack J `/bma-simulate`) running the full Page Setup + polygon-draw workflow on `lite/test.pdf`. LITE-BUG-MODAL-NEST: a missing `</div>` caused `#setupModal` to be nested inside the hidden `#modal` container, making Page Setup invisible on click. LITE-BUG-DBLCLICK-OVER-POP: an unbounded `while` loop in the dblclick handler consumed legitimate polygon vertices (4 pts saved as 3 pts, 713 m² reported as 356 m²). Both patches are surgical zero-net-line changes. Live Playwright verify confirms all 3 PASS assertions (modal rect nonzero, calib modal regression-clean, dblclick preserves vertex count at 714.07 m²).

## Files Changed

| File | Change |
|---|---|
| `lite/ui-lite.html` | Added missing `</div>` after line 194 (closes `#modal` before `#setupModal`); replaced unbounded `while` with bounded `for(_np<2)` at lines 502-503; 0 net lines; 1197 total (cap 1200) |
| `sprints/completed/2026-05-24-lite-bug-2-opus47-findings/LITE-BUG-2-OPUS47-FINDINGS-2026-05-24.md` | NEW — sprint card with bug IDs, root causes, patches, self-check |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero proto/ edits — lite-only sprint)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; untouched
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED

## Tests Run

```
python -c "open('lite/ui-lite.html', encoding='utf-8').read()"    → parseable PASS
wc -l lite/ui-lite.html                                            → 1197 (≤1200 cap) PASS
<div> vs </div> regex balance: opens=92 closes=92 delta=0          PASS (was delta=1)
cd lite && python -m py_compile server_lite.py                     → PASS
cd lite && python tests/test_pan_controls.py                       → BUG_20260521_LITE_PAN_OK PASS

Live Playwright verify (artifacts/sim/lite/test-pdf-opus47-direct-20260524T194000/verify_bug_fixes.py):
  BUG_A_modal_rect_nonzero:        PASS — #setupModal 1600×958, parent=#stage
  BUG_A_calib_modal_still_works:   PASS — no regression, 1600×958
  BUG_B_dblclick_preserves_vertex: PASS — 4 pts saved, area=714.07 m² (drift 0.13% acceptable)

No-test rationale for proto E2E: lite-only sprint; zero proto/ edits.
Reference baseline: proto full E2E = 102 _OK markers (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED (measure-engine.js untouched)
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Size cap honored — lite/ui-lite.html 1197 ≤ 1200

---

# Previous (older): LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite

Branch: main

Date: 2026-05-22

## Outcome: PASS — Lite gains an editable web report (plan-left / area-table-right, A4 landscape) opened in a new window via sessionStorage handoff, edited Word-style, printed to PDF. Area numbers read-only. LITE_REPORT_OK GREEN (17/17). ZERO proto/ edits. MEASURE_PARITY_OK unchanged.

## Summary

Added `lite/lite-report.html` — a standalone A4-landscape web page that opens in a new window from the File menu "ส่งออกรายงาน (แก้ไขได้)…". The report shows one sheet per measured page: left = plan image with SVG polygon overlay + numbered badges; right = area table grouped by semanticTag with per-group subtotals + page net (deductions sign −1) + header. Header fields, row labels, and notes are `contenteditable`; area cells are read-only (raw-geometry contract). `@page` + `@media print` CSS enables WYSIWYG browser-print-to-PDF. Payload passed via `sessionStorage["bmaReportPayload"]` — images reference `/page/{n}` URLs so only geometry+metadata are serialised (well under 5 MB). A sample standalone fallback renders when opened without a payload.

## Files Changed

| File | Change |
|---|---|
| `lite/lite-report.html` | NEW — standalone editable report page (A4 landscape, plan+SVG overlay, area table, contenteditable, @page print CSS, sample fallback) |
| `lite/server_lite.py` | +9 lines — `_REPORT_FILE` const + `GET /report` FileResponse route (additive) |
| `lite/ui-lite.html` | +52 lines — File-menu item #mi-report + `reportPageTitle()` / `buildReportPayload()` / `openReport()` (reads polyMetrics/PS/catOf READ-ONLY; handoff via sessionStorage + window.open) |
| `lite/tests/test_report.py` | NEW — LITE_REPORT_OK Playwright guard (17 checks) |
| `docs/status/PHASE_INDEX.md` | LITE-REPORT marked done |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (read-only consumer; MEASURE_PARITY_OK)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED (measure-engine.js untouched)
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no schema touch at all (report reads in-memory PS, ephemeral edits)

## Tests Run

```
py_compile lite/server_lite.py lite/launch_lite.py         → PY_COMPILE_OK
lite/tests/test_report.py                                  → LITE_REPORT_OK GREEN (17/17)
lite/tests/test_measure_parity.py                          → MEASURE_PARITY_OK GREEN (16 fns + 2 consts)
lite/tests/test_menu_clickable.py                          → BUG_20260521_LITE_MENU_CLIP_OK GREEN
lite/tests/test_pan_controls.py                            → BUG_20260521_LITE_PAN_OK GREEN
artifacts/realflow_check.py                                → REALFLOW_OK (real PDF → popup → naturalWidth 3576 → polygon overlay → net 222.22)

No-test rationale for proto E2E: lite-only tree; zero proto/ edits.
Reference baseline: proto full E2E = 102 _OK markers (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (read-only consumer)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED (measure-engine.js untouched; MEASURE_PARITY_OK)
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (no schema touch)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (area facts only)

---

# Previous (older): BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite

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

# Previous (older): LITE-0 — scaffold standalone /lite/ tree (sub-sprint 1 of epic INV-2026-05-21-001)

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
