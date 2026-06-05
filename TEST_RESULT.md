# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: SLICE report-edit-1 — Editable lite report

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

# Previous: BUG-20260526-lite-stale-pf-folder-cleanup

Branch: main
Date: 2026-05-26

## Result: PASS (lite tests only — proto NOT TOUCHED)

## No Proto-Test Rationale

Per AGENTS.md §1: proto `py_compile + smoke + full` not re-run because this sprint made zero changes to `proto/` source files. Lite-only sprint. Reference baseline: proto full E2E = 22 _OK markers (PHASE_CENTERLINE_SNAP_OK 10/10, last run 2026-05-25, unchanged).

## Commands

```bash
python -m py_compile lite/server_lite.py
python lite/tests/test_pf_cleanup_on_exclude.py
python lite/tests/test_page_folder_model.py
python lite/tests/test_page_folder_persist.py
python lite/tests/test_pf_kind_folders.py
python lite/tests/test_custom_layer_persist.py
python lite/tests/test_tree_persist.py
# /bma-simulate verify re-run (manual)
# verify_dblclick_manual.py (manual Playwright)
```

## Lite — PF_CLEANUP_OK (4/4 cases)

| Case | Description | Result |
|---|---|---|
| A — basic cleanup | tag p1=B1, p2=floor1, p3=floor2 → seed → re-tag p2 excluded → re-seed → assert PF_floor_1 gone + layers gone + PF_excluded gained p2 | PASS |
| B — safety preservation | same as A but push user-drawn object onto "GFA ชั้น 1" before re-tag → assert PF_floor_1 PRESERVED | PASS |
| C — idempotency | 5x back-to-back seedPageFolders produces same FOLDERS state as 1x | PASS |
| D — PF_excluded never pruned | PF_excluded is never pruned even when empty | PASS |

## Lite — Regression Suite (5 markers GREEN)

| Marker | Result |
|---|---|
| LITE_PAGE_FOLDER_MODEL_OK | PASS |
| LITE_PAGE_FOLDER_PERSIST_OK | PASS |
| LITE_PF_KIND_OK (11/11) | PASS |
| LITE_LAYER_PERSIST_OK | PASS |
| LITE_TREE_PERSIST_OK | PASS |

## /bma-simulate Verify Re-run

```
stale_PF_floor_1_exists = false
dom_render_order = [PF_basement_1, PF_floor_2, PF_excluded]
Result: VERIFIED PASS
```

## Manual E2E

```
verify_dblclick_manual.py → DBLCLICK_OK (objects=1, pts=4)
```

---

# Previous: Centerline Snap arc (invent → INV-002a proto → INV-002b lite → 2 post-ship bugfixes)

Branch: main
Date: 2026-05-25

## Result: PASS

Proto full E2E PASS (21/21 + NEW PHASE_CENTERLINE_SNAP_OK 10/10). Lite LITE_CENTERLINE_SNAP_OK 8/8 PASS. MEASURE_PARITY_OK GREEN. All prior baseline markers retained. Commits: `0208314` `6db0461` `ad920c6` `916d379` `ff3f9fe` `5783df4`.

## Commands

```bash
# Proto
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
python proto/e2e_ui_test.py full

# Lite
python lite/tests/test_centerline_snap.py
python lite/tests/test_measure_parity.py
```

## Proto — Smoke (18 baseline markers)

| Marker | Result |
|---|---|
| CACHE_OK | PASS |
| SETUP_OK | PASS |
| MAIN_UI_OK | PASS |
| VECTOR_OK | PASS |
| RECAL_OK | PASS |
| SITE_UI_OK | PASS |
| XLSX_OK | PASS |
| PROJECT_OK | PASS |
| RASTER_OK | PASS |
| WHEEL_OK | PASS |
| SNAP_OK | PASS |
| SELECT_OK | PASS |
| SETBACK_OK | PASS |
| EXT_MEASURE_OK | PASS |
| MENU_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| PHASE_I_A_OK | PASS |
| PHASE_I_B1_OK | PASS |

## Proto — Full (3 additional markers + NEW centerline marker)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| **PHASE_CENTERLINE_SNAP_OK (10/10 sub-checks)** | **PASS — NEW** |

Sub-checks for PHASE_CENTERLINE_SNAP_OK:
- fnsExist, versionExists, toggleExists, stateExists, buttonExists, prefDefault: all PASS
- sanity: PASS (skeleton pixels found on synthetic dashed canvas)
- accuracy: PASS (maxDelta=0.140%, target ≤0.5%)
- subFnsExist: PASS (CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton)
- refineHookInFinish: PASS (finishCurrentArea calls refine for poly branch)

Note: PROJECT_OK + PERSIST_OK confirm `obj.traceMode = "centerline-roi"` additive field round-trips through save/load without breaking existing .bmaplan files.

## Lite — LITE_CENTERLINE_SNAP_OK (8/8 sub-checks)

| Sub-check | Result |
|---|---|
| jsFnsExist | PASS (CL_snapCanvasToCenterline + CL_litePolyClick + CL_litePolyFinish present) |
| toggleBtnInstalled | PASS (floating toggle button self-installs on page load) |
| localStoragePersist | PASS (centerlineSnapOn state persists across page reload) |
| accuracy | PASS (maxDelta=0.1778% ≤0.5% on synthetic dashed pentagon) |
| skeletonFound | PASS (algorithm finds dark pixels on synthetic canvas) |
| refineHookInFinish | PASS (finishDraft calls CL_litePolyFinish for poly branch) |
| dprBridge | PASS (source scan confirms both glue functions reference `dpr` for coord conversion) |
| activeCssRule | PASS (.active CSS rule present: green background + glow when toggle ON) |

## Lite — MEASURE_PARITY_OK

```bash
python lite/tests/test_measure_parity.py  → GREEN
```

16 functions + 2 constants in `lite/static/js/measure-engine.js` are byte-identical to proto.
`centerline-snap.js` Section A is byte-identical to `proto/static/js/centerline-snap.js` per drift-locked vendoring contract.

## TEST-H Rationale (Skipped)

Per AGENTS.md: feature defaults OFF; user must opt-in via "⊙ CL" Helpers ribbon button (proto) or floating toggle (lite). The existing `bma-human-journey-tester` does not toggle Helpers ribbon options. The full E2E with 10/8 sub-check synthetic proof (including accuracy gate, hook wiring, DPR bridge, and active CSS verification) constitutes sufficient verification. TEST-H will be relevant when the feature is promoted to default-ON.

---

<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
