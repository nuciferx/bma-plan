# WIDGET_MENU_PLACEMENT_SYSTEM.md — Sprint Report

Date: 2026-05-11
Sprint: Widget/Menu Placement System
Result: PASS — py_compile + smoke + full

---

## Goal

Create a safe Widget/Menu placement system that lets users control individual widget visibility, region (left/right/hidden), order, and size for the side panels — without touching backend, measurement math, save/load schema, or coordinate logic.

The previous "Layout Options" panel only switched whole sections (Current vs Mockup V3). This sprint adds a finer-grained per-widget mechanism.

---

## Design

- **Storage:** `localStorage` only. Key: `bmaPlan.widgetPlacement.v1`. No `.bmaplan` schema change.
- **Backward-compatible default:** If localStorage is empty, the registry's `defaultRegion / defaultOrder / defaultSize / visible` values reconstruct the current stable left/right layout — no visible difference vs prior sprint.
- **Locked-by-default policy:** Most existing UI blocks are tightly coupled to their original parent (Sheets, Layers, Inspection Status, etc.). They are registered but `locked:true` and `allowedRegions` is restricted to their original region. Only visibility (and size class) is changeable for locked items. They never move regions.
- **Movable widgets:** `workflow`, `reviewWarnings`, `exportReady` can move between `left`, `right`, and `hidden`. They are the minimum needed to satisfy region-move E2E coverage without destabilising the left/right workflow.
- **Re-parenting strategy:** Wrap & reorder rather than rewrite. Two zone containers `#wp-left-zone` (inside `.sidebar-scroll-body`) and `#wp-right-zone` (inside `#right-panel`) are the destinations for movable widgets. Default position is preserved by appending movable widgets to `#wp-left-zone` only when they are placed in `left` (which is also their default region) — the zone sits at the same point in the sidebar where these widgets already lived.
- **Order:** Applied via inline `style.order` on each widget element. The hosting `flex-direction: column` containers (`sidebar-scroll-body`, `wp-left-zone`, `wp-right-zone`) honor flex order.
- **Size:** Applied via CSS class `.widget-size-{collapsed,small,medium,large,full}`. `collapsed` hides body details but preserves DOM and internal state.
- **Visibility:** Applied via CSS class `.widget-hidden` (`display:none !important`). Hidden does not destroy state.
- **Robustness:** `normalizeWidgetPlacement(cfg)` ignores unknown IDs, drops illegal regions for a widget, drops locked-cross-region moves, dedupes duplicate IDs, falls back to defaults on missing entries, and treats malformed JSON as empty.

---

## Registry Items

| id | label | category | default region | allowed regions | default size | locked |
|----|-------|----------|----------------|------------------|--------------|--------|
| `pageInfo` | Page Info | info | left | left, hidden | small | yes |
| `inspectionStatus` | Inspection Status | status | left | left, hidden | medium | yes |
| `workflow` | Workflow Status | status | left | left, right, hidden | small | no |
| `scaleStatus` | Scale Status | status | top | top | small | yes |
| `reviewWarnings` | Review Warnings | review | left | left, right, hidden | small | no |
| `exportReady` | Export Ready | export | left | left, right, hidden | small | no |
| `sheets` | Sheets | navigation | left | left | full | yes |
| `objects` | Objects | navigation | left | left | full | yes |
| `properties` | Properties | navigation | left | left | full | yes |
| `layerContext` | Layer Context | layer | right | right | small | yes |
| `currentPageLayers` | Current Page Layers | layer | right | right | full | yes |

### Why locked

- `sheets`, `objects`, `properties` — left-panel tab content; relocating them would break `setSidebarMode()` toggling and tab switching.
- `inspectionStatus` — managed by `updateInspectionPanel()` and lives outside the sidebar scroll body.
- `pageInfo` — lives between the sidebar header and the mode tabs; moving it would disturb that header strip.
- `scaleStatus` — embedded in the topbar; relocating it would break the topbar grid layout.
- `layerContext`, `currentPageLayers` — driven by `buildRightPanel()`; relocating them risks breaking the page-scoped layers workflow.

Locked widgets are still in the registry so visibility and size class can be toggled safely.

---

## localStorage Key

```
bmaPlan.widgetPlacement.v1
```

### Default config (rebuilt from registry defaults)

```json
{
  "left":  [
    {"id":"pageInfo","order":1,"size":"small","visible":true},
    {"id":"inspectionStatus","order":2,"size":"medium","visible":true},
    {"id":"workflow","order":3,"size":"small","visible":true},
    {"id":"reviewWarnings","order":5,"size":"small","visible":true},
    {"id":"exportReady","order":6,"size":"small","visible":true},
    {"id":"sheets","order":10,"size":"full","visible":true},
    {"id":"objects","order":11,"size":"full","visible":true},
    {"id":"properties","order":12,"size":"full","visible":true}
  ],
  "right": [
    {"id":"layerContext","order":1,"size":"small","visible":true},
    {"id":"currentPageLayers","order":2,"size":"full","visible":true}
  ]
}
```

