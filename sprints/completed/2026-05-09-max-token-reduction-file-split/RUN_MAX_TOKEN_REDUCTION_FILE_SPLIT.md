# RUN_MAX_TOKEN_REDUCTION_FILE_SPLIT.md

## 0. Sprint Identity

Sprint Name: Max Token Reduction / File Split
Sprint Type: Refactor / Housekeeping
Status: IN PROGRESS
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: 4bda145 (root) / b2389b5 (proto)
py_compile PASS · smoke PASS (confirmed at sprint start)

Source file sizes at baseline:
- proto/ui.html: 1437 lines
- proto/server.py: 1451 lines
- proto/e2e_ui_test.py: 1525 lines

---

## 2. Goal

Reduce future agent token cost by splitting oversized files into smaller focused modules.
Behavior must remain 100% identical. Tests must remain PASS throughout.

---

## 3. Checklist

### Part A — Doc / Log Token Reduction
- [x] Update CURRENT_STATUS.md to reflect Sprint B (Fast UI Testability Polish)
- [x] Update log.md with new session entry
- [x] Update docs/status/LATEST_STATUS.md
- [x] Update docs/status/NEXT_ACTIONS.md
- [x] Update docs/status/COMMIT_HISTORY.md
- [x] Create docs/status/READ_ORDER.md (new — agent read guide)

### Part B — Runtime File Size Audit
- [x] Create docs/design/RUNTIME_FILE_SPLIT_AUDIT.md

### Part C — Server Export Module Split
- [x] Create proto/export/__init__.py
- [x] Create proto/export/semantic_metadata.py (SEMANTIC maps + _derive_measurement_meta + _get_meta)
- [x] Create proto/export/xlsx_helpers.py (geometry + calculation helpers)
- [x] Modify server.py: add imports, remove moved definitions
- [x] py_compile PASS after Part C
- [x] smoke PASS after Part C
- [x] full PASS after Part C
- [x] Commit proto: refactor: split export metadata helpers

### Part D — Frontend JS Modules
- [x] Assessed: static file serving not present; adding StaticFiles is safe but deferred
- [x] Documented in RUNTIME_FILE_SPLIT_AUDIT.md
- [x] No implementation — risk too high relative to benefit in isolation

### Part E — E2E Test Organization
- [x] Assessed: splitting e2e_ui_test.py risks shared browser state and test ordering
- [x] Created docs/design/E2E_SPLIT_PLAN.md
- [x] No implementation — documented plan only

### Part F — Root Doc Update and Final Commit
- [x] Update all docs/status/ files with final sprint result
- [x] Update FINAL_REPORT_FOR_CHATGPT.md
- [x] Update PATCH_SUMMARY.md
- [x] Update TEST_RESULT.md
- [x] Update log.md
- [x] Move sprint card to sprints/completed/
- [x] Commit root: refactor: reduce token load with split status and runtime files

---

## 4. Stop Conditions

- Open PDF / Set Scale / Area+Opening drawing breaks
- XLSX / JSON / CSV export breaks
- save/load behavior changes
- E2E tests fail with non-local fix
- Static serving requires broad backend rewrite
- Frontend split breaks global event handlers
- Test split weakens assertions
- Legal/OCR/AI/Rule Engine appears

---

## 5. Files Allowed

### Part A, F
- CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md, UI_MANUAL_TEST.md, index.md
- docs/status/, docs/archive/, docs/process/, docs/design/
- sprints/active/RUN_MAX_TOKEN_REDUCTION_FILE_SPLIT.md

### Part B
- docs/design/RUNTIME_FILE_SPLIT_AUDIT.md (new)
- docs/design/E2E_SPLIT_PLAN.md (new)

### Part C, D, E
- proto/server.py
- proto/export/ (new package)
- proto/static/ (new if created)
- proto/tests/ (new if created)
- proto/e2e_ui_test.py

## 6. Files Forbidden

- proto/ui.html (no UI redesign)
- Legal/OCR/AI/Rule Engine
- save/load migration
- export behavior change (internal extraction only)
