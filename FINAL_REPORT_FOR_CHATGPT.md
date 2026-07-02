# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: BLOCK-20260703-clear-queue — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. Five same-session ships, cleared back-to-back overnight under a user directive to close out the entire remaining queue ("ทำทั้งหมด"). **Ship 1 — `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`):** per-case `threading.Lock` now serializes all `fitz.Document` access in `lite/server_lite.py`, including moving `/export-pdf-overlay`'s render off the event loop entirely (completing the S2 threadpool goal deferred from `AUDIT-20260702-infra-bundle`). NEW `LITE_CASE_LOCK_OK` hammer test (96 requests / 8 threads / mid-flight doc-swap / concurrent overlay export), zero 5xx — honestly recorded as a hardening test, not a deterministic RED-before-fix proof, since native races are probabilistic. **Ship 2 — render-followups (a)+(c) (`aec375b`):** PDF.js-unavailable no longer blanks the canvas (falls back to server JPEG raster); scanned/image-only pages get a capped re-render scale (saves wasted CPU, zero accuracy change) plus a one-time hint. **Ship 3 (`13054b6`):** tiered test runner (`--tier t0/t1/t2`, part of the new V2 migration blueprint), and — most notably — the first PIXEL-level proof (not just exact-inverse math) that the raster canvas and exported overlay stay registered (max offset 0.50 device px), closing an evidence gap the 2026-05-28 render-quality spike never closed. Range-streaming research was also completed and correctly HALTED at the human decision checkpoint rather than shipped, per this project's invention discipline. **Ship 4 — `ACC-20260703-verify-scale-port` (`bea2119`):** ported Verify-Scale from proto to lite, closing the single remaining accuracy gap vs. Foxit identified by the 2026-07-02 competitive comparison. **Ship 5:** wrote down the day's operating lessons as two new process docs (`DEVELOPMENT_PILLARS.md`, `DEVELOPMENT_V2_BLUEPRINT.md`) before they were lost. Full lite test suite validated at 70/70 files green (grown from 60 across the two days); `MEASURE_PARITY_OK` stayed green through every ship. Zero `proto/` edits across the whole block.

## What was delivered

- `lite/server_lite.py` — per-case `_case_lock` guarding all `fitz.Document` access; `/export-pdf-overlay` now threadpool-offloaded (Ship 1)
- `lite/ui-lite.html` — raster fallback when PDF.js fails to load (Ship 2); new Verify Scale menu item + `Shift+S` shortcut, +3 net lines (Ship 4)
- render module — scanned-page detection + capped re-render scale with transform compensation (Ship 2)
- `lite/tests/run_all_tests.py` — `--tier t0/t1/t2` flag, `t0` (measure math) runs in 1.26s (Ship 3)
- `lite/tests/test_overlay_registration.py` (NEW) — pixel-level raster↔overlay registration proof, `LITE_OVERLAY_REG_OK` (Ship 3)
- `docs/invent/lite-range-streaming.md` (NEW) — Range-streaming research, verdict `PRIOR_ART_PARTIAL`, HALTED at human checkpoint (Ship 3)
- `lite/static/js/verify-scale.js` (NEW, 225 lines) — ported from proto's `INV-2026-05-20-001` (Ship 4)
- `docs/process/DEVELOPMENT_PILLARS.md` + `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` (NEW) — process doctrine (Ship 5)
- 5 NEW guard tests total: `LITE_CASE_LOCK_OK` / `LITE_RENDER_FB_SCAN_OK` / (tier flag, no dedicated marker) / `LITE_OVERLAY_REG_OK` / `LITE_VERIFY_SCALE_OK`
- Shipped as commits `d0a5dde` + `aec375b` + `13054b6` + `bea2119` + `16e6495` + `b676652` on `main`

## What's next

- **(1) HUMAN DECISION: Range-streaming spike GO/NOGO/RESHAPE** (`docs/invent/lite-range-streaming.md`) — the only item in the whole cleared queue still awaiting anything, and it specifically awaits a human call, not more agent work.
- **(2) V2 migration continuation** — `INVARIANTS.md` (U1), roadmap split + reconcile (U4), `SHIPS.jsonl` ledger (U3) remain queued from `docs/process/DEVELOPMENT_V2_BLUEPRINT.md`; the tiered test runner (U2) is partially landed via Ship 3.
- **(3) `ptToScreen`/`screenToPt` into the parity fixture** — last drift-lock nicety carried over from `BUG-20260702-lite-pagerot-registration`.
- **(4) Stale `PHASE_INDEX.md` rows** — `lpm-1..9` show `queued` but `bug-archive.jsonl` says fixed; needs a reconciliation pass.

## Position in Plan

Phase 1 — BMA-Plan Lite epic. This block spans three tracks at once: reliability hardening (fitz lock), rendering robustness (fallback + scan detection + registration proof), and measurement-accuracy parity with the competitive benchmark (Verify-Scale port) — plus capturing the day's process lessons as durable doctrine. With the queue now cleared, the only forward motion pending is the human GO/NOGO decision on Range-streaming; everything else is either shipped or explicitly queued for a future sprint. No forbidden surface touched.

---

# Previous: PERF-20260702-lite-foxit-smoothness — PASS

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

- **(1) `PERF-20260702-open-streaming` (queued invent, `/lite-invent`)** — the only remaining perf piece. CHH's remaining ~600 MB doc-level heap needs Range-streaming (`PDFDataRangeTransport`), which touches the page-renderer's buffer-ownership contract and has documented quirks — correctly routed to the invent pipeline. **(Resolved by BLOCK-20260703-clear-queue Ship 3: research complete, HALTED at human checkpoint.)**
- **(2) `AUDIT-20260702-render-followups` remainder** — pdfjs-fail → JPEG fallback, scanned-PDF detection messaging, memory-claim doc correction, real overlay-registration Playwright test. Pan double-buffer item is CLOSED-no-bug per this block's probe. **(Resolved by BLOCK-20260703-clear-queue Ships 2+3.)**
- **(3) `AUDIT-20260702-s2-fitz-lock`** — per-case PyMuPDF lock needed before Sprint 4's thumbnail warm (or the overlay-render step) can safely go concurrent. **(Resolved by BLOCK-20260703-clear-queue Ship 1.)**
- **(4) Calibration multi-sample / Verify-Scale port to lite** — accuracy gap vs. Foxit, unrelated to this perf block. **(Resolved by BLOCK-20260703-clear-queue Ship 4.)**
- **(5) `ptToScreen`/`screenToPt` parity-fixture addition** — remains queued from the pagerot-registration sprint. **(Still queued after BLOCK-20260703-clear-queue.)**

## Position in Plan

Phase 1 — BMA-Plan Lite epic, performance hardening track ("Foxit-grade open smoothness"). Closes the four highest-leverage perf gaps identified by the same-day empirical probe: open ~0.5-1.5s any size, page switch perceived-instant, zoom/pan at par, overview hot, memory page-level bounded. Doc-level memory (Range-streaming) is the one remaining piece, deliberately deferred to the invent pipeline rather than risked same-day. No forbidden surface touched.

---

<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
