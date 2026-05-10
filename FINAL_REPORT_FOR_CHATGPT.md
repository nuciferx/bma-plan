# FINAL_REPORT_FOR_CHATGPT.md — Latest Sprint Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# RUN_UI_LAYOUT_OPTIONS_MOCKUP_V3 — PASS

> Date: 2026-05-10
> Sprint type: Source
> Result: PASS — py_compile + smoke + full
> Proto commit: `087c769`

---

## What This Sprint Did

Added a UI Layout Options system that lets users switch between the current stable UI and mockup-v3-inspired visual modes for each major area independently. The current UI is preserved as the default and is never removed. All switches are CSS-class-based — no DOM restructuring, no element hiding.

---

## Feature Details

### Options Button
`#btn-ui-layout` (⚙ Layout) added to topbar zone-a after Page Setup. Toggles `#ui-layout-panel` open/closed.

### Options Panel (`#ui-layout-panel`)
Fixed-position floating panel (340px). Sections:
- **Presets**: Current Stable / Mockup V3 / Inspection Focus / Layer Focus / Compact
- **A. Top Area**: Current Compact Topbar | Mockup V3 Menu Style
- **B. Left Panel**: Current Inspection Sidebar | Mockup V3 Sheets Style
- **C. Right Panel**: Current Layers Panel | Mockup V3 Layer Manager
- **D. Widgets**: Current Status Widgets | Mockup V3 Summary Style
- **Footer**: Reset to Current Stable | Reset to Mockup V3

### Persistence
`localStorage['bmaPlan.uiLayoutOptions.v1']` = JSON `{top,left,right,widgets}`. Never written to `.bmaplan`. Default = `current` stable everywhere (no surprise on first load).

### v3 CSS Modes (class-based, additive)

| Mode class | What changes |
|-----------|-------------|
| `body.ui-top-v3` | `#topbar` bg → #141618, border → #0d0e10, no glow shadow |
| `body.ui-right-v3` | Right panel bg → #22262c; layer rows → flat style (no card box, left-border accent) |
| `body.ui-left-v3` | Sidebar bg → #22262c; header → #1e2226; tab font smaller |
| `body.ui-widgets-v3` | Widget cards → rounded 10px, backdrop-filter, compact badge border-radius |

---

## E2E Assertions Added (11 new, all PASS)

`optionsBtnVisible`, `optionsPanelExists`, `currentStablePresetExists`, `mockupV3PresetExists`, `optionsPanelOpens`, `topModeSwitchNoCrash`, `leftModeSwitchNoCrash`, `rightModeSwitchNoCrash`, `widgetsModeSwitchNoCrash`, `localStorageKeyWritten`, `resetRestoresCurrentStable`

---

## Hard Rules Confirmed

- Current UI preserved — not removed, not hidden
- No save/load format changes
- No export rewrite
- No legal/OCR/AI/Rule Engine
- No draggable widgets, no autosave
- All prior E2E assertions still PASS

---

# Page-Scoped Layer Implementation Batch — PASS (6 sprints)

> Date: 2026-05-10
> Sprint type: Docs + Source
> Result: PASS — all 6 sprints, full E2E green after each source sprint

---

## What This Batch Did

Implemented the full page-scoped layer architecture for BMA-Plan's measurement tool.
Each page now has its own independent `layers[]` array. The global `layerVis`/`layerLock`
objects are kept in sync via a backward-compat bridge (`_syncPageLayersToGlobals`).
No save/load format changed. No export rewritten. No forbidden items touched.

---

## Sprint Summary

| Sprint | Type | Result | Proto commit |
|--------|------|--------|--------------|
| RUN_LAYER_SCOPE_AUDIT | docs-only | PASS | — |
| RUN_PAGE_LAYER_INSTANCE_MODEL | source | PASS | `ed9944d` |
| RUN_PAGE_TYPE_LAYER_PRESETS | source + e2e | PASS | `eefab31` |
| RUN_OBJECT_LAYER_VALIDATION | source | PASS | `94db3d9` |
| RUN_LAYER_TOOL_AWARENESS | source | PASS | `a6c67e7` |
| RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR | docs-only | PASS | — |

---

## Architecture Added

