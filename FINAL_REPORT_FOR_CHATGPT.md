# FINAL_REPORT_FOR_CHATGPT.md — Latest Sprint Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Widget / Menu Placement System — PASS

> Date: 2026-05-11
> Sprint: Widget / Menu Placement System
> Result: PASS — py_compile + smoke + full
> Proto HEAD: (current working tree)

---

## Goal

Replace the coarse-grained "Current vs Mockup V3" Layout Options with a finer Widget/Menu placement system that lets users control visibility, region, order, and size of individual UI blocks in the left and right panels. No backend changes, no measurement / scale / coordinate / save-load / export changes, no `.bmaplan` schema change. Storage is `localStorage`-only.

---

## Changes Applied

### 1. HTML structure (`proto/ui.html`)

- Inserted `<div id="wp-left-zone" class="wp-zone">` inside `.sidebar-scroll-body` between the existing `#widget-export-ready` and `#sidebar-content`. This is where movable widgets land when placed in the left region.
- Inserted `<div id="wp-right-zone" class="wp-zone">` inside `#right-panel` after `#rp-content`. This is where movable widgets land when placed in the right region.
- Added a new "G. Widget / Menu Placement" section inside `#ui-layout-panel` containing:
  - `#wp-search` search box
  - `#wp-category` category filter (`all`, `info`, `status`, `navigation`, `layer`, `review`, `export`)
  - `#wp-list` widget list container
  - `#ulp-wp-reset` reset button → calls `resetWidgetPlacement()`
  - `#ulp-wp-apply` apply button → calls `applyWidgetPlacement()`

### 2. JS (`proto/ui.html`)

Added a new "Widget / Menu Placement System" block:

- `WIDGET_PLACEMENT_KEY = 'bmaPlan.widgetPlacement.v1'`
- `WIDGET_MENU_REGISTRY` — array of widget descriptors with `id`, `label`, `description`, `category`, `selector`, `defaultRegion`, `allowedRegions`, `defaultOrder`, `defaultSize`, `visible`, `locked`.
- `getDefaultWidgetPlacement()` — rebuilds defaults from registry.
- `loadWidgetPlacement()` — reads localStorage; falls back to defaults on missing / malformed JSON.
- `saveWidgetPlacement(cfg)` — writes JSON.
- `normalizeWidgetPlacement(cfg)` — drops unknown IDs, drops illegal regions, drops locked-cross-region moves, dedupes IDs, fills missing widgets with defaults.
- `resetWidgetPlacement()` — wipes localStorage key, restores defaults.
- `setWidgetPlacementOption(id, field, value)` — updates a single field (`region`, `visible`, `order`, `size`); enforces lock / allowedRegions; persists.
- `applyWidgetPlacement()` — for each registry item: clears prior size class, optionally adds `.widget-hidden`, applies `.widget-size-*`, sets `style.order`, re-parents into `#wp-left-zone` / `#wp-right-zone` (movable items) or restores to its captured original parent (locked items).
- `renderWidgetPlacementOptions()` — rebuilds the `#wp-list` rows reflecting current state.
- `filterWidgetPlacementList()` — re-renders with current search + category filter applied.
- `_captureWidgetOriginalParents()` — captures original DOM parent + nextSibling for each registry widget on first call so locked widgets can be reliably restored.

Startup: `loadWidgetPlacement()` is invoked after `loadPanelLayout()`.

### 3. CSS (`proto/static/css/app.css`)

- `.wp-zone { display:flex; flex-direction:column; }` and zone-specific styling.
- `.widget-hidden { display:none !important; }`.
- `.widget-size-collapsed` collapses inner body content while preserving DOM/state.
- `.widget-size-small/medium/large/full` are present (currently visually neutral — class hooks ready for future visual tuning).
- Layout-panel widget-row styles (`.ulp-wp-search`, `.ulp-wp-filter`, `.ulp-wp-list`, `.wp-row`, `.wp-info`, `.wp-name`, `.wp-desc`, `.wp-toggle`, `.wp-region`, `.wp-size`, `.wp-order`, `.wp-lock`).

### 4. E2E (`proto/e2e_ui_test.py`)

15 new JS assertions + 15 new Python guard checks covering registry presence, helper presence, search/filter UI, list rendering, persistence, visibility, order, region move, size class, reset, malformed-JSON tolerance, locked-widget protection, scroll body health on both panels, and current-page-layers visibility.

---

## Registry (initial)

| id | region | locked | allowed regions |
|----|--------|--------|------------------|
| `pageInfo` | left | yes | left, hidden |
| `inspectionStatus` | left | yes | left, hidden |
| `workflow` | left | no | left, right, hidden |
| `scaleStatus` | top | yes | top |
| `reviewWarnings` | left | no | left, right, hidden |
| `exportReady` | left | no | left, right, hidden |
| `sheets` | left | yes | left |
| `objects` | left | yes | left |
| `properties` | left | yes | left |
| `layerContext` | right | yes | right |
| `currentPageLayers` | right | yes | right |

`Active Layer Detail`, `Compatibility Properties`, `Summary Widget`, and Status Bar items from the brief are intentionally not in the registry yet — they are rendered as parts of bigger components (`buildRightPanel`, `#bottombar`) and are not safely movable today. Documented as known gaps.

---

## Tests

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

All 15 new placement assertions are True. All existing assertions (inspection panel, page info widget, review warning widget, export ready widget, layers panel, scale badge, drawing, save/load, export, real-PDF round-trip, panel layout, layout options, etc.) remain PASS.

---

## What Did NOT Change

- `proto/server.py` — untouched.
- `.bmaplan` schema — unchanged.
- `save/load`, `export`, measurement, scale, coordinate, snap, PDF render — unchanged.
- Existing `bmaPlan.uiLayoutOptions.v1` and `bmaPlan.panelLayoutOptions.v1` behavior — unchanged.
- No new dependency, no new endpoint, no new tool.

---

## Stop Conditions

None triggered. Tests pass; current page layers still visible; left/right scroll still works; drawing/export workflow uninterrupted.

---

## Known Gaps

- Active Layer Detail / Compatibility Properties / Summary Widget are not yet first-class registry entries.
- Size classes `small/medium/large/full` are class hooks today (only `collapsed` produces visible change). Visual differentiation can be added later via CSS-only changes.
- Apply button is a no-op convenience (state already applies live on every change).

---

## Next Safe Action

Manual UI walkthrough of the new section (search, category filter, visibility toggle, region move for `reviewWarnings`, size collapsed/large, reset). Then resume the queued polish sprints (e.g., `RUN_SAVE_STATE_LABEL_FIX.md`).

---

> Previous report history archived in `docs/archive/`.
