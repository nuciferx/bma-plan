# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: BUG-20260702-lite-cfss-summary — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Fixed bug 2 of 2 from the 2026-07-02 measurement-accuracy audit. CFSS (cross-floor shared shapes) instances — `{kind:'instance', masterId, offsetPt}`, no `.pts`, no `.catId` — were skipped by every area rollup, so promoting a polygon into a shared shape silently REMOVED its area from all totals. Triage widened this to a CRASH finding: `buildExportData` and `exportPdfOverlay` called `catOf(o.catId).name`/`.color` BEFORE the `kind` guard, throwing `TypeError` on any page holding an instance — XLSX and annotated-PDF export crashed outright, not just under-counted. Root cause: `cfssCommitPromote` called `addMaster()` without the `opts` arg, so masters never captured `catId`/`semanticTag`. Fixed by passing `{catId, semanticTag}` into `addMaster` at promote time (additive schema, free persistence via existing masters serialization) plus new `rollupAreaM2`/`rollupCatId` dispatch helpers used at all 6 rollup sites — replacing the "swap the callee 6 times" pattern from bug 1 with a single reusable helper, per that bug's postmortem lesson. New guard test proves the bug was real (RED, totals 2000 instead of 2100, exports threw) and the fix is complete (GREEN, all 6 consumers agree, exports do not throw). Legacy pre-fix `.bmaplan` saves degrade safely (instance skipped + one-time warning, no crash). Both bugs from the 2026-07-02 audit are now shipped.

## What was delivered

- `lite/static/js/cross-floor-shapes.js` — `cfssCommitPromote` now passes `{catId, semanticTag}` to `addMaster`; NEW `rollupAreaM2(o,pg)` + `rollupCatId(o)` dispatch helpers
- 6 rollup sites rewired: `computeSummary` (`ui-lite.html:1049`), `buildExportData`, `exportPdfOverlay`, `buildReportPayload` (`export-annotate.js`), `_ltOwnArea` (`layer-tree.js`), `_lovsLayerArea` (`overview-setup.js`)
- 2 crash sites fixed: `catOf` resolution moved after `catId` resolution, made null-safe, in `buildExportData` + `exportPdfOverlay`
- `lite/tests/test_summary_cfss_parity.py` (NEW) — `LITE_SUMMARY_CFSS_OK` guard test, exercises the REAL promote flow, proven RED→GREEN
- `lite/tests/bug-archive.jsonl` — entry appended (fixed_commit `02e35af`) via the bug-report pipeline
- `docs/status/PHASE_INDEX.md` — row updated to ✅ done via the bug-report pipeline
- Shipped as commit `02e35af` on `main`

## What's next

- Both bugs from the 2026-07-02 measurement-accuracy audit are SHIPPED. File the remaining audit findings as queued cards: (1) calibration relies on a single sample point with no multi-point averaging safety net — port Verify-Scale to lite; (2) export payload size caps not stress-tested against very large multi-page projects — add real export-endpoint tests; (3) `ptToScreen`/`screenToPt` sit outside the drift-lock contract despite being coordinate-critical — fold into the parity-locked set; (4) no single "run all lite tests" runner exists — each test file is invoked individually; (5) no free-space preflight check before large exports/renders.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track. This closes the 2-bug audit initiated 2026-07-02 (bug 1 = `BUG-20260702-lite-arc-summary`, commits `e5264e2`+`e1a8e1c`; bug 2 = this sprint, commit `02e35af`). Bug-report pipeline (triage → specialist patch plan on Opus → fix → regression → this write-up) ran end-to-end without a stop-condition. No forbidden surface touched; no Phase 2 scope crossed. Next sprint: file the 5 remaining audit follow-on findings as individually scoped cards.

---

# Previous: BUG-20260702-lite-arc-summary — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Fixed a silent measurement-accuracy bug: arc-edge polygon areas were correct on the per-object canvas label but wrong in EVERY downstream rollup — summary panel, XLSX export, annotated-PDF overlay, report, layer totals, and site-setup rollup all under-counted curved rooms because 6 call sites dropped `o.edges` when calling the area function. Fixed by swapping all 6 sites to the arc-aware `polyMetricsAnyShape`. A new guard test proves the bug was real (RED on pre-fix code) and that the fix is complete (GREEN post-fix, all 6 consumers now agree with the canvas label). Zero edits to the drift-locked vendored geometry engine; non-arc measurements are byte-identical to before. Bug 1 of 2 from the 2026-07-02 measurement-accuracy audit — bug 2 (CFSS shared-shape instances excluded from totals) shipped next as `BUG-20260702-lite-cfss-summary`.

## What was delivered

- `lite/ui-lite.html:1049`, `lite/static/js/export-annotate.js:14/27/58`, `lite/static/js/layer-tree.js:62`, `lite/static/js/overview-setup.js:642` — 6 callee swaps: `polyMetrics({pts:o.pts})` → `polyMetricsAnyShape(o,pg)`
- `lite/tests/test_summary_arc_parity.py` (NEW) — `LITE_SUMMARY_ARC_OK` guard test, independent closed-form fixture, proven RED→GREEN across the fix
- `lite/tests/bug-archive.jsonl` — entry appended (fixed_commit `e5264e2`, status `fixed`) via the bug-report pipeline
- `docs/status/PHASE_INDEX.md` — row updated to ✅ done via the bug-report pipeline
- Shipped as commit `e5264e2` on `main`

## What's next

- **(1)** `BUG-20260702-lite-cfss-summary` — CFSS shared-shape instances have no `.pts` of their own, so `computeSummary` skips them entirely; promoting a shared shape removes its source polygon from totals with no replacement. SHIPPED same day (see Latest above).
- **(2)** File the remaining 2026-07-02 measurement-accuracy audit findings as queued cards: calibration single-sample risk, export payload size stress-testing, `ptToScreen` outside the drift-lock contract, no all-tests runner for lite.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track. Part of a 2-bug audit initiated 2026-07-02; this is bug 1 of 2. Bug-report pipeline (triage → specialist review widened scope from 4 to 6 sites → fix → regression → this write-up) ran end-to-end without a stop-condition. No forbidden surface touched; no Phase 2 scope crossed.

---

<!-- SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
