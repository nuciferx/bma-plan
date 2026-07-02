# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: AUDIT-20260702-infra-bundle — Test-Runner Preflight + Export Payload Caps + Render-Engine Review

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

Verdict: `PDFJS-VIEWPORT-CLIPPED` coordinate contract is algebraically exact for `V.rot`/`pgRot`=0 (residual ≈ ±0.5 device px, click-precision floor not a measured-value error). Real BROKEN bug found: `BUG-20260702-lite-pagerot-registration` — no existing test guards manual page-rotation registration; filed as top-priority next work, not fixed this sprint.

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

# Previous: BUG-20260702-lite-cfss-summary — CFSS shared-shape instances excluded from every rollup consumer + export crash

Branch: main
Date: 2026-07-02

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files. Lite-only sprint; no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_summary_cfss_parity.py
python lite/tests/test_cfss_model.py
python lite/tests/test_cfss_persist.py
python lite/tests/test_cfss_drag.py
python lite/tests/test_cfss_edit.py
python lite/tests/test_cfss_ui.py
python lite/tests/test_cfss_rightclick_menu.py
python lite/tests/test_summary_arc_parity.py
python lite/tests/test_measure_parity.py
python lite/tests/test_arc_edge.py
python lite/tests/test_report.py
python lite/tests/test_report_vars_rollup.py
python lite/tests/test_export_submenu.py
python lite/tests/test_tree_rollup.py
python lite/tests/test_overview_setup.py
```

## Lite — Results (15 commands, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_summary_cfss_parity.py | LITE_SUMMARY_CFSS_OK (NEW) | PASS |
| test_cfss_model.py | LITE_CFSS_MODEL_OK | PASS |
| test_cfss_persist.py | LITE_CFSS_PERSIST_OK | PASS |
| test_cfss_drag.py | LITE_CFSS_DRAG_OK | PASS |
| test_cfss_edit.py | LITE_CFSS_EDIT_OK | PASS |
| test_cfss_ui.py | LITE_CFSS_UI_OK | PASS |
| test_cfss_rightclick_menu.py | LITE_CFSS_RIGHTCLICK_MENU_OK | PASS |
| test_summary_arc_parity.py | LITE_SUMMARY_ARC_OK | PASS (bug-1 guard stays green) |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact) |
| test_arc_edge.py | LITE_ARC_EDGE_OK | PASS |
| test_report.py | (no named marker) | PASS |
| test_report_vars_rollup.py | LITE_REPORT_VARS_ROLLUP_OK | PASS |
| test_export_submenu.py | LITE_EXPORT_SUBMENU_OK | PASS |
| test_tree_rollup.py | LITE_TREE_ROLLUP_OK | PASS |
| test_overview_setup.py | LITE_OVERVIEW_SETUP_OK | PASS |

## LITE_SUMMARY_CFSS_OK — Bug Reproduction Proof

`test_summary_cfss_parity.py` exercises the REAL promote flow (`__cfssTestPromote`) then asserts all 6 rollup consumers report ground truth 2100 m² (2000 plain area + 100 instance area, using `instanceAreaM2` as the instance ground truth since `areaOf` is null-by-design for instances) and that both export builders (`buildExportData`, `exportPdfOverlay`) do not throw.

- **RED (pre-fix, via `git stash`):** totals reported 2000 (instance area silently missing); `master_has_catId` false; `edThrew`/`ovThrew` both true (confirms the crash sub-finding — XLSX and annotated-PDF export were broken outright, not just under-counted).
- **GREEN (post-fix):** all 6 consumers report 2100; both export builders complete without throwing.

## CRASH Sub-Finding

`buildExportData` and `exportPdfOverlay` called `catOf(o.catId).name`/`.color` BEFORE the `kind` guard — any page containing a CFSS instance (`o.catId === undefined`) threw a `TypeError`, crashing XLSX export and annotated-PDF export entirely. Fixed by moving `catOf` resolution after `catId` is resolved via `rollupCatId(o)`, made null-safe.

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (AUDIT-20260702-infra-bundle sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
