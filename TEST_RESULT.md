# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md) · [docs/archive/test-history-2026-07-02.md](docs/archive/test-history-2026-07-02.md) · [docs/archive/test-history-2026-07-03.md](docs/archive/test-history-2026-07-03.md)

---

<!-- GEN:START gen_status_docs -->

# Latest: BUG-20260706-lite-layer-page-binding

Date: 2026-07-06 · Area: layer / page-tagging (lite)

_lite-only, proto untouched. No forbidden surface (measure-engine/pdfToC/RS/snap untouched) — no proto E2E run._

First run of `test_layer_scope.py` (9 checks incl. 2 new) FAILED at `foreignDrawCommitBlocked` — the guard's warning wrote directly to `#hint`, which `draw()` → `updateHUD()` immediately overwrote. Fixed by switching to the `state.hintFlash` pattern (same as SCALE-GATE). Second run: 9/9 green.

| Marker / Suite | Result |
|---|---|
| test_layer_scope.py (incl. `LITE_ACTIVE_LAYER_FOLLOW_OK`, `LITE_LAYER_SCOPE_MULTI_PAGE_FOLDER_OK`) | FAIL (1st run, hintFlash) → PASS (9/9, 2nd run) |
| test_page_folder_ui.py | PASS |
| test_pf_folder_order.py | PASS (4/4) |
| test_pf_kind_folders.py | PASS (11/11) |
| test_custom_layer_ui.py | PASS |
| test_wiz_auto.py | PASS (8/8) |
| test_measure_parity.py (`MEASURE_PARITY_OK`) | PASS |

Commit: `ba109f0`. Closes: BUG-20260706-lite-active-layer-not-following-page, BUG-20260706-lite-multi-site-page-tag

---

# Previous: 2026-07-04 full-day block — 8 ships

Date: 2026-07-04 · Area: layer / report / measure / render (lite)

_lite-only, proto untouched. Full lite suite: 97/98 files green — the 1 failure (`test_closing_dup_strip.py`) is a pre-existing bug in the test itself (verified against HEAD), not an app regression; queued for housekeeping._

| Marker | Result |
|---|---|
| LITE_LAYER_SCOPE_OK | PASS (6/6) |
| LITE_LAYER_SEARCH_OK | PASS (5/5) |
| LITE_BULK_APPLY_OK | PASS (5/5) |
| LITE_GRID_GROUP_VIEW_OK | PASS (5/5) |
| LITE_TAG_JIT_OK | PASS (6/6) |
| LITE_EXPORT_TRUTH_OK | PASS (5/5) |
| LITE_GRID_ALL_PAGES_OK | PASS (5/5) |
| LITE_REPORT_SINGLE_MODE_OK | PASS (5/5) |
| LITE_EXPORT_DOORS_OK | PASS (4/4) |
| LITE_REPORT_APPENDIX_OK | PASS (5/5) |
| LITE_NATIVE_ROTATE_OK | PASS (24/24) |
| LITE_SNAP_ENGINE_OK | PASS (5/5) |
| LITE_SNAP_RAY_OK | PASS (6/6) |
| LITE_SNAP_TYPES_OK | PASS (9/9) |
| LITE_SCALE_GATE_OK | PASS (5/5) |

Visual proof: 10 screenshots in `artifacts/report-truth-proof/` (8 feature + 2 native-rotate), zero console errors. `LITE_NATIVE_ROTATE_OK` repro-first fixture: 6/6 checks proven RED pre-fix → 24/24 GREEN post-fix; registration ≤0.5px.

Closes: INV-2026-07-04-001, INV-2026-07-04-002, report-truth A-4/B-6/B-2/B-3/S-1/S-6/S-12, BUG-20260704-lite-native-rotate, SNAP-2026-07-04, SCALE-GATE

---

# AUDIT-20260703-roadmap-staleness

Date: 2026-07-03 · Area: process / roadmap hygiene

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: PERF-20260702-open-streaming, BUG-20260526-lite-force-setup, LITE-PROBE-DBLCLICK-REWRITE, HK-1

---

# AUDIT-20260703-lfoc-order-b-verify

