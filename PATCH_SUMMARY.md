# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

Branch: main

Date: 2026-07-02

## Outcome: PASS — Fixed the top-priority BROKEN bug filed earlier today by the AUDIT-20260702-infra-bundle render-engine accuracy review. Manual page rotation (`pageRot`) rotated the PDF.js raster canvas but `ptToScreen`/`screenToPt` ignored `pgRot` (`getRot()` hardcoded to 0) — pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1), geometry drawn while rotated bound itself to the wrong feature, and `/export-pdf-overlay` never applied `pageRot` either. Fixed (commit `9f4b298`, "Fix A — proto-parity" over "Fix B — geometry-baking"): `getRot()` now returns `pageRot[pg]||0`; `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches (net 0 lines, zero geometry mutation, no migration needed); server `/export-pdf-overlay` now prerotates the raster and maps every coordinate through a new `_rp` helper mirroring `pdfToC`. New guard test `LITE_PAGEROT_REG_OK` proven RED→GREEN; 16 at-risk regression files + 26 more from a partial full-suite run = 42 distinct files green.

## Summary

Fixed `BUG-20260702-lite-pagerot-registration`, filed BROKEN/top-priority earlier today by the `AUDIT-20260702-infra-bundle` render-engine accuracy review (Review C). Manual page rotate (`pageRot`) rotated the PDF.js `getViewport({rotation: V.rot + pgRot})` raster, but the coordinate contract `ptToScreen`/`screenToPt` ignored `pgRot` entirely — `getRot()` was hardcoded to return 0. Effect: pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1) on manual rotate; geometry drawn WHILE a page was rotated stored bound to the un-rotated frame (correct area value, wrong on-screen location — a "right value, wrong location" bug); `/export-pdf-overlay` did not apply `pageRot` at all, so exported PDFs never matched the screen when `pgRot≠0`. Intrinsic PDF `/Rotate` was always correct — only manual rotate was broken. The vendored rotation-aware `pdfToC`/`cToPdf` already existed in `measure-engine.js` (drift-locked, parity-tested) but were dead code at runtime. Fix (commit `9f4b298`, "Fix A — proto-parity", chosen over "Fix B — geometry-baking" by an Opus specialist patch plan): (1) `getRot()` (host contract function, editable per `measure-engine.js`'s own header) now returns `pageRot[pg]||0`; (2) `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches — net 0 lines in `ui-lite.html`, zero user-geometry mutation, no undo interaction, no float drift, old `.bmaplan` files (which already persisted `pageRotations`) just start rendering correctly with no migration; side effect: closes the "un-vendored coordinate math" drift-lock gap flagged by the same audit — lite runtime coords now run through the tested kernel; (3) export WYSIWYG: `export-annotate.js` sends per-page rotation, server `/export-pdf-overlay` prerotates the raster via `Matrix(RS,RS).prerotate(rot)` and maps all coordinates (objects, labels, annotations) through a new `_rp` helper mirroring `pdfToC` — prerotate direction verified EMPIRICALLY against all 4 angles with a standalone pixel test before wiring it in. Fix B (transform stored points at rotate time) rejected: mutates ~6 geometry stores, needs undo snapshotting, causes float drift on repeated rotate, and needs a save-format migration the additive-only schema can't express. New guard test `lite/tests/test_pagerot_registration.py` (marker `LITE_PAGEROT_REG_OK`) covers 4-angle mapping vs. closed-form transform, exact-inverse round-trip, area invariance under rotate, real save/load round-trip, and export dimension/pixel checks — proven RED on pre-fix code via `git stash`, GREEN after.

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

Regression: 16 at-risk files green (`test_page_rotate.py`, `test_metamorphic_pages.py`, `test_snap_types.py`, `test_arc_edge.py`, `test_ortho.py`, `test_cfss_drag.py`, `test_cfss_ui.py`, `test_centerline_snap.py`, `test_annot_label.py`, `test_live_overlay.py`, `test_measure_parity.py`, `test_pbt_measure.py`, `test_export_endpoints.py`, `test_summary_arc_parity.py`, `test_summary_cfss_parity.py`, `test_pagerot_registration.py`) + 26 more files green from a partial `run_all_tests.py` pass = 42 distinct files green. `MEASURE_PARITY_OK` green confirms the drift-locked vendored math is untouched. Proto E2E n/a (lite-only sprint; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged (routed through, not edited)
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `.bmaplan` schema version stays 1; `pageRotations` already persisted, zero migration needed
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ MEASURE_SCOPE_OK equivalent (inline check): `ptToScreen`/`screenToPt` are lite-owned, not forbidden, but are the de-facto coordinate contract — heavy regression run and green
- ✅ Prerotate direction verified empirically with a standalone pixel test before wiring into the export endpoint

---

# Previous: AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review

Branch: main

Date: 2026-07-02

## Outcome: PASS — Same-day follow-on to the 2-bug 2026-07-02 measurement-accuracy audit (both bugs already shipped earlier today). Sprint A (`9c4c36e`): NEW aggregate `lite/tests/run_all_tests.py` with disk/dependency PREFLIGHT (hardened after the 2026-07-02 ENOSPC incident) — first full run 60/60 PASS in 8.5 min. Sprint B (`60d424a`): `/export-pdf-overlay` + `/export-xlsx` now validate payloads BEFORE rendering (5 caps, HTTP 400 on violation, no silent truncation; fixes a latent 500 as a bonus); NEW `test_export_endpoints.py` (`LITE_EXPORT_ENDPOINTS_OK` 14/14) is the first real HTTP test of either export endpoint. Review C (read-only, Opus): render-engine coordinate contract verdict SOUND for `V.rot`/`pgRot`=0, but surfaces a real BROKEN bug — `BUG-20260702-lite-pagerot-registration` (manual page rotation desyncs stored geometry from the raster) — plus a follow-up hardening bundle, both filed to `PHASE_INDEX.md`, no code applied. **This bug SHIPPED same-day — see Latest above.**

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

<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
