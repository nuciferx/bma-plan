# RUN_E2E_TEST_SPLIT_AUDIT_AND_SAFE_SPLIT.md

## 0. Sprint Identity

Sprint Name: E2E Test Split Audit and Safe Split
Sprint Type: Audit / Refactor
Status: COMPLETE — AUDIT_ONLY_STOP
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: a331adb (root) / 9fa57a0 (proto)
py_compile PASS · smoke PASS · full PASS (confirmed at sprint start)

Source file sizes at baseline:
- proto/e2e_ui_test.py: 1525 lines

---

## 2. Goal

Reduce token load from proto/e2e_ui_test.py by splitting E2E tests into focused modules,
while preserving:
  python proto/e2e_ui_test.py smoke
  python proto/e2e_ui_test.py full

---

## 3. Checklist

### Part A — E2E Audit
- [x] Read e2e_ui_test.py in full (1525 lines)
- [x] Map all test functions and helper functions
- [x] Identify state dependencies across test functions
- [x] Assess risk of splitting
- [x] Create docs/design/E2E_TEST_SPLIT_AUDIT.md
- [x] Decision recorded: AUDIT_ONLY_STOP

### Part B — Safe Split
- [N/A] Audit said AUDIT_ONLY_STOP — no source changes made

### Part C — Doc Update and Root Commit
- [x] Update CURRENT_STATUS.md
- [x] Update FINAL_REPORT_FOR_CHATGPT.md
- [x] Update PATCH_SUMMARY.md
- [x] Update TEST_RESULT.md
- [x] Update log.md
- [x] Move sprint card to sprints/completed/
- [x] Commit root: docs: add e2e test split audit

---

## 4. Stop Conditions Triggered

AUDIT_ONLY_STOP triggered because:
- Test functions form an irreversible stateful pipeline (state from each test feeds the next).
- Splitting into independent modules requires either (a) duplicating state setup (test weakening)
  or (b) passing fragile state across module boundaries.
- Token reduction would be minimal: only helpers (~114 lines, 7%) are safe to extract.
- No functional problem exists; tests pass cleanly.

---

## 5. Files Allowed (Audit-only)

Docs:
- docs/design/E2E_TEST_SPLIT_AUDIT.md (new)
- CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md
- sprints/active/ → sprints/completed/

## 6. Files Forbidden

- proto/e2e_ui_test.py (no changes)
- proto/ui.html, proto/server.py, proto/static/*, proto/export/*
- Legal/OCR/AI/Rule Engine

---

## 7. Audit Summary

| File | Before | After |
|------|--------|-------|
| proto/e2e_ui_test.py | 1525 | 1525 (unchanged) |
| docs/design/E2E_TEST_SPLIT_AUDIT.md | — | new |
