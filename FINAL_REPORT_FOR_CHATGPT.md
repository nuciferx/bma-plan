# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: SIM-2 — /bma-simulate regression-probe hardening — PASS

**Date:** 2026-05-24
**Branch:** main

## Outcome

PASS. `/bma-simulate` (Pack J) gains a permanent hard-probe channel: `.claude/skills/bma-simulate/regression_probes.json` (tracked, curated per sprint) holds mandatory probe steps prepended to every SCENARIO_PLAN. Two probes are registered — LITE-BUG-MODAL-NEST and LITE-BUG-DBLCLICK-OVER-POP (both closed by LITE-BUG-2-OPUS47-FINDINGS) — and both verify PASS against the current build (860 ms + 2919 ms). A false probe assertion returns a new REGRESSION severity tier (above CRASH), triggering the SIM_REGRESSION stop condition. Zero changes to `lite/` or `proto/` runtime code. Proto 102-marker baseline unchanged.

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

# Previous: LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop) — PASS

**Date:** 2026-05-24
**Branch:** main

## Outcome

PASS. Two silent bugs in `lite/ui-lite.html` found by the Opus-4.7 multi-model simulator (Pack J) and fixed in a zero-net-line patch. LITE-BUG-MODAL-NEST (BROKEN): `#setupModal` was nested inside hidden `#modal` — Page Setup modal was completely invisible to users. LITE-BUG-DBLCLICK-OVER-POP (FRICTION): unbounded `while` loop in the dblclick handler consumed intentional polygon vertices, saving 4-point polygons as triangles (713 m² reported as 356 m²). All live Playwright verify checks PASS: modal renders 1600x958, polygon saves 4 pts at 714.07 m² (0.13% drift from screen-to-pt rounding, acceptable). `lite/ui-lite.html` stays at 1197 lines (cap 1200). ZERO proto/ edits.

## What was delivered

- `lite/ui-lite.html` — two surgical patches: missing `</div>` at line 194 (closes `#modal` before `#setupModal`); bounded `for(_np<2)` replacing unbounded `while` at lines 502-503; 0 net lines
- `sprints/completed/2026-05-24-lite-bug-2-opus47-findings/LITE-BUG-2-OPUS47-FINDINGS-2026-05-24.md` — sprint card with bug IDs, root causes, patches, self-check

## What's next

- (1) Simulator reflection-loop hardening (SIM-2 — DONE)
- (2) Snap-to-walls polygon strategy
- (3) Lite PDF page classifier

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic. Bug-fix sprint closing two simulator-found regressions. No Phase 2 scope boundary crossed. Proto/ runtime untouched. LITE-7 (packaging) remains the only deferred epic item.

---

# Previous (older): LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite — PASS

**Date:** 2026-05-22
**Branch:** main

## Outcome

PASS. Lite gains a standalone editable web-report page (`lite/lite-report.html`) opened in a new window from the File menu. The report renders one A4-landscape sheet per measured page — plan image with SVG polygon overlay on the left, area table grouped by category on the right — and supports WYSIWYG browser-print-to-PDF. Area numbers are read-only (raw-geometry contract preserved); header fields, row labels, and per-row notes are `contenteditable`. LITE_REPORT_OK GREEN (17/17). REALFLOW_OK confirmed on a real 562 MB permit PDF (net 222.22). ZERO proto/ edits; proto 102-marker baseline unchanged.

## What was delivered

- `lite/lite-report.html` — A4 landscape report page: plan+SVG overlay with numbered polygon badges; area table grouped by semanticTag; per-group subtotals; page net (deductions −1); contenteditable header/row-name/note; read-only area cells; @page + @media print WYSIWYG; sample standalone fallback
- `lite/server_lite.py` — additive `GET /report` FileResponse route (+9 lines)
- `lite/ui-lite.html` — File-menu item #mi-report + `reportPageTitle()` / `buildReportPayload()` / `openReport()` (+52 lines); sessionStorage["bmaReportPayload"] handoff; images via /page/{n} URLs
- `lite/tests/test_report.py` — NEW LITE_REPORT_OK Playwright guard (17 checks)
- `docs/status/PHASE_INDEX.md` — LITE-REPORT sprint card marked done

## What's next

- Optional LITE-REPORT v2 follow-ups: custom branding, cross-page roll-up summary sheet, persist header/notes edits to .bmaplan — all out of scope for this sprint, queued as backlog.
- LITE-7 PyInstaller .exe — still deferred by user.
- "Lock the site-plan line" E2E guard (queued optional) — verifies no FAR/OSR/setback verdict UI renders in lite.

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic (INV-2026-05-21-001 / INV-2026-05-21-002). LITE-REPORT closes the last user-facing output gap in the lite epic (the only missing output was a human-readable, printable, editable document). No Phase 2 scope boundary crossed. Proto/ runtime untouched. LITE-7 (packaging) is the only remaining epic item, and it is deferred.

