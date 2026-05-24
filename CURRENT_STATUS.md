# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-25 (updated: Centerline Snap arc PASS — INV-002a proto (commit 6db0461) + INV-002b lite (commit ad920c6) shipped; 2 post-ship lite bugs fixed (DPR coord mismatch ff3f9fe; button overlap 5783df4). PHASE_CENTERLINE_SNAP_OK 10/10 (maxDelta=0.140%), LITE_CENTERLINE_SNAP_OK 8/8 (maxDelta=0.1778%). All prior baseline markers GREEN. Zero server changes.)

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

2026-05-25: Centerline snap shipped to proto (INV-002a, commit 6db0461) + lite (INV-002b, commit ad920c6); 2 post-ship lite bugs fixed (DPR coord mismatch ff3f9fe, button overlap 5783df4). PHASE_CENTERLINE_SNAP_OK 10/10, LITE_CENTERLINE_SNAP_OK 8/8, all baseline markers GREEN.

## Latest Sprint

- Centerline Snap arc (invent 2026-05-24-22-14 → INV-002a proto → INV-002b lite → 2 post-ship bugfixes): PASS (2026-05-25) — user problem "วัดที่ดินเส้นปะได้ 3 ค่าต่างกัน" → /bma-invent 7-phase pipeline (commit 0208314) → Approach A (Otsu + Zhang-Suen + PCA corner refine, maxDelta=0.185% PASS 4/4) → proto: NEW proto/static/js/centerline-snap.js 208 LOC + ui.html +15 net lines + e2e_ui_test.py +162 lines; PHASE_CENTERLINE_SNAP_OK 10/10 (maxDelta=0.140%) → lite: NEW lite/static/js/centerline-snap.js 306 LOC (Section A byte-identical proto, Section B lite glue) + ui-lite.html 1197→1199; LITE_CENTERLINE_SNAP_OK 8/8 (maxDelta=0.1778%) → 2 user-reported bugs fixed same day: DPR coord mismatch (commits ff3f9fe) + button overlap (5783df4); additive schema obj.traceMode; MEASURE_PARITY_OK GREEN; zero server changes.
- SIM-2 — /bma-simulate regression-probe hardening: PASS (2026-05-24) — regression_probes.json (tracked, curated per sprint) added as hard memory channel; 2 probes (LITE-BUG-MODAL-NEST evaluate-type 860ms + LITE-BUG-DBLCLICK-OVER-POP mouse_sequence-type 2919ms) prepended to every SCENARIO_PLAN; REGRESSION severity (above CRASH) + SIM_REGRESSION stop condition; SKILL.md + bma-sim-driver.md updated; zero lite/proto runtime edits.
- LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop): PASS (2026-05-24) — LITE-BUG-MODAL-NEST: missing </div> caused #setupModal nested in hidden #modal, Page Setup invisible; LITE-BUG-DBLCLICK-OVER-POP: unbounded while loop ate intentional vertex (4 pts → 3 pts, 713→356 m²); bounded for(_np<2) fix; zero net lines; 1197 lines (cap 1200); live Playwright verify 3/3 PASS; ZERO proto/ edits.
- LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite: PASS (2026-05-22) — A4 landscape, plan image+SVG polygon overlay left, area table grouped by semanticTag right, contenteditable header/row-name/note, read-only area cells, @page print-to-PDF, sessionStorage handoff, sample fallback; LITE_REPORT_OK GREEN (17/17); REALFLOW_OK (net 222.22); ZERO proto/ edits; MEASURE_PARITY_OK unchanged.
- BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite: PASS (2026-05-21) — spacebar/middle-mouse pan in any mode + H pan-tool + setCursor helper + smooth exp zoom clamped [0.02,40] + zoomCenter/actualSize + F/Ctrl+0/Ctrl+1/Ctrl+=/Ctrl+- shortcuts; BUG_20260521_LITE_PAN_OK GREEN (13/13); ZERO proto/ edits; MEASURE_PARITY_OK unchanged.
- BUG-20260521-lite-menu-clip — lite top-bar dropdowns unclickable: PASS (2026-05-21) — #topbar overflow:hidden→visible + position:relative;z-index:60; BUG_20260521_LITE_MENU_CLIP_OK GREEN (4/4); ZERO proto/ edits.
- LITE-0 — scaffold standalone /lite/ tree (epic INV-2026-05-21-001 sub-sprint 1): PASS (2026-05-21) — /lite/ sibling tree scaffolded; measure-engine.js vendored byte-identical from proto/ui.html; anti-drift parity gate MEASURE_PARITY_OK (10 fns + 2 consts + 5 polys/2 paths/4 coords); skeleton server_lite.py + launch_lite.py; ui-lite.html self-test 25.00 m2; ZERO proto/ edits; proto baseline unchanged.
- HT-ACC series (HT-ACC-1/2/3 + HT-NAV-1) — Calibration accuracy UX: PASS (2026-05-20) — Area math proven exact; calibRaw[] + snap-deviation warning (HT-ACC-1); Verify ribbon + longest-baseline tip (HT-ACC-2); pts_per_m tooltip on scale status (HT-ACC-3); HT-NAV-1 no-fix; HT_ACC_OK GREEN (5 sub-checks); commit c0834f0.
- BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore: PASS (2026-05-20) — F11 unconditional preventDefault + widened exit; F9/F10 keybindings; dead `~` CSS selector → `:has()` fix; BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks); commit 9453777.
- INV-2026-05-20-002/003/004 — Layer model rebuild L1+L2+L3: PASS (2026-05-20) — Page-scoped layer as single authority; slug guarantee + render/hit helpers (L1); reassign-layer UI + objLayerKey (L2); global layerVis/layerLock demoted to mirror (L3); INV_LAYER_L1/L2/L3_OK GREEN; HT8D5A restored; site-plan overlap bug fixed.
- INV-2026-05-20-001 — Verify Scale tool: PASS (2026-05-20) — Verify Scale flow (approach A): %dev band green/yellow/red + Accept/Re-calibrate/Average modal; `calibPanelOk` router; `finishCalib` unchanged; `calibScale.verifyResult` additive schema; INV_VERIFY_SCALE_OK 9/9; full EXIT 0; zero regression.

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS (18 baseline markers)
python proto/e2e_ui_test.py full                           # PASS (21 baseline + PHASE_CENTERLINE_SNAP_OK 10/10 = 22 total _OK)
```

Last full run: 2026-05-25 (Centerline Snap arc; PHASE_CENTERLINE_SNAP_OK 10/10 NEW; 22 proto _OK total; all 21 prior markers retained; LITE_CENTERLINE_SNAP_OK 8/8; MEASURE_PARITY_OK unchanged). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- `5783df4` — fix(lite): BUG-20260525-lite-cl-position — CL button no longer overlaps zoom controls
- `ff3f9fe` — fix(lite): BUG-20260525-lite-cl-dpr — centerline snap silently no-op on HiDPI displays
- `916d379` — chore(roadmap): fill INV-2026-05-24-002b commit hash in PHASE_INDEX
- `ad920c6` — feat(lite): INV-2026-05-24-002b — centerline snap (vendor from proto, LITE_CENTERLINE_SNAP_OK)
- `6db0461` — feat(measure): INV-2026-05-24-002a — centerline snap for area tool (PHASE_CENTERLINE_SNAP_OK)
- `0208314` — invent(centerline-snap-dashed-boundary): GO — split proto+lite, spike PASS 4/4

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
