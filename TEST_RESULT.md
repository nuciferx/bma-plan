# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md)

---

# Latest: PERF-20260702-lite-foxit-smoothness — Foxit-grade open smoothness (4-sprint block)

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

# Previous: BUG-20260702-lite-pagerot-registration — Manual page rotate desyncs geometry from raster + export

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

<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
