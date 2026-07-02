# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (BUG-20260702-lite-cfss-summary / BUG-20260702-lite-arc-summary / SLICE report-edit-1 + invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard / AUDIT-20260702-infra-bundle)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-07-02 — PERF-20260702-lite-foxit-smoothness (4-sprint block: page-cache LRU + local-first open + worker warm-up/prefetch + thumbnail warm) — PASS (branch: main)

**What changed:** Four same-day lite performance sprints, driven by an empirical perf probe (`artifacts/perf/probe_results_20260702.txt`) that measured real cold-open cost on three files: RAMA4 (18.3 MB) first-paint 3.9s cold, CHH (90.8 MB real customer file) 9.6s first-paint + 766 MB heap after 10 pages viewed, and a flat ~1.2s PDF.js library+worker boot floor present on every open regardless of file size. The probe's time-attribution also showed `UPLOAD` dominates at ~80ms/MB while the `/raw` fetch itself is nearly free, and it REFUTED (0/10 across 3 files) a standing suspicion that panning blanks the canvas mid-drag; a reported "overview thumbnails 0/0" finding turned out to be a probe selector artifact — the real number is 45/45 thumbnails in 9.2s cold (~200ms/thumb), instant warm. **Sprint 1 — page-cache LRU (commit `ae0f168`):** `lite/static/js/page-renderer.js` gets `MAX_PAGE_CACHE=4` with LRU eviction; an evicted `PDFPageProxy` gets `.cleanup()` called only when no remaining alias key still references it; the currently-rendering page (`curPage`) is never evicted; `getPage()` transparently re-fetches on a cache miss. Measured: cache key count dropped 12→4, CHH heap dropped 766→~628 MB (−18%). The remaining ~600 MB is PDF.js document-level shared state (fonts, XObjects) that page-level eviction cannot reach — explicitly left to the queued Range-streaming invent card rather than attempted here. NEW guard `lite/tests/test_pagecache_lru.py` (`LITE_PAGECACHE_LRU_OK`), proven RED pre-fix, 10/10 regression. **Sprint 2 — local-first open (commit `3ec9239`):** `uploadPdf()` in `lite/ui-lite.html` now opens the locally-selected file's bytes immediately via `PageRenderer.openLocal()` — first paint happens before the server upload even starts — while the server upload runs in the background; `PageRenderer.adoptCase(caseId)` later binds the returned `case_id` so `/raw` is NEVER fetched (the client already has the bytes). Server-gated features (case-dependent endpoints) are guarded during the null-`caseId` window: `openOv` is a no-op, exports alert instead of silently failing. The direct-HTTP-upload path used by every other existing test is preserved unchanged. Measured: paint at 475ms with upload still in flight; on a real 91 MB binder this removes the dominant ~80ms/MB upload wait from the critical path (roughly 7.5s → ~1-2s to first paint). NEW guard `lite/tests/test_local_open.py` (`LITE_LOCAL_OPEN_OK` — paint-before-upload ordering, feature gate, adoption, zero `/raw` fetches, post-adoption page switch still works), proven RED pre-fix, 10/10 regression. **Sprint 3 — worker warm-up + adjacent prefetch (commit `e0fb856`):** the flat ~1.2s PDF.js library+worker boot cost is now preloaded at app idle via `requestIdleCallback` (`window.__pdfjsWarmed` flag) so it's paid once during idle time instead of on the critical path of the first page open; after `loadPage(n)` completes, the `n±1` `PDFPageProxy` is fetched at idle time too, so forward/back page switches skip the worker round-trip entirely; prefetched pages count toward the `MAX_PAGE_CACHE` budget from Sprint 1, and `curPage` stays LRU-protected. NEW guard `lite/tests/test_warm_prefetch.py` (`LITE_WARM_PREFETCH_OK`), proven RED pre-fix, 9/9 regression. **Sprint 4 — sequential thumbnail warm (commit `a0c1152`):** `PageRenderer.warmThumbs()` fetches `/thumb/1..N` sequentially with 120ms gaps between requests after the upload lands, so the page-overview grid opens already-hot; deliberately sequential (not a parallel burst) — both to avoid repeating the `lpm-8` lesson (parallel bursts overwhelm the server) and because the shared `fitz` `Document` per case is not thread-safe (the `AUDIT-20260702-s2-fitz-lock` card is still queued, so no concurrent `get_pixmap()` pressure is safe yet). Token-cancelled on `resetCache()`/new upload so a stale warm doesn't race a fresh session. NEW guard `lite/tests/test_thumb_warm.py` (`LITE_THUMB_WARM_OK` — all pages warmed exactly once, ≥60ms sequential gaps proven, mid-run cancellation works), 8/8 regression.

