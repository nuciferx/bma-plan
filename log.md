# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

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

## 2026-06-05 — SLICE report-edit-1 — Editable lite report — PASS (branch: main)

**What changed:** Shipped the editable lite report feature — the BUILD of invent Approach D3 from `docs/invent/lite-editable-report.md`. A new module `lite/static/js/report-edit.js` (404 LOC) wraps jspreadsheet-ce community edition with three sub-systems: (a) a custom Excel-style cell-click formula picker (~70 LOC) that hooks `oneditionstart`+`oncreateeditor`, activates picker mode on a leading "=", and injects `B<n>` refs via capture-phase mousedown; (b) a stable-row-id subtotal mapper (~60 LOC) — `rowIds[]` parallel array + `subMeta` semantic capture + `rebuildSubtotals()` re-projects formulas after structural mutations so deleting a row drops the term and raises a red flag rather than silently shifting references; (c) render/persist/provenance helpers (~160 LOC) — `baseline[]` for computed-vs-override stale detection (orange warning), NaN-guard that rejects non-numeric input and reverts to the previous value, and localStorage v1 persistence keyed by payload hash. `lite/lite-report.html` gained 46 lines of override-overlay toggle markup, grid mount, and four vendor `<script>`/`<link>` tags. jspreadsheet-ce + jsuites vendored offline (~440 KB minified, MIT) into `lite/static/js/vendor/` — CDN use forbidden after the pdfjs-cdn bug. A new skill `.claude/skills/lite-spike-iterate/SKILL.md` codifies the SPIKE→EVAL→fix loop after the sprint hit the 3rd-RESHAPE memory-escalation trigger. All prior tests GREEN; zero proto/ edits.

**Why:** The existing `lite/lite-report.html` report shipped read-only area cells (raw-geometry contract). Users need to add custom subtotals and override values for plan-submission documents. The /lite-invent pipeline went through 3 RESHAPE rounds (B raw contenteditable → D jspreadsheet CE → D2 custom cell-click picker → D3 stable-row-id mapper) before arriving at an approach that satisfied both the live-cell-click UX requirement (PRO-only in jss-CE → solved with custom picker) and the structural-mutation correctness requirement (positional B-refs → solved with rowIds[]).

**Files touched:**
- `lite/static/js/report-edit.js`: NEW 404 LOC — formula picker + stable-row-id mapper + render/persist/provenance + NaN-guard
- `lite/lite-report.html`: +46 lines — override-overlay toggle, grid mount, 4 vendor tags
- `lite/static/js/vendor/jspreadsheet.min.js`: NEW vendored MIT (jspreadsheet-ce)
- `lite/static/js/vendor/jspreadsheet.min.css`: NEW vendored MIT
- `lite/static/js/vendor/jsuites.min.js`: NEW vendored MIT (jsuites peer dep)
- `lite/static/js/vendor/jsuites.min.css`: NEW vendored MIT
- `lite/tests/test_report_edit.py`: NEW 245 LOC — 7-case Playwright marker LITE_REPORT_EDIT_OK
- `docs/invent/lite-editable-report.md`: NEW — full invent record (PICK/RESEARCH/FRAME/DIVERGE/SCORE/SPIKE + 3 RESHAPE sections)
- `.claude/skills/lite-spike-iterate/SKILL.md`: NEW — SPIKE→EVAL→fix iteration loop skill
- `docs/status/PHASE_INDEX.md`: +11 lines — 2 idea entries under ### ideas 2026-06-04
- `lite/sandbox/invent-lite-editable-report*.{html,py}`: NEW spike artifacts (5 HTML + 5 eval scripts)
- `lite/sandbox/vendor/*`: NEW vendor copies for sandbox reproducibility

**Tests:**
```
python lite/tests/test_report_edit.py  →  LITE_REPORT_EDIT_OK 7/7  PASS
```
Cases: PICKER regression =B1+B2→86.93 DOM-driven / STABLE delete-unreferenced re-projects =B1+B3→=B1+B2 value 76.61 / STABLE delete-referenced term dropped 50.45 red flag / STABLE multi-op =B1+B2+B3-B4 delete-ref re-project 66.61 / GUARD label-col click no A2 injection / PERSIST semantic subMeta survives save-reopen / NaN-GUARD "abc" reverts to 50.45. Zero page errors.
Proto py_compile + smoke + full NOT re-run: lite-only sprint, zero proto/ edits, no forbidden-trigger surface touched.

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto untouched entirely)
- ✅ `lite/static/js/measure-engine.js` (drift-locked vendored copy) unchanged
- ✅ `.bmaplan` schema — no change at all; persistence = localStorage v1 only
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR
- ✅ `lite/ui-lite.html` untouched (stays at cap)
- ✅ Size caps: report-edit.js 404/1000 ✅

**Known gaps / follow-ups:**
- Print-to-PDF CSS needs re-validation: grid replaces the contenteditable report wholesale so `@page` CSS for the jss grid renderer needs a dedicated print sprint
- ~440 KB vendored payload doubles lite static size (accepted cost per invent doc, but should be noted for future LITE-7 PyInstaller build)
- jss-CE positional NaN-eval is guarded at the input layer only, not at the library layer — if jss internally coerces a formula to NaN, the guard may not catch it
- Grid is currently behind the `#re-toggle` dev gate; needs a production wire-up sprint before shipping to users

---

<!-- BUG-20260702-lite-arc-summary + SLICE report-edit-1 are the 2 sessions kept in this file -->
<!-- invent lite-pdf-render-quality (resumed+completed) + invent lite-pdf-render-quality (paused) + BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 archived to docs/archive/log-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-arc-summary sprint) -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
