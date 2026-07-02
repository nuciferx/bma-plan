# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md) · [docs/archive/patch-history-2026-07-02.md](docs/archive/patch-history-2026-07-02.md)

---

# Latest: BLOCK-20260703-clear-queue — 5-ship "ทำทั้งหมด" session (fitz lock, render fallback+scan, V2 tiers/overlay-proof/streaming-research, Verify-Scale port, process docs)

Branch: main

Date: 2026-07-03

## Outcome: PASS — Five same-session ships clearing the entire remaining queue per user directive "ทำทั้งหมด" (2026-07-02 night → 2026-07-03). Ship 1 `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`): per-case `threading.Lock` serializing all `fitz.Document` access, incl. moving `/export-pdf-overlay` render off the event loop; hammer-test guard `LITE_CASE_LOCK_OK`, zero 5xx across 96 concurrent requests. Ship 2 render-followups a+c (`aec375b`): raster fallback when PDF.js unavailable + scanned-page detection with capped re-render scale; `LITE_RENDER_FB_SCAN_OK` 6/6. Ship 3 (`13054b6`): tiered test runner (V2 blueprint U2), NEW pixel-level `LITE_OVERLAY_REG_OK` registration proof (max offset 0.50 px), and Range-streaming research HALTED at human checkpoint per Pack H. Ship 4 `ACC-20260703-verify-scale-port` (`bea2119`): Verify-Scale ported from proto, closing the last known accuracy gap vs. Foxit; `LITE_VERIFY_SCALE_OK` 7/7. Ship 5 (`16e6495`+`b676652`): `DEVELOPMENT_PILLARS.md` + `DEVELOPMENT_V2_BLUEPRINT.md` process docs. Full lite suite validated at 70/70 files green (grew 60→70 across the two days); `MEASURE_PARITY_OK` green throughout. Zero `proto/` edits.

## Summary

Five same-session ships, run back-to-back overnight under a user directive to clear the entire remaining queue in one sitting. **Ship 1 — `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`):** a per-case `threading.Lock` (`_case_lock`) in `lite/server_lite.py` now serializes all `fitz.Document` access — `/page` + `/thumb` (double-checked cache), `/pageinfo`, and the whole `/export-pdf-overlay` render path (now also moved off the event loop via `run_in_threadpool` around a new `_render_overlay` helper, completing the S2 threadpool goal deferred by `AUDIT-20260702-infra-bundle`), plus copy/close/swap critical sections of apply-page-mutations + merge-pages. Urgency raised by `PERF-20260702-lite-foxit-smoothness` Sprint 4's thumbnail warm making concurrent `/thumb`+`/page` traffic routine. NEW `lite/tests/test_case_lock.py` (`LITE_CASE_LOCK_OK`): 96-request 8-thread hammer + mid-flight doc-swap mutation + concurrent overlay export, zero 5xx — an honest hardening-hammer test, not a deterministic RED-before-fix proof (native races are probabilistic). Regression 9/9. **Ship 2 — render-followups (a)+(c) (`aec375b`):** (a) raster fallback — PDF.js unavailable no longer blanks the canvas; `loadPage` falls back to server JPEG (`/pageinfo`+`/page?rot`) drawn through the same view transform, with an `instanceof` guard keeping legacy shims safe; measurement stays fully functional. (c) scanned-page detection — an operator-list heuristic (free, post-render) flags image-only pages; re-render scale capped at `RS*4` (~432 DPI) with transform compensation so registration is bit-identical, saving only wasted re-raster CPU; one-time Thai hint. NEW `lite/tests/test_render_fallback_scanned.py` (`LITE_RENDER_FB_SCAN_OK`, 6 checks); 2 false alarms traced to the test harness itself and fixed there. Regression 8/8. **Ship 3 — V2 tiers + overlay proof + streaming research (`13054b6`):** (i) `run_all_tests.py --tier t0/t1/t2` (V2 blueprint U2) — `t0` measure-math-via-Node runs in 1.26 s, hitting the <5 s target; (ii) NEW `lite/tests/test_overlay_registration.py` (`LITE_OVERLAY_REG_OK`), built by a delegated agent and independently re-run — the first PIXEL-level raster↔overlay registration proof (max offset 0.50 px at zoom×2, 0.33 px at fit, 0.40 px at `pageRot=90°`, tolerance 4), the evidence the 2026-05-28 render-quality spike never produced; (iii) `docs/invent/lite-range-streaming.md` — Range-streaming research (`bma-researcher`): `PRIOR_ART_PARTIAL` verdict, key risks (PDF.js worker-heap bug #10730, untested `Blob.slice` transport, unknown customer-PDF linearization, `/raw` may already support Range), 5-step spike design + GO/NOGO criteria — **HALTED at the human checkpoint per Pack H, no code shipped for this piece by design.** **Ship 4 — `ACC-20260703-verify-scale-port` (`bea2119`):** Verify-Scale ported from proto's `INV-2026-05-20-001` — the single remaining accuracy gap vs. Foxit identified by the 2026-07-02 comparison. NEW `lite/static/js/verify-scale.js` (225 lines): 2-point verify capture reusing the calibration pipeline, %deviation banding (green/yellow/red), accept/recalibrate/average actions, additive `PS[pg].scale.verifyResult` riding the existing `calibScale` serialization. `lite/ui-lite.html` +3 net lines (menu item, `state.verifyMode` routing, `Shift+S`); `menu-flyout.js` +2 lines. Built by `lite-builder` subagent, independently verified. NEW `lite/tests/test_verify_scale.py` (`LITE_VERIFY_SCALE_OK`, 7 checks incl. save/load round-trip + average-re-derives-areas). **Ship 5 — process docs (`16e6495`+`b676652`):** `docs/process/DEVELOPMENT_PILLARS.md` (6-pillar doctrine + incident evidence + halt conditions) and `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` (6 weaknesses → 6 structural upgrades + migration order + success bar); U2 migration step partially landed via Ship 3. **Final validation:** full lite suite — 70 files, 70/70 green — run in chunks (17+27+26) after background runs kept getting killed; `artifacts/run_all_tests_20260703_final.log` covers the first 17; `MEASURE_PARITY_OK` green throughout every ship; suite grew 60→70 files across the two days.

