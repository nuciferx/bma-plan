# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-07-02 (AUDIT-20260702-infra-bundle SHIPPED — same-day follow-on to the 2-bug measurement-accuracy audit. NEW aggregate lite test runner (LITE_RUN_ALL_OK 60/60 in 8.5 min) + export payload validation caps on both export endpoints (LITE_EXPORT_ENDPOINTS_OK 14/14, first real HTTP tests of either endpoint, HTTP 400 on oversize/malformed payloads, fixes a latent 500) + read-only render-engine accuracy review that found a real BROKEN bug — BUG-20260702-lite-pagerot-registration (manual page rotate desyncs stored geometry from the raster; now top of NEXT_ACTIONS). Zero proto/ edits. Both 2026-07-02 audit bugs (arc-summary + cfss-summary) shipped earlier today. Previous ship before the audit: SLICE report-edit-1 SHIPPED 2026-06-05.)

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

2026-07-02: AUDIT-20260702-infra-bundle SHIPPED — same-day follow-on to the 2-bug measurement-accuracy audit closed earlier today. NEW `lite/tests/run_all_tests.py` aggregate runner with disk/dependency PREFLIGHT (`LITE_RUN_ALL_OK` 60/60 in 8.5 min, first full run) closes the "no aggregate runner" gap both audit bugs flagged; `/export-pdf-overlay` + `/export-xlsx` now validate payloads BEFORE rendering with 5 caps (HTTP 400, no silent truncation, bonus fix for a latent 500) + `LITE_EXPORT_ENDPOINTS_OK` 14/14 (first real HTTP tests of either endpoint); read-only Opus render-engine accuracy review verdict SOUND for the coordinate contract but found one real BROKEN bug — `BUG-20260702-lite-pagerot-registration` (manual page rotate desyncs stored geometry from the raster, `ptToScreen`/`screenToPt` ignore `pgRot`), filed as top-priority next work. Zero proto/ edits, zero forbidden-surface edits.

2026-07-02 (earlier): BUG-20260702-lite-cfss-summary SHIPPED — CFSS shared-shape instances had no `.pts`/`.catId`, so every area rollup skipped them (silent total loss on promote) and `buildExportData`/`exportPdfOverlay` called `catOf(o.catId)` before the `kind` guard (TypeError → XLSX + annotated-PDF export crashed outright on any page with an instance); fixed by passing `{catId, semanticTag}` into `addMaster` at promote time plus new `rollupAreaM2`/`rollupCatId` dispatch helpers reused at all 6 rollup sites; new `LITE_SUMMARY_CFSS_OK` guard test proven RED→GREEN (14/14 tests exit 0). Zero proto/ edits, zero forbidden-surface edits. This closes the 2-bug 2026-07-02 measurement-accuracy audit (bug 1 = `BUG-20260702-lite-arc-summary`, shipped earlier today).

2026-07-02 (earlier): BUG-20260702-lite-arc-summary SHIPPED — arc-edge polygon areas were correct on the canvas label but silently wrong in every rollup because 6 call sites dropped `o.edges` when computing area; fixed by swapping to `polyMetricsAnyShape` at all 6 sites; new `LITE_SUMMARY_ARC_OK` guard test proven RED→GREEN. Zero proto/ edits.

2026-06-05: SLICE report-edit-1 SHIPPED — editable lite report with jspreadsheet-ce grid, custom cell-click formula picker, stable-row-id subtotal mapper, NaN-guard, and localStorage v1 persistence. LITE_REPORT_EDIT_OK 7/7. Zero proto/ edits. Grid behind #re-toggle dev gate.

## Latest Sprint

- AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review: PASS (2026-07-02) — same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit. Sprint A (`9c4c36e`): NEW `lite/tests/run_all_tests.py` aggregate test runner (discovers + runs every `test_*.py`, per-test timeout, summary table, `LITE_RUN_ALL_OK`/`FAIL`) with disk/dependency PREFLIGHT (fails fast on <2 GB free on repo or system drive, hardened after the 2026-07-02 ENOSPC incident, or missing uvicorn/playwright/fitz/node); first full run 60/60 PASS in 8.5 min. Sprint B (`60d424a`): `/export-pdf-overlay` + `/export-xlsx` now validate payloads BEFORE rendering (5 caps: `MAX_EXPORT_PAGES`/`MAX_OBJECTS_PER_PAGE`/`MAX_ANNOTS_PER_PAGE`/`MAX_PTS_PER_OBJECT`/`MAX_COORD_ABS`, HTTP 400 not silent truncation, ≥10x realistic worst case, bonus fix for a latent 500 on non-numeric page key); `wb.save()` offloaded via `run_in_threadpool`; NEW `lite/tests/test_export_endpoints.py` marker `LITE_EXPORT_ENDPOINTS_OK` 14/14 — first real HTTP tests of either export endpoint. Review C (read-only, Opus agent): `PDFJS-VIEWPORT-CLIPPED` render architecture verdict SOUND for `V.rot`/`pgRot`=0 (coordinate contract algebraically exact, residual ≈ ±0.5 device px = click-precision floor); filed real BROKEN bug `BUG-20260702-lite-pagerot-registration` (manual page rotate desyncs stored geometry from raster — `ptToScreen`/`screenToPt` ignore `pgRot`) as top-priority next work, plus bundle `AUDIT-20260702-render-followups` (pdfjs-fail fallback / pan double-buffer / scanned-PDF detection / memory-claim correction / real overlay-registration test) and `AUDIT-20260702-s2-fitz-lock` (per-case PyMuPDF lock needed before overlay-render threadpool offload). Proto NOT TOUCHED; zero forbidden-surface edits.
- BUG-20260702-lite-cfss-summary — CFSS shared-shape instances excluded from every rollup consumer + export crash: PASS (2026-07-02) — bug 2 of the 2026-07-02 measurement-accuracy audit; instances (`{kind:'instance', masterId, offsetPt}`, no `.pts`/`.catId`) skipped by all 6 rollup consumers (silent total loss on promote); `buildExportData`/`exportPdfOverlay` called `catOf(o.catId)` before the `kind` guard → TypeError → XLSX + annotated-PDF export crashed on any page with an instance; root cause `cfssCommitPromote` called `addMaster()` without the `opts` arg; fixed by passing `{catId, semanticTag}` into `addMaster` (additive schema, free persistence) + NEW `rollupAreaM2`/`rollupCatId` dispatch helpers in `cross-floor-shapes.js` (typeof-guarded, load-order-mandatory) reused at all 6 rollup sites + 2 crash-site fixes; patch plan by `bma-path-geometry-reviewer` on Opus (user-requested); NEW `lite/tests/test_summary_cfss_parity.py` marker `LITE_SUMMARY_CFSS_OK` exercises the real promote flow, proven RED (totals 2000, exports threw) → GREEN (totals 2100, no throw); 14/14 tests exit 0; commit `02e35af`; proto NOT TOUCHED; ui-lite.html line-neutral. Both audit bugs now SHIPPED.
- BUG-20260702-lite-arc-summary — Arc-edge polygon areas excluded from every rollup consumer: PASS (2026-07-02) — 6 call sites (`ui-lite.html:1049` computeSummary, `export-annotate.js:14/27/58` buildExportData/exportPdfOverlay/buildReportPayload, `layer-tree.js:62` _ltOwnArea, `overview-setup.js:642` _lovsLayerArea) passed `{pts:o.pts}` into `polyMetrics` (drops `o.edges` → straight-chord area) instead of `polyMetricsAnyShape(o,pg)` (arc-correct); triage found 4 sites, specialist review widened to 6; fixed by callee swap at all 6, zero edits to drift-locked measure-engine.js; NEW `lite/tests/test_summary_arc_parity.py` marker `LITE_SUMMARY_ARC_OK` proven RED (git stash) → GREEN; 8 regression suites GREEN (MEASURE_PARITY_OK, LITE_ARC_EDGE_OK, test_report, LITE_REPORT_VARS_OK, LITE_REPORT_VARS_ROLLUP_OK, LITE_EXPORT_SUBMENU_OK, LITE_TREE_ROLLUP_OK, LITE_OVERVIEW_SETUP_OK); commit `e5264e2`; proto NOT TOUCHED; ui-lite.html stays 1,154/1,200 cap.
- SLICE report-edit-1 — Editable lite report: PASS (2026-06-05) — shipped jspreadsheet-ce grid + custom cell-click formula picker + stable-row-id subtotal mapper + NaN-guard + localStorage v1 persistence; report-edit.js NEW 404 LOC; lite-report.html +46; ~440 KB vendor bundle (MIT offline); LITE_REPORT_EDIT_OK 7/7; proto NOT TOUCHED; grid behind #re-toggle dev gate.
- BUG-20260526-lite-stale-pf-folder-cleanup: PASS (2026-05-26) — fixed seedPageFolders() never removing stale PF_floor_N folders+seed layers when floor pages re-tagged; added _pflFolderHasUserDrawnObjects + _pflPrunePF helpers; safety guard preserves folders with user objects; PF_CLEANUP_OK 4/4 (basic cleanup / safety preservation / idempotency / PF_excluded never pruned); 5 regressions GREEN; page-folder-layers.js 743→790; proto NOT TOUCHED.
- Centerline Snap arc (invent 2026-05-24-22-14 → INV-002a proto → INV-002b lite → 2 post-ship bugfixes): PASS (2026-05-25) — user problem "วัดที่ดินเส้นปะได้ 3 ค่าต่างกัน" → /bma-invent 7-phase pipeline (commit 0208314) → Approach A (Otsu + Zhang-Suen + PCA corner refine, maxDelta=0.185% PASS 4/4) → proto: NEW proto/static/js/centerline-snap.js 208 LOC + ui.html +15 net lines + e2e_ui_test.py +162 lines; PHASE_CENTERLINE_SNAP_OK 10/10 (maxDelta=0.140%) → lite: NEW lite/static/js/centerline-snap.js 306 LOC (Section A byte-identical proto, Section B lite glue) + ui-lite.html 1197→1199; LITE_CENTERLINE_SNAP_OK 8/8 (maxDelta=0.1778%) → 2 user-reported bugs fixed same day: DPR coord mismatch (commits ff3f9fe) + button overlap (5783df4); additive schema obj.traceMode; MEASURE_PARITY_OK GREEN; zero server changes.
- SIM-2 — /bma-simulate regression-probe hardening: PASS (2026-05-24) — regression_probes.json (tracked, curated per sprint) added as hard memory channel; 2 probes (LITE-BUG-MODAL-NEST evaluate-type 860ms + LITE-BUG-DBLCLICK-OVER-POP mouse_sequence-type 2919ms) prepended to every SCENARIO_PLAN; REGRESSION severity (above CRASH) + SIM_REGRESSION stop condition; SKILL.md + bma-sim-driver.md updated; zero lite/proto runtime edits.
- LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop): PASS (2026-05-24) — LITE-BUG-MODAL-NEST: missing </div> caused #setupModal nested in hidden #modal, Page Setup invisible; LITE-BUG-DBLCLICK-OVER-POP: unbounded while loop ate intentional vertex (4 pts → 3 pts, 713→356 m²); bounded for(_np<2) fix; zero net lines; 1197 lines (cap 1200); live Playwright verify 3/3 PASS; ZERO proto/ edits.
- LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite: PASS (2026-05-22) — A4 landscape, plan image+SVG polygon overlay left, area table grouped by semanticTag right, contenteditable header/row-name/note, read-only area cells, @page print-to-PDF, sessionStorage handoff, sample fallback; LITE_REPORT_OK GREEN (17/17); REALFLOW_OK (net 222.22); ZERO proto/ edits; MEASURE_PARITY_OK unchanged.
- BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite: PASS (2026-05-21) — spacebar/middle-mouse pan in any mode + H pan-tool + setCursor helper + smooth exp zoom clamped [0.02,40] + zoomCenter/actualSize + F/Ctrl+0/Ctrl+1/Ctrl+=/Ctrl+- shortcuts; BUG_20260521_LITE_PAN_OK GREEN (13/13); ZERO proto/ edits; MEASURE_PARITY_OK unchanged.

Older sprints (BUG-20260521-lite-menu-clip, LITE-0, HT-ACC series and earlier) — see [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md) "Recently Done" and archived logs.

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS (18 baseline markers)
python proto/e2e_ui_test.py full                           # PASS (22 total: 21 baseline + PHASE_CENTERLINE_SNAP_OK 10/10)
```

Last proto full run: 2026-05-25 (Centerline Snap arc; 22 proto _OK total; all markers retained).
Last lite test run: 2026-06-05 (SLICE report-edit-1; LITE_REPORT_EDIT_OK 7/7).
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
