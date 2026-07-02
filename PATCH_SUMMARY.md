# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

Branch: main

Date: 2026-07-02

## Outcome: PASS — Four same-day lite perf sprints driven by an empirical probe (`artifacts/perf/probe_results_20260702.txt`): page-cache LRU (commit `ae0f168`, CHH heap 766→~628 MB), local-first open (commit `3ec9239`, paint before server upload lands, removes the ~80ms/MB upload wait from the critical path), worker warm-up + adjacent prefetch (commit `e0fb856`, hides the flat ~1.2s PDF.js boot cost + instant page-switch), sequential thumbnail warm (commit `a0c1152`, overview grid opens hot without concurrent `fitz` pressure). Probe also REFUTED pan-blanking (0/10 across 3 files) and found the "overview thumbs 0/0" report was a probe selector artifact (real: 45/45 in 9.2s cold). All 4 guard tests RED→GREEN (or new), regression 10/10 + 10/10 + 9/9 + 8/8, `MEASURE_PARITY_OK` green throughout. Lite suite now 67 files, all green. Only remaining perf piece (doc-level memory) is correctly routed to the `PERF-20260702-open-streaming` invent card, not attempted here.

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

---

# Previous: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

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

<!-- AUDIT-20260702-infra-bundle archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