### Data model (runtime-only, no save/load impact)

```js
pageStore[n].layers = [
  { id, pageId, name, slug, color, visible, locked, order, presetKey, objectCount }
]
pageStore[n].activeLayerSlug = "base_area"
```

### Key functions added to proto/ui.html

| Function | Purpose |
|----------|---------|
| `DEFAULT_LAYER_PRESETS` | Constant: pageType → default layer template array |
| `ensurePageLayers(n)` | Lazy-init `pageStore[n].layers[]` from preset |
| `getCurrentPageLayers()` | Returns `ensurePageLayers(curPage)` |
| `getLayerBySlug(n, slug)` | Lookup layer by slug on page n |
| `getLayerById(n, id)` | Lookup layer by id |
| `getActiveLayerForPage(n)` | Returns active layer object for page n |
| `setActiveLayerForPage(n, slug)` | Sets `pageStore[n].activeLayerSlug` |
| `_syncPageLayersToGlobals(n)` | Pushes page layer vis/lock into global `layerVis`/`layerLock` |
| `updateLayerObjectCounts(n)` | Counts objects per layer for right panel display |
| `validateObjectLayerScope(n)` | Assigns `pageIndex`/`layerSlug`/`layerId` to objects; repairs orphaned refs |
| `assignDefaultObjectLayer(n, obj)` | Assigns layer fields to newly-created objects |

### Backward-compat bridge

Global `layerVis`/`layerLock` preserved. After `restorePage(n)`:
1. `_syncPageLayersToGlobals(n)` pushes page layer state into globals.
2. All existing render/hit-test code (drawRefLines, hitTestAll, etc.) reads globals unchanged.

After `toggleLayer(lyr)` / `toggleLayerLock(lyr)`:
- Global is updated first (as before).
- Page layer object is also updated to stay in sync.

---

## Layer Presets by Page Type

| Page type | Layers |
|-----------|--------|
| plan | พื้นที่หลัก, พื้นที่ย่อย, ช่องว่าง, เส้นอ้างอิง, ป้าย |
| site | ที่ดิน/แนวเขต, กรอบอาคาร/แนวอาคาร, ที่ว่าง, เส้นอ้างอิง, ป้าย/หมายเหตุ |
| elev | ผิวอาคาร, ช่องเปิด, เส้นอ้างอิง, ป้าย |
| section | พื้นที่ตัด, เส้นอ้างอิง, ป้าย |
| detail / other | same as plan |

---

## Invariants Preserved

- `layerVis.deduction === true && layerLock.deduction === true` after `toggleLayerLock("deduction")` — PASS
- `layerVis.reference_geometry === true && layerLock.reference_geometry === true` after toggle — PASS
- Export uses `semanticTag`/`reportTarget`, never layer name — confirmed by docs sprint 6

---

## Files Changed

| File | Change |
|------|--------|
| `proto/ui.html` | Added layer model block, updated toggleLayer/Lock, restorePage, buildRightPanel, updateActiveLayerControl, finishCurrentArea, finishPathLike |
| `proto/e2e_ui_test.py` | Updated layer-row assertion for site-preset labels |
| `docs/design/LAYER_SCOPE_RUNTIME_AUDIT.md` | Created — audit of all global layer state |
| `docs/design/AREA_SUMMARY_BY_TAG_AND_FLOOR_AUDIT.md` | Created — confirms export is layer-name-free |

---

## What Did Not Change

- No save/load format migration.
- No export rewrite.
- No legal/OCR/AI/Rule Engine/FAR/OSR.
- No layer name in any calculation or export grouping key.
- All prior E2E assertions still PASS.

---

# RUN_PAGE_SCOPED_LAYER_MODEL_LOCK — PASS

> Date: 2026-05-10
> Sprint type: Docs-only
> Result: PASS

---

## What This Sprint Did

Locked the canonical page-scoped layer model for BMA-Plan.
No runtime behavior was changed. No source code was modified.
All outputs are documentation that future implementation sprints must follow.

---

## Files Created / Updated

