# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Mockup V3 Alignment — Phase A (Subtractive Removal)

Branch: feature/mockup-v3-alignment

Date: 2026-05-11

## Outcome: PASS

## Plan
`C:\Users\nucif\.claude\plans\ui-wise-finch.md` — approved 2026-05-11. Phase A is the first of 6 phases (A subtractive → B header rebuild → C panels → D summary widget → E CSS sync → F tests+docs).

## Files Changed

| File | Change |
|------|--------|
| `proto/ui.html` | Removed `#ui-layout-panel` modal (97 lines), `#btn-ui-layout` button, `#inspection-panel`, `#workflow-card`, `#widget-review-warnings`, `#widget-export-ready`, `#wp-left-zone`, `#wp-right-zone`, `#quick-tag-bar`. Removed UI Layout Options, Panel Layout Options, Widget/Menu Placement JS systems. Stubbed `updateInspectionPanel`, `toggleInspectionPanel`, `updateWidgets`. Removed `loadUiLayout/loadPanelLayout/loadWidgetPlacement` init calls. 1675 → 1252 lines (-423). |
| `proto/e2e_ui_test.py` | Removed ~35 assertions referencing removed systems. Added `leftPanelScrollOk` / `rightPanelScrollOk`. Stubbed workflow assertions to `true`. |

## Files NOT Changed (Deferred to Phase E)

- `proto/static/css/app.css` — dead styles `.ulp-*`, `.isp-*`, `.wp-*`, `.widget-card`, `.workflow-*`, `.wf-row`, `.qt-btn` still present (harmless, will clean in Phase E).

## What Did Not Change

- `proto/server.py` — untouched
- `.bmaplan` schema — unchanged
- Save/load, export, measurement, scale, coordinate, snap, PDF render — unchanged
- `polyMetrics()`, `polyAreaM2()`, `pdfToC`, `cToPdf` — unchanged
- Core workflow (PDF upload → set scale → draw area/opening → picker → layer lock/visibility → save/load → XLSX export) — intact

## Tests

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

All test markers OK: CACHE / SETUP / MAIN_UI / VECTOR / RECAL / SITE_UI / XLSX / PROJECT / RASTER / WHEEL / SNAP / SELECT / SETBACK / EXT_MEASURE / ANNOT / PERSIST / REAL.

## Commits

- proto: `72d621c`
- root: `76977ff`

## Known Risks

- Topbar + tool-row still present (Phase B will replace them with title-bar + menu-bar + ribbon)
- Visual look unchanged from current UI (just less cluttered sidebar — no inspection panel, no workflow card, no widgets)
- localStorage keys for removed systems (`bmaPlan.uiLayoutOptions.v1`, `bmaPlan.panelLayoutOptions.v1`, `bmaPlan.widgetPlacement.v1`) are no longer read but old user data will harmlessly persist

## Merge Recommendation

DO NOT MERGE — Phase A alone is not feature-complete. Continue Phase B–F on this branch first.

---

# Previous: Widget / Menu Placement System

Date: 2026-05-11

## Outcome: PASS

## Files Changed