## Files Changed

| File | Change |
|---|---|
| `lite/server_lite.py` | Ship 1 — `_case_lock` wraps all `fitz.Document` access incl. `/export-pdf-overlay` via new `_render_overlay` + `run_in_threadpool` |
| `lite/tests/test_case_lock.py` | NEW (Ship 1) — `LITE_CASE_LOCK_OK`, 96-request 8-thread hammer, zero 5xx |
| `lite/ui-lite.html` | Ship 2 — `loadPage()` raster fallback to server JPEG; Ship 4 — +3 net lines (Verify Scale menu item, verify-mode routing, `Shift+S`) |
| render module (page-renderer) | Ship 2 — scanned-page heuristic + `RS*4` capped re-render scale + transform compensation |
| `lite/tests/test_render_fallback_scanned.py` | NEW (Ship 2) — `LITE_RENDER_FB_SCAN_OK`, 6 checks |
| `lite/tests/run_all_tests.py` | Ship 3 — `--tier t0/t1/t2` flag (V2 blueprint U2) |
| `lite/tests/test_overlay_registration.py` | NEW (Ship 3) — `LITE_OVERLAY_REG_OK`, pixel-level registration proof |
| `docs/invent/lite-range-streaming.md` | NEW (Ship 3) — Range-streaming research, HALTED at human checkpoint |
| `lite/static/js/verify-scale.js` | NEW (Ship 4) — 225 lines, ported from proto `INV-2026-05-20-001` |
| `lite/static/js/menu-flyout.js` | Ship 4 — +2 lines, picks up new menu item |
| `lite/tests/test_verify_scale.py` | NEW (Ship 4) — `LITE_VERIFY_SCALE_OK`, 7 checks |
| `docs/process/DEVELOPMENT_PILLARS.md` | NEW (Ship 5) — 6-pillar doctrine |
| `docs/process/DEVELOPMENT_V2_BLUEPRINT.md` | NEW (Ship 5) — 6 weaknesses → 6 upgrades + migration order |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED (lite-only block; zero proto/ edits)
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `lite/static/js/measure-engine.js` drift-locked vendored math — UNCHANGED across all 5 ships
- `.bmaplan` schema version stays 1; only additive field this block is `PS[pg].scale.verifyResult` (Ship 4, mirrors proto's already-shipped equivalent)
- `docs/status/PHASE_INDEX.md` / `lite/tests/bug-archive.jsonl` — deliberately NOT touched by this docs-batching write

## Tests Run

```
python lite/tests/test_case_lock.py               → LITE_CASE_LOCK_OK          PASS (NEW; hardening hammer, not deterministic RED proof)
python lite/tests/test_render_fallback_scanned.py → LITE_RENDER_FB_SCAN_OK     PASS (NEW, 6 checks)
python lite/tests/run_all_tests.py --tier t0       → t0 in 1.26s (<5s target)  PASS
python lite/tests/test_overlay_registration.py    → LITE_OVERLAY_REG_OK       PASS (NEW, pixel-level proof)
python lite/tests/test_verify_scale.py            → LITE_VERIFY_SCALE_OK      PASS (NEW, 7 checks)
python lite/tests/run_all_tests.py                → 70/70 files green (chunked: 17 + 27 + 26)
```

`MEASURE_PARITY_OK` green throughout every ship — zero vendored-math touch. Lite suite grew 60→70 files across 2026-07-02 → 2026-07-03. Proto E2E n/a (lite-only block; zero `proto/` edits).

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` unchanged
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math unchanged
- ✅ `proto/server.py` core endpoints unchanged (proto NOT TOUCHED — lite-only block)
- ✅ `.bmaplan` schema version stays 1; only additive field is Ship 4's `verifyResult`
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ No forbidden surface touched — Ship 3's Range-streaming (the one piece that would touch the page-renderer's buffer-ownership contract) correctly HALTED at the human checkpoint rather than shipped
- ✅ `lite/ui-lite.html` stays under 1200-line cap (1170/1200 after Ship 4)

---

# Previous: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

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

<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/patch-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/patch-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older entries archived to docs/archive/patch-history-2026-05-09.md -->