**Why:** The empirical probe made clear that BMA-Plan Lite's open experience on large real customer PDFs (CHH at 90.8 MB, 9.6s to first paint) was far behind the "Foxit-grade smoothness" bar this block explicitly targets, and pinpointed exactly where the time goes (upload transfer, not `/raw`, not the render itself) and where memory goes (page cache size, not a leak) rather than guessing. Fixing the four highest-leverage, lowest-risk items same-day — bounded page cache, paint-before-upload, idle-time worker warm-up + adjacent prefetch, and hot thumbnails — closes every perf gap that does NOT require touching the page-renderer's buffer-ownership contract or wrestling with `PDFDataRangeTransport`'s quirks; those two remaining, riskier pieces (Range-streaming for doc-level memory) are deliberately left to the invent pipeline (`PERF-20260702-open-streaming`) rather than rushed into a same-day sprint.

**Files touched:**
- `lite/static/js/page-renderer.js`: `MAX_PAGE_CACHE=4` LRU eviction + `.cleanup()` on evicted pages (Sprint 1); `openLocal()` + `adoptCase(caseId)` (Sprint 2); `requestIdleCallback` worker warm-up (`window.__pdfjsWarmed`) + adjacent n±1 prefetch (Sprint 3); `warmThumbs()` sequential thumbnail warm with token-cancel (Sprint 4)
- `lite/ui-lite.html`: `uploadPdf()` now opens local bytes immediately via `PageRenderer.openLocal()`, backgrounds the server upload, adopts the case once it lands; server-gated features (`openOv`, exports) guarded during the null-`caseId` window
- `lite/tests/test_pagecache_lru.py`: NEW — `LITE_PAGECACHE_LRU_OK`, RED pre-fix
- `lite/tests/test_local_open.py`: NEW — `LITE_LOCAL_OPEN_OK`, RED pre-fix
- `lite/tests/test_warm_prefetch.py`: NEW — `LITE_WARM_PREFETCH_OK`, RED pre-fix
- `lite/tests/test_thumb_warm.py`: NEW — `LITE_THUMB_WARM_OK`
- `artifacts/perf/probe_results_20260702.txt`: empirical perf probe results that drove this block's scoping (reference artifact, not sprint output)
- `docs/status/PHASE_INDEX.md`: 4 sprint cards updated to ✅ done — via the perf-sprint pipeline, not this write

**Tests:**
```
python lite/tests/test_pagecache_lru.py   → LITE_PAGECACHE_LRU_OK   PASS (NEW, RED→GREEN)
python lite/tests/test_local_open.py      → LITE_LOCAL_OPEN_OK      PASS (NEW, RED→GREEN)
python lite/tests/test_warm_prefetch.py   → LITE_WARM_PREFETCH_OK   PASS (NEW, RED→GREEN)
python lite/tests/test_thumb_warm.py      → LITE_THUMB_WARM_OK      PASS (NEW)
```
Regression: Sprint 1 10/10, Sprint 2 10/10, Sprint 3 9/9, Sprint 4 8/8 — all green throughout the block, including `MEASURE_PARITY_OK` at every step (zero vendored-math touch across all four sprints). Full lite test suite now stands at 67 files, all green. `lite/ui-lite.html` stays under its 1200-line cap; `lite/static/js/page-renderer.js` stays well under 1000 lines. Proto E2E n/a — lite-only block, zero `proto/` edits.

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `lite/static/js/measure-engine.js` drift-locked vendored math unchanged across all four sprints
- ✅ `.bmaplan` schema version stays 1; no schema fields touched (perf-only block, no new persisted state)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched: `page-renderer.js` buffer-ownership contract was deliberately NOT touched by Range-streaming (left to the queued invent card)

