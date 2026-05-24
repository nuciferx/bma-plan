# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Centerline Snap arc (invent 2026-05-24-22-14 → INV-002a proto → INV-002b lite → 2 post-ship bugfixes)

Branch: main

Date: 2026-05-25

## Outcome: PASS — Centerline snap shipped to proto (INV-002a, commit 6db0461) + lite (INV-002b, commit ad920c6); 2 user-reported lite bugs fixed same day (DPR coord mismatch ff3f9fe; button overlap 5783df4). PHASE_CENTERLINE_SNAP_OK 10/10 (maxDelta=0.140%), LITE_CENTERLINE_SNAP_OK 8/8 (maxDelta=0.1778%). All prior baseline markers GREEN. Zero server changes.

## Summary

User reported "วัดที่ดินเส้นปะได้ 3 ค่าต่างกัน" (SCR_ผังต่อโฉนด.pdf, thick dashed cadastral boundary). Correct measurement = stroke centerline. `/bma-invent` 7-phase pipeline (commit `0208314`) selected Approach A: click-time local-ROI Zhang-Suen thinning + post-draw PCA corner refinement. Spike pass 3 achieved maxDelta=0.185% PASS 4/4; user GO + requested lite vendor. INV-002a (proto): NEW `proto/static/js/centerline-snap.js` 208 LOC (Otsu + Zhang-Suen + ROI snap + PCA refine); `proto/ui.html` +15 lines net; E2E +162 lines; PHASE_CENTERLINE_SNAP_OK 10/10. INV-002b (lite): NEW `lite/static/js/centerline-snap.js` 306 LOC (Section A byte-identical to proto per drift-locked vendoring contract, Section B lite glue); `lite/ui-lite.html` +2 net lines (1197→1199 ≤ 1200 cap); LITE_CENTERLINE_SNAP_OK 8/8. Two user-reported bugs fixed same day: DPR coord mismatch (Windows 125/150% scaling → ROI read wrong canvas region → zero effect; fix: multiply CSS coords by dpr before algorithm, divide back after; also added missing `.active` CSS to make toggle visually distinguishable) and CL button overlapping zoom controls (moved from fixed position into `#hud-br` flex-column). Additive schema field: `obj.traceMode = "centerline-roi"` on corrected polygons (optional; legacy .bmaplan loads fine).

## Files Changed

| File | Change |
|---|---|
| `docs/invent/centerline-snap-dashed-boundary.md` | NEW — full 7-phase invent record (PICK→RESEARCH→FRAME→DIVERGE→SCORE→SPIKE→CHECKPOINT) |
| `proto/sandbox/invent-centerline-snap-dashed-boundary.html` | NEW — interactive spike, commit `0208314` |
| `proto/static/js/centerline-snap.js` | NEW 208 LOC — Otsu threshold + Zhang-Suen thinning + CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton (IIFE, no CDN) |
| `proto/ui.html` | +15 lines net — script include, "⊙ CL" Helpers ribbon button, toggleCenterlineSnap() + state, area mousedown click-hook, finishCurrentArea refine call, PREFS.measure.centerlineSnap false, _applyCenterlineSnapPref() |
| `proto/e2e_ui_test.py` | +162 lines — _test_centerline_snap 10 sub-checks + PHASE_CENTERLINE_SNAP_OK |
| `lite/static/js/centerline-snap.js` | NEW 306 LOC — Section A: proto algo byte-identical (drift-locked); Section B: lite glue (CL_litePolyClick + CL_litePolyFinish + floating toggle + localStorage) |
| `lite/ui-lite.html` | +2 net lines (1197→1199, ≤1200 cap) — script include + poly click hook + finishDraft hook; DPR bugfix: dpr multiply/divide + inline .active CSS; button position bugfix: insertBefore #hud-br firstChild |
| `lite/tests/test_centerline_snap.py` | NEW 235 LOC — LITE_CENTERLINE_SNAP_OK Playwright; 6 sub-checks in 002b, expanded to 8 post-bugfix (dprBridge + activeCssRule) |
| `docs/status/PHASE_INDEX.md` | 002a + 002b sprint rows added, backlog flipped, commit hashes backfilled (commit `916d379`) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (zero server changes across entire arc; purely client-side feature)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (centerline snap is pre-processing, injects corrected pts before area math reads them; uses `getImageData` public API only)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED (centerline snap fires only AFTER vector snap found no match)
- `.bmaplan` schema version stays 1; NEW additive `obj.traceMode` optional field only (absent = legacy behavior)
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → 18/18 PASS
python proto/e2e_ui_test.py full                           → 21/21 PASS
  NEW: PHASE_CENTERLINE_SNAP_OK 10/10 (accuracy maxDelta=0.140%, target ≤0.5%)
  PROJECT_OK + PERSIST_OK confirm obj.traceMode additive field round-trips through save/load

python lite/tests/test_centerline_snap.py  → LITE_CENTERLINE_SNAP_OK 8/8 PASS
  accuracy maxDelta=0.1778% ≤0.5%; dprBridge + activeCssRule regression locks added post-bugfix
python lite/tests/test_measure_parity.py   → MEASURE_PARITY_OK GREEN (no regression)
wc -l lite/ui-lite.html                    → 1199 (≤1200 cap) PASS

TEST-H skipped per AGENTS.md rationale: feature defaults OFF, user must opt-in via Helpers ribbon;
existing journey tester does not toggle Helpers ribbon options; full E2E + 10/8-sub-check synthetic
proof = sufficient verification.

Commit trail: 0208314 (invent spike GO) → 6db0461 (INV-002a proto)
            → ad920c6 (INV-002b lite) → 916d379 (roadmap chore)
            → ff3f9fe (DPR bugfix) → 5783df4 (button position bugfix)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`obj.traceMode` optional; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (centerline-of-stroke is geometry/snap, in-scope Phase 1)
- ✅ Lite-vendoring contract honored — `measure-engine.js` UNCHANGED; `centerline-snap.js` Section A byte-identical to proto
- ✅ Lite size cap — `ui-lite.html` 1199/1200 (1-line headroom); all `lite/static/js/*.js` ≤1000

---

# Previous: SIM-2 — /bma-simulate regression-probe hardening (permanent regression probes)

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
  → LITE-BUG-MODAL-NEST:        PASS (860ms)
  → LITE-BUG-DBLCLICK-OVER-POP: PASS (2919ms)
  → 2 PASS · 0 FAIL

No proto/lite source changes → proto py_compile + E2E not re-run.
Reference baseline: proto full E2E = 21 markers (HT-ACC 2026-05-20, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; probes read in-memory PS only)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Size cap honored (no lite/ runtime files touched)

---

<!-- LITE-BUG-2-OPUS47-FINDINGS and older entries archived to docs/archive/patch-history-2026-05-09.md -->
