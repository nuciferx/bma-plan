# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-cfss-summary — CFSS shared-shape instances excluded from every rollup consumer + export crash

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

<!-- SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