**Known gaps / follow-ups:**
- **PERF-20260702-open-streaming (queued invent, `/lite-invent`)** — the only remaining perf piece. CHH's remaining ~600 MB doc-level heap (fonts/XObjects, PDF.js document-level shared state) is not reachable by page-level cache eviction; needs Range-streaming (`PDFDataRangeTransport`) which touches the page-renderer's buffer-ownership contract and has documented quirks — correctly routed to the invent pipeline rather than a same-day sprint.
- `AUDIT-20260702-render-followups` remainder still open: pdfjs-fail → JPEG fallback, scanned-PDF detection, memory-claim doc correction, real overlay-registration Playwright test. The pan double-buffer item from that bundle is CLOSED-no-bug — this block's probe empirically refuted pan-blanking 0/10 across 3 files.
- `AUDIT-20260702-s2-fitz-lock` still queued — Sprint 4's thumbnail warm was deliberately kept sequential specifically because this per-case PyMuPDF lock doesn't exist yet.
- Verify-Scale port to lite (accuracy gap vs. Foxit) remains queued, unrelated to this perf block.
- `ptToScreen`/`screenToPt` parity-fixture addition remains queued from the pagerot-registration sprint.

---

## 2026-07-02 — BUG-20260702-lite-pagerot-registration — PASS (branch: main)

