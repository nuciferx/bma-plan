# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Static Asset Healthcheck

Date: 2026-05-09

## Outcome: PASS

## Root Cause Fixed

`os.path.dirname(__file__)` returns `""` when `__file__` has no directory component
(e.g., `python server.py` from `proto/`). `os.path.join("", "static")` = `"static"` —
a CWD-relative path that breaks if CWD ≠ `proto/`.

## What Changed

- `proto/server.py`: Added `from pathlib import Path`. Changed `_STATIC_DIR` from
  `os.path.join(os.path.dirname(__file__), "static")` to
  `Path(__file__).resolve().parent / "static"` (always absolute). Updated `os.path.exists`
  to `_STATIC_DIR.exists()` and `directory=str(_STATIC_DIR)`.
- `proto/e2e_ui_test.py`: Added 4 new JS evaluate keys + 4 Python assertions:
  `cssLinkPresent`, `cssVarLoaded`, `semanticMetaJsLoaded`, `openingParentJsLoaded`.

## What Did Not Change

- No UI changes. No export/save-load changes. No legal/OCR/AI/Rule Engine.
- `proto/ui.html` unchanged — static paths were already correct (`/static/css/app.css` etc.).
- All existing 17 test assertions still PASS.

---

# Previous: Visible Test Widgets UI

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/ui.html` — +9 lines (1111→1120): `#widget-review-warnings`, `#widget-export-ready`
  divs added after `#workflow-card` in left sidebar. `updateWidgets()` call added to
  `updateBottomBar()`. `updateWidgets()` function definition added.
- `proto/static/css/app.css` — +8 lines (307→315): `.widget-card`, `.widget-title`,
  `.widget-body`, `.widget-link`, `.widget-link:hover`, `.widget-badge`, `.widget-badge.ok`,
  `.widget-badge.warn`, `.widget-badge.error`.
- `proto/e2e_ui_test.py` — +8 lines: 4 JS evaluate keys + 4 Python assertions for
  `scaleStatusWidgetVisible`, `pageInfoWidgetVisible`, `reviewWarningWidgetVisible`,
  `exportReadyWidgetVisible`.
- Sprint card: sprints/completed/2026-05-09-visible-test-widgets-ui/

## What Did Not Change

- No `proto/server.py` changes. No export logic changes. No legal/OCR/AI/Rule Engine.
- All existing 17 test assertions still PASS.

---

# Previous: E2E Test Split Audit

Date: 2026-05-09

## Outcome: AUDIT_ONLY_STOP

- proto/e2e_ui_test.py (1525 lines) — stateful pipeline, AUDIT_ONLY_STOP.
- docs/design/E2E_TEST_SPLIT_AUDIT.md created.

---

# Previous: Frontend UI HTML Split

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/static/css/app.css` — new file; 307 lines extracted from ui.html `<style>` block.
- `proto/static/js/semantic-meta.js` — new file; 6 constants + 2 functions (isAreaSemanticTag, deriveMeasurementMeta) extracted.
- `proto/static/js/opening-parent.js` — new file; 5 functions (openingProbePoints, openingInsidePoly, openingParentCandidates, linkOpeningParent, linkOpeningsInStore) extracted.
- `proto/server.py` — added StaticFiles mount (guarded by os.path.exists). 3 lines added.
- `proto/ui.html` — 1437 → 1111 lines (-326 lines, -23%); `<style>` replaced with `<link>`, 2 `<script src>` added, 13 inline definitions removed.
- Sprint card moved to sprints/completed/.

## What Did Not Change

- No behavior changes — all extracted JS runs in same global scope.
- No save/load format changes.
- No export behavior changes.
- No legal/OCR/AI/Rule Engine.

## Files Touched

- `proto/server.py`, `proto/export/__init__.py`, `proto/export/semantic_metadata.py`, `proto/export/xlsx_helpers.py`
- `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md`, `docs/design/E2E_SPLIT_PLAN.md`, `docs/status/READ_ORDER.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`
- `docs/status/LATEST_STATUS.md`, `docs/status/NEXT_ACTIONS.md`, `docs/status/COMMIT_HISTORY.md`
