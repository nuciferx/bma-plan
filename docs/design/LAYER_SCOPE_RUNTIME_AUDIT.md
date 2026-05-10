# LAYER_SCOPE_RUNTIME_AUDIT.md — Runtime Layer Scope Audit

> Sprint: RUN_LAYER_SCOPE_AUDIT
> Date: 2026-05-10
> Source files read: proto/ui.html, proto/e2e_ui_test.py

---

## 1. layerVis / layerLock / activeLayer — Definitions

### Global declarations (ui.html line 311)

```js
let layerVis = {
  base_area: true,
  sub_area: true,
  deduction: true,
  reference_geometry: true,
  labels: true
};
let layerLock = {
  base_area: false,
  sub_area: false,
  deduction: false,
  reference_geometry: false
};
```

Both are plain JS objects, declared once at module scope.
They are shared across ALL pages — changing one affects the entire session.

**There is no `activeLayer` variable.** The active layer is derived at read-time from
`document.getElementById("active-layer-select")?.value` in `activeLayerLabel()`.

---

## 2. areaType → Layer Inference

```js
// ui.html line 313
function areaTypeLayer(t) {
  return (t === "land" || t === "gfa" || t === "building") ? "base_area" : "sub_area";
}
```

- All area objects have an `areaType` field.
- Layer slug is NOT stored on the object — it is computed at render/hit-test time.
- Opening objects always map to `"deduction"` (hardcoded in multiple places).
- Reference lines always map to `"reference_geometry"` (hardcoded).
- Lines always map to `"reference_geometry"` or `"dimensions"` (context-dependent).

---

## 3. Object Field Inventory

Objects in `pageStore[n].polys`, `.openings`, `.refs`, `.lines`, `.parking` currently have:

| Field | Present? | Notes |
|-------|----------|-------|
| `id` | Yes | assigned by `ensureStoreObjectIds()` |
| `pageIndex` / `pageId` | **No** | page is implicit from `pageStore[n]` |
| `layerId` | **No** | layer is derived from `areaType` at render time |
| `layerSlug` | **No** | not stored |
| `areaType` | Yes (polys) | drives layer derivation |
| `semanticTag` | Yes (recent) | drives calculation/export |
| `measurementProfile` | Yes | |
| `reportTarget` | Yes | |

---

## 4. pageStore[n] Structure

```js
function getStore(n) {
  if (!pageStore[n]) pageStore[n] = {
    lines: [],
    polys: [],
    openings: [],
    refs: [],
    parking: [],
    calibScale: null
  };
  return pageStore[n];
}
```

No `layers[]` array. No `activeLayerSlug`. No `layerVis`/`layerLock` per page.

---

## 5. All Functions That Read/Write Layer State

| Function | Location | Reads | Writes |
|----------|----------|-------|--------|
| `toggleLayer(lyr)` | line 961 | `layerVis[lyr]` | `layerVis[lyr]` |
| `toggleLayerLock(lyr)` | line 962 | `layerLock[lyr]` | `layerLock[lyr]` |
| `setActiveLayer(layer)` | line 945 | —  | changes drawing mode, calls `updateActiveLayerControl()` |
| `updateActiveLayerControl()` | line 944 | `mode`, `openingMode`, `curAType` | `#active-layer-select` value |
| `activeLayerLabel()` | line 421 | `#active-layer-select` selectedText | — |
| `buildRightPanel()` | line 805 | `layerVis`, `layerLock`, `mPolys`, `mOpenings`, etc. | DOM |
| `rightPanelLayerCount(k)` | line 804 | `mPolys`, `mOpenings`, `mRefs`, `mLines` | — |
| `objLayerKey(sel, obj)` | line 796 | `sel.type`, `obj.areaType` | — |
| `areaTypeLayer(t)` | line 313 | `t` (areaType string) | — |
| `hitVertex()` | line 867 | `layerVis.reference_geometry`, `layerLock.reference_geometry` | — |
| `hitTestAll()` | (line ~605) | `layerVis`, `layerLock` per type | — |
| `drawRefLines()` | line 848 | `layerVis.reference_geometry` | — |
| `shouldDrawLabelForObject()` | line 844 | `layerVis.labels` | — |
| `drawPolyLabel()` | line 845 | `layerVis.labels` | — |

---

## 6. Render Paths Affected by Layer Visibility/Lock

