# TEST_RESULT.md Archive — 2026-06 sessions (archived 2026-07-02)

> Archived from root TEST_RESULT.md on 2026-07-02 (BUG-20260702-lite-cfss-summary sprint archived during BUG-20260702-lite-pagerot-registration sprint; BUG-20260702-lite-arc-summary sprint archived during AUDIT-20260702-infra-bundle sprint; SLICE report-edit-1 added 2026-07-02 during BUG-20260702-lite-cfss-summary sprint; AUDIT-20260702-infra-bundle archived 2026-07-02 during the PERF-20260702-lite-foxit-smoothness sprint block; BUG-20260702-lite-pagerot-registration archived 2026-07-03 during the BLOCK-20260703-clear-queue session; PERF-20260702-lite-foxit-smoothness archived 2026-07-03 during the GO-20260703-invariants-streaming-worker-recycle session) to keep root at Latest + 1 Previous.

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

Verdict: `PDFJS-VIEWPORT-CLIPPED` coordinate contract is algebraically exact for `V.rot`/`pgRot`=0 (residual ≈ ±0.5 device px, click-precision floor not a measured-value error). Real BROKEN bug found: `BUG-20260702-lite-pagerot-registration` — no existing test guards manual page-rotation registration; filed as top-priority next work. **Fixed same-day.**

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

# Archived: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

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

# Archived: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

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
