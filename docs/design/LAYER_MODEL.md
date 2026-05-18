# LAYER_MODEL.md — BMA-Plan Layer Model Reference

> Date: 2026-05-10
> Status: LOCKED — page-scoped model adopted

This file is the canonical reference for BMA-Plan's layer model.
For the full spec, see: [PAGE_SCOPED_LAYER_MODEL.md](PAGE_SCOPED_LAYER_MODEL.md)
For the current-vs-target audit, see: [LAYER_MODEL_ALIGNMENT_AUDIT.md](LAYER_MODEL_ALIGNMENT_AUDIT.md)

---

## Adopted Rule (2026-05-10)

**Layers are page-scoped. Every page has its own independent layer set.**

- `layer.pageId` is required and immutable.
- Same layer name on different pages means two different layers with two different `id`s.
- Layer name is never used for calculation or reporting.

---

## Current Implementation Status

| Aspect | Status |
|--------|--------|
| Layer model | Global (slugs in JS state) — **not yet page-scoped** |
| Object `layerId` field | Missing — layer is derived from `areaType` |
| Object `pageId` field | Missing — implicit from `pageStore[n]` position |
| Page `layers[]` array | Missing — no per-page layer list |
| Layer visibility/lock | Global `layerVis`/`layerLock` objects — **not per-page** |
| Calculation uses layer name | No — uses `areaType`/`semanticTag` — **CORRECT** |
| Export uses layer name | No — groups by page number + `semanticTag` — **CORRECT** |

See the audit doc for the full gap list and recommended implementation sequence.

---

## Layer Slugs (Current)

The four current layer slugs (global, not per-page):

| Slug | Purpose |
|------|---------|
| `base_area` | GFA, site boundary, building footprint |
| `sub_area` | room, corridor, stair, parking, other area types |
| `deduction` | openings (holes, voids) |
| `reference_geometry` | reference lines, dimension lines |
| `labels` | visibility of label overlays (not a drawing layer) |

These will become **per-page** layer instances in future sprints.

---

## Target Model Summary

```
Project
  └─ pages[]
       └─ Page
            id, label, pageType, floorName, scale
            layers[]
              └─ Layer
                   id, pageId, name, slug, visible, locked, order, presetKey
            objects[]
              └─ Object
                   id, pageId, layerId, objectType, semanticTag, ...
```

Full field definitions: [PAGE_SCOPED_LAYER_MODEL.md](PAGE_SCOPED_LAYER_MODEL.md)

---

## What Must Never Change (Invariants)

1. Calculation uses `semanticTag`, `measurementProfile`, `reportTarget` — not layer name.
2. Export groups by `pageId`/`floorCode` + `semanticTag`/`reportTarget` — not layer name.
3. A layer on Page A and a same-named layer on Page B are different objects with different `id`s.
4. No legal/FAR/OSR/pass-fail logic anywhere in Phase 1.
