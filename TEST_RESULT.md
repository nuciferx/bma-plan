# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: GO-20260703-invariants-streaming-worker-recycle — V2-U1 invariants + Range-streaming spike (NOGO→RESHAPE) + worker-recycle build

Branch: main
Date: 2026-07-03

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (invariants doc + spike + worker-recycle); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_worker_recycle.py
python lite/tests/run_all_tests.py --tier t0
python lite/tests/test_measure_parity.py
```

## Lite — Results (1 new guard test + regression, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_worker_recycle.py | LITE_WORKER_RECYCLE_OK (NEW) | PASS (7/7 checks: teardown state, transparent reinit repaint, zero-refetch when a local blob is retained, metadata survival, in-flight-render SKIP, heap-not-worse −0.8%; built by lite-builder subagent, independently verified via diff + targeted subset re-run + t0) |
| run_all_tests.py --tier t0 | — | PASS (measure-math tier, <5s target) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact — confirms `measure-engine.js` vendored math untouched across all 4 pieces of this block) |

Regression: 6/6 targeted at-risk files green + `run_all_tests.py --tier t0` green. Lite suite now stands at 72 test files (up from 70). The V2-U1 invariant registry (`lite/tests/INVARIANTS.md`) and the Range-streaming spike (`lite/sandbox/invent-range-streaming/`) are docs/research, not app-code changes, and are covered by this same regression run rather than a dedicated guard marker.

## Range-streaming spike — real measured results (not a pass/fail test; the spike's own acceptance criteria are recorded here for auditability)

5-step spike run for real (not simulated) on RAMA4 (19 MB) + the real CHH customer binder (95 MB), in `lite/sandbox/invent-range-streaming/`:
- (S1) both PDFs are NON-linearized yet stream fine — only 20% of bytes fetched; the standing linearization concern is moot.
- (S2) Starlette's `/raw` route already serves `206 Partial Content` + `Content-Range` — zero backend changes needed.
- (S3) streaming cut CHH's RSS by only 10% (1675→1503 MB) against a ≥50% GO criterion — **FAILS**.
- pdf.js worker-heap bug #10730 CONFIRMED on the pinned 4.0.379 build: `doc.destroy()` frees the main document heap (409→98 MB) but the separate pdf.js WORKER heap survives untouched — this worker heap, not the document heap, is the real ~1.5 GB ceiling.
- (S4) `PDFDataRangeTransport` over `Blob.slice` works mechanically (no full local copy required) but delivers no memory win given (S3).
- **VERDICT: NOGO on streaming-as-a-memory-fix.** RESHAPE to worker-recycle, which was then built and independently guarded (see below).

## Worker-recycle — LITE_WORKER_RECYCLE_OK honesty note

The full "CHH RSS −50%" acceptance bar was measured in the spike's own pattern (S3 above), not re-measured against this specific shipped implementation. `LITE_WORKER_RECYCLE_OK`'s own heap check (−0.8%, "not worse") is a weaker, mechanically-verifiable claim proven on the test's own fixture. A production re-probe of the real worker-recycle build against the real CHH binder is recorded as queued follow-up measurement, not assumed to already match the spike's number.

## Reference Baseline (proto, unchanged this block)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

# Previous: BLOCK-20260703-clear-queue — 5-ship "ทำทั้งหมด" session

Branch: main
Date: 2026-07-03

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (5 ships); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_case_lock.py
python lite/tests/test_render_fallback_scanned.py
python lite/tests/run_all_tests.py --tier t0
python lite/tests/test_overlay_registration.py
python lite/tests/test_verify_scale.py
python lite/tests/test_measure_parity.py
python lite/tests/run_all_tests.py
```

## Lite — Results (5 new guard tests + full-suite regression, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_case_lock.py | LITE_CASE_LOCK_OK (NEW) | PASS (96-request 8-thread hammer + mid-flight doc-swap + concurrent overlay export, zero 5xx; Ship 1 — hardening hammer, NOT a deterministic RED-before-fix proof, native race is probabilistic) |
| test_render_fallback_scanned.py | LITE_RENDER_FB_SCAN_OK (NEW) | PASS (6/6 checks; Ship 2) |
| run_all_tests.py --tier t0 | — | PASS (measure-math-via-Node 1.26s, target <5s; Ship 3, V2 blueprint U2) |
| test_overlay_registration.py | LITE_OVERLAY_REG_OK (NEW) | PASS (pixel-level proof: max offset 0.50px zoom×2 / 0.33px fit / 0.40px pageRot=90°, tolerance 4; Ship 3; built by a delegated agent, independently re-run) |
| test_verify_scale.py | LITE_VERIFY_SCALE_OK (NEW) | PASS (7/7 checks incl. save/load round-trip + average-re-derives-areas; Ship 4; built by lite-builder subagent, independently verified via diff + 9-test subset re-run) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact throughout every ship — confirms `measure-engine.js` vendored math untouched) |

Per-ship regression: Ship 1 9/9 · Ship 2 8/8 · Ship 3 (no dedicated regression count — additive test-tooling + research doc) · Ship 4 (9-test targeted subset independently re-run) · Ship 5 (docs-only, py_compile n/a for `.md`). **Final full-suite validation:** `run_all_tests.py` was killed repeatedly when run in the background, so validation was done in 3 chunks: 17 files (log preserved at `artifacts/run_all_tests_20260703_final.log`) + 27 files + 26 files in foreground runs = **70/70 files green**. Lite suite grew from 60 to 70 files across 2026-07-02 → 2026-07-03 (10 new test files across the two days' sprints).

## Ship 1 — LITE_CASE_LOCK_OK honesty note

This guard is a probabilistic hardening-hammer test (96 requests / 8 threads / mixed `/page`+`/thumb`+doc-swap-mutation+overlay-export), not a deterministic RED-before-fix proof — native `fitz` races cannot reliably be forced to fail on demand pre-fix. Zero 5xx across the hammer run is the evidence recorded; a future regression here would need a more targeted repro than "more hammer iterations."

## Ship 3 — LITE_OVERLAY_REG_OK detail

First PIXEL-level (not exact-inverse-only) proof that the raster canvas and the export overlay stay registered: max device-pixel offset 0.50 at zoom×2, 0.33 at fit-to-page, 0.40 at `pageRot=90°` — all well inside the 4px tolerance. Closes render-followups item (d)/(e) (the render-quality spike's earlier 24/24 PASS was measured only within PDF.js's own coordinate space, never cross-checked against `ptToScreen`) and adds the visual coverage `BUG-20260702-lite-pagerot-registration`'s guard test lacked for the combined `V.rot≠0` + `pgRot≠0` case.

## Reference Baseline (proto, unchanged this block)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- GO-20260703-invariants-streaming-worker-recycle + BLOCK-20260703-clear-queue are the 2 kept in this file -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
