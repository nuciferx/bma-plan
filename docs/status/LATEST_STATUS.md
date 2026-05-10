# LATEST_STATUS.md — BMA-Plan Current Feature State

Date: 2026-05-10

## Phase

Phase 1 = Raster PDF Measurement Assistant. No legal checker, OCR, AI, Rule Engine, FAR/OSR/pass-fail.

## Latest Sprint Results

| Sprint | Result |
|--------|--------|
| Page-Scoped Layer Model Lock (docs) | PASS — root `82e1e4e` |
| Layer Scope Audit (docs) | PASS — root `a3e1166` |
| Page Layer Instance Model | PASS — proto `ed9944d` |
| Page Type Layer Presets | PASS — proto `eefab31` |
| Object Layer Validation | PASS — proto `94db3d9` |
| Layer Tool Awareness | PASS — proto `a6c67e7` |
| Area Summary by Tag and Floor (docs) | PASS — root `186bee8` |
| 8-Sprint UI/Measurement Usability Batch | PASS — proto `4a09693` |
| Widget Placement Polish | PASS |
| Left Inspection Status Panel | PASS — proto `24b41c5` |
| Static 404 Fix (critical regression) | PASS — proto `a2099ec` |
| UI Layout Options (mockup v3 modes) | PASS — proto `087c769` |
| Panel Scroll + Page-Scoped Layer UI | PASS — proto `fb39f28` |
| Mockup V3 App Shell Theme | PASS — proto `b271577` |
| Save System Audit (docs) | PASS — root `9a46ff4` |
| Save / Save As / Overwrite | PASS — proto `266d365` |
| Open / Recent Project Workflow | PASS — proto `5ad2cc0` |
| Annotated PDF Export Audit (docs) | PASS — root `9a46ff4` |
| Export Current-Page Annotated PDF | PASS — proto `55dccdf` |
| Export All-Pages Annotated PDF | PASS — proto `55dccdf` |

## Active Feature State (2026-05-10)

- **Save System**: `saveProject()` async — overwrites via FSAPI if handle exists, else `saveProjectAs()`. `saveProjectAs()` uses `showSaveFilePicker` with fallback to `dlBlob()` download. `isDirty` flag set by `pushUndo()`, cleared by save/load. Ctrl+S shortcut. "Save As" button in export panel.
- **Recent Projects**: `localStorage['bmaPlan.recentProjects.v1']` stores up to 10 recent `.bmaplan` filenames. `#top-open-project` shows dropdown with Browse + recent files. Both load paths (`proj-input`, `proj-input2`) call `addRecentProject()` after successful load.
- **Annotated PDF Export**: "Export หน้าปัจจุบัน + Annotations" and "Export ทุกหน้า + Annotations" buttons in export panel PDF section. Reuse `/export-pdf` endpoint with full `pageStore` annotations.
- **UI Layout Options**: `#btn-ui-layout` (⚙ Layout) button in topbar. `#ui-layout-panel` with Presets (Current Stable / Mockup V3 / Inspection Focus / Layer Focus / Compact) and per-section switches (Top / Left / Right / Widgets). Persisted in `localStorage['bmaPlan.uiLayoutOptions.v1']`. v3 modes = CSS-class overrides on `<body>`. Default = Current Stable.

## Active Feature State (prior)

- **Workflow**: Open PDF → Set Scale → Page Setup → Measure → Review → Export (locked)
- **Page-Scoped Layer Model**: layers are now per-page instances — each page has its own
  independent layer set with `Layer {id, pageId, name, slug, color, visible, locked, order, presetKey}`.
  Global `layerVis`/`layerLock` are kept in sync via bridge for all existing render code.
- **Layer Presets by Page Type**: site/plan/elev/section page types get appropriate default layers.
  Same preset applied to different pages creates independent layer instances with distinct IDs.
- **Object Layer Fields**: new objects get `pageIndex`, `layerSlug`, `layerId` assigned at creation.
  Existing objects get safe defaults on restore via `validateObjectLayerScope()`.
- **Right Panel Layers**: layer rows driven by `getCurrentPageLayers()` with live object counts.
- **Tool-Layer Sync**: `updateActiveLayerControl()` syncs active layer slug to page model via
  `setActiveLayerForPage()`. Tool mode changes keep page layer state consistent.
- **Area Summary**: confirmed — driven by `semanticTag`/`measurementProfile`/`reportTarget`,
  not layer name. Export groups by page number + semantic metadata.
- **Left Inspection Status Panel**: collapsible panel with workflow steps, per-page stats,
  measurement summary (gross/opening/land/parking), warnings, next action.
- **Right panel**: Layers-first (page-scoped), Legacy/Compatibility Properties+ObjectTree below.
- **Status bar**: Tool, Scale, Objects, Warnings, Layer, Save, Page.
- **5 measurement metadata fields**: measurementProfile, objectCategory, reportTarget, lawBasis, countingRule.
- **XLSX export**: Page Scales, Report Target Summary sheet, 5 metadata columns.

## Test Baseline (2026-05-10)

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

## Latest Commits (proto submodule)

- `55dccdf` export: add current-page and all-pages annotated PDF export buttons
- `5ad2cc0` save: improve open and recent project workflow
- `266d365` save: support save as and overwrite current project
- `b271577` ui: add mockup v3 app shell theme
- `fb39f28` ui: make panels scrollable and show page-scoped layers

## Latest Commits (root)

- `9a46ff4` docs: audit annotated pdf export feasibility
- (proto submodule pointer updated)
