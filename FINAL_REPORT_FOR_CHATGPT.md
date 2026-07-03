# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md) · [docs/archive/reports-2026-07-02.md](docs/archive/reports-2026-07-02.md) · [docs/archive/reports-2026-07-03.md](docs/archive/reports-2026-07-03.md)

---

# Latest: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — PASS

**Date:** 2026-07-03
**Branch:** main

## Outcome

PASS. Three pieces filed/shipped the same morning. **(1) CRASH fix — save wiped all data (`d40b20b`):** Ctrl+S wrote an empty `.bmaplan` and destroyed the in-memory session — the most severe defect class this project tracks, total silent data loss on the single most-used action in the app. Root cause: `pageMgr` seeded `PS_by_id` as empty `deepCopy` snapshots taken at upload time, never refreshed, then projected back over live `PS` right before save serialized it. 72 previously-green tests missed this because every existing save test drove the API/serialization path directly, never the real `mi-save` click. Fixed via a new `projectToGlobals(livePS)` resolver plus the same latent wipe on the Apply/merge path (a backwards commit-order bug, 2 sites). NEW guard `LITE_SAVE_CLICKPATH_OK` drives the real click and closes the click-path-vs-API-path testing gap; RED pre-fix (exact journey repro) → GREEN; regression 17/17. **(2) UX review filed (`UX-20260703-review-findings`):** a full journey (29 screenshots on the real 45-page permit) + static-code review surfaced 9 FRICTION findings (dead hotkey, key collisions, an undiscoverable Page Manager, invisible post-verify scale state, a silently mouse-blocking wizard, misleading upload messaging, a modal-detection gap that leaks hotkeys into open dialogs, raw error text, and a native `window.prompt()` in Verify Scale) plus 6 COSMETIC findings, with 3 GOODs explicitly pinned so future work doesn't regress them. This is the review methodology validating itself in the same session — the CRASH it surfaced was fixed same-morning. **(3) Layer↔measurement invent reached its human checkpoint (`INV-20260703-layer-linkage`):** an investigation mapped 8 concrete problems in the current layer/measurement data model (3 rated HIGH, all tracing to two independently-maintained rollup engines that can silently disagree), scored 5 candidate redesigns, and staged a rollout plan around the winning "one aggregation engine" approach. GO was received; the first build increment and a batch of UX quick-win fixes are in progress right now via two parallel builder subagents, not yet shipped as of this report. Lite suite regression green throughout; `MEASURE_PARITY_OK` intact. Zero `proto/` edits.

## What was delivered

- `lite/static/js/page-manager.js` — NEW `projectToGlobals(livePS)`, resolves page content from live `PS` by identity at commit time
- `lite/static/js/page-manager-ui.js` — Apply/merge commit-order fix (2 sites), closing the same latent save-wipe on that path
- `lite/tests/test_save_clickpath.py` (NEW, 190 lines) — `LITE_SAVE_CLICKPATH_OK`, drives the real `mi-save` click via `URL.createObjectURL` interception
- `artifacts/ux-review-20260703/` (NEW) — 29 journey screenshots backing the filed UX findings
- `docs/status/PHASE_INDEX.md` — bug filed + fixed; UX review bundle + layer-linkage invent checkpoint filed
- Shipped as commits `d40b20b` + `912c3e2` + `2249400` on `main`

## What's next

- **(1)** Verify + commit the two in-flight builder sprints: B0 (tuple-stream aggregation engine + `I11` invariant oracle) and UX quick-wins batch 1 (F-7/F-1/F-2/F-3 + cheatsheet accuracy pass).
- **(2)** B1-B2 — reroute the existing summary/review/export consumers onto the new tuple-stream aggregation engine once B0 lands.
- **(3)** UX quick-wins batch 2 — F-4 (visible scale-verified badge), F-5/F-6 (wizard/upload messaging), F-9 (replace `window.prompt()` in Verify Scale), plus summary seeded-vars red-error display and a wizard Next-button gate.
- **(4)** Production RSS re-probe of worker-recycle on the CHH binder (carried over, still open).
- **(5)** V2 migration continuation — `SHIPS.jsonl` ledger (U3) and roadmap split+reconcile tooling (U4).

## Position in Plan

Phase 1 — BMA-Plan Lite epic. A CRASH-tier bug on the core save path was found and fixed the same morning a broader UI/UX health review was run — direct validation of why the review methodology exists. The layer↔measurement redesign is upstream R&D discipline (Pack H): rather than patching 8 symptom-level problems ad hoc, the investigation found and scored a structural root-cause fix before committing build time, and correctly halted at the human GO checkpoint rather than auto-promoting. No forbidden surface touched.

---

# Previous: GO-20260703-invariants-streaming-worker-recycle — PASS

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

<!-- UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data / GO-20260703-invariants-streaming-worker-recycle are the 2 kept in this file -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/reports-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/reports-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/reports-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older reports archived to docs/archive/reports-2026-05-09.md -->
