# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Max Token Reduction / File Split

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/export/__init__.py` — new empty package init.
- `proto/export/semantic_metadata.py` — SEMANTIC_*_MAPs, AREA_SEMANTIC_TAGS, _derive_measurement_meta, _get_meta (moved from server.py lines 722–790).
- `proto/export/xlsx_helpers.py` — _hex_to_rgb, _poly_area_pt2, _line_points, _line_length_pt, _nearest_on_segment, _object_points_for_ref_report, _distance_to_ref, _m2_to_rwu (moved from server.py lines 523–585 and 1415–1422).
- `proto/server.py` — removed ~160 lines of moved definitions; added 2 import blocks from export package. Behavior identical.
- `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md` — new audit doc (file sizes, risk levels, split sequence).
- `docs/design/E2E_SPLIT_PLAN.md` — e2e test split plan (implementation deferred).
- `docs/status/READ_ORDER.md` — new agent reading guide.
- All status docs updated.

## What Did Not Change

- No `proto/ui.html` changes.
- No save/load format changes.
- No export behavior changes — all moved functions re-imported at module level.
- No legal/OCR/AI/Rule Engine.

## Files Touched

- `proto/server.py`, `proto/export/__init__.py`, `proto/export/semantic_metadata.py`, `proto/export/xlsx_helpers.py`
- `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md`, `docs/design/E2E_SPLIT_PLAN.md`, `docs/status/READ_ORDER.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`
- `docs/status/LATEST_STATUS.md`, `docs/status/NEXT_ACTIONS.md`, `docs/status/COMMIT_HISTORY.md`