Date: 2026-07-03 · Area: layer / folders (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PF_KIND_OK | PASS |

Closes: INV-2026-05-26-LFOC-ORDER-B

---

# TEST-20260526-wiz-followup-guard

Date: 2026-07-03 · Area: wizard / test (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| BUG_20260526_LITE_WIZ_FOLLOWUP_OK | PASS |

Closes: BUG-20260526-lite-wizard-followup

---

# FIX-20260703-undo-layers-folders

Date: 2026-07-03 · Area: layer / undo (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UNDO_LAYERS_OK | PASS |

Closes: layer-redesign-followup-a, b4-undo-flag

---

# INV-20260703-layer-redesign

Date: 2026-07-03 · Area: layer / model + ux (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_LAYER_FLOORKEY_OK | PASS |
| LITE_LAYER_TARGET_UI_OK | PASS |

Closes: P1-layer-floor-mismatch, P2-wrong-layer-draws, P3-role-layer-ambiguity

---

# UX-20260703-quickwins-batch3

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_BATCH3_OK | PASS |

Closes: UX-F8, UX-COSMETIC-1-4

---

# PROC-20260703-probe-dblclick-rewrite

Date: 2026-07-03 · Area: test-infra (simulate)

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: NEXT_ACTIONS-item-11

---

# PROC-20260703-v2-u6-changelog

Date: 2026-07-03 · Area: process / release-tooling

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: V2-U6-tooling

---

# PROC-20260703-v2-u2-impact-map

Date: 2026-07-03 · Area: process / test-infra

| Marker | Result |
|---|---|
| LITE_RUN_ALL_OK | PASS |

Closes: V2-U2-impact-map

---

# PROC-20260703-v2-u3gen-u5-truth

Date: 2026-07-03 · Area: process / docs-tooling

| Marker | Result |
|---|---|
| TRUTH_CHECK_OK | PASS |

Closes: V2-U3-generator, V2-U5

---

# PROC-20260703-v2-u3ledger-u4-roadmap

Date: 2026-07-03 · Area: process / docs-tooling

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: V2-U3-ledger, V2-U4

---

# SLICE-20260703-report-edit-default-grid

Date: 2026-07-03 · Area: report / ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_REPORT_DEFAULT_GRID_OK | PASS |

Closes: NEXT_ACTIONS-item-8

---

# PERF-20260703-worker-recycle-chh-probe

Date: 2026-07-03 · Area: perf-probe / docs

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: —

---

# BUG-20260703-lite-cfss-undo-masters

Date: 2026-07-03 · Area: measure / undo (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UNDO_MASTERS_OK | PASS |

Closes: BUG-20260703-lite-cfss-undo-masters

---

# UX-20260703-quickwins-batch2

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_BATCH2_OK | PASS |

Closes: F-4, F-5, F-6, F-9

---

# INV-20260703-layer-linkage

Date: 2026-07-03 · Area: measure+layer (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_OBJECT_TUPLES_OK | PASS |
| LITE_B1_ROLE_REROUTE_OK | PASS |
| LITE_B2_SINGLE_ENGINE_OK | PASS |
| LITE_B3_ORPHAN_HEAL_OK | PASS |
| LITE_B4_MOVE_LAYER_OK | PASS |
| LITE_B5_REF_BADGES_OK | PASS |

Closes: H1, H2, H3, M4, M6

---

# UX-20260703-quickwins-batch1

Date: 2026-07-03 · Area: ui (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_UX_QUICKWINS_OK | PASS |

Closes: F-1, F-2, F-3, F-7

---

# BUG-20260703-lite-save-wipes-data

Date: 2026-07-03 · Area: save/load (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SAVE_CLICKPATH_OK | PASS |

Closes: BUG-20260703-lite-save-wipes-data

---

# GO-20260703-invariants-streaming-worker-recycle

Date: 2026-07-03 · Area: test-infra + perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_WORKER_RECYCLE_OK | PASS |

Closes: —

---

# DOCS-20260702-dev-pillars-blueprint

Date: 2026-07-02 · Area: process / docs

_No guard markers — docs / process / research ship (no dedicated marker)._

Closes: —

---

# ACC-20260703-verify-scale-port

Date: 2026-07-03 · Area: measure-ux / accuracy (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_VERIFY_SCALE_OK | PASS |

Closes: ACC-20260703-verify-scale-port

---

# AUDIT-20260702-render-followups

Date: 2026-07-03 · Area: render + test-infra (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_RENDER_FB_SCAN_OK | PASS |
| LITE_OVERLAY_REG_OK | PASS |

Closes: AUDIT-20260702-render-followups

---

# AUDIT-20260702-s2-fitz-lock

Date: 2026-07-02 · Area: server perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_CASE_LOCK_OK | PASS |

Closes: AUDIT-20260702-s2-fitz-lock

---

# PERF-20260702-lite-foxit-smoothness

Date: 2026-07-02 · Area: perf (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PAGECACHE_LRU_OK | PASS |
| LITE_LOCAL_OPEN_OK | PASS |
| LITE_WARM_PREFETCH_OK | PASS |
| LITE_THUMB_WARM_OK | PASS |

Closes: —

---

# AUDIT-20260702-infra-bundle

Date: 2026-07-02 · Area: test-infra + server (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_RUN_ALL_OK | PASS |
| LITE_EXPORT_ENDPOINTS_OK | PASS |

Closes: AUDIT-20260702-runner-preflight, AUDIT-20260702-export-caps

---

# BUG-20260702-lite-pagerot-registration

Date: 2026-07-02 · Area: measure-geometry / render (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_PAGEROT_REG_OK | PASS |

Closes: BUG-20260702-lite-pagerot-registration

---

# BUG-20260702-lite-cfss-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SUMMARY_CFSS_OK | PASS |

Closes: BUG-20260702-lite-cfss-summary

---

# BUG-20260702-lite-arc-summary

Date: 2026-07-02 · Area: measure-geometry (lite)

_lite-only, proto untouched._

| Marker | Result |
|---|---|
| LITE_SUMMARY_ARC_OK | PASS |

Closes: BUG-20260702-lite-arc-summary

---

<!-- GEN:END -->


---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data are the 2 kept in this file -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/test-history-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/test-history-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary (2026-07-02) + SLICE report-edit-1 (2026-06-05) + BUG-20260526-lite-stale-pf-folder-cleanup + Centerline Snap arc (2026-05-25) archived to docs/archive/test-history-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- SIM-2 (2026-05-24) and older test results archived to docs/archive/test-history-2026-05-09.md -->