| File | Change |
|------|--------|
| `proto/ui.html` | Added `#wp-left-zone` inside `.sidebar-scroll-body` and `#wp-right-zone` inside `#right-panel`. Added "G. Widget / Menu Placement" section to `#ui-layout-panel` (search box, category filter, list, reset/apply buttons). Added `WIDGET_MENU_REGISTRY` constant and placement JS (`getDefaultWidgetPlacement`, `loadWidgetPlacement`, `saveWidgetPlacement`, `normalizeWidgetPlacement`, `resetWidgetPlacement`, `setWidgetPlacementOption`, `applyWidgetPlacement`, `renderWidgetPlacementOptions`, `filterWidgetPlacementList`, `_captureWidgetOriginalParents`). Added `loadWidgetPlacement()` startup call. |
| `proto/static/css/app.css` | Added `.wp-zone`, `#wp-left-zone`, `#wp-right-zone`, `.widget-hidden`, `.widget-size-collapsed/small/medium/large/full`, and Layout-panel `ulp-wp-*` / `wp-row` styles. |
| `proto/e2e_ui_test.py` | Added 15 JS assertions + 15 Python guards: `widgetPlacementRegistryExists`, `widgetPlacementHelpersExist`, `widgetPlacementSearchBox`, `widgetPlacementListRendered`, `widgetPlacementKeyWritten`, `widgetVisibilityToggleWorks`, `widgetOrderInputWorks`, `widgetRegionMoveWorks`, `widgetSizeClassApplies`, `widgetPlacementResetWorks`, `widgetPlacementMalformedJsonSafe`, `widgetLockedRespected`, `widgetLeftPanelScrollOk`, `widgetRightPanelScrollOk`, `widgetCurrentPageLayersVisible`. |
| `docs/status/WIDGET_MENU_PLACEMENT_SYSTEM.md` | New sprint report (goal, design, registry, localStorage key, default config, locked widgets and why, files changed, tests, known gaps, next action). |

## What Changed

1. **Per-widget placement control** for left/right panels via the existing Layout Options panel — search, category filter, visibility toggle, region select (`left/right/hidden`), order input, size select.
2. **`WIDGET_MENU_REGISTRY`** records 11 UI blocks with `defaultRegion`, `allowedRegions`, `defaultOrder`, `defaultSize`, `visible`, `locked`.
3. **localStorage-only persistence** with key `bmaPlan.widgetPlacement.v1`. Schema unchanged (`.bmaplan` untouched).
4. **Movable widgets:** `workflow`, `reviewWarnings`, `exportReady`. They can move between left, right, or hidden. Re-parenting uses two dedicated zone containers.
5. **Locked widgets:** `pageInfo`, `inspectionStatus`, `scaleStatus`, `sheets`, `objects`, `properties`, `layerContext`, `currentPageLayers`. Visibility and size class can still be toggled; region is fixed.
6. **CSS size classes** for collapsed/small/medium/large/full (`collapsed` is the only one with visible effect today; others are hooks).
7. **Robust loader**: `normalizeWidgetPlacement()` drops unknown IDs, illegal regions, locked-cross-region moves, dupes; falls back to defaults; tolerates malformed JSON.

## What Did Not Change

- `proto/server.py` not modified.
- `.bmaplan` schema unchanged.
- Save/load, export, measurement, scale, coordinate, snap, PDF render logic unchanged.
- Existing `bmaPlan.uiLayoutOptions.v1` and `bmaPlan.panelLayoutOptions.v1` behavior unchanged.
- No legal/OCR/AI/Rule Engine/FAR/OSR work.
- No drag/drop editor, no widget internal editor.

---

# Previous: Docked Toolbar + Panel Layout Options

Date: 2026-05-11

## Outcome: PASS

## Files Changed

| File | Change |
|------|--------|
| `proto/ui.html` | Moved `#float-toolbar` from outside `#app` into new `#tool-row` between `#topbar` and `#main`. Added panel layout sections E (Left Panel) and F (Right Panel) to `#ui-layout-panel`. Added panel layout JS (`loadPanelLayout`, `savePanelLayout`, `applyPanelLayout`, `setPanelLayoutOption`, `resetPanelLayout`, `_updatePanelLayoutPanelState`). Added `loadPanelLayout()` startup call. |
| `proto/static/css/app.css` | Added `--tool-row-h:44px` to `:root`. Added `#tool-row` styles. Changed `#float-toolbar` from `position:fixed` to `position:static` inside `#tool-row`. Added `#right-panel.collapsed` styles. Removed obsolete `#float-toolbar` media query. |
| `proto/e2e_ui_test.py` | Replaced `toolbarFitsWorkspace` with `toolbarInToolRow` + `toolRowAboveWorkspace`. Added 4 new JS assertions (`panelLayoutControlsExist`, `panelLayoutKeyWritten`, `panelResetRestoresDefaults`, `panelCollapseWorks`) + 4 Python assertions. |
