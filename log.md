# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (BUG-20260702-lite-arc-summary / SLICE report-edit-1 + invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-07-02 — AUDIT-20260702-infra-bundle (runner-preflight + export-caps + render-engine review) — PASS (branch: main)

**What changed:** Same-day follow-on to the 2-bug measurement-accuracy audit (arc-summary + cfss-summary, both shipped earlier today). Three pieces of work, batched as one docs update: **Sprint A — AUDIT-20260702-runner-preflight** (commit `9c4c36e`): NEW `lite/tests/run_all_tests.py`, an aggregate test runner that discovers every `test_*.py` in `lite/tests/`, runs each standalone with a per-test timeout (default 420s), prints a summary table, and exits `LITE_RUN_ALL_OK`/`LITE_RUN_ALL_FAIL`. Options `--filter`/`--fail-fast`/`--timeout`. PREFLIGHT step fails fast on low disk (<2 GB on both the repo drive and the system drive — hardening from the 2026-07-02 `ENOSPC` incident where a full C: made Google Drive File Stream unable to hydrate any repo file, which had silently broken editing mid-session), missing `uvicorn`/`playwright`/`fitz`, or missing `node`. First full run: 60/60 tests PASS in 8.5 minutes (log at `artifacts/run_all_tests_20260702.log`). This closes the "no aggregate runner" gap flagged as follow-up item (4) in both audit bugs' `log.md` entries — previously every lite test had to be invoked individually, raising the risk of a silently-skipped regression test. **Sprint B — AUDIT-20260702-export-caps** (commit `60d424a`): `lite/server_lite.py` — S1: `/export-pdf-overlay` now validates the payload BEFORE rendering with 5 caps (`MAX_EXPORT_PAGES=2000`, `MAX_OBJECTS_PER_PAGE=500`, `MAX_ANNOTS_PER_PAGE=500`, `MAX_PTS_PER_OBJECT=2000`, `MAX_COORD_ABS=20000` — rejects NaN/inf coordinates), returning HTTP 400 with a detail message rather than silently truncating output or hanging; every cap set ≥10x the realistic worst case observed on the real 45-page permit PDF so no legitimate flow is blocked. Bonus find: this validation pass also fixes a latent HTTP 500 where a non-numeric page-key crashed `sorted(key=int)` before any cap check ran. S5: `/export-xlsx` gets a row cap `MAX_XLSX_ROWS=20000`. S2 (partial): `wb.save()` offloaded via `run_in_threadpool` — provably safe because it only touches pure local objects; the overlay-render offload was deliberately DEFERRED to a new card (`AUDIT-20260702-s2-fitz-lock`, filed below) because `/page/{n}` and `/thumb/{n}` are already `sync def` (threadpooled by FastAPI itself) and PyMuPDF `Document` objects are not thread-safe — naively wrapping the overlay-render endpoint the same way would allow concurrent `get_pixmap()` calls on the same `doc`, which is unsafe; the correct fix needs a per-case lock first. NEW `lite/tests/test_export_endpoints.py` (marker `LITE_EXPORT_ENDPOINTS_OK`, 14 checks) — the first real HTTP tests of either export endpoint (previously only client-side `dlPost` stubs existed, never exercising the server route): XLSX bytes are openable by `openpyxl` with sheet+row assertions, overlay output is a valid `%PDF` with the correct page count, oversize payloads (too many pages / points / objects) all return 400, malformed payloads (unknown `case_id`, non-numeric page key, a `1e12` coordinate) all return 400, and the XLSX row cap returns 400. The patch plan for both S1/S2/S5 was authored by an Opus reviewer agent (read-only) including a cap-justification table; the main agent applied the edits. **Review C — PDF render-engine accuracy review** (read-only, Opus agent; findings filed to `PHASE_INDEX.md`, zero code change): verdict is that the `PDFJS-VIEWPORT-CLIPPED` architecture (shipped 2026-05-28 via the `lite-pdf-render-quality` invent) is sound — the coordinate contract between the raster canvas and `ptToScreen`/`screenToPt` is algebraically exact when `V.rot` and `pgRot` are both 0 (residual ≈ ±0.5 device px, roughly 1 mm at working zoom or 30 mm at fit-to-page on a 1:100 A1 sheet — this is the click-precision floor of a mouse-driven canvas UI, not a measured-value error); intrinsic PDF `/Rotate` metadata is handled correctly; the stale-render token guard (`_renderToken`) is solid against race conditions; vector sharpness holds to roughly 4320 DPI effective, versus proto's fixed 108 DPI raster. The review surfaced one real BROKEN bug and filed one bundle of follow-up hardening cards (both below).

**Why:** The two audit bugs fixed earlier today (arc-summary, cfss-summary) both independently flagged "no all-tests runner exists" and "export caps not stress-tested" as follow-up risks in their own `log.md` entries — this sprint closes both gaps same-day while the context was still fresh, rather than letting them queue indefinitely. The render-engine review was prompted by the same audit's broader theme (silent correctness bugs that don't show up as crashes) — since `lite`'s render path was substantially rewritten in the 2026-05-28 PDF.js migration, a focused accuracy review of the coordinate contract was due, and it surfaced a real registration bug (page rotation) that no existing test guards.

