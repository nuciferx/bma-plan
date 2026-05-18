# RUN_FAST_UI_TESTABILITY_POLISH.md

## 0. Sprint Identity

Sprint Name: Fast UI Testability Polish
Sprint Type: UI Polish / Usability
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

Baseline PASS after commit b278456 (root) / e32122e (proto).
Left panel tabs working. Right panel Layers-first. All E2E assertions PASS.

---

## 2. Goal

Make the existing UI easier to test and use in a fast guarded session.
Usability polish only — no architecture rewrite, no export/save/load rewrite,
no new drawing tools.

Source files: proto/ui.html, proto/e2e_ui_test.py only.

---

## 3. Micro Sprint Checklist

- [x] 0. Confirm Commit / Clean State — PASS (b278456)
- [x] 1. Test Mode Landing / Start Screen — empty-state card with action buttons + numbered workflow
- [x] 2. Top Action Bar Simplify — .sep divider between file group and workflow group
- [x] 3. Set Scale CTA / Scale Status — .scale-cta orange highlight on Set Scale when PDF open, no scale
- [x] 4. Page Setup Mini Panel — #lp-page-info strip in sidebar: page name · tag · scale
- [x] 5. Measurement Toolbar Clean Mode — aria-label attributes on toolbar groups for testability
- [x] 6. Properties Panel Usability — buildLeftProperties() grouped: Basic / Measurement / Metadata
- [x] 7. Right Panel Layers Visual Cleanup — Layers title styled, compat note improved
- [x] 8. Review Warning Summary — QA warnings grouped: Error / Warning / Info sub-sections
- [x] 9. Export Ready Screen — #export-readiness summary bar in export panel
- [x] 10. Quick Test Guide — docs/process/QUICK_TEST_GUIDE.md created

---

## 4. Stop Conditions

- Open PDF breaks
- Set Scale breaks
- Area/Opening drawing breaks
- Export breaks
- Save/load behavior changes
- Tests fail and fix is not local
- Change requires backend/export/save-load rewrite
- Change becomes broad refactor
- Legal/OCR/AI/Rule Engine appears

---

## 5. Files Allowed

Source: proto/ui.html, proto/e2e_ui_test.py
Docs: docs/process/QUICK_TEST_GUIDE.md, status files, sprint card, CURRENT_STATUS.md, log.md, etc.

## 6. Files Forbidden

- proto/server.py
- proto/requirements.txt
- Legal/OCR/AI/Rule Engine logic
- Save/load or export model changes
