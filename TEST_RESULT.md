# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

Branch: main
Date: 2026-07-02

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files. Lite-only sprint; no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_pagerot_registration.py
python lite/tests/test_page_rotate.py
python lite/tests/test_metamorphic_pages.py
python lite/tests/test_snap_types.py
python lite/tests/test_arc_edge.py
python lite/tests/test_ortho.py
python lite/tests/test_cfss_drag.py
python lite/tests/test_cfss_ui.py
python lite/tests/test_centerline_snap.py
python lite/tests/test_annot_label.py
python lite/tests/test_live_overlay.py
python lite/tests/test_measure_parity.py
python lite/tests/test_pbt_measure.py
python lite/tests/test_export_endpoints.py
python lite/tests/test_summary_arc_parity.py
python lite/tests/test_summary_cfss_parity.py
python lite/tests/run_all_tests.py
```

## Lite — Results (16 at-risk files + 26-file partial `run_all_tests.py` subset, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_pagerot_registration.py | LITE_PAGEROT_REG_OK (NEW) | PASS (5/5 checks; RED→GREEN proven) |
| test_page_rotate.py | — | PASS (regression, at-risk) |
| test_metamorphic_pages.py | — | PASS (regression, at-risk) |
| test_snap_types.py | — | PASS (regression, at-risk) |
| test_arc_edge.py | LITE_ARC_EDGE_OK | PASS (regression, at-risk) |
| test_ortho.py | — | PASS (regression, at-risk) |
| test_cfss_drag.py | LITE_CFSS_DRAG_OK | PASS (regression, at-risk) |
| test_cfss_ui.py | LITE_CFSS_UI_OK | PASS (regression, at-risk) |
| test_centerline_snap.py | LITE_CENTERLINE_SNAP_OK | PASS (regression, at-risk) |
| test_annot_label.py | — | PASS (regression, at-risk) |
| test_live_overlay.py | — | PASS (regression, at-risk) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact — confirms `measure-engine.js` vendored math untouched) |
| test_pbt_measure.py | — | PASS (regression, at-risk) |
| test_export_endpoints.py | LITE_EXPORT_ENDPOINTS_OK | PASS (regression — export path also touched this sprint) |
| test_summary_arc_parity.py | LITE_SUMMARY_ARC_OK | PASS (bug-1 guard stays green) |
| test_summary_cfss_parity.py | LITE_SUMMARY_CFSS_OK | PASS (bug-2 guard stays green) |

Plus 26 more files green from a partial `run_all_tests.py` pass (not individually enumerated here). Total: 42 distinct files green this sprint.

## LITE_PAGEROT_REG_OK — 5 checks

Guard test proving the registration bug and the fix: (i) 4-angle screen-coordinate mapping vs. a closed-form quadrant transform; (ii) `screenToPt` is the exact inverse of `ptToScreen` (tolerance 1e-9); (iii) area is invariant under rotate (confirms stored points are never mutated); (iv) `pageRotations` round-trip through a real `loadProto` save/load cycle; (v) export: output page dimensions swap correctly (600×450) and stroke pixels are found at the expected rotated vertex (585,15).

- **RED (pre-fix, via `git stash`):** mapping produced (15,15) instead of (585,15); `rotRestored` false; export output un-rotated at 450×600.
- **GREEN (post-fix):** all 5 checks pass.

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

# Previous: AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review

Branch: main
Date: 2026-07-02

## Result: PASS (lite tests + read-only review — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files (Sprint A + B are `lite/`-only; Review C is read-only, zero code change anywhere). Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_export_endpoints.py
python lite/tests/run_all_tests.py
python lite/tests/test_apply_page_mutations.py
python lite/tests/test_pm_apply_flush_unified.py
python lite/tests/test_metamorphic_pages.py
python lite/tests/test_pdfjs_offline.py
python lite/tests/test_summary_arc_parity.py
python lite/tests/test_summary_cfss_parity.py
python lite/tests/test_measure_parity.py
python lite/tests/test_export_submenu.py
python lite/tests/test_report.py
```

## Lite — Results (all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_export_endpoints.py | LITE_EXPORT_ENDPOINTS_OK (NEW) | PASS (14/14 checks) |
| run_all_tests.py | LITE_RUN_ALL_OK (NEW) | PASS (60/60 tests, 8.5 min, first full run) |
| test_apply_page_mutations.py | — | PASS (regression subset) |
| test_pm_apply_flush_unified.py | — | PASS (regression subset) |
| test_metamorphic_pages.py | — | PASS (regression subset) |
| test_pdfjs_offline.py | — | PASS (regression subset) |
| test_summary_arc_parity.py | LITE_SUMMARY_ARC_OK | PASS (bug-1 guard stays green) |
| test_summary_cfss_parity.py | LITE_SUMMARY_CFSS_OK | PASS (bug-2 guard stays green) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact) |
| test_export_submenu.py | LITE_EXPORT_SUBMENU_OK | PASS (regression subset) |
| test_report.py | (no named marker) | PASS (regression subset) |

Plus a partial full-suite run covering 11 additional files, all exit 0 (not individually enumerated here — see `artifacts/run_all_tests_20260702.log` for the complete 60/60 aggregate run).

## LITE_EXPORT_ENDPOINTS_OK — 14 checks

First real HTTP tests of `/export-xlsx` and `/export-pdf-overlay` (previously only client-side `dlPost` stubs existed, never exercising the server route). Covers: XLSX bytes openable by `openpyxl` with sheet+row assertions; overlay output is a valid `%PDF` with correct page count; oversize payloads (too many pages / points / objects) all return 400; malformed payloads (unknown `case_id`, non-numeric page key, a `1e12` coordinate) all return 400; XLSX row-cap violation returns 400.

## Review C — Render-Engine Accuracy (read-only, no test markers — findings filed to PHASE_INDEX.md)

Verdict: `PDFJS-VIEWPORT-CLIPPED` coordinate contract is algebraically exact for `V.rot`/`pgRot`=0 (residual ≈ ±0.5 device px, click-precision floor not a measured-value error). Real BROKEN bug found: `BUG-20260702-lite-pagerot-registration` — no existing test guards manual page-rotation registration; filed as top-priority next work. **Fixed same-day — see Latest above.**

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
