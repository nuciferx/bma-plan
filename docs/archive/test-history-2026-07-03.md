# test-history-2026-07-03.md — Archived Test Results

> Archived from root TEST_RESULT.md on 2026-07-03 (BLOCK-20260703-clear-queue archived during the UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block, to keep root at Latest + 1 Previous).

---

# BLOCK-20260703-clear-queue — 5-ship "ทำทั้งหมด" session

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
