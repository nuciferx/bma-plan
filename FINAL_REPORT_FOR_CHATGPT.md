# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: AUDIT-20260702-infra-bundle — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit (both bugs already shipped earlier today, see Previous below). Three pieces batched into one docs update. **Sprint A (`9c4c36e`, AUDIT-20260702-runner-preflight):** NEW aggregate `lite/tests/run_all_tests.py` — discovers + runs every `test_*.py` with per-test timeout, summary table, `LITE_RUN_ALL_OK`/`FAIL`; PREFLIGHT fails fast on low disk (<2 GB, hardened after the 2026-07-02 ENOSPC incident) or missing dependencies. First full run: 60/60 PASS in 8.5 min. **Sprint B (`60d424a`, AUDIT-20260702-export-caps):** `/export-pdf-overlay` and `/export-xlsx` now validate payloads BEFORE rendering (5 caps, HTTP 400, no silent truncation, ≥10x realistic worst case; bonus fix for a latent 500). NEW `test_export_endpoints.py` (`LITE_EXPORT_ENDPOINTS_OK` 14/14) is the first real HTTP test of either export endpoint. **Review C (read-only, Opus agent):** render-engine coordinate contract verdict SOUND for the common case, but surfaces a real BROKEN bug (`BUG-20260702-lite-pagerot-registration` — manual page rotation desyncs stored geometry from the raster) plus a hardening bundle, both filed to `PHASE_INDEX.md` with zero code applied.

## What was delivered

- `lite/tests/run_all_tests.py` (NEW) — aggregate test runner with disk/dependency PREFLIGHT
- `lite/server_lite.py` — export payload validation caps on `/export-pdf-overlay` + `/export-xlsx`; `wb.save()` offloaded via `run_in_threadpool`
- `lite/tests/test_export_endpoints.py` (NEW) — first real HTTP tests of both export endpoints, `LITE_EXPORT_ENDPOINTS_OK` 14/14
- `docs/status/PHASE_INDEX.md` — `BUG-20260702-lite-pagerot-registration` (BROKEN) + `AUDIT-20260702-render-followups` (bundle) + `AUDIT-20260702-s2-fitz-lock` filed by Review C / Sprint B
- Shipped as commits `9c4c36e` + `60d424a` on `main`

## What's next

- **(1, top priority) `BUG-20260702-lite-pagerot-registration`** — manual page rotate desyncs stored geometry from the raster because `ptToScreen`/`screenToPt` ignore `pgRot`. Needs `/bma-check-forbidden` first — fix likely touches coordinate-critical functions.
- **(2) `AUDIT-20260702-render-followups` bundle** — pdfjs-fail → JPEG fallback / pan double-buffer blanking / scanned-PDF detection messaging / memory-claim correction / real overlay-registration Playwright test.
- **(3) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before the overlay-render step of `/export-pdf-overlay` can safely move to a threadpool.
- Older queued audit follow-ons (calibration multi-sample, `ptToScreen`/`screenToPt` into the drift-lock set) remain queued below the 3 new items.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track, test/render infrastructure sub-track. Direct same-day follow-on to the 2-bug audit (arc-summary + cfss-summary, both shipped earlier 2026-07-02). No forbidden surface touched by Sprint A/B; Review C is read-only. `BUG-20260702-lite-pagerot-registration` is now the top of the queue — a real, previously-unguarded correctness bug in the 2026-05-28 PDF.js render migration.

---

# Previous: BUG-20260702-lite-cfss-summary — PASS

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

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track. This closes the 2-bug audit initiated 2026-07-02 (bug 1 = `BUG-20260702-lite-arc-summary`, commits `e5264e2`+`e1a8e1c`; bug 2 = this sprint, commit `02e35af`). Bug-report pipeline (triage → specialist patch plan on Opus → fix → regression → this write-up) ran end-to-end without a stop-condition. No forbidden surface touched; no Phase 2 scope crossed. Both items (2) and (4) of "what's next" here are now SHIPPED same-day by `AUDIT-20260702-infra-bundle` (see Latest above).

---

<!-- BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (AUDIT-20260702-infra-bundle sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
