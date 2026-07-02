# PATCH_SUMMARY.md Archive — 2026-06 sessions (archived 2026-07-02)

> Archived from root PATCH_SUMMARY.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint archived 2026-07-02 during BUG-20260702-lite-pagerot-registration sprint; BUG-20260702-lite-arc-summary sprint archived 2026-07-02 during AUDIT-20260702-infra-bundle sprint; SLICE report-edit-1 added 2026-07-02 during BUG-20260702-lite-cfss-summary sprint; AUDIT-20260702-infra-bundle archived 2026-07-02 during the PERF-20260702-lite-foxit-smoothness sprint block; PERF-20260702-lite-foxit-smoothness archived 2026-07-03 during the GO-20260703-invariants-streaming-worker-recycle sprint block) to keep root at Latest + 1 Previous.

---

# Previous: AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review

Branch: main

Date: 2026-07-02

## Outcome: PASS — Same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit (both bugs already shipped earlier today). Sprint A (`9c4c36e`): NEW aggregate `lite/tests/run_all_tests.py` with disk/dependency PREFLIGHT (hardened after the 2026-07-02 ENOSPC incident) — first full run 60/60 PASS in 8.5 min. Sprint B (`60d424a`): `/export-pdf-overlay` + `/export-xlsx` now validate payloads BEFORE rendering (5 caps, HTTP 400 on violation, no silent truncation; fixes a latent 500 as a bonus); NEW `test_export_endpoints.py` (`LITE_EXPORT_ENDPOINTS_OK` 14/14) is the first real HTTP test of either export endpoint. Review C (read-only, Opus): render-engine coordinate contract verdict SOUND for `V.rot`/`pgRot`=0, but surfaces a real BROKEN bug — `BUG-20260702-lite-pagerot-registration` (manual page rotation desyncs stored geometry from the raster) — plus a follow-up hardening bundle, both filed to `PHASE_INDEX.md`, no code applied. **This bug SHIPPED same-day.**

## Summary

Three pieces of work batched into one docs update because they all landed the same day as a direct follow-on to the arc-summary/cfss-summary audit. **Sprint A — AUDIT-20260702-runner-preflight:** `lite/tests/run_all_tests.py` discovers every `test_*.py`, runs each standalone with a per-test timeout (default 420s), prints a summary table, exits `LITE_RUN_ALL_OK`/`FAIL`; `--filter`/`--fail-fast`/`--timeout` options; PREFLIGHT fails fast on <2 GB free on repo drive or system drive, missing `uvicorn`/`playwright`/`fitz`, or missing `node`. Closes the "no aggregate runner" gap both audit bugs flagged as a follow-up. **Sprint B — AUDIT-20260702-export-caps:** S1 `/export-pdf-overlay` pre-render validation — `MAX_EXPORT_PAGES=2000`, `MAX_OBJECTS_PER_PAGE=500`, `MAX_ANNOTS_PER_PAGE=500`, `MAX_PTS_PER_OBJECT=2000`, `MAX_COORD_ABS=20000` (rejects NaN/inf) — HTTP 400 with detail, never silent truncation, all caps ≥10x realistic worst case; bonus fix for a latent 500 on non-numeric page key. S5 `/export-xlsx` row cap `MAX_XLSX_ROWS=20000`. S2 partial: `wb.save()` offloaded via `run_in_threadpool` (provably safe — pure local objects); overlay-render offload deliberately deferred to new card `AUDIT-20260702-s2-fitz-lock` (PyMuPDF `Document` not thread-safe; needs a per-case lock first — naive threadpooling would allow concurrent `get_pixmap()` on the same doc). Patch plan authored by an Opus reviewer agent (read-only, cap-justification table); main agent applied. **Review C — PDF render-engine accuracy review:** `PDFJS-VIEWPORT-CLIPPED` architecture (shipped 2026-05-28) verdict SOUND — coordinate contract algebraically exact for `V.rot`/`pgRot`=0 (residual ≈ ±0.5 device px, click-precision floor not a measured-value error); intrinsic `/Rotate` handled correctly; stale-render token guard solid; vector sharpness to ~4320 DPI effective vs proto's fixed 108 DPI. Filed `BUG-20260702-lite-pagerot-registration` (BROKEN — manual rotate desyncs raster from `ptToScreen`/`screenToPt`, which ignore `pgRot`) plus bundle `AUDIT-20260702-render-followups` (pdfjs-fail fallback / pan double-buffer / scanned-PDF detection / memory-claim correction / real overlay-registration test).

