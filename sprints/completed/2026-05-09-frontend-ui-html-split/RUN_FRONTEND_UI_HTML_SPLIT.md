# RUN_FRONTEND_UI_HTML_SPLIT.md

## 0. Sprint Identity

Sprint Name: Frontend UI HTML Split
Sprint Type: Refactor / Token Reduction
Status: COMPLETE
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: 599efca (root) / fb89ecd (proto)
py_compile PASS · smoke PASS (confirmed at sprint start)

Source file sizes at baseline:
- proto/ui.html: 1437 lines, 233185 bytes
- proto/server.py: ~1290 lines
- proto/e2e_ui_test.py: 1525 lines

---

## 2. Goal

Reduce token load from proto/ui.html by safely extracting:
1. CSS block → proto/static/css/app.css
2. Semantic metadata constants + helpers → proto/static/js/semantic-meta.js
3. Opening parent geometry helpers → proto/static/js/opening-parent.js

Add StaticFiles serving to server.py (minimal: 3 lines, guarded by os.path.exists).
Behavior must remain 100% identical. Tests must PASS throughout.

---

## 3. Checklist

### Part A — Static Serving Infrastructure
- [x] Add `from fastapi.staticfiles import StaticFiles` to server.py imports
- [x] Add `_STATIC_DIR` + guarded `app.mount("/static", StaticFiles(...))` after `app = FastAPI()`
- [x] py_compile PASS after server.py edit

### Part B — CSS Extraction
- [x] Create proto/static/css/app.css (content from ui.html lines 8-313)
- [x] Replace `<style>...</style>` block with `<link rel="stylesheet" href="/static/css/app.css">`
- [x] Smoke test: layout assertions still PASS

### Part C — Semantic Metadata JS
- [x] Create proto/static/js/semantic-meta.js
  - AREA_SEMANTIC_TAGS, SEMANTIC_PROFILE_MAP, SEMANTIC_CATEGORY_MAP
  - SEMANTIC_REPORT_TARGET_MAP, SEMANTIC_LAW_BASIS_MAP, SEMANTIC_COUNTING_RULE_MAP
  - isAreaSemanticTag, deriveMeasurementMeta
- [x] Add `<script src="/static/js/semantic-meta.js"></script>` before inline `<script>`
- [x] Remove 8 declarations from ui.html inline script

### Part D — Opening Parent JS
- [x] Create proto/static/js/opening-parent.js
  - openingProbePoints, openingInsidePoly, openingParentCandidates
  - linkOpeningParent, linkOpeningsInStore
- [x] Add `<script src="/static/js/opening-parent.js"></script>` before inline `<script>`
- [x] Remove 5 function definitions from ui.html inline script

### Part E — Test and Commit
- [x] py_compile PASS
- [x] smoke PASS (all 14 assertions)
- [x] full PASS (all 17 assertions)
- [x] Commit proto: refactor: extract static CSS and JS modules from ui.html

### Part F — Doc Update and Root Commit
- [x] Update CURRENT_STATUS.md, docs/status/, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md, log.md
- [x] Move sprint card to sprints/completed/
- [x] Commit root: refactor: frontend html split sprint - static CSS and JS extracted

---

## 4. Stop Conditions

- Open PDF breaks
- Set Scale breaks
- Area/Opening drawing breaks
- Properties panel breaks
- Opening parent reassignment breaks
- Export breaks
- Static serving causes 404 on /static/* routes
- Layout E2E assertions fail (toolbarFitsWorkspace, toolbarBelowHeader, etc.)
- Any test assertion fails with non-local fix

---

## 5. Files Allowed

Source:
- proto/ui.html
- proto/server.py (StaticFiles mount only)
- proto/static/css/app.css (new)
- proto/static/js/semantic-meta.js (new)
- proto/static/js/opening-parent.js (new)

Docs:
- CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md
- docs/status/, docs/design/
- sprints/active/ → sprints/completed/

## 6. Files Forbidden

- proto/e2e_ui_test.py (no test changes needed)
- Legal/OCR/AI/Rule Engine
- Export behavior changes
- Save/load migration
- UI redesign or new features

---

## 7. Before/After Line Counts

| File | Before | After |
|------|--------|-------|
| proto/ui.html | 1437 | 1111 |
| proto/static/css/app.css | — | 307 |
| proto/static/js/semantic-meta.js | — | 10 |
| proto/static/js/opening-parent.js | — | 16 |
| proto/server.py | ~1290 | ~1294 |