**What changed:** Fixed `BUG-20260702-lite-pagerot-registration` (BROKEN, top priority, filed earlier today by the Review C render-engine accuracy review during `AUDIT-20260702-infra-bundle`). Manual page rotation (`pageRot`) rotated the PDF.js raster canvas (`getViewport({rotation: V.rot + pgRot})`) but the coordinate contract `ptToScreen`/`screenToPt` ignored `pgRot` entirely — `getRot()` was hardcoded to return 0. Effect: pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1) whenever a user manually rotated a page; geometry drawn WHILE a page was rotated got stored bound to the un-rotated frame — correct area value, wrong on-screen location, the classic "right value, wrong location" measurement bug; `/export-pdf-overlay` did not apply `pageRot` at all, so exported annotated PDFs never matched what the user saw on screen whenever `pgRot≠0`. Intrinsic PDF `/Rotate` metadata was always handled correctly — only the manual rotate-page menu path was broken. The vendored rotation-aware `pdfToC`/`cToPdf` rotation branches already existed in `measure-engine.js` (drift-locked, parity-tested) but were dead code at runtime because the live `ptToScreen`/`screenToPt` in `ui-lite.html` never routed through them. Fix (commit `9f4b298`, "Fix A — proto-parity"; chosen over "Fix B — geometry-baking" by an Opus specialist patch plan): (1) `getRot()` (a host contract function, explicitly editable per `measure-engine.js`'s own header) now returns `pageRot[pg]||0` instead of a hardcoded 0; (2) `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches — net 0 lines added to `ui-lite.html` (stays within the ~1128/1200 cap), zero user-geometry mutation, no undo interaction, no float drift, and old `.bmaplan` files (which already persisted `pageRotations`) simply start rendering correctly with no migration step; (3) side effect: closes the "un-vendored coordinate math" drift-lock gap flagged by the 2026-07-02 audit — lite runtime coords now run through the tested vendored kernel; (4) export WYSIWYG: `export-annotate.js` now sends the per-page rotation with the export payload, and the server `/export-pdf-overlay` prerotates the raster via `Matrix(RS,RS).prerotate(rot)` and maps every coordinate (objects, labels, annotations) through a new `_rp` helper mirroring `pdfToC` — the prerotate direction was verified EMPIRICALLY against all 4 angles with a standalone pixel test BEFORE wiring it into the endpoint. Fix B (transform stored points at rotate time) was rejected: it would mutate ~6 different geometry stores, require new undo snapshotting, introduce float drift on repeated rotate operations, and need a save-format migration the additive-only `.bmaplan` schema cannot express.

**Why:** A "right value, wrong location" bug is the most dangerous class of measurement error for a raster PDF measurement assistant — the reported area/length numbers stay correct while the on-screen geometry silently drifts off the feature it was measuring, so nothing looks visibly wrong until a user compares against the plan. Filed as top priority (BROKEN) by the same-day render-engine accuracy review; fixing it same-day keeps the audit's momentum and closes the last real correctness gap left by the 2026-05-28 PDF.js render migration.

**Files touched:**
- `lite/static/js/measure-engine.js`: host contract function `getRot()` only (not the drift-locked vendored math) — now returns `pageRot[pg]||0` instead of hardcoded 0
- `lite/ui-lite.html`: `ptToScreen`/`screenToPt` rewired to route through the vendored rotation-aware `pdfToC`/`cToPdf` branches — net 0 lines
- `lite/static/js/export-annotate.js`: export payload now includes per-page rotation
- `lite/server_lite.py`: `/export-pdf-overlay` — raster prerotated via `Matrix(RS,RS).prerotate(rot)`; new `_rp` coordinate-mapping helper (mirrors `pdfToC`) applied to objects/labels/annotations
- `lite/tests/test_pagerot_registration.py`: NEW — guard test, marker `LITE_PAGEROT_REG_OK`, proven RED on pre-fix code via `git stash`
- `lite/tests/bug-archive.jsonl`: entry appended (fixed_commit `9f4b298`) — via the bug-report pipeline, not this write
- `docs/status/PHASE_INDEX.md`: row updated to ✅ done — via the bug-report pipeline, not this write

**Tests:**
```
python lite/tests/test_pagerot_registration.py → LITE_PAGEROT_REG_OK  PASS (NEW)
```
5 checks: (i) 4-angle screen-coordinate mapping vs. a closed-form quadrant transform; (ii) `screenToPt` is the exact inverse of `ptToScreen` (tolerance 1e-9); (iii) area is invariant under rotate (confirms stored points are never mutated); (iv) `pageRotations` round-trip through a real `loadProto` save/load cycle; (v) export: output page dimensions swap correctly (600×450) and stroke pixels are found at the expected rotated vertex (585,15). Proven RED on pre-fix code via `git stash`: pre-fix mapped to (15,15) instead of (585,15), `rotRestored` was false, export output was un-rotated 450×600.

Regression: 16 at-risk files green — `test_page_rotate.py`, `test_metamorphic_pages.py`, `test_snap_types.py`, `test_arc_edge.py`, `test_ortho.py`, `test_cfss_drag.py`, `test_cfss_ui.py`, `test_centerline_snap.py`, `test_annot_label.py`, `test_live_overlay.py`, `test_measure_parity.py`, `test_pbt_measure.py`, `test_export_endpoints.py`, `test_summary_arc_parity.py`, `test_summary_cfss_parity.py`, `test_pagerot_registration.py` — plus 26 more files green from a partial `run_all_tests.py` pass. Total: 42 distinct files green. `MEASURE_PARITY_OK` green confirms `measure-engine.js`'s drift-locked vendored math is untouched (only the host contract `getRot()` changed). Proto E2E n/a — lite-only sprint, zero `proto/` edits.

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged (routed through, not edited)
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only sprint)
- ✅ `lite/static/js/measure-engine.js` drift-locked vendored math unchanged — only the host contract function `getRot()` (explicitly editable per the file's own header) was changed
- ✅ `.bmaplan` schema version stays 1; `pageRotations` was already persisted, zero migration needed
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ MEASURE_SCOPE_OK equivalent (inline check): `ptToScreen`/`screenToPt` are lite-owned, not forbidden, but are the de-facto coordinate contract — heavy regression run and green
- ✅ Prerotate direction verified empirically with a standalone pixel test before wiring into the export endpoint

**Known gaps / follow-ups:**
- Combined `V.rot≠0` AND `pgRot≠0` is asserted only via exact-inverse round-trip, not raster-pixel alignment — per specialist analysis, `fit()`'s corner-min absorbs the translation. The queued `AUDIT-20260702-render-followups` bundle item (e) "real overlay-registration Playwright test" remains open and would add visual coverage for this combined case.
- `lite/static/js/page-rotate.js` has a stale comment claiming the server handles rotation via `?rot=N` — actually client-side PDF.js rotation. Noted but not edited this sprint (out of scope for a bug fix).
- `ptToScreen`/`screenToPt` themselves are still not literally inside the `test_measure_parity.py` fixture — this fix routes them through the vendored kernel at runtime, but adding them to the parity fixture directly is separate remaining work.

---

<!-- PERF-20260702-lite-foxit-smoothness + BUG-20260702-lite-pagerot-registration are the 2 sessions kept in this file -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/log-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary + SLICE report-edit-1 + invent lite-pdf-render-quality (resumed+completed) + invent lite-pdf-render-quality (paused) + BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 archived to docs/archive/log-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