## Files Changed

| File | Change |
|---|---|
| `lite/tests/run_all_tests.py` | NEW — aggregate runner, per-test timeout, summary table, `LITE_RUN_ALL_OK`/`FAIL`, disk/dependency PREFLIGHT |
| `lite/server_lite.py` | `/export-pdf-overlay` pre-render payload validation (5 caps, HTTP 400, fixes latent 500); `/export-xlsx` `MAX_XLSX_ROWS` cap; `wb.save()` offloaded via `run_in_threadpool` |
| `lite/tests/test_export_endpoints.py` | NEW — `LITE_EXPORT_ENDPOINTS_OK` (14 checks), first real HTTP tests of both export endpoints |
| `docs/status/PHASE_INDEX.md` | `BUG-20260702-lite-pagerot-registration` + `AUDIT-20260702-render-followups` + `AUDIT-20260702-s2-fitz-lock` filed — via the review/bug-filing step |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `.bmaplan` schema version stays 1; no fields touched
- Review C is read-only — zero code changes; findings filed as tracked backlog cards only

## Tests Run

```
python lite/tests/test_export_endpoints.py           → LITE_EXPORT_ENDPOINTS_OK  PASS (NEW, 14/14 checks)
python lite/tests/run_all_tests.py                    → LITE_RUN_ALL_OK          PASS (60/60 tests, 8.5 min, first full run)
```

