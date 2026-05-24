# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: Centerline Snap arc (invent → INV-002a proto → INV-002b lite → 2 post-ship bugfixes) — PASS

**Date:** 2026-05-25
**Branch:** main
**Commits:** `0208314` (invent spike GO) · `6db0461` (INV-002a proto) · `ad920c6` (INV-002b lite) · `916d379` (roadmap chore) · `ff3f9fe` (DPR bugfix) · `5783df4` (button position bugfix)

## Outcome

PASS. Centerline snap is now available in both proto and lite as an opt-in feature. Users who trace the outer, inner, or centerline of a thick dashed cadastral boundary will now all get the same m² result when "⊙ CL" is toggled ON. The full invent pipeline (7 phases, commit `0208314`) ran from user problem report to SPIKE PASS 4/4 in one day. Two user-reported post-ship bugs in lite (silent no-op on HiDPI displays and CL button overlapping zoom controls) were filed and fixed within hours of the lite ship. PHASE_CENTERLINE_SNAP_OK 10/10 (accuracy maxDelta=0.140%). LITE_CENTERLINE_SNAP_OK 8/8 (accuracy maxDelta=0.1778%). All 21 prior proto markers GREEN. Zero server changes across the entire arc.

## What was delivered

- **`docs/invent/centerline-snap-dashed-boundary.md`** — full 7-phase invent record: research verdict PRIOR_ART_PARTIAL (Zhang-Suen 1984 exists; no incumbent exposes it as user choice); 5 approaches scored; Approach A 27/30 wins; 3 spike passes; CHECKPOINT: user GO + "ทำลง lite ด้วย"
- **`proto/static/js/centerline-snap.js`** (208 LOC, commit `6db0461`) — Otsu adaptive threshold + Zhang-Suen thinning + CL_snapCanvasToCenterline (click-time, ~4ms) + CL_refineCornersOnSkeleton (post-draw PCA, ~6ms); no CDN dependency; IIFE
- **`proto/ui.html`** (+15 lines net, commit `6db0461`) — "⊙ CL" Helpers ribbon button; feature defaults OFF; click-hook fires only when no vector snap matched; `obj.traceMode = "centerline-roi"` additive schema field
- **`proto/e2e_ui_test.py`** (+162 lines, commit `6db0461`) — PHASE_CENTERLINE_SNAP_OK 10/10 sub-checks including accuracy gate (maxDelta=0.140% ≤ 0.5%)
- **`lite/static/js/centerline-snap.js`** (306 LOC, commit `ad920c6`) — Section A byte-identical to proto (drift-locked vendoring contract); Section B lite glue with toggle button + localStorage persistence
- **`lite/ui-lite.html`** (+2 net lines, 1197→1199, commit `ad920c6` + `ff3f9fe` + `5783df4`) — DPR coord bridge (multiply/divide by devicePixelRatio) + inline `.active` CSS (green glow when ON) + CL button repositioned inside `#hud-br` flex-column (no overlap with zoom controls)
- **`lite/tests/test_centerline_snap.py`** (235 LOC, 8/8 sub-checks) — LITE_CENTERLINE_SNAP_OK with accuracy gate + dprBridge + activeCssRule regression locks

## What's next

The invent pipeline for centerline snap is fully closed. Four follow-on candidates — user decides priority (none auto-promoted):

- **(1) Real-user verification** — ask user to re-measure SCR_ผังต่อโฉนด.pdf with CL ON on both proto + lite; confirm 3 traces (outer/inner/center) converge to same m². Low-risk, high-confidence closure.
- **(2) Vector PDF route (Approach E from diverge)** — extract stroke-width from `extract_snaps_typed()` server response, surface as additive field, client offset by w/2 when `snap.t==='nl'`. Separate sprint; does not depend on 002a/b.
- **(3) Real-raster threshold robustness** — if contrast-faded scans misfire with Otsu, swap to adaptive Sauvola/Niblack. Wait for user reports before committing to this sprint.
- **(4) Sharp corner < 60° fallback** — PCA fit from 5 samples can be unstable on very short edges; add step-1-only fallback when refine confidence is low.

## Position in Plan

Phase 1 — BMA-Plan Lite epic + proto geometry/snap track. The centerline snap feature is a Phase 1 in-scope capability (geometry/snap, not auto-boundary-detection). Invent pipeline (Pack H) ran correctly: idea filed → 7-phase research+diverge+spike → human CHECKPOINT → two sprint cards → dev loop ships → bugs fixed. No Phase 2 scope boundary crossed. Proto/ server untouched. Lite size cap respected (1199/1200). LITE-7 (PyInstaller .exe) remains the only deferred epic item.

---

# Previous: SIM-2 — /bma-simulate regression-probe hardening — PASS

**Date:** 2026-05-24
**Branch:** main

## Outcome

PASS. `/bma-simulate` (Pack J) gains a permanent hard-probe channel: `.claude/skills/bma-simulate/regression_probes.json` (tracked, curated per sprint) holds mandatory probe steps prepended to every SCENARIO_PLAN. Two probes are registered — LITE-BUG-MODAL-NEST and LITE-BUG-DBLCLICK-OVER-POP (both closed by LITE-BUG-2-OPUS47-FINDINGS) — and both verify PASS against the current build (860 ms + 2919 ms). A false probe assertion returns a new REGRESSION severity tier (above CRASH), triggering the SIM_REGRESSION stop condition. Zero changes to `lite/` or `proto/` runtime code. Proto 21-marker baseline unchanged.

## What was delivered

- `.claude/skills/bma-simulate/regression_probes.json` — NEW: 2 active probes (evaluate-type: MODAL-NEST; mouse_sequence-type: DBLCLICK-OVER-POP) + `_schema` block (~50 lines, tracked)
- `.claude/skills/bma-simulate/SKILL.md` — Phase A reads probes + prepends probe steps; REGRESSION severity (highest tier) added; SIM_REGRESSION + SIM_PROBES_MALFORMED stop conditions; soft/hard memory channel table
- `.claude/agents/bma-sim-driver.md` — `regression_probe` step type + execution recipe sub-section
- `sprints/active/SIM-2-REGRESSION-PROBES-2026-05-24.md` — sprint card (to move to completed/)

## What's next

- **(OPTION 2) Snap-to-walls polygon strategy** — replace synthetic 80%-quad placeholder with real wall-snap geometry (read PDF vector edges, snap to walls); new `lite/static/js/snap-walls.js`; run via `/bma-lite-dev`
- **(OPTION 3) Lite PDF page classifier** — auto-tag floor/site/cover from title block OCR or layout hints; invention-level — run `/bma-invent` first

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic, simulator tooling hardening sub-track. SIM-2 closes the "simulator reflection-loop" follow-up filed in LITE-BUG-2-OPUS47-FINDINGS. No Phase 2 scope boundary crossed. Proto/ and lite/ runtime untouched. LITE-7 (packaging) remains the only deferred epic item.

---

<!-- LITE-BUG-2-OPUS47-FINDINGS and older reports archived to docs/archive/reports-2026-05-09.md -->
