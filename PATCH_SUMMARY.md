# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-arc-summary — Arc-edge polygon areas excluded from every rollup consumer

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

# Previous: SLICE report-edit-1 — Editable lite report

Branch: main

Date: 2026-06-05

## Outcome: PASS — Editable lite report shipped — vendored jspreadsheet-ce grid + custom Excel-style cell-click formula picker + stable-row-id subtotal mapper + NaN-guard; LITE_REPORT_EDIT_OK 7/7.

## Summary

New module `lite/static/js/report-edit.js` (404 LOC) wraps jspreadsheet-ce CE with a custom formula picker (cell-click-while-editing UX that CE lacks), a stable-row-id subtotal mapper (deleting a referenced row drops the term + raises a red flag instead of silently shifting), and render/persist/provenance helpers (stale detection, NaN-guard, localStorage v1). jspreadsheet-ce + jsuites vendored offline (~440 KB, MIT). `lite/lite-report.html` gains 46 lines for the override-overlay toggle and grid mount. Full test suite: LITE_REPORT_EDIT_OK 7/7. Zero proto/ edits; all forbidden surfaces untouched.

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

<!-- BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-arc-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
