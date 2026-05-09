# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Left Inspection Status Panel

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/ui.html`: Added `#inspection-panel` div between `#lp-page-info` and `#sidebar-mode-tabs`.
  Added `toggleInspectionPanel()` and `updateInspectionPanel()` functions. `updateBottomBar()`
  now calls `updateInspectionPanel()` on each update. Global `inspPanelCollapsed=false`.
- `proto/static/css/app.css`: Added 22 CSS classes — `.inspection-panel`, `.isp-hdr`,
  `.isp-body`, `.isp-body.collapsed`, `.isp-wf-row` (+ `.done`, `.current`, `.warn` modifiers),
  `.isp-section-title`, `.isp-kv`, `.isp-warn-badge`, `.isp-next-action`, `.isp-wf-dot`.
- `proto/e2e_ui_test.py`: Added 6 new JS evaluate keys + 6 Python assertions:
  `inspectionPanelVisible`, `inspectionPanelInSidebar`, `inspectionPanelNotInCanvas`,
  `inspectionPanelWorkflowVisible`, `inspectionPanelContextVisible`, `inspectionPanelToggleWorks`.
- Sprint card moved to `sprints/completed/2026-05-09-left-inspection-status-panel/`.

## What Did Not Change

- No `proto/server.py` changes. No export/save-load changes. No legal/OCR/AI/Rule Engine.
- Tabs (Sheets/Objects/Properties) unaffected — panel IDs not in `setSidebarMode()` hide list.
- All 17 + 6 prior assertions still PASS.

---

# Previous: Static 404 Fix (Critical Regression — Unconditional Mount)

Date: 2026-05-09

## Outcome: PASS

## Root Causes Fixed

Two compounding bugs caused `/static/*` to return 404:

1. **`aiofiles` not installed** — `StaticFiles` (starlette) requires `aiofiles` for async file
   serving. Without it, `StaticFiles(directory=...)` raises `RuntimeError` at init time.
2. **Guard hid the failure** — `if _STATIC_DIR.exists(): app.mount(...)` meant the mount was
   attempted but the `RuntimeError` from missing `aiofiles` caused it to fail silently,
   leaving `/static/*` unregistered. All static requests returned 404.

## What Changed

- `proto/server.py`: Removed `if _STATIC_DIR.exists():` guard. Mount now unconditional.
  Added `print(f"[static] serving from: {_STATIC_DIR}")` for startup confirmation.
  Renamed `_STATIC_DIR` → uses `_BASE_DIR / "static"` for clarity.
- `proto/requirements.txt`: Added `aiofiles` (previous commit `65f5a65`).
- `proto/static/css/app.css`: Removed UTF-8 BOM (previous commit `65f5a65`).
- Installed `aiofiles==25.1.0` into the active Python environment.

## What Did Not Change

- No ui.html changes. No export/save-load changes. No legal/OCR/AI/Rule Engine.
- All 17 E2E test assertions still PASS including cssVarLoaded, all widget visibility.

---

# Previous: CSS BOM Fix

Date: 2026-05-09

## Outcome: PASS

## Root Cause Fixed

`proto/static/css/app.css` had a UTF-8 BOM (`\xef\xbb\xbf`) at byte position 0, written
when the file was extracted from ui.html. Some browsers fail to apply a stylesheet with
a BOM prefix — the CSS text starts with `*{` but the browser sees `\xef\xbb\xbf*{` and
may reject the first rule, causing the page to render as unstyled HTML.

## What Changed

- `proto/static/css/app.css`: BOM stripped (bytes 0-2 removed). Content unchanged, 315 lines.
- `proto/server.py` line 1298: `UI_PATH = os.path.join(os.path.dirname(__file__), "ui.html")`
  → `UI_PATH = Path(__file__).resolve().parent / "ui.html"` (consistent with `_STATIC_DIR`).
- `proto/requirements.txt`: Added `aiofiles` for explicit StaticFiles support.

## What Did Not Change

- No ui.html changes. No export/save-load changes. No legal/OCR/AI/Rule Engine.
- All 17 E2E test assertions still PASS including all widget visibility and cssVarLoaded.

---

# Previous: Mockup Layout Mapping (Docs Only)

Date: 2026-05-09

## Outcome: PASS (docs only, no source changes)

## What Changed

- `docs/design/MOCKUP_LAYOUT_MAPPING.md` — created. Full map of mockup v3 vs. current UI:
  13 mockup zones mapped, 10 widgets mapped, gap classification table, forbidden items list.
- `docs/design/MOCKUP_IMPLEMENTATION_PLAN.md` — created. 6 sequenced implementation sprints.
- Status docs updated.
- Sprint card: sprints/completed/2026-05-09-mockup-layout-mapping/

## Key Findings

| Classification | Count |
|----------------|-------|
| DONE (already implemented) | 10 |
| SMALL POLISH | 9 |
| MEDIUM IMPLEMENTATION | 4 |
| LATER | 2 |
| FORBIDDEN | 3 |

Next sprint: Widget Placement Polish (Sprint 1 of 6, LOW risk).

## What Did Not Change

- No runtime source changes. proto/ui.html, proto/static/*, proto/server.py unchanged.
- Baseline proto 797a4a2 still valid.

---

# Previous: Static Asset Healthcheck

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