Regression: partial full-suite run (11 files) + targeted 9-file subset (`test_apply_page_mutations.py`, `test_pm_apply_flush_unified.py`, `test_metamorphic_pages.py`, `test_pdfjs_offline.py`, `test_summary_arc_parity.py`, `test_summary_cfss_parity.py`, `test_measure_parity.py`, `test_export_submenu.py`, `test_report.py`) — all exit 0. `MEASURE_PARITY_OK` green confirms no vendored-math touch. Proto E2E n/a (lite-only sprint; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema — no fields touched; version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Export caps set ≥10x realistic worst case — no legitimate flow blocked; clear HTTP 400, never silent truncation
- ✅ Review C read-only — findings filed as backlog cards, not applied directly

---

# Previous: BUG-20260702-lite-cfss-summary — CFSS shared-shape instances excluded from every rollup consumer + export crash

Branch: main

Date: 2026-07-02

## Outcome: PASS — Bug 2 of 2 from the 2026-07-02 measurement-accuracy audit. CFSS shared-shape instances (`{kind:'instance', masterId, offsetPt}`) had no `.pts`/`.catId` and were skipped by every area rollup — promoting a poly to a shared shape silently removed its area from all totals. Worse: `buildExportData`/`exportPdfOverlay` called `catOf(o.catId)` BEFORE the kind guard → TypeError → XLSX and annotated-PDF export crashed outright on any page with an instance. Fixed by passing `{catId, semanticTag}` into `addMaster` at promote time + new `rollupAreaM2`/`rollupCatId` dispatch helpers; new guard test `LITE_SUMMARY_CFSS_OK` proven RED→GREEN.

## Summary

Root cause: `cfssCommitPromote` called `addMaster()` without the `opts` arg, so masters never captured `catId`/`semanticTag`. Fix (commit `02e35af`): (1) promote passes `{catId, semanticTag}` to `addMaster` — additive master schema, persists for free via existing masters serialization in `cfssWrapSave`/`cfssWrapLoad`; legacy pre-fix masters → `rollupCatId` returns `null` → instance skipped from bucket totals safely with a one-time `console.warn`, no crash, no migration UI. (2) NEW helpers `rollupAreaM2(o,pg)` + `rollupCatId(o)` in `cross-floor-shapes.js` co-located with `instanceAreaM2` (single dispatch helper instead of 6 per-site branches — the arc-bug postmortem lesson); `typeof`-guarded at every consumer because `cross-floor-shapes.js` is dynamically injected AFTER `layer-tree.js`/`export-annotate.js` load. (3) Rewired 6 rollup sites — `computeSummary`, `buildExportData`, `exportPdfOverlay` (instances now export as resolved-pts poly overlays via `resolveInstancePts`), `buildReportPayload`, `_ltOwnArea`, `_lovsLayerArea` — and fixed the 2 crash sites (`catOf` moved after `catId` resolution, null-safe). Patch plan by `bma-path-geometry-reviewer` running on Opus (user-requested model override). New guard test `lite/tests/test_summary_cfss_parity.py` (`LITE_SUMMARY_CFSS_OK`) exercises the REAL promote flow (`__cfssTestPromote`) then asserts all 6 consumers report ground truth 2100 m² and both export builders do not throw; proven RED on pre-fix code via `git stash` (totals 2000, `master_has_catId` false, `edThrew`/`ovThrew` true).

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/cross-floor-shapes.js` | `cfssCommitPromote` passes `{catId, semanticTag}` to `addMaster`; NEW `rollupAreaM2(o,pg)` + `rollupCatId(o)` helpers |
| `lite/ui-lite.html:1049` | `computeSummary` — rewired to rollup helpers, line-neutral |
| `lite/static/js/export-annotate.js` | `buildExportData`/`exportPdfOverlay` — rewired + crash fix (catOf moved after catId resolution); `buildReportPayload` — instances in rows/subtotal/net |
| `lite/static/js/layer-tree.js` | `_ltOwnArea` — rewired to rollup helpers |
| `lite/static/js/overview-setup.js` | `_lovsLayerArea` — rewired to rollup helpers |
| `lite/tests/test_summary_cfss_parity.py` | NEW — `LITE_SUMMARY_CFSS_OK` guard test, real promote flow, RED→GREEN proof |
| `lite/tests/bug-archive.jsonl` | Appended (fixed_commit `02e35af`) — via bug-report pipeline |
| `docs/status/PHASE_INDEX.md` | Row updated to ✅ done — via bug-report pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `.bmaplan` schema version stays 1; master `catId`/`semanticTag` is additive only
- `lite/ui-lite.html` — stays under line cap (line-neutral edit)

## Tests Run

```
python lite/tests/test_summary_cfss_parity.py  → LITE_SUMMARY_CFSS_OK       PASS (NEW)
python lite/tests/test_cfss_model.py           → LITE_CFSS_MODEL_OK        PASS
python lite/tests/test_cfss_persist.py         → LITE_CFSS_PERSIST_OK      PASS
python lite/tests/test_cfss_drag.py            → LITE_CFSS_DRAG_OK         PASS
python lite/tests/test_cfss_edit.py            → LITE_CFSS_EDIT_OK         PASS
python lite/tests/test_cfss_ui.py              → LITE_CFSS_UI_OK           PASS
python lite/tests/test_cfss_rightclick_menu.py → LITE_CFSS_RIGHTCLICK_MENU_OK PASS
python lite/tests/test_summary_arc_parity.py   → LITE_SUMMARY_ARC_OK       PASS (bug-1 guard stays green)
python lite/tests/test_measure_parity.py       → MEASURE_PARITY_OK         PASS (drift-lock intact)
python lite/tests/test_arc_edge.py             → LITE_ARC_EDGE_OK          PASS
python lite/tests/test_report.py               → PASS
python lite/tests/test_report_vars_rollup.py   → LITE_REPORT_VARS_ROLLUP_OK PASS
python lite/tests/test_export_submenu.py       → LITE_EXPORT_SUBMENU_OK    PASS
python lite/tests/test_tree_rollup.py          → LITE_TREE_ROLLUP_OK       PASS
python lite/tests/test_overview_setup.py       → LITE_OVERVIEW_SETUP_OK    PASS
```

14/14 exit 0. Proto py_compile + smoke + full NOT re-run. Lite-only sprint; proto zero edits; no forbidden-trigger surface touched.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema — additive only (master `catId`/`semanticTag`); version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` stays under line cap (line-neutral edit)
- ✅ MEASURE_SCOPE_OK verdict (geometry-core + export-impact + additive schema, atomic, not split)

---

# Previous: BUG-20260702-lite-arc-summary — Arc-edge polygon areas excluded from every rollup consumer

Branch: main

Date: 2026-07-02

## Outcome: PASS — 6 rollup call sites (summary panel, XLSX export, annotated-PDF overlay, report, layer totals, site-setup rollup) were computing straight-chord area instead of arc-corrected area for arc-edge polygons; fixed by swapping to `polyMetricsAnyShape`; new guard test `LITE_SUMMARY_ARC_OK` proven RED→GREEN across the fix.

## Summary

Arc-edge polygon areas were correct on the per-object canvas label (`areaOf`, uses `polyMetricsAnyShape`) but silently wrong in EVERY downstream rollup — 6 call sites passed `{pts:o.pts}` (dropping `o.edges`) into `polyMetrics`, computing the straight-chord area instead. Fix swaps the callee to `polyMetricsAnyShape(o,pg)` at all 6 sites: `lite/ui-lite.html:1049` (`computeSummary`), `export-annotate.js:14/27/58`, `layer-tree.js:62`, `overview-setup.js:642`. Triage (`bma-bug-triager`) found 4 sites; specialist review (`bma-path-geometry-reviewer`) widened to 6. Zero edits to the drift-locked vendored `measure-engine.js`; non-arc behavior byte-identical. New `LITE_SUMMARY_ARC_OK` guard test asserts "every rollup consumer == Σ areaOf labels (arc-inclusive)" via an independent closed-form fixture, proven RED on pre-fix code (git stash) then GREEN after. Shipped commit `e5264e2`.

## Files Changed

| File | Change |
|---|---|
| `lite/ui-lite.html:1049` | `computeSummary` — `polyMetrics({pts:o.pts})` → `polyMetricsAnyShape(o,pg)` |
| `lite/static/js/export-annotate.js:14` | `buildExportData` — same callee swap |
| `lite/static/js/export-annotate.js:27` | `exportPdfOverlay` — same callee swap |
| `lite/static/js/export-annotate.js:58` | `buildReportPayload` — same callee swap |
| `lite/static/js/layer-tree.js:62` | `_ltOwnArea` — same callee swap (found by specialist review) |
| `lite/static/js/overview-setup.js:642` | `_lovsLayerArea` — same callee swap (found by specialist review) |
| `lite/tests/test_summary_arc_parity.py` | NEW — `LITE_SUMMARY_ARC_OK` guard test, closed-form fixture, RED→GREEN proof |
| `lite/tests/bug-archive.jsonl` | Appended (fixed_commit `e5264e2`, status `fixed`) — via bug-report pipeline |
| `docs/status/PHASE_INDEX.md` | Row updated to ✅ done — via bug-report pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (callee swap only, function bodies untouched)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; no fields touched
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `lite/ui-lite.html` — stays within line cap (1,154/1,200)

## Tests Run

```
python lite/tests/test_summary_arc_parity.py   → LITE_SUMMARY_ARC_OK        PASS
python lite/tests/test_measure_parity.py       → MEASURE_PARITY_OK          PASS (drift-lock intact)
python lite/tests/test_arc_edge.py             → LITE_ARC_EDGE_OK           PASS
python lite/tests/test_report.py               → PASS
python lite/tests/test_report_vars.py          → LITE_REPORT_VARS_OK        PASS
python lite/tests/test_report_vars_rollup.py   → LITE_REPORT_VARS_ROLLUP_OK PASS
python lite/tests/test_export_submenu.py       → LITE_EXPORT_SUBMENU_OK     PASS
python lite/tests/test_tree_rollup.py          → LITE_TREE_ROLLUP_OK        PASS
python lite/tests/test_overview_setup.py       → LITE_OVERVIEW_SETUP_OK     PASS
```

All exit 0. Proto py_compile + smoke + full NOT re-run. Lite-only sprint; proto zero edits; no forbidden-trigger surface touched.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged (callee swap only)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema — no change; version stays 1
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` stayed within line cap (1,154/1,200)
- ✅ MEASURE_SCOPE_OK verdict (geometry-core + export-impact, atomic, not split)

---

# Previous: BUG-20260526-lite-stale-pf-folder-cleanup

Branch: main

Date: 2026-05-26

## Outcome: PASS — Pruned stale PF_floor_N folders + seed layers in lite when their pages re-tagged (with user-object preservation guard). PF_CLEANUP_OK 4/4 + 5 regressions GREEN. Lite-only sprint; proto NOT TOUCHED.

## Summary

`seedPageFolders()` in `lite/static/js/page-folder-layers.js` never removed folders that disappeared from `folderPageMap`. `removeFolder` was imported at line 8 but never called anywhere in the file (grep-verified). Side effect: every time a user re-tagged a floor page to non-floor, the previous `PF_floor_N` folder + its 3 seed layers ("GFA ชั้น N", "หักช่องลิฟต์", "หักช่องบันได") lingered as ghost rows. Two internal helpers added: `_pflFolderHasUserDrawnObjects(folderId)` walks descendant layers and scans `PS[*].objects` for user-drawn objects; `_pflPrunePF(activeFolderIds)` reverse-walks FOLDERS of kind `page-folder`, skips `PF_excluded` and folders with user objects, then removes the rest. `PF_excluded` is never pruned even when empty. All changes are in the module only; `lite/ui-lite.html` untouched (cap 1200/1200).

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/page-folder-layers.js` | +47/-2 (743→790 lines, ≤1000 cap) — added `_pflFolderHasUserDrawnObjects`, `_pflPrunePF`; wired into `seedPageFolders`; return shape adds `pruned` (in-memory only) |
| `lite/tests/test_pf_cleanup_on_exclude.py` | NEW 168 lines — 4-case Playwright marker `PF_CLEANUP_OK`: case A basic cleanup / case B safety preservation / case C idempotency / case D PF_excluded never pruned |
| `.claude/skills/bma-simulate/regression_probes.json` | setup_js for LITE-BUG-DBLCLICK-OVER-POP probe updated to call `_lwizAutoLiftLock()` + clear `ov.show` (partial workaround; full probe rewrite deferred to LITE-PROBE-DBLCLICK-REWRITE) |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; `pruned` return field is in-memory only, not serialized
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `lite/ui-lite.html` — UNCHANGED (at 1200/1200 cap)

## Tests Run

```
python -m py_compile lite/server_lite.py                   → OK
python lite/tests/test_pf_cleanup_on_exclude.py            → PF_CLEANUP_OK 4/4
python lite/tests/test_page_folder_model.py                → LITE_PAGE_FOLDER_MODEL_OK
python lite/tests/test_page_folder_persist.py              → LITE_PAGE_FOLDER_PERSIST_OK
python lite/tests/test_pf_kind_folders.py                  → LITE_PF_KIND_OK 11/11
python lite/tests/test_custom_layer_persist.py             → LITE_LAYER_PERSIST_OK
python lite/tests/test_tree_persist.py                     → LITE_TREE_PERSIST_OK
/bma-simulate verify re-run                                → PF cleanup VERIFIED PASS
                                                             (stale_PF_floor_1_exists=false;
                                                              dom_render_order=[PF_basement_1, PF_floor_2, PF_excluded])
Manual e2e verify_dblclick_manual.py                       → DBLCLICK_OK (objects=1, pts=4)

Proto py_compile + smoke + full NOT re-run (proto untouched; lite-only sprint).
Reference baseline: proto full E2E = 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10, unchanged).
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema additive only (return-value field `pruned` is in-memory, not serialized)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` UNCHANGED (at 1200/1200 cap)

---

# Previous: Centerline Snap arc (invent 2026-05-24-22-14 → INV-002a proto → INV-002b lite → 2 post-ship bugfixes)

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

# Previous: SLICE report-edit-1 — Editable lite report

Branch: main

Date: 2026-06-05

## Outcome: PASS — Editable lite report shipped — vendored jspreadsheet-ce grid + custom Excel-style cell-click formula picker + stable-row-id subtotal mapper + NaN-guard; LITE_REPORT_EDIT_OK 7/7.

## Summary

New module `lite/static/js/report-edit.js` (404 LOC) wraps jspreadsheet-ce CE with a custom formula picker (cell-click-while-editing UX that CE lacks), a stable-row-id subtotal mapper (deleting a referenced row drops the term + raises a red flag instead of silently shifting references), and render/persist/provenance helpers (stale detection, NaN-guard, localStorage v1). `lite/lite-report.html` gains 46 lines for the override-overlay toggle and grid mount. Full test suite: LITE_REPORT_EDIT_OK 7/7. Zero proto/ edits; all forbidden surfaces untouched.

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/report-edit.js` | NEW 404 LOC — formula picker + stable-row-id mapper + render/persist/provenance + NaN-guard |
| `lite/lite-report.html` | +46 lines — override-overlay toggle, grid mount, 4 vendor tags |
| `lite/static/js/vendor/jspreadsheet.min.js` | NEW vendored MIT jspreadsheet-ce |
| `lite/static/js/vendor/jspreadsheet.min.css` | NEW vendored MIT |
| `lite/static/js/vendor/jsuites.min.js` | NEW vendored MIT jsuites peer dep |
| `lite/static/js/vendor/jsuites.min.css` | NEW vendored MIT |
| `lite/tests/test_report_edit.py` | NEW 245 LOC — 7-case Playwright, marker LITE_REPORT_EDIT_OK |
| `docs/invent/lite-editable-report.md` | NEW — full invent record (PICK/RESEARCH/FRAME/DIVERGE/SCORE/SPIKE + 3 RESHAPE) |
| `.claude/skills/lite-spike-iterate/SKILL.md` | NEW — SPIKE→EVAL→fix iteration loop skill |
| `docs/status/PHASE_INDEX.md` | +11 lines — 2 idea entries under ### ideas 2026-06-04 |
| `lite/sandbox/invent-lite-editable-report*.{html,py}` | NEW spike artifacts (5 HTML + 5 eval scripts) |
| `lite/sandbox/vendor/*` | NEW vendor copies for sandbox reproducibility |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema — NO change at all; persistence = localStorage v1 only
- `lite/static/js/measure-engine.js` (drift-locked vendored copy) — UNCHANGED
- `lite/ui-lite.html` — UNCHANGED (stays at cap)

## Tests Run

```
python lite/tests/test_report_edit.py  →  LITE_REPORT_EDIT_OK 7/7  PASS
```

Proto py_compile + smoke + full NOT re-run. Lite-only sprint; proto zero edits; no forbidden-trigger surface touched.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema — no change; persistence = localStorage v1 only
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/static/js/measure-engine.js` UNCHANGED (drift-locked vendored copy)
- ✅ `lite/ui-lite.html` UNCHANGED (stays at cap)
- ✅ Size caps: report-edit.js 404/1000

---

# Archived: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

Branch: main

Date: 2026-07-02

## Outcome: PASS — Fixed the top-priority BROKEN bug filed earlier that day by the AUDIT-20260702-infra-bundle render-engine accuracy review. Manual page rotation (`pageRot`) rotated the PDF.js raster canvas but `ptToScreen`/`screenToPt` ignored `pgRot` (`getRot()` hardcoded to 0) — pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1), geometry drawn while rotated bound itself to the wrong feature, and `/export-pdf-overlay` never applied `pageRot` either. Fixed (commit `9f4b298`, "Fix A — proto-parity" over "Fix B — geometry-baking"): `getRot()` now returns `pageRot[pg]||0`; `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches (net 0 lines, zero geometry mutation, no migration needed); server `/export-pdf-overlay` now prerotates the raster and maps every coordinate through a new `_rp` helper mirroring `pdfToC`. New guard test `LITE_PAGEROT_REG_OK` proven RED→GREEN; 16 at-risk regression files + 26 more from a partial full-suite run = 42 distinct files green.

## Summary

Fixed `BUG-20260702-lite-pagerot-registration`, filed BROKEN/top-priority earlier that day by the `AUDIT-20260702-infra-bundle` render-engine accuracy review (Review C). Manual page rotate (`pageRot`) rotated the PDF.js `getViewport({rotation: V.rot + pgRot})` raster, but the coordinate contract `ptToScreen`/`screenToPt` ignored `pgRot` entirely — `getRot()` was hardcoded to return 0. Effect: pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1) on manual rotate; geometry drawn WHILE a page was rotated stored bound to the un-rotated frame (correct area value, wrong on-screen location — a "right value, wrong location" bug); `/export-pdf-overlay` did not apply `pageRot` at all, so exported PDFs never matched the screen when `pgRot≠0`. Intrinsic PDF `/Rotate` was always correct — only manual rotate was broken. The vendored rotation-aware `pdfToC`/`cToPdf` already existed in `measure-engine.js` (drift-locked, parity-tested) but were dead code at runtime. Fix (commit `9f4b298`, "Fix A — proto-parity", chosen over "Fix B — geometry-baking" by an Opus specialist patch plan): (1) `getRot()` (host contract function, editable per `measure-engine.js`'s own header) now returns `pageRot[pg]||0`; (2) `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches — net 0 lines in `ui-lite.html`, zero user-geometry mutation, no undo interaction, no float drift, old `.bmaplan` files (which already persisted `pageRotations`) just start rendering correctly with no migration; side effect: closes the "un-vendored coordinate math" drift-lock gap flagged by the same audit — lite runtime coords now run through the tested kernel; (3) export WYSIWYG: `export-annotate.js` sends per-page rotation, server `/export-pdf-overlay` prerotates the raster via `Matrix(RS,RS).prerotate(rot)` and maps all coordinates (objects, labels, annotations) through a new `_rp` helper mirroring `pdfToC` — prerotate direction verified EMPIRICALLY against all 4 angles with a standalone pixel test before wiring it in. Fix B (transform stored points at rotate time) rejected: mutates ~6 geometry stores, needs undo snapshotting, causes float drift on repeated rotate, and needs a save-format migration the additive-only schema can't express. New guard test `lite/tests/test_pagerot_registration.py` (marker `LITE_PAGEROT_REG_OK`) covers 4-angle mapping vs. closed-form transform, exact-inverse round-trip, area invariance under rotate, real save/load round-trip, and export dimension/pixel checks — proven RED on pre-fix code via `git stash`, GREEN after.

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/measure-engine.js` | `getRot()` (host contract fn only) now returns `pageRot[pg]||0` instead of hardcoded 0 |
| `lite/ui-lite.html` | `ptToScreen`/`screenToPt` rewired to route through vendored `pdfToC`/`cToPdf` rotation branches — net 0 lines |
| `lite/static/js/export-annotate.js` | export payload now includes per-page rotation |
| `lite/server_lite.py` | `/export-pdf-overlay` — raster prerotated via `Matrix(RS,RS).prerotate(rot)`; NEW `_rp` coordinate-mapping helper (mirrors `pdfToC`) applied to objects/labels/annotations |
| `lite/tests/test_pagerot_registration.py` | NEW — `LITE_PAGEROT_REG_OK` guard test, proven RED→GREEN |
| `docs/status/PHASE_INDEX.md` | row updated to ✅ done — via the bug-report pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only sprint; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED (routed through, not edited)
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED; only the host contract function `getRot()` (explicitly editable per the file's own header) was changed
- `.bmaplan` schema version stays 1; `pageRotations` was already persisted, zero migration needed

## Tests Run

```
python lite/tests/test_pagerot_registration.py → LITE_PAGEROT_REG_OK  PASS (NEW)
```

Regression: 16 at-risk files green + 26 more files green from a partial `run_all_tests.py` pass = 42 distinct files green. `MEASURE_PARITY_OK` green confirms the drift-locked vendored math is untouched.

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged (routed through, not edited)
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema version stays 1; `pageRotations` already persisted, zero migration needed
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ MEASURE_SCOPE_OK equivalent (inline check): `ptToScreen`/`screenToPt` are lite-owned, not forbidden, but are the de-facto coordinate contract — heavy regression run and green
- ✅ Prerotate direction verified empirically with a standalone pixel test before wiring into the export endpoint


---

# Archived: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

Branch: main

Date: 2026-07-02

## Outcome: PASS — Four same-day lite perf sprints driven by an empirical probe (`artifacts/perf/probe_results_20260702.txt`): page-cache LRU (commit `ae0f168`, CHH heap 766→~628 MB), local-first open (commit `3ec9239`, paint before server upload lands, removes the ~80ms/MB upload wait from the critical path), worker warm-up + adjacent prefetch (commit `e0fb856`, hides the flat ~1.2s PDF.js boot cost + instant page-switch), sequential thumbnail warm (commit `a0c1152`, overview grid opens hot without concurrent `fitz` pressure). Probe also REFUTED pan-blanking (0/10 across 3 files) and found the "overview thumbs 0/0" report was a probe selector artifact (real: 45/45 in 9.2s cold). All 4 guard tests RED→GREEN (or new), regression 10/10 + 10/10 + 9/9 + 8/8, `MEASURE_PARITY_OK` green throughout. Lite suite now 67 files, all green. Only remaining perf piece (doc-level memory) is correctly routed to the `PERF-20260702-open-streaming` invent card, not attempted here. **This piece's spike + build now SHIPPED via `GO-20260703-invariants-streaming-worker-recycle` (2026-07-03): spike verdict NOGO-as-memory-fix, RESHAPE to worker-recycle shipped instead.**

## Summary

Four same-day lite performance sprints, driven by an empirical perf probe that measured real cold-open cost on three files: RAMA4 (18.3 MB) first-paint 3.9s cold, CHH (90.8 MB real customer file) 9.6s first-paint + 766 MB heap after 10 pages, and a flat ~1.2s PDF.js library+worker boot floor on every open. The probe's time attribution showed `UPLOAD` dominates at ~80ms/MB while `/raw` is nearly free, refuted pan-blanking (0/10 across 3 files), and found the "overview thumbs 0/0" report was a probe selector artifact (real: 45/45 in 9.2s cold, ~200ms/thumb, instant warm). **Sprint 1 — page-cache LRU (`ae0f168`):** `lite/static/js/page-renderer.js` gets `MAX_PAGE_CACHE=4` LRU eviction with `.cleanup()` on truly-unreferenced evicted pages; `curPage` never evicted; transparent re-fetch on miss. Cache keys 12→4, CHH heap 766→~628 MB (−18%); the remaining ~600 MB is PDF.js doc-level shared state, left to the queued Range-streaming invent card. **Sprint 2 — local-first open (`3ec9239`):** `uploadPdf()` opens local bytes immediately via `PageRenderer.openLocal()` — paint happens before the server upload starts — while upload runs in background; `adoptCase(caseId)` binds the case once it lands so `/raw` is NEVER fetched; server-gated features (`openOv`, exports) guarded during the null-`caseId` window. Paint at 475ms with upload still in flight; on a real 91 MB binder this removes the dominant upload wait from the critical path (~7.5s → ~1-2s). **Sprint 3 — worker warm-up + adjacent prefetch (`e0fb856`):** the flat ~1.2s PDF.js boot is preloaded at app idle via `requestIdleCallback` (`window.__pdfjsWarmed`); after `loadPage(n)`, the `n±1` page is prefetched at idle too, so page switches skip the worker round-trip; prefetched pages count toward the Sprint-1 cache budget. **Sprint 4 — sequential thumbnail warm (`a0c1152`):** `PageRenderer.warmThumbs()` fetches `/thumb/1..N` sequentially (120ms gaps) after upload lands, deliberately sequential (not parallel) to avoid the `lpm-8` lesson and because the per-case `fitz` lock (`AUDIT-20260702-s2-fitz-lock`) doesn't exist yet; token-cancelled on new upload. All 4 sprints kept `lite/static/js/measure-engine.js` drift-locked vendored math untouched (`MEASURE_PARITY_OK` green throughout).

## Files Changed

| File | Change |
|---|---|
| `lite/static/js/page-renderer.js` | `MAX_PAGE_CACHE=4` LRU eviction + `.cleanup()` (S1); `openLocal()` + `adoptCase(caseId)` (S2); idle worker warm-up + n±1 prefetch (S3); `warmThumbs()` sequential thumbnail warm (S4) |
| `lite/ui-lite.html` | `uploadPdf()` opens local bytes immediately via `PageRenderer.openLocal()`, backgrounds server upload, adopts case once it lands; server-gated features guarded during null-`caseId` window |
| `lite/tests/test_pagecache_lru.py` | NEW — `LITE_PAGECACHE_LRU_OK`, RED→GREEN |
| `lite/tests/test_local_open.py` | NEW — `LITE_LOCAL_OPEN_OK`, RED→GREEN |
| `lite/tests/test_warm_prefetch.py` | NEW — `LITE_WARM_PREFETCH_OK`, RED→GREEN |
| `lite/tests/test_thumb_warm.py` | NEW — `LITE_THUMB_WARM_OK` |
| `docs/status/PHASE_INDEX.md` | 4 sprint cards updated to ✅ done — via the perf-sprint pipeline |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED across all 4 sprints
- `.bmaplan` schema version stays 1; no schema fields touched (perf-only block, no new persisted state)

## Tests Run

```
python lite/tests/test_pagecache_lru.py   → LITE_PAGECACHE_LRU_OK   PASS (NEW, RED→GREEN)
python lite/tests/test_local_open.py      → LITE_LOCAL_OPEN_OK      PASS (NEW, RED→GREEN)
python lite/tests/test_warm_prefetch.py   → LITE_WARM_PREFETCH_OK   PASS (NEW, RED→GREEN)
python lite/tests/test_thumb_warm.py      → LITE_THUMB_WARM_OK      PASS (NEW)
```

Regression: Sprint 1 10/10, Sprint 2 10/10, Sprint 3 9/9, Sprint 4 8/8 — all green throughout, `MEASURE_PARITY_OK` green at every step. Lite suite now 67 files, all green. Proto E2E n/a (lite-only block; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; no fields touched
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched — Range-streaming (the one piece that would touch `page-renderer.js`'s buffer-ownership contract) deliberately left to the queued invent card
- ✅ `lite/ui-lite.html` stays under 1200-line cap; `page-renderer.js` well under 1000 lines
