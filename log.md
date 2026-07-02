# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (SLICE report-edit-1 + invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-07-02 — BUG-20260702-lite-cfss-summary — PASS (branch: main)

**What changed:** Fixed bug 2 of 2 from the 2026-07-02 measurement-accuracy audit (bug 1 = `BUG-20260702-lite-arc-summary`, shipped earlier today, commits `e5264e2` + `e1a8e1c`). CFSS (cross-floor shared shapes) instances — objects of shape `{kind:'instance', masterId, offsetPt}` with no `.pts` and no `.catId` of their own — were skipped by every area rollup, so promoting a polygon to a shared shape silently REMOVED its area from all totals. Triage widened this to a CRASH sub-finding: `buildExportData` and `exportPdfOverlay` called `catOf(o.catId).name`/`.color` BEFORE the `kind` guard, throwing `TypeError` on any page holding an instance — XLSX and annotated-PDF export crashed outright, not just under-counted. Root cause: `cfssCommitPromote` called `addMaster()` without the `opts` arg, so masters never captured `catId`/`semanticTag` in the first place. Fix (commit `02e35af` on `main`): (1) promote now passes `{catId, semanticTag}` into `addMaster` — additive master schema field, persists for free via the existing masters serialization in `cfssWrapSave`/`cfssWrapLoad`; legacy pre-fix masters (saved before this fix) have no `catId` → `rollupCatId` returns `null` → instance is skipped from bucket totals safely with a one-time `console.warn`, no crash, no migration UI required. (2) New helpers `rollupAreaM2(o,pg)` + `rollupCatId(o)` added in `cross-floor-shapes.js` next to the existing `instanceAreaM2` (single dispatch helper instead of re-deriving the same kind-branch 6 times at each call site — the direct postmortem lesson from the arc-summary bug's 6 near-duplicate call sites); both helpers are `typeof`-guarded at every consumer because `cross-floor-shapes.js` is dynamically injected AFTER `layer-tree.js`/`export-annotate.js` load, so the guard is load-order-mandatory, not defensive boilerplate. (3) Rewired 6 rollup sites to use the new helpers and fixed the 2 crash sites: `computeSummary` (`ui-lite.html:1049`, line-neutral), `buildExportData`, `exportPdfOverlay` (instances now export as resolved-pts poly overlays with area labels via `resolveInstancePts`, `catOf` moved after `catId` resolution and made null-safe), `buildReportPayload` (instances included in rows/subtotal/net), `_ltOwnArea` (`layer-tree.js`), `_lovsLayerArea` (`overview-setup.js`). Patch plan authored by `bma-path-geometry-reviewer` running on Opus (user-requested model override).

**Why:** Bug 1 of the 2026-07-02 audit fixed arc-edge areas being wrong in rollups; this bug is the same failure class (a whole geometry representation silently excluded from totals) but with an added CRASH severity — shared-shape instances are a core CFSS feature (draw once, reuse across floors), so any project using them could not export at all. User-facing measurement accuracy and export reliability are both load-bearing for a Phase 1 raster measurement assistant.

**Files touched:**
- `lite/static/js/cross-floor-shapes.js`: `cfssCommitPromote` now passes `{catId, semanticTag}` to `addMaster`; NEW `rollupAreaM2(o,pg)` + `rollupCatId(o)` dispatch helpers co-located with `instanceAreaM2`
- `lite/ui-lite.html:1049`: `computeSummary` — rewired to `rollupAreaM2`/`rollupCatId` (typeof-guarded), line-neutral
- `lite/static/js/export-annotate.js`: `buildExportData` — rewired + crash fix (catOf moved after catId resolution, null-safe); `exportPdfOverlay` — same crash fix, instances export as resolved-pts poly overlays via `resolveInstancePts`; `buildReportPayload` — instances included in rows/subtotal/net
- `lite/static/js/layer-tree.js`: `_ltOwnArea` — rewired to rollup helpers
- `lite/static/js/overview-setup.js`: `_lovsLayerArea` — rewired to rollup helpers
- `lite/tests/test_summary_cfss_parity.py`: NEW — `LITE_SUMMARY_CFSS_OK` guard test, exercises the REAL promote flow (`__cfssTestPromote`), asserts all 6 consumers report ground truth 2100 m² (2000 plain + 100 instance) and both export builders do not throw; proven RED on pre-fix code via `git stash` (totals 2000, `master_has_catId` false, `edThrew`/`ovThrew` true)
- `lite/tests/bug-archive.jsonl`: entry appended (fixed_commit `02e35af`) — already updated by the bug-report pipeline, not by this write
- `docs/status/PHASE_INDEX.md`: row updated to ✅ done — already updated by the bug-report pipeline, not by this write

**Tests:**
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
14/14 exit 0. Proto E2E NOT re-run — lite-only change, zero `proto/` edits, no forbidden-trigger surface touched in proto (no-test rationale for the proto side).

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `lite/static/js/measure-engine.js` (drift-locked vendored copy) UNCHANGED
- ✅ `.bmaplan` schema version stays 1; master `catId`/`semanticTag` is additive; unknown keys already carried forward on load (zero persistence-layer edits needed)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/ui-lite.html` stays under cap (line-neutral edit)
- ✅ MEASURE_SCOPE_OK verdict (geometry-core + export-impact + additive schema, atomic, not split)

**Known gaps / follow-ups:**
- Legacy pre-fix `.bmaplan` saves with masters lacking `catId` keep instances out of bucket totals (safe, warned via one-time `console.warn`, documented) — a migration helper could be a future COSMETIC card.
- Server `/export-pdf-overlay` draw path for instance-as-poly overlays verified only via payload shape, not a rendered-PDF pixel check.
- Both bugs from the 2026-07-02 measurement-accuracy audit are now SHIPPED. Remaining audit findings still to be filed as queued cards: (1) calibration relies on a single sample point with no multi-point averaging safety net, (2) export payload size caps not stress-tested against very large multi-page projects, (3) `ptToScreen`/`screenToPt` sit outside the drift-lock contract despite being coordinate-critical, (4) no single "run all lite tests" runner exists, (5) no free-space preflight check before large exports/renders.

---

## 2026-07-02 — BUG-20260702-lite-arc-summary — PASS (branch: main)

**What changed:** Fixed a silent measurement-accuracy bug in lite where arc-edge polygon areas were correct in the per-object canvas label (`areaOf`, which uses `polyMetricsAnyShape`) but wrong in EVERY rollup consumer downstream — summary panel, XLSX export rows + summary sheet, annotated-PDF overlay labels, report rows/subtotal/net, layer-panel per-layer totals, and site-setup layer rollup. Root cause: 6 call sites passed `{pts:o.pts}` (a bare-pts stub, dropping `o.edges`) into `polyMetrics`, which computes the straight-chord polygon area instead of the arc-corrected area. Fix swaps the callee to `polyMetricsAnyShape(o,pg)` at all 6 sites: `lite/ui-lite.html:1049` (`computeSummary`), `lite/static/js/export-annotate.js:14` (`buildExportData`), `:27` (`exportPdfOverlay`), `:58` (`buildReportPayload`), `lite/static/js/layer-tree.js:62` (`_ltOwnArea`), `lite/static/js/overview-setup.js:642` (`_lovsLayerArea`). Zero edits to the drift-locked vendored `measure-engine.js`; `polyMetricsAnyShape` falls through to `polyMetrics` for non-arc polygons, so behavior for every non-arc object is byte-identical to before. Bug was found by `bma-bug-triager` (4 of the 6 sites) then widened to 6 by `bma-path-geometry-reviewer` specialist review (caught the 2 layer-panel sites). New guard test `lite/tests/test_summary_arc_parity.py` (marker `LITE_SUMMARY_ARC_OK`) asserts the invariant "every rollup consumer == Σ areaOf labels (arc-inclusive)" across all 6 consumers, using an independent closed-form fixture (10000 + 1250π ≈ 13926.99 m² arc room + plain 2000 m² room). Proven RED on pre-fix code via `git stash` (old code returned chord totals of 12000 while the per-object label still showed the correct 10000 for the arc room alone) then GREEN after the fix. Shipped as commit `e5264e2` on `main`.

**Why:** User-facing measurement accuracy is the single most load-bearing property of this app (Phase 1 = raster measurement assistant). Curved rooms (any polygon using `o.edges` arc segments) were silently under-counted in every summary/export/report path while looking correct on the canvas — the worst kind of bug because there was no error, warning, or visual signal; only the final numbers were wrong. This is bug 1 of 2 filed from the 2026-07-02 measurement-accuracy audit; bug 2 (`BUG-20260702-lite-cfss-summary` — CFSS shared-shape instances excluded from totals) runs next via `/bma-bug-report`.

**Files touched:**
- `lite/ui-lite.html:1049`: `computeSummary` — `polyMetrics({pts:o.pts})` → `polyMetricsAnyShape(o,pg)`
- `lite/static/js/export-annotate.js:14`: `buildExportData` — same callee swap
- `lite/static/js/export-annotate.js:27`: `exportPdfOverlay` — same callee swap
- `lite/static/js/export-annotate.js:58`: `buildReportPayload` — same callee swap
- `lite/static/js/layer-tree.js:62`: `_ltOwnArea` — same callee swap (found by specialist review, not triage)
- `lite/static/js/overview-setup.js:642`: `_lovsLayerArea` — same callee swap (found by specialist review, not triage)
- `lite/tests/test_summary_arc_parity.py`: NEW — `LITE_SUMMARY_ARC_OK` guard test, independent closed-form fixture, proven RED→GREEN across the fix
- `lite/tests/bug-archive.jsonl`: entry appended (fixed_commit `e5264e2`, status `fixed`) — already updated by the bug-report pipeline, not by this write
- `docs/status/PHASE_INDEX.md`: row updated to ✅ done — already updated by the bug-report pipeline, not by this write

**Tests:**
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
All exit 0. Proto `py_compile + smoke + full` NOT re-run — lite-only change, zero `proto/` edits, no forbidden-trigger surface touched in proto (no-test rationale for the proto side).

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged (callee swap only, no edits to the functions themselves)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `lite/static/js/measure-engine.js` (drift-locked vendored copy) UNCHANGED
- ✅ `.bmaplan` schema version stays 1; no schema fields touched
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ `lite/ui-lite.html` stayed within line cap (callee swap only, net-zero lines; cap 1,154/1,200)
- ✅ MEASURE_SCOPE_OK verdict (geometry-core + export-impact, same single defect, atomic — not split)

**Known gaps / follow-ups:**
- **BUG-20260702-lite-cfss-summary** (queued next, same audit): CFSS shared-shape instances have no `.pts` of their own → skipped entirely by `computeSummary` → promoting a shared shape removes its source polygon from totals with no replacement. Runs next via `/bma-bug-report`.
- Broader 2026-07-02 measurement-accuracy audit findings still to be filed as queued cards: (1) calibration relies on a single sample point with no multi-point averaging safety net, (2) export payload size caps not stress-tested against very large multi-page projects, (3) `ptToScreen` sits outside the drift-lock contract despite being coordinate-critical, (4) no single "run all lite tests" runner exists — each test file is invoked individually, raising the risk of a silently-skipped regression test.

---

<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary are the 2 sessions kept in this file -->
<!-- SLICE report-edit-1 + invent lite-pdf-render-quality (resumed+completed) + invent lite-pdf-render-quality (paused) + BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 archived to docs/archive/log-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint) -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
