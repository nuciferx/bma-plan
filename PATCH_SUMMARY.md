# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review

Branch: main

Date: 2026-07-02

## Outcome: PASS — Same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit (both bugs already shipped earlier today). Sprint A (`9c4c36e`): NEW aggregate `lite/tests/run_all_tests.py` with disk/dependency PREFLIGHT (hardened after the 2026-07-02 ENOSPC incident) — first full run 60/60 PASS in 8.5 min. Sprint B (`60d424a`): `/export-pdf-overlay` + `/export-xlsx` now validate payloads BEFORE rendering (5 caps, HTTP 400 on violation, no silent truncation; fixes a latent 500 as a bonus); NEW `test_export_endpoints.py` (`LITE_EXPORT_ENDPOINTS_OK` 14/14) is the first real HTTP test of either export endpoint. Review C (read-only, Opus): render-engine coordinate contract verdict SOUND for `V.rot`/`pgRot`=0, but surfaces a real BROKEN bug — `BUG-20260702-lite-pagerot-registration` (manual page rotation desyncs stored geometry from the raster) — plus a follow-up hardening bundle, both filed to `PHASE_INDEX.md`, no code applied.

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

<!-- BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (AUDIT-20260702-infra-bundle sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
