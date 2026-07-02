# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md)

---

# Latest: GO-20260703-invariants-streaming-worker-recycle — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. Continuation of the same-day "GO" loop block, resumed right after `BLOCK-20260703-clear-queue` closed and the Range-streaming human checkpoint was cleared. **(1) V2-U1 invariant registry (`6d6e39b`):** NEW `lite/tests/INVARIANTS.md` — a canonical registry of 10 invariants (I1–I10), each mapped to its guard test + tier, plus the two mandatory SCOPE questions this project's own `DEVELOPMENT_V2_BLUEPRINT.md` U1 called for, born directly from the arc/CFSS-summary postmortem. Same commit reconciles 16 stale `PHASE_INDEX.md` rows with real `fixed_commit`, and closes the queued `ptToScreen` parity-fixture card with rationale rather than code (the behavioral lock already exists as invariant I7). **(2) Range-streaming SPIKE (`9466fe4`+`f8c2981`), GO received:** the 5-step spike was run for real on RAMA4 (19 MB) and the actual CHH customer binder (95 MB), not simulated. It found streaming cuts CHH's memory by only 10% against a ≥50% acceptance bar — **FAILS** — and confirmed the real ~1.5 GB memory ceiling is a pdf.js worker-heap defect (bug #10730), not a document-buffering problem Range-streaming could ever fix. **VERDICT: NOGO on streaming-as-a-memory-fix.** This is exactly what a spike is for: it prevented real engineering effort from being spent building the wrong fix. **(3) worker-recycle BUILT (`d52ddbb`), the RESHAPE:** explicit pdf.js worker lifecycle management — the worker is now recycled (torn down + transparently reinitialized) on tab-hidden or app-idle triggers, targeting the actual root cause the spike identified. New guard test `LITE_WORKER_RECYCLE_OK` (7/7 checks) passes; a production re-probe of the real memory-reduction number on the CHH binder is honestly recorded as a queued follow-up measurement, not assumed. **(4) Streaming-as-bandwidth deferred:** the spike's secondary "80% fewer bytes" benefit was explicitly NOT built — the current product is desktop-only over localhost, so there is no user who benefits from it today; revisit if/when a remote deployment exists. Lite suite now 72 files; `MEASURE_PARITY_OK` green throughout. Zero `proto/` edits.

## What was delivered

- `lite/tests/INVARIANTS.md` (NEW) — 10 invariants (I1–I10) + 2 mandatory SCOPE questions + new-object-kind fixture rule
- `docs/status/PHASE_INDEX.md` — 16 stale rows reconciled; `ptToScreen` parity card closed with rationale; streaming-spike verdict + worker-recycle + bandwidth-deferral recorded
- `docs/invent/lite-range-streaming.md` — updated with the real spike results and NOGO-as-memory-fix verdict
- `lite/sandbox/invent-range-streaming/` (NEW) — spike scripts + raw results
- `lite/static/js/page-renderer.js` — explicit `PDFWorker` ownership, `_docSource` re-open handle, `recycleDocWorker()`, hidden/idle/manual triggers
- `lite/tests/test_worker_recycle.py` (NEW) — `LITE_WORKER_RECYCLE_OK`, 7/7 checks
- Shipped as commits `6d6e39b` + `9466fe4` + `f8c2981` + `d52ddbb` on `main` (streaming-as-bandwidth deferral recorded as a documentation-only follow-on)

## What's next

