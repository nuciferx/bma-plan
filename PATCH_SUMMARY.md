# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Left Properties Migration

Date: 2026-05-09

## Outcome: PASS

## What Changed

- `proto/ui.html` — added `data-mode` attributes and `onclick="setSidebarMode('...')"` to 3 `.sidebar-mode-tab` divs.
- `proto/ui.html` — added `#lp-objects-content` and `#lp-properties-content` hidden divs after `#sidebar-content`.
- `proto/ui.html` — added `let lSidebarMode="sheets"` global.
- `proto/ui.html` — added `setSidebarMode(mode)`: toggles tab `.active` class; shows/hides sheets content vs objects/properties content.
- `proto/ui.html` — added `buildLeftObjects()`: flat object list; clicking auto-selects and switches to Properties.
- `proto/ui.html` — added `buildLeftProperties()`: full property editor in left panel; placeholder when nothing selected.
- `proto/ui.html` — `selectObjectFromTree`, `_initDrag`, `showObjPicker` row click: each calls `setSidebarMode("properties")` to auto-switch on selection.
- `proto/e2e_ui_test.py` — added `leftPanelTabsOk` IIFE to MAIN_UI_OK; added Python assertion.

## What Did Not Change

- No `proto/server.py` changes.
- No save/load format changes.
- No legal/OCR/AI/Rule Engine/FAR/OSR/pass-fail logic.
- Right panel properties section (`#rp-properties-section`, `#rp-object-tree-section`) remains present.

## Files Touched

- `proto/ui.html`, `proto/e2e_ui_test.py`
- `sprints/completed/2026-05-09-left-properties-migration/RUN_LEFT_PROPERTIES_MIGRATION.md`
- `CURRENT_STATUS.md`, `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `log.md`
- `docs/status/`, `docs/archive/` (token reduction sprint)
