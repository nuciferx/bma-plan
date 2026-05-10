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

## Active Feature State

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

- `a6c67e7` ui: add layer tool awareness
- `94db3d9` ui: validate object layer scope
- `eefab31` ui: add page type layer presets
- `ed9944d` ui: add page-scoped layer instances

## Latest Commits (root)

- `186bee8` docs: confirm area summaries use tags and floors
- `a3e1166` docs: audit runtime layer scope
- `82e1e4e` docs: lock page-scoped layer model
