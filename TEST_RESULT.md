# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: BUG-20260702-lite-arc-summary — Arc-edge polygon areas excluded from every rollup consumer

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

# Previous: SLICE report-edit-1 — Editable lite report

Branch: main
Date: 2026-06-05

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files. Lite-only sprint; no forbidden-trigger surface (export, rotation, save/load, real-PDF, snap, layer) touched in proto. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python lite/tests/test_report_edit.py  →  LITE_REPORT_EDIT_OK 7/7  PASS
```

## Lite — LITE_REPORT_EDIT_OK (7/7 cases)

| Case | Description | Result |
|---|---|---|
| PICKER regression | =B1+B2 formula evaluates to 86.93 via DOM-driven cell-click picker | PASS |
| STABLE delete-unreferenced | delete row 2 (B2 was =B1+B3), re-project → =B1+B2, value 76.61 preserved | PASS |
| STABLE delete-referenced | delete a row whose ref is used in formula → term dropped + red flag, value 50.45 | PASS |
| STABLE multi-op | =B1+B2+B3-B4; delete referenced row → re-project 66.61 correct | PASS |
| GUARD label-col click | clicking the label column (A) never injects A2 ref into formula | PASS |
| PERSIST | semantic subMeta survives save-reopen cycle via localStorage v1 | PASS |
| NaN-GUARD | entering "abc" in a numeric cell reverts to previous value 50.45 | PASS |

## Reference Baseline (from previous sprint BUG-20260526-lite-stale-pf-folder-cleanup)

```
python -m py_compile lite/server_lite.py                   → OK
python lite/tests/test_pf_cleanup_on_exclude.py            → PF_CLEANUP_OK 4/4
python lite/tests/test_page_folder_model.py                → LITE_PAGE_FOLDER_MODEL_OK
python lite/tests/test_page_folder_persist.py              → LITE_PAGE_FOLDER_PERSIST_OK
python lite/tests/test_pf_kind_folders.py                  → LITE_PF_KIND_OK 11/11
python lite/tests/test_custom_layer_persist.py             → LITE_LAYER_PERSIST_OK
python lite/tests/test_tree_persist.py                     → LITE_TREE_PERSIST_OK
```

Proto baseline: `python3.11 proto/e2e_ui_test.py full` → PASS 22 markers (PHASE_CENTERLINE_SNAP_OK 10/10), last run 2026-05-25.

---

<!-- BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-arc-summary sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