**Files touched:**
- `lite/tests/run_all_tests.py`: NEW — aggregate test runner, discovers + runs every `test_*.py`, per-test timeout, summary table, `LITE_RUN_ALL_OK`/`FAIL`, `--filter`/`--fail-fast`/`--timeout` options, disk/dependency PREFLIGHT
- `lite/server_lite.py`: `/export-pdf-overlay` — pre-render payload validation (5 caps, HTTP 400 on violation, fixes latent 500 on non-numeric page key); `/export-xlsx` — `MAX_XLSX_ROWS=20000` row cap; `wb.save()` offloaded via `run_in_threadpool`
- `lite/tests/test_export_endpoints.py`: NEW — `LITE_EXPORT_ENDPOINTS_OK` (14 checks), first real HTTP tests of both export endpoints
- `docs/status/PHASE_INDEX.md`: bug `BUG-20260702-lite-pagerot-registration` filed + card `AUDIT-20260702-render-followups` filed + card `AUDIT-20260702-s2-fitz-lock` filed — already updated by the review/bug-filing step, not by this write

**Tests:**
```
python lite/tests/test_export_endpoints.py           → LITE_EXPORT_ENDPOINTS_OK  PASS (NEW, 14/14 checks)
python lite/tests/run_all_tests.py                    → LITE_RUN_ALL_OK          PASS (60/60 tests, 8.5 min, first full run)
```
Regression (partial full-suite run + targeted subset, both green): a partial full-suite pass covering 11 files, plus a targeted 9-file subset — `test_apply_page_mutations.py`, `test_pm_apply_flush_unified.py`, `test_metamorphic_pages.py`, `test_pdfjs_offline.py`, `test_summary_arc_parity.py`, `test_summary_cfss_parity.py`, `test_measure_parity.py`, `test_export_submenu.py`, `test_report.py` — all exit 0. `MEASURE_PARITY_OK` green confirms no vendored-math touch. Proto E2E n/a (lite-only sprint; zero `proto/` edits).

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `lite/static/js/measure-engine.js` (drift-locked vendored copy) UNCHANGED
- ✅ `.bmaplan` schema version stays 1; no schema fields touched
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ Export caps set ≥10x realistic worst case — no legitimate flow blocked; caps reject with clear HTTP 400, never silently truncate
- ✅ Review C is read-only — zero code changes; findings filed as tracked backlog cards, not applied directly

**Known gaps / follow-ups:**
- **BUG-20260702-lite-pagerot-registration (BROKEN, top priority, filed by Review C):** manual page rotate rotates the raster canvas but `ptToScreen`/`screenToPt` ignore `pgRot` — pre-existing geometry detaches from the visible plan by up to a page diagonal; geometry drawn while the page is rotated is stored bound to the un-rotated frame (correct area value, wrong on-screen location); export does not apply `pageRot` either. No test currently guards this. Needs `/bma-check-forbidden` before fixing — the fix likely touches `ptToScreen`/`screenToPt`, both coordinate-critical.
- **AUDIT-20260702-render-followups (bundle, filed by Review C):** (1) no fallback from PDF.js failure to the legacy `/page/{n}` JPEG raster path — canvas goes blank today if PDF.js fails to load/render; (2) pan uses a single shared `_offCanvas` double-buffer cleared before the async render completes — likely blanks the canvas mid-drag on slow renders; (3) no scanned-PDF detection — vector sharpness gain is real for vector PDFs but a raster-scanned PDF gets zero benefit and no messaging tells the user; (4) the "13 MB" memory footprint claim in existing docs excludes the whole-PDF resident buffer plus an unbounded `pageCache` — needs correction; (5) no real overlay-registration Playwright test exists — the render-quality spike's 24/24 PASS was measured within PDF.js's own coordinate space only, never cross-checked against `ptToScreen`.
- **AUDIT-20260702-s2-fitz-lock (filed by Sprint B):** the overlay-render offload for `/export-pdf-overlay` was deliberately deferred — needs a per-case `fitz` lock added first (PyMuPDF `Document` is not thread-safe) before the render step can safely move to a threadpool.
- Export PDF output is still a 108-DPI PyMuPDF raster (unchanged from proto) even though the on-screen canvas is now vector-sharp via PDF.js — noted by Review C as a follow-on, not filed as its own card yet.
- Older still-queued audit follow-on cards (calibration multi-sample / Verify-Scale port, `ptToScreen`/`screenToPt` into the drift-lock contract) remain queued below the 3 new items in `NEXT_ACTIONS.md`.

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

<!-- AUDIT-20260702-infra-bundle + BUG-20260702-lite-cfss-summary are the 2 sessions kept in this file -->
<!-- BUG-20260702-lite-arc-summary + SLICE report-edit-1 + invent lite-pdf-render-quality (resumed+completed) + invent lite-pdf-render-quality (paused) + BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 archived to docs/archive/log-2026-07-02.md on 2026-07-02 (AUDIT-20260702-infra-bundle sprint) -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
