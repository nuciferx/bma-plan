# RUN_STATIC_ASSET_HEALTHCHECK.md

## 0. Sprint Identity

Sprint Name: Static Asset Healthcheck
Sprint Type: Narrow Bug-Fix + E2E Guard Sprint
Status: IN PROGRESS
Date: 2026-05-09

---

## 1. Baseline

Baseline commit: a2a6e81 (proto) / 05ef1d1 (root)
py_compile PASS · smoke PASS · full PASS (confirmed from Visible Test Widgets sprint)

Source file sizes at baseline:
- proto/server.py: ~1290 lines
- proto/e2e_ui_test.py: 1465 lines (after CRLF normalization)

---

## 2. Problem

After Frontend UI HTML Split, CSS and JS were extracted to proto/static/.
StaticFiles mount in server.py uses `os.path.dirname(__file__)` which returns `""`
when run as `python server.py` from the proto/ directory (no directory component in __file__).
`os.path.join("", "static")` = `"static"` — a CWD-relative path.
If CWD ≠ proto/, the /static/ route silently does not mount, serving 404 for all assets.

---

## 3. Root Cause

`os.path.dirname(__file__)` is CWD-dependent when __file__ is a bare filename.
`Path(__file__).resolve().parent` always gives the absolute directory of server.py.

---

## 4. Scope

### In Scope
- Fix _STATIC_DIR in proto/server.py to use Path(__file__).resolve().parent
- Add E2E assertions: cssLinkPresent, cssVarLoaded, semanticMetaJsLoaded, openingParentJsLoaded

### Not Scope
- UI redesign, feature changes, export/save-load changes, legal/OCR/AI/Rule Engine
- server.py rewrite beyond the 3-line _STATIC_DIR fix

---

## 5. Files Allowed

Source:
- proto/server.py
- proto/e2e_ui_test.py

Docs:
- CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md, PATCH_SUMMARY.md, TEST_RESULT.md
- sprints/active/ → sprints/completed/

## 6. Files Forbidden

- proto/ui.html (paths already correct)
- proto/export/*
- proto/static/css/app.css
- proto/static/js/semantic-meta.js
- proto/static/js/opening-parent.js

---

## 7. Fix Contract

- /static/css/app.css must return 200 regardless of CWD
- /static/js/semantic-meta.js must return 200 regardless of CWD
- /static/js/opening-parent.js must return 200 regardless of CWD
- CSS variable --blue (defined in app.css :root) must be non-empty string after load
- AREA_SEMANTIC_TAGS (from semantic-meta.js) must be defined in global scope
- openingProbePoints (from opening-parent.js) must be defined in global scope

---

## 8. Test Plan

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py   # PASS
python proto/e2e_ui_test.py smoke                            # PASS (+ new assertions)
python proto/e2e_ui_test.py full                             # PASS
```

New assertions added to MAIN_UI_OK:
- cssLinkPresent
- cssVarLoaded
- semanticMetaJsLoaded
- openingParentJsLoaded

---

## 9. Acceptance Criteria

- `Path(__file__).resolve().parent / "static"` used in server.py
- 4 new MAIN_UI_OK assertions all PASS
- No existing assertions broken
- No forbidden Phase 1 strings introduced

## 10. Stop Conditions

- Open PDF breaks
- Set Scale breaks
- Any existing test assertion fails
- Implementation requires broad server rewrite

---

## 11. Checklist

### Part A — server.py
- [x] Add `from pathlib import Path` to imports
- [x] Change `_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")` to use Path
- [x] Change `os.path.exists(_STATIC_DIR)` to `_STATIC_DIR.exists()`
- [x] Pass `str(_STATIC_DIR)` to StaticFiles

### Part B — e2e_ui_test.py
- [x] Add cssLinkPresent, cssVarLoaded, semanticMetaJsLoaded, openingParentJsLoaded to JS evaluate
- [x] Add 4 Python assertion checks

### Part C — Testing
- [x] py_compile PASS
- [x] smoke PASS
- [x] full PASS

### Part D — Doc Update and Commit
- [x] Update status docs
- [x] Commit proto: fix static asset loading after frontend split
- [x] Move sprint card to sprints/completed/
- [x] Commit root: docs: record static asset healthcheck

---

## 12. Before/After

| File | Before | After |
|------|--------|-------|
| proto/server.py | CWD-relative _STATIC_DIR | absolute Path-based _STATIC_DIR |
| proto/e2e_ui_test.py | no static asset assertions | +4 assertions |