| Layer Slug | Visibility Guard | Lock Guard |
|-----------|-----------------|------------|
| `reference_geometry` | `drawRefLines()` skips if `!layerVis.reference_geometry` | `hitVertex()` skips scan if `layerLock.reference_geometry` |
| `labels` | `shouldDrawLabelForObject()` returns false if `!layerVis.labels` | not locked |
| `base_area` | guarded in `hitTestAll()` (via `buildRightPanel` toggle) | guarded in hit test |
| `sub_area` | guarded in `hitTestAll()` | guarded in hit test |
| `deduction` | guarded in `hitTestAll()` | guarded in hit test |

`hitTestAll()` uses `layerVis` and `layerLock` to filter which objects are selectable.

---

## 7. E2E Assertions Touching Layers

From `proto/e2e_ui_test.py`:

| Line | Assertion |
|------|-----------|
| 892–895 | `toggleLayerLock("deduction")` → `layerVis.deduction === true && layerLock.deduction === true` |
| 950–952 | `toggleLayerLock("reference_geometry")` → `layerVis.reference_geometry === true && layerLock.reference_geometry === true` |

Both assertions check the **global** `layerVis` and `layerLock` objects directly.
Any implementation must preserve these global objects and their behavior.

---

## 8. Export/Report Paths That May Be Affected

From `proto/server.py`:
- Export groups by page number (`pg_str`) and `semanticTag`/`reportTarget` — **no layer name used**.
- `_semantic_tag()` derives tag from `areaType`, not layer.
- `_get_meta()` reads from object fields, not layer.
- No layer slug appears in any export grouping key.

**Conclusion:** Export is already layer-name-free. No export changes needed.

---

## 9. Minimal Implementation Plan for Page-Scoped Layers

### Constraints from E2E tests
The global `layerVis` and `layerLock` objects MUST remain in place and functional.
New page-layer model is ADDITIVE — it mirrors and extends the global model.

### Phase A — Additive data model (Sprint 2)
1. Add `DEFAULT_LAYER_PRESETS` constant (page-type → layer template array).
2. Add `ensurePageLayers(pageIndex)` — lazy-initializes `pageStore[n].layers[]`.
3. Add helper functions: `getLayerBySlug`, `getActiveLayerForPage`, `setActiveLayerForPage`,
   `getObjectLayerSlug`, `assignDefaultObjectLayer`.
4. Update `toggleLayer()` and `toggleLayerLock()` to sync page layer `visible`/`locked` fields.
5. Add `_syncPageLayersToGlobals(pageIndex)` — reads page layers and updates `layerVis`/`layerLock`.
6. Call `_syncPageLayersToGlobals(curPage)` at end of `restorePage(n)` to ensure page-specific
   layer state is applied when switching pages.

### Phase B — Right panel uses page layers (Sprint 3)
7. Update `buildRightPanel()` layer rows to be driven by `getCurrentPageLayers()`.
8. Update `rightPanelLayerCount(k)` to also work per current page.
9. Call `updateLayerObjectCounts(curPage)` before rendering.

### Phase C — Object layer fields (Sprint 4)
10. Update `ensureStoreObjectIds()` / `normalizeCurrentObjects()` to assign
    `pageIndex` and `layerSlug` (and `layerId`) to objects that lack them.
11. Add `validateObjectLayerScope(pageIndex)` — silent repair + non-blocking warning.
12. Call after `restorePage()`.

### Phase D — Tool awareness (Sprint 5)
13. Update `updateActiveLayerControl()` to call `setActiveLayerForPage(curPage, slug)`.
14. Call `assignDefaultObjectLayer(curPage, newObj)` when new objects are finalized.

### Phase E — Area summary confirmation (Sprint 6)
15. Confirm export/summary still uses semanticTag/reportTarget, not layer name.
16. Docs-only if already correct.

### Non-negotiable constraints
- `layerVis.deduction === true && layerLock.deduction === true` after `toggleLayerLock("deduction")` — MUST remain true.
- `layerVis.reference_geometry === true && layerLock.reference_geometry === true` after `toggleLayerLock("reference_geometry")` — MUST remain true.
- `pageStore[n]` structure is additive only — no existing fields removed.
- No save/load format migration — `layers[]` is runtime-only state.
- No layer name in calculation/export.
