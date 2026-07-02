# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: PERF-20260702-lite-foxit-smoothness — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Four same-day lite performance sprints, driven by an empirical perf probe (`artifacts/perf/probe_results_20260702.txt`) that measured real cold-open cost on RAMA4 (18.3 MB, 3.9s first-paint), CHH (90.8 MB real customer file, 9.6s first-paint + 766 MB heap after 10 pages), and found a flat ~1.2s PDF.js library+worker boot floor on every open. The probe also showed `UPLOAD` dominates at ~80ms/MB while `/raw` is nearly free, REFUTED a standing pan-blanking suspicion (0/10 across 3 files), and found the "overview thumbs 0/0" report was a probe selector artifact (real: 45/45 in 9.2s cold). Four sprints closed the highest-leverage, lowest-risk gaps this exposed: (1) page-cache LRU (`ae0f168`) — `MAX_PAGE_CACHE=4` with `.cleanup()` eviction, CHH heap 766→~628 MB (−18%); (2) local-first open (`3ec9239`) — paint happens on local bytes before the server upload lands, `/raw` never fetched, removes the dominant upload wait from the critical path on real binders; (3) worker warm-up + adjacent prefetch (`e0fb856`) — the flat 1.2s PDF.js boot is hidden behind idle time, page switches skip the worker round-trip; (4) sequential thumbnail warm (`a0c1152`) — overview grid opens hot, deliberately sequential (not parallel) pending the still-queued per-case `fitz` lock. All 4 guard tests RED→GREEN (or new), regression 10/10 + 10/10 + 9/9 + 8/8, `MEASURE_PARITY_OK` green throughout — zero vendored-math touch. Lite suite now 67 files, all green.

## What was delivered

- `lite/static/js/page-renderer.js` — `MAX_PAGE_CACHE=4` LRU eviction (S1); `openLocal()` + `adoptCase()` (S2); idle worker warm-up + n±1 prefetch (S3); `warmThumbs()` sequential thumbnail warm (S4)
- `lite/ui-lite.html` — `uploadPdf()` opens local bytes immediately, backgrounds server upload, adopts case once it lands
- `lite/tests/test_pagecache_lru.py`, `test_local_open.py`, `test_warm_prefetch.py`, `test_thumb_warm.py` (all NEW) — `LITE_PAGECACHE_LRU_OK` / `LITE_LOCAL_OPEN_OK` / `LITE_WARM_PREFETCH_OK` / `LITE_THUMB_WARM_OK`
- `docs/status/PHASE_INDEX.md` — 4 sprint cards updated to ✅ done via the perf-sprint pipeline
- Shipped as commits `ae0f168` + `3ec9239` + `e0fb856` + `a0c1152` on `main`

## What's next

- **(1) `PERF-20260702-open-streaming` (queued invent, `/lite-invent`)** — the only remaining perf piece. CHH's remaining ~600 MB doc-level heap needs Range-streaming (`PDFDataRangeTransport`), which touches the page-renderer's buffer-ownership contract and has documented quirks — correctly routed to the invent pipeline.
- **(2) `AUDIT-20260702-render-followups` remainder** — pdfjs-fail → JPEG fallback, scanned-PDF detection messaging, memory-claim doc correction, real overlay-registration Playwright test. Pan double-buffer item is CLOSED-no-bug per this block's probe.
- **(3) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before Sprint 4's thumbnail warm (or the overlay-render step) can safely go concurrent.
- **(4) Calibration multi-sample / Verify-Scale port to lite** — accuracy gap vs. Foxit, unrelated to this perf block.
- **(5) `ptToScreen`/`screenToPt` parity-fixture addition** — remains queued from the pagerot-registration sprint.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, performance hardening track ("Foxit-grade open smoothness"). Closes the four highest-leverage perf gaps identified by the same-day empirical probe: open ~0.5-1.5s any size, page switch perceived-instant, zoom/pan at par, overview hot, memory page-level bounded. Doc-level memory (Range-streaming) is the one remaining piece, deliberately deferred to the invent pipeline rather than risked same-day. No forbidden surface touched.

---

# Previous: BUG-20260702-lite-pagerot-registration — PASS

**Date:** 2026-07-02
**Branch:** main

## Outcome

PASS. Fixed the top-priority BROKEN bug filed earlier today by the `AUDIT-20260702-infra-bundle` render-engine accuracy review. Manual page rotation (`pageRot`) rotated the PDF.js raster canvas but the coordinate contract `ptToScreen`/`screenToPt` ignored `pgRot` (`getRot()` was hardcoded to 0) — pre-existing geometry detached from the visible plan by up to a page diagonal (~84 m at 1:100 A1), geometry drawn while a page was rotated stored bound to the wrong feature (correct area value, wrong location — the classic "right value, wrong location" measurement bug), and `/export-pdf-overlay` never applied `pageRot` at all. Intrinsic PDF `/Rotate` was always correct — only manual rotate was broken. Fixed by commit `9f4b298` ("Fix A — proto-parity" over "Fix B — geometry-baking", per an Opus specialist patch plan): `getRot()` now returns the real per-page rotation; `ptToScreen`/`screenToPt` route through the vendored, parity-tested `pdfToC`/`cToPdf` rotation branches (net 0 lines, zero geometry mutation, no migration); `/export-pdf-overlay` now prerotates the raster and maps all coordinates through a new `_rp` helper. New guard test `LITE_PAGEROT_REG_OK` proven RED→GREEN; 42 distinct regression files green.

## What was delivered

- `lite/static/js/measure-engine.js` — `getRot()` host contract function now returns `pageRot[pg]||0`
- `lite/ui-lite.html` — `ptToScreen`/`screenToPt` rewired through vendored rotation-aware `pdfToC`/`cToPdf`, net 0 lines
- `lite/static/js/export-annotate.js` — export payload includes per-page rotation
- `lite/server_lite.py` — `/export-pdf-overlay` prerotates raster + maps coordinates via new `_rp` helper
- `lite/tests/test_pagerot_registration.py` (NEW) — `LITE_PAGEROT_REG_OK` guard test, RED→GREEN proven
- `docs/status/PHASE_INDEX.md` — row updated to ✅ done via the bug-report pipeline
- Shipped as commit `9f4b298` on `main`

## What's next

- **(1) `AUDIT-20260702-render-followups` bundle** — pdfjs-fail → JPEG fallback / pan double-buffer blanking / scanned-PDF detection messaging / memory-claim correction / real overlay-registration Playwright test (item (e) would add visual coverage for the combined `V.rot≠0` + `pgRot≠0` case, still only exact-inverse-tested).
- **(2) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before the overlay-render step of `/export-pdf-overlay` can safely move to a threadpool.
- **(3) Calibration multi-sample / Verify-Scale port to lite** — the 2026-07-02 Foxit comparison identified this as the single remaining accuracy gap vs. competitors.
- **(4) `ptToScreen`/`screenToPt` into the drift-lock parity fixture** — partially resolved by this fix (runtime now routes through the vendored kernel); remaining work is only adding the functions themselves to `test_measure_parity.py`.

## Position in Plan

Phase 1 — BMA-Plan Lite epic, measurement-accuracy hardening track, render-registration sub-track. This closes the top-priority BROKEN bug filed same-day by `AUDIT-20260702-infra-bundle`'s render-engine accuracy review, resolving the last real correctness gap left by the 2026-05-28 PDF.js render migration. No forbidden surface touched.

---

<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
