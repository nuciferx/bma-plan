# test-history archive — rotated out on 2026-08-10 (ค่ำ finalize)

> Archived from `TEST_RESULT.md`'s "Previous" slot to make room for the 2026-08-10 (ค่ำ) PKG-PORTABLE + PM-REDESIGN-D + SHELL sprint.

---

# BUG-20260706-lite-layer-page-binding

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
