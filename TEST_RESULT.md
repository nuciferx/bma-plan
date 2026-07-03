# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md) · [docs/archive/test-history-2026-07-03.md](docs/archive/test-history-2026-07-03.md)

---

# Latest: UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data — CRASH fix (Ctrl+S wiped all data) + full UI/UX journey review + layer↔measurement invent checkpoint

Branch: main
Date: 2026-07-03

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (save-wipe CRASH fix + UX review + invent checkpoint); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (`PHASE_CENTERLINE_SNAP_OK` 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_save_clickpath.py
```

## Lite — Results (1 new guard test + 17-file targeted regression, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_save_clickpath.py | LITE_SAVE_CLICKPATH_OK (NEW) | PASS (4 checks: real `mi-save` click driven via `URL.createObjectURL` interception, polys/calib survive save, duplicate-page content follows identity not position, Apply/merge commit-order also verified. RED pre-fix = exact journey repro: polys 0, calib null) |

Regression: 17/17 targeted at-risk files green — metamorphic suite, page-manager suite, apply-mutations suite, all persist suites, arc-summary parity, CFSS-summary parity, `MEASURE_PARITY_OK` (drift-lock intact — confirms `measure-engine.js` vendored math untouched). The UX review (`UX-20260703-review-findings`) and the layer-linkage invent checkpoint (`INV-20260703-layer-linkage`) are findings-filing / research work, not app-code changes, and carry no dedicated test marker — covered by the same regression context rather than a standalone guard.

## Save-wipe CRASH — the click-path-vs-API-path gap

72 previously-green tests missed this CRASH-tier bug because every existing save test called `buildPageStore()` directly (the API/serialization path) rather than driving the real `mi-save` button click a user actually triggers. `test_save_clickpath.py` closes that specific gap by intercepting `URL.createObjectURL` to capture the blob the real click handler produces. This is recorded here as a testing-methodology lesson, not yet promoted into `lite/tests/INVARIANTS.md` (that file was explicitly out of scope for this docs-batching write while two `lite-builder` subagents are actively editing `lite/`).

## In-progress work not covered by this test result

B0 (tuple-stream aggregation engine + new `I11` invariant oracle) and UX quick-wins batch 1 (F-7/F-1/F-2/F-3 + cheatsheet accuracy pass) are being built right now by two `lite-builder` subagents in parallel. No test results are recorded for either here — they are unshipped as of this write and will get their own `TEST_RESULT.md` update when they land.

## Reference Baseline (proto, unchanged this block)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

# Previous: GO-20260703-invariants-streaming-worker-recycle — V2-U1 invariants + Range-streaming spike (NOGO→RESHAPE) + worker-recycle build

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

<!-- UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data / GO-20260703-invariants-streaming-worker-recycle are the 2 kept in this file -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