| File | Action | Notes |
|------|--------|-------|
| `docs/design/PAGE_SCOPED_LAYER_MODEL.md` | Created | Canonical spec: Project→Page→Layer→Object, invariants, presets, calculation rules |
| `docs/design/LAYER_MODEL.md` | Created | Reference index; current vs. target status table |
| `docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md` | Created | Full audit: current state, gap list G1–G8, risk table, implementation sequence |
| `docs/status/NEXT_ACTIONS.md` | Updated | Prepended 6 layer implementation sprints |
| `log.md` | Updated | Sprint entry added |
| `FINAL_REPORT_FOR_CHATGPT.md` | Updated | This file |

---

## Canonical Model (Summary)

```
Project
  └─ pages[]
       └─ Page  { id, label, pageType, floorName, floorCode, scale }
            └─ layers[]
                 └─ Layer  { id, pageId, name, slug, visible, locked, order, presetKey }
            └─ objects[]
                 └─ Object { id, pageId, layerId, objectType, semanticTag,
                              measurementProfile, reportTarget, geometry }
```

**Core rule:** Each page has its own independent layer set. Same name on different pages = different layers.
**Calculation rule:** Uses semanticTag/measurementProfile/reportTarget — never layer name.

---

## Current Implementation Audit (Key Findings)

### What is correct today
- Area calculation: `_poly_area_pt2(pts) / pts_per_m²` — no layer name involved
- Export grouping: by page number + `semanticTag`/`reportTarget` — no layer name involved
- `semanticTag`, `measurementProfile`, `reportTarget` fields exist on objects — correct foundation

### What is missing or wrong
| Gap | Current | Required |
|-----|---------|----------|
| G1 | `layerVis`/`layerLock` are global JS objects | Must be per-page in `pageStore[n]` |
| G2 | No `Layer` data model | Need `{ id, pageId, name, slug, visible, locked }` |
| G3 | `pageStore[n]` has no `layers[]` | Need per-page layer list |
| G4 | Objects have no `layerId` | Need `object.layerId` → `Layer.id` |
| G5 | Objects have no `pageId` | Need `object.pageId` → `Page.id` |
| G6 | No layer presets | Need preset templates per pageType |
| G7 | Active layer sets mode, not `layerId` | Need to write `layerId` on new objects |
| G8 | Cross-page total ignores page type | Need to filter by `floorCode`/`pageType` |

---

## Risks if Layers Stay Global

1. Hiding "Deduction" layer affects all floors simultaneously — measurement error on multi-page projects.
2. Layer lock on Page 1 prevents editing on all other pages — UX confusion.
3. Export cannot distinguish "ชั้น 1 deduction" vs "ชั้น 2 deduction" — report quality degrades.
4. Layer preset applied globally pollutes unrelated pages.

---

## Recommended Next Sprints

| # | Sprint | Type |
|---|--------|------|
| 1 | RUN_LAYER_SCOPE_AUDIT | Docs / Code audit |
| 2 | RUN_PAGE_LAYER_INSTANCE_MODEL | Code — migrate layerVis/layerLock per-page |
| 3 | RUN_PAGE_TYPE_LAYER_PRESETS | Code — preset templates by pageType |
| 4 | RUN_OBJECT_LAYER_VALIDATION | Code — add layerId + pageId to objects |
| 5 | RUN_LAYER_TOOL_AWARENESS | Code — active layer writes layerId on objects |
| 6 | RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR | Code — group totals by semanticTag + floorCode |

---

## Phase 1 Scope Check

- [x] No legal checker, OCR, AI, Rule Engine introduced
- [x] No FAR/OSR/pass-fail logic
- [x] No save/load format changed
- [x] No export rewritten
- [x] No runtime behavior changed
- [x] Layer name not used in any calculation — enforced as invariant in the locked model

---

## Test Result

Docs-only sprint. Source baseline unchanged.

```
proto/server.py  — not modified
proto/ui.html    — not modified
```

Previous baseline (from 8-Sprint UI batch, 2026-05-10):
```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS
python proto/e2e_ui_test.py full                           → PASS
```

No re-run required for docs-only sprint.

---

## Known Gaps

All gaps documented in `docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md` (G1–G8).
None are blocking for current Phase 1 measurement workflow.
Layer implementation sprints are required before multi-floor project reporting becomes reliable.
