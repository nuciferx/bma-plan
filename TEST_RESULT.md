# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-cfss-summary — CFSS shared-shape instances excluded from every rollup consumer + export crash

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

# Previous: BUG-20260702-lite-arc-summary — Arc-edge polygon areas excluded from every rollup consumer

Branch: main
Date: 2026-07-02

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files. Lite-only sprint; no forbidden-trigger surface touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_summary_arc_parity.py
python lite/tests/test_measure_parity.py
python lite/tests/test_arc_edge.py
python lite/tests/test_report.py
python lite/tests/test_report_vars.py
python lite/tests/test_report_vars_rollup.py
python lite/tests/test_export_submenu.py
python lite/tests/test_tree_rollup.py
python lite/tests/test_overview_setup.py
```

## Lite — Results (9 commands, all exit 0)

| Test | Marker | Result |
|---|---|---|
| test_summary_arc_parity.py | LITE_SUMMARY_ARC_OK (NEW) | PASS |
| test_measure_parity.py | MEASURE_PARITY_OK | PASS (drift-lock intact) |
| test_arc_edge.py | LITE_ARC_EDGE_OK | PASS |
| test_report.py | (no named marker) | PASS |
| test_report_vars.py | LITE_REPORT_VARS_OK | PASS |
| test_report_vars_rollup.py | LITE_REPORT_VARS_ROLLUP_OK | PASS |
| test_export_submenu.py | LITE_EXPORT_SUBMENU_OK | PASS |
| test_tree_rollup.py | LITE_TREE_ROLLUP_OK | PASS |
| test_overview_setup.py | LITE_OVERVIEW_SETUP_OK | PASS |

## LITE_SUMMARY_ARC_OK — Bug Reproduction Proof

`test_summary_arc_parity.py` asserts the invariant "every rollup consumer == Σ areaOf labels (arc-inclusive)" across all 6 fixed call sites, using an independent closed-form fixture (10000 + 1250π ≈ 13926.99 m² arc room + plain 2000 m² room).

- **RED (pre-fix, via `git stash`):** old code returned chord-area totals (e.g. 12000 instead of 13926.99) at all 6 rollup consumers while the per-object canvas label still showed the correct arc-inclusive value — confirming the bug was real and isolated to the rollup path.
- **GREEN (post-fix):** all 6 consumers now match Σ areaOf labels exactly.

## Reference Baseline (proto, unchanged this sprint)

```
python3.11 proto/e2e_ui_test.py full → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.
```

---

<!-- SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
