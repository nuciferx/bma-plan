# RUN_MOCKUP_LAYOUT_MAPPING.md

## 0. Sprint Identity

Sprint Name: Mockup Layout Mapping
Sprint Type: Fast Guarded UI Planning Sprint (Docs Only)
Status: IN PROGRESS
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: 797a4a2 (proto) / c19bf65 (root)
py_compile PASS · smoke PASS · full PASS (confirmed from Static Asset Healthcheck sprint)
No source code changes in this sprint.

---

## 2. Goal

Map the existing BMA-Plan UI to the intended mockup v3 design layout.
Identify every gap, classify by effort, and produce a sequenced implementation plan.
This sprint is mapping/planning only — no UI redesign, no implementation.

---

## 3. Scope

### In Scope
- Read mockup v3 HTML and produce layout mapping document
- Read current ui.html / app.css and produce current structure map
- Create docs/design/MOCKUP_LAYOUT_MAPPING.md
- Create docs/design/MOCKUP_IMPLEMENTATION_PLAN.md
- Update status docs and commit root

### Not Scope
- Any changes to proto/ui.html, proto/static/css/app.css, proto/*.js
- Any backend changes
- Any visual implementation
- Legal/OCR/AI/Rule Engine

---

## 4. Files Allowed

Docs (write):
- docs/design/MOCKUP_LAYOUT_MAPPING.md
- docs/design/MOCKUP_IMPLEMENTATION_PLAN.md
- CURRENT_STATUS.md
- docs/status/LATEST_STATUS.md, NEXT_ACTIONS.md, KNOWN_ISSUES.md, COMMIT_HISTORY.md
- log.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md
- sprints/active/RUN_MOCKUP_LAYOUT_MAPPING.md → sprints/completed/

Source (read only):
- docs/design/bma-plan-mockup-v3.html
- proto/ui.html
- proto/static/css/app.css

## 5. Files Forbidden (write)

- proto/ui.html
- proto/static/css/app.css
- proto/static/js/*.js
- proto/server.py
- proto/e2e_ui_test.py
- proto/export/*

---

## 6. Stop Conditions

- Any source file needs editing to complete this sprint
- Scope expands into visual implementation
- Legal/OCR/AI/Rule Engine scope appears

---

## 7. Checklist

### Part A — Mapping Document
- [x] Read mockup v3 HTML structure (all zones)
- [x] Read current ui.html structure (all zones)
- [x] Create docs/design/MOCKUP_LAYOUT_MAPPING.md (structure map + gap table + widget map)

### Part B — Implementation Plan
- [x] Create docs/design/MOCKUP_IMPLEMENTATION_PLAN.md (6 sequenced sprints)

### Part C — Status + Commit
- [x] Update CURRENT_STATUS.md, docs/status/*, log.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md
- [x] Move sprint card to sprints/completed/
- [x] Commit root: docs: add mockup layout mapping plan

---

## 8. Testing

No app tests required (docs only, no source changes).
Verified: git status --short shows only doc files staged.