`scaleStatus` (region=`top`) is not stored in `left/right`; it is recorded in the registry only and remains in its native topbar slot.

---

## Files Changed

- `proto/ui.html`
  - Added `#wp-left-zone` inside `.sidebar-scroll-body` (between `#widget-export-ready` and `#sidebar-content`).
  - Added `#wp-right-zone` inside `#right-panel` (after `#rp-content`).
  - Added new section "G. Widget / Menu Placement" inside `#ui-layout-panel` with search box, category select, list container, reset, and apply buttons.
  - Added JS: `WIDGET_MENU_REGISTRY`, `getDefaultWidgetPlacement()`, `loadWidgetPlacement()`, `saveWidgetPlacement()`, `normalizeWidgetPlacement()`, `resetWidgetPlacement()`, `setWidgetPlacementOption()`, `applyWidgetPlacement()`, `renderWidgetPlacementOptions()`, `filterWidgetPlacementList()`, `_captureWidgetOriginalParents()`.
  - Added `loadWidgetPlacement()` call after `loadPanelLayout()`.
- `proto/static/css/app.css`
  - Added `.wp-zone`, `#wp-left-zone`, `#wp-right-zone`, `.widget-hidden`, `.widget-size-*`, and the `ulp-wp-*`, `.wp-row`, `.wp-info`, `.wp-name`, `.wp-desc`, `.wp-toggle`, `.wp-region`, `.wp-size`, `.wp-order`, `.wp-lock` styles.
- `proto/e2e_ui_test.py`
  - Added 15 JS assertions and 15 Python guard checks for the placement system.

No changes were made to: `proto/server.py`, save/load code, export code, scale math, coordinate conversion, PDF render logic, or `.bmaplan` schema.

---

## Tests Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

New assertions (all True):

| Key | Check |
|-----|-------|
| `widgetPlacementRegistryExists` | `WIDGET_MENU_REGISTRY` is a non-empty array (>= 10 entries) |
| `widgetPlacementHelpersExist` | All 9 helper functions defined |
| `widgetPlacementSearchBox` | `#wp-search` and `#wp-category` exist |
| `widgetPlacementListRendered` | At least 5 `.wp-row` rows in `#wp-list` |
| `widgetPlacementKeyWritten` | `bmaPlan.widgetPlacement.v1` written after option change |
| `widgetVisibilityToggleWorks` | `.widget-hidden` class toggled on `#widget-review-warnings` |
| `widgetOrderInputWorks` | `style.order="9"` applied via order input |
| `widgetRegionMoveWorks` | `#widget-review-warnings` moves to `#wp-right-zone` then back into `#sidebar` |
| `widgetSizeClassApplies` | `.widget-size-collapsed` and `.widget-size-large` classes apply |
| `widgetPlacementResetWorks` | Reset restores defaults |
| `widgetPlacementMalformedJsonSafe` | Loader does not crash on bad JSON |
| `widgetLockedRespected` | `currentPageLayers` (locked) stays in right panel after region change attempt |
| `widgetLeftPanelScrollOk` | `.sidebar-scroll-body` keeps `overflow-y: auto` |
| `widgetRightPanelScrollOk` | `#rp-content` keeps `overflow-y: auto` |
| `widgetCurrentPageLayersVisible` | `#rp-content` not hidden by placement |

Existing assertions for inspection panel, page info widget, review warning widget, export ready widget, layers panel, scale badge, drawing, export, save/load, and real-PDF round-trip all remain PASS.

---

## Known Gaps

- "Active Layer Detail", "Compatibility Properties", and "Summary Widget" are mentioned in the sprint brief but are not yet first-class widgets in the registry. They are rendered as parts of the right-panel layer view (`buildRightPanel()`), not as independent DOM blocks, so they are not safely movable today. Future sprint can register `#rp-properties-section` / `#rp-object-tree-section` once they become independent widgets.
- Status Bar items (`#bottombar`) are intentionally not registered — moving them risks breaking layout and tooling indicators.
- The size dimensions for `small`, `medium`, `large`, `full` are visually identical today (only `collapsed` has visible effect). The classes are applied to make further visual differentiation a CSS-only change.
- The "Apply" button is a no-op convenience (changes already apply live on each option change) — kept for the requirement that the UI must provide one.

---

## Next Safe Action

- Manual UI walkthrough: open `proto/ui.html`, open the Layout Options panel, exercise the Widget / Menu section (search, category filter, visibility toggles, region select for `reviewWarnings`, size collapsed/full, reset). Confirm the left and right panels behave as expected and that current page layers, area drawing, opening drawing, and export still work.
- If everything looks good, proceed to the next polish sprint from `NEXT_ACTIONS.md` (e.g., `RUN_SAVE_STATE_LABEL_FIX.md` for the cosmetic TC-12-B1 issue).
