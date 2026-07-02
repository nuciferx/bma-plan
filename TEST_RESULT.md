# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: BLOCK-20260703-clear-queue — 5-ship "ทำทั้งหมด" session

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

# Previous: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

Branch: main
Date: 2026-07-02

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this block made zero changes to `proto/` source files. Lite-only block (4 sprints); no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_pagecache_lru.py
python lite/tests/test_local_open.py
python lite/tests/test_warm_prefetch.py
python lite/tests/test_thumb_warm.py
python lite/tests/test_measure_parity.py
python lite/tests/run_all_tests.py
```

## Lite — Results (4 new guard tests + regression, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_pagecache_lru.py | LITE_PAGECACHE_LRU_OK (NEW) | PASS (RED→GREEN proven; Sprint 1) |
| test_local_open.py | LITE_LOCAL_OPEN_OK (NEW) | PASS (RED→GREEN proven; Sprint 2) |
| test_warm_prefetch.py | LITE_WARM_PREFETCH_OK (NEW) | PASS (RED→GREEN proven; Sprint 3) |
| test_thumb_warm.py | LITE_THUMB_WARM_OK (NEW) | PASS (Sprint 4) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact at every step — confirms `measure-engine.js` vendored math untouched across all 4 sprints) |

Per-sprint regression: Sprint 1 (page-cache LRU) 10/10 · Sprint 2 (local-first open) 10/10 · Sprint 3 (worker warm-up + prefetch) 9/9 · Sprint 4 (thumbnail warm) 8/8 — not individually enumerated here. Full lite test suite now stands at 67 files, all green.

## Empirical Perf Probe (drove this block's scoping — not a pass/fail test, reference measurements)

Source: `artifacts/perf/probe_results_20260702.txt`.

- RAMA4 (18.3 MB): first-paint 3.9s cold.
- CHH (90.8 MB real customer file): first-paint 9.6s cold; heap 766 MB after 10 pages viewed pre-fix → ~628 MB post Sprint-1 LRU (−18%).
- PDF.js library+worker boot: flat ~1.2s floor on every open regardless of file size, now hidden behind Sprint 3's idle-time warm-up.
- Time attribution: `UPLOAD` dominates at ~80ms/MB; `/raw` fetch is nearly free — motivated Sprint 2 (local-first open).
- Pan-blank suspicion (from `AUDIT-20260702-render-followups`): REFUTED, 0/10 occurrences across 3 test files.
- Overview thumbnails: earlier "0/0" report was a probe selector artifact — real measurement is 45/45 thumbnails in 9.2s cold (~200ms/thumb), instant on warm cache; confirms Sprint 4's approach is sound.

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