---

# Previous (older): BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite — PASS

**Date:** 2026-05-21
**Branch:** main

## Outcome

PASS. Forked proto's entire view/navigation control system into `lite/ui-lite.html`, adapted to lite's single-canvas `V={k,ox,oy,rot}` transform model. The headline bug (pan blocked entirely when any draw tool was selected) is fixed. All 7 control gaps are closed: spacebar/middle-mouse pan in any mode, sticky H pan-tool, cursor feedback, smooth exponential zoom clamped to [0.02, 40], fit/actual-size/zoom keyboard shortcuts. New Playwright regression guard validates 13 control paths (BUG_20260521_LITE_PAN_OK GREEN). ZERO proto/ edits. MEASURE_PARITY_OK confirms ptToScreen/screenToPt/RS untouched.

## What was delivered

- `lite/ui-lite.html` — full view-control system: spacebar/middle-mouse pan intercept at top of mousedown (works in any mode including mid-draw); sticky H pan-tool (`state.panTool`); `setCursor()` helper (grab/grabbing/crosshair/default); smooth exponential wheel zoom `exp(-deltaY*0.0015)` clamped to [ZMIN=0.02, ZMAX=40]; `zoomCenter(f)` zoom about viewport center; `actualSize()` reset to 1:1; keyboard shortcuts F/Ctrl+0=fit, Ctrl+1=actual, Ctrl+=/Ctrl+-=zoom; enriched hint text
- `lite/tests/test_pan_controls.py` — NEW Playwright regression guard (13 checks)
- `docs/status/PHASE_INDEX.md` — bug filed + marked done

## What's next

- Continue lite epic: LITE-7 PyInstaller .exe (deferred by user), or pick next queued PHASE_INDEX item.
- Optional follow-up: lite per-page rotation parity with proto (V.rot global vs. proto per-page server-side rotation — deeper change, out of view-control scope).

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic (INV-2026-05-21-001). This is a bug-fix sprint on the lite tree. No Phase 2 scope boundary crossed. Proto/ runtime untouched. All lite functionality (snap, export, save/load cross-open) remains intact.

---

# Previous (older): LITE-0 — scaffold standalone /lite/ tree (epic INV-2026-05-21-001 sub-sprint 1) — PASS

**Date:** 2026-05-21
**Branch:** main

## Outcome

PASS. LITE-0 scaffolds the `/lite/` sibling tree as the foundation of BMA-Plan Lite (Approach A: vendored-copy + contract-test). The measurement engine is vendored byte-identical from `proto/ui.html` and protected by an anti-drift parity gate that verifies both source byte-identity (10 fns + 2 consts) and numeric parity. The LITE-0 UI shell self-tests on load (unit square = 25.00 m2, 0 console errors). Proto full E2E baseline is unchanged at 102 _OK markers — zero proto/ edits were made.

## What was delivered

- `lite/static/js/measure-engine.js` — vendored engine (RS, pdfToC, cToPdf, polyAreaM2, polyMetrics, polySelfIntersects, pathAreaM2, 6 path helpers) + lite-only `objectAreaM2Lite`
- `lite/tests/test_measure_parity.py` + `lite/tests/fixtures/measure_parity_v1.json` — anti-drift parity gate (MEASURE_PARITY_OK)
- `lite/server_lite.py` — skeleton FastAPI (static mount + /health + /); endpoints deferred to LITE-1
- `lite/launch_lite.py` — free-port (8100+) launcher
- `lite/ui-lite.html` — LITE-0 shell with self-test
- `lite/README.md` — vendoring contract + version-sync policy
- `docs/invent/bma-plan-lite-standalone.md` — invent research + approach decision record
- `proto/sandbox/invent-bma-plan-lite-standalone.html` — invention spike
- `docs/status/PHASE_INDEX.md` — LITE-0 sprint card added + status done

## What's next

LITE-1: backend endpoints (`/upload`, `/page/{n}`, `/thumb`) reusing PyMuPDF for the raster render path. Epic continues LITE-1..7 (chrome, tools, dimension rendering, save/load+count, export, packaging).

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic (INV-2026-05-21-001). LITE-0 is the scaffold sprint (sub-sprint 1 of 8). No Phase 2 scope boundary crossed. Proto/ runtime untouched. Parity gate enforces that any future proto engine change is immediately visible.

<!-- HT-ACC series and older reports archived to docs/archive/reports-2026-05-09.md -->