- **(1) Production RSS re-probe of worker-recycle on the CHH binder** — the −50% acceptance bar was measured in the spike's pattern, not yet re-verified against the shipped implementation on the real 95 MB file. Small measurement task.
- **(2) V2 migration continuation** — U1 (`INVARIANTS.md`) now DONE; U2 (tiered test runner) partially landed earlier. Remaining: U3 (`SHIPS.jsonl` ledger — the token-cost killer), U4 (full roadmap split ACTIVE/DONE + a reconcile script — this block's 16-row fix was done by hand).
- **(3) proto backlog decision** — proto is de-facto in maintenance mode; decide whether to formally freeze it or schedule a hardening pass against its known issues (circle 32-gon storage bias, snap-radius zoom growth, soft-pass markers).
- **(4) Release ritual per V2-U6** — tag + CHANGELOG + full 4-tier test run + `/lite-sandbox-test`, due before the next build hand-off.

## Position in Plan

Phase 1 — BMA-Plan Lite epic. This block is the direct continuation of the invention discipline `BLOCK-20260703-clear-queue` Ship 3 halted at: the Range-streaming research reached a human checkpoint, work resumed once it cleared, a real spike caught that the memory problem was misdiagnosed, and the RESHAPE redirected the same acceptance bar at the real root cause instead. Process debt (invariant registry, roadmap reconciliation) was paid down opportunistically in the same session. No forbidden surface touched.

---

# Previous: BLOCK-20260703-clear-queue — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. Five same-session ships, cleared back-to-back overnight under a user directive to close out the entire remaining queue ("ทำทั้งหมด"). **Ship 1 — `AUDIT-20260702-s2-fitz-lock` (`d0a5dde`):** per-case `threading.Lock` now serializes all `fitz.Document` access in `lite/server_lite.py`, including moving `/export-pdf-overlay`'s render off the event loop entirely (completing the S2 threadpool goal deferred from `AUDIT-20260702-infra-bundle`). NEW `LITE_CASE_LOCK_OK` hammer test (96 requests / 8 threads / mid-flight doc-swap / concurrent overlay export), zero 5xx — honestly recorded as a hardening test, not a deterministic RED-before-fix proof, since native races are probabilistic. **Ship 2 — render-followups (a)+(c) (`aec375b`):** PDF.js-unavailable no longer blanks the canvas (falls back to server JPEG raster); scanned/image-only pages get a capped re-render scale (saves wasted CPU, zero accuracy change) plus a one-time hint. **Ship 3 (`13054b6`):** tiered test runner (`--tier t0/t1/t2`, part of the new V2 migration blueprint), and — most notably — the first PIXEL-level proof (not just exact-inverse math) that the raster canvas and exported overlay stay registered (max offset 0.50 device px), closing an evidence gap the 2026-05-28 render-quality spike never closed. Range-streaming research was also completed and correctly HALTED at the human decision checkpoint rather than shipped, per this project's invention discipline. **Ship 4 — `ACC-20260703-verify-scale-port` (`bea2119`):** ported Verify-Scale from proto to lite, closing the single remaining accuracy gap vs. Foxit identified by the 2026-07-02 competitive comparison. **Ship 5:** wrote down the day's operating lessons as two new process docs (`DEVELOPMENT_PILLARS.md`, `DEVELOPMENT_V2_BLUEPRINT.md`) before they were lost. Full lite test suite validated at 70/70 files green (grown from 60 across the two days); `MEASURE_PARITY_OK` stayed green through every ship. Zero `proto/` edits across the whole block. **Ship 3's Range-streaming checkpoint was cleared and resolved by `GO-20260703-invariants-streaming-worker-recycle`.**

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

## What's next (as recorded at the time; see GO-20260703-invariants-streaming-worker-recycle above for resolution)

- **(1) HUMAN DECISION: Range-streaming spike GO/NOGO/RESHAPE** (`docs/invent/lite-range-streaming.md`) — the only item in the whole cleared queue still awaiting anything, and it specifically awaits a human call, not more agent work. **(Resolved: GO received, spike ran, NOGO-as-memory-fix, RESHAPE shipped.)**
- **(2) V2 migration continuation** — `INVARIANTS.md` (U1), roadmap split + reconcile (U4), `SHIPS.jsonl` ledger (U3) remain queued from `docs/process/DEVELOPMENT_V2_BLUEPRINT.md`; the tiered test runner (U2) is partially landed via Ship 3. **(U1 done; U3/U4 remainder still queued.)**
- **(3) `ptToScreen`/`screenToPt` into the parity fixture** — last drift-lock nicety carried over from `BUG-20260702-lite-pagerot-registration`. **(Closed with rationale — registered as invariant I7.)**
- **(4) Stale `PHASE_INDEX.md` rows** — `lpm-1..9` show `queued` but `bug-archive.jsonl` says fixed; needs a reconciliation pass. **(Resolved — 16 rows reconciled.)**

## Position in Plan

Phase 1 — BMA-Plan Lite epic. This block spans three tracks at once: reliability hardening (fitz lock), rendering robustness (fallback + scan detection + registration proof), and measurement-accuracy parity with the competitive benchmark (Verify-Scale port) — plus capturing the day's process lessons as durable doctrine. With the queue now cleared, the only forward motion pending is the human GO/NOGO decision on Range-streaming; everything else is either shipped or explicitly queued for a future sprint. No forbidden surface touched.

---

<!-- GO-20260703-invariants-streaming-worker-recycle + BLOCK-20260703-clear-queue are the 2 kept in this file -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
