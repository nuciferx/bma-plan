# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-28 (invent `lite-pdf-render-quality` (id `2026-05-27-23-05`) COMPLETED — Sprint #1 + spike v4 + Sprint #2 shipped in 4 commits. PDF.js viewport-clipped now the default lite render path. SMOKE_PDFJS_LIVE_OK 8/8. Previous ship: BUG-20260526-lite-stale-pf-folder-cleanup.)

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

2026-05-28 (continued): invent `lite-pdf-render-quality` RESUMED + COMPLETED — 4 commits shipped: b9cda6c (invent docs + spike v1/v2/v3), f53d239 (Sprint #1 extract page-renderer + export-annotate), 8fca51a (spike v4 — PDF.js ↔ lite's ptToScreen contract PASS 24/24), 382b30a (Sprint #2 PDFJS-VIEWPORT-CLIPPED-INTEGRATION — Chrome-grade sharp at any zoom, mem constant ~13 MB). All forbidden surfaces (ptToScreen / screenToPt / RS / polyAreaM2 / polyMetrics / .bmaplan schema) UNTOUCHED. 8/8 named tests + smoke probe PASS. arcHUDText debt found pre-resolved (no fix needed). Tech debt: curImg compat shim in 6 test files (cleanup follow-up).

2026-05-28: invent `lite-pdf-render-quality` PAUSED — spike v3 PDF.js viewport-clipped PASS on 95-page A1 (mem constant 13.6 MB across zoom 1×→100×), sprint #1 PDFJS-PREP-EXTRACT-RENDERER WIP uncommitted (ui-lite.html 1195→1100, page-renderer.js + export-annotate.js extracted). Sprint #2 design captured. Pre-existing `arcHUDText` debt blocks lite tests. Resume: see `docs/status/NEXT_ACTIONS.md`.

2026-05-26: BUG-20260526-lite-stale-pf-folder-cleanup SHIPPED. Stale PF_floor_N folders + seed layers now pruned on re-tag (user-object preservation guard active). PF_CLEANUP_OK 4/4 + 5 regressions GREEN. Proto baseline unchanged (22 markers).

## Latest Sprint

- BUG-20260526-lite-stale-pf-folder-cleanup: PASS (2026-05-26) — fixed seedPageFolders() never removing stale PF_floor_N folders+seed layers when floor pages re-tagged; added _pflFolderHasUserDrawnObjects + _pflPrunePF helpers; safety guard preserves folders with user objects; PF_CLEANUP_OK 4/4 (basic cleanup / safety preservation / idempotency / PF_excluded never pruned); 5 regressions GREEN; page-folder-layers.js 743→790; proto NOT TOUCHED.
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
python proto/e2e_ui_test.py full                           # PASS (22 total: 21 baseline + PHASE_CENTERLINE_SNAP_OK 10/10)
```

Last proto full run: 2026-05-25 (Centerline Snap arc; 22 proto _OK total; all markers retained).
Last lite test run: 2026-05-26 (BUG-20260526-lite-stale-pf-folder-cleanup; PF_CLEANUP_OK 4/4 + 5 regressions GREEN).
Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- (latest) — fix(BUG-20260526-lite-stale-pf-folder-cleanup): prune stale PF folders + seed layers on re-tag; safety guard for user objects; PF_CLEANUP_OK 4/4
- `969cfca` — fix(BUG-20260526-lite-wizard-followup): block dblclick escape + refresh picker on Done + always lift lock
- `32d5f38` — fix(BUG-20260526-lite-force-setup): force Page Setup on PDF upload, hard-block UI, auto-fill missing tags
- `b902f39` — feat(lite): LFOC-ORDER-B — kind-aware PF folder separation
- `5783df4` — fix(lite): BUG-20260525-lite-cl-position — CL button no longer overlaps zoom controls
- `ff3f9fe` — fix(lite): BUG-20260525-lite-cl-dpr — centerline snap silently no-op on HiDPI displays

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
