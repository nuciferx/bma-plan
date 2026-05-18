# PAGE_SCOPED_LAYER_MODEL.md — Canonical Page-Scoped Layer Specification

> Sprint: RUN_PAGE_SCOPED_LAYER_MODEL_LOCK
> Date: 2026-05-10
> Status: LOCKED (docs-only — no source code changed)

---

## 1. Core Rule

Every page/sheet/floor has its own independent layer set.
Layers with the same display name on different pages are **not** the same layer.
Layer name must **never** be used for calculation, reporting, or legal logic.

---

## 2. Canonical Data Model

### Project

```
Project
  └─ pages[]        — ordered list of Page objects
```

### Page

```
Page
  id          : string   — unique across project (e.g. UUID or "p1")
  label       : string   — display name (e.g. "ชั้น 1", "ผังบริเวณ")
  pageType    : string   — enum: site | plan | elev | section | detail | schedule | other
  floorName   : string?  — human label ("ชั้น 2", "ชั้นดาดฟ้า") — optional, display only
  floorCode   : string?  — machine key ("f2", "roof") — optional, display only
  scale       : ScaleInfo?
  layers[]    : Layer[]  — page-owned, independent from all other pages
  objects[]   : Object[] — all objects belonging to this page
```

### Layer

```
Layer
  id          : string   — unique across the whole project
  pageId      : string   — foreign key → Page.id (REQUIRED)
  name        : string   — display name, may repeat across pages
  slug        : string   — machine key within this page (e.g. "base_area", "deduction")
  color       : string?  — hex color hint
  visible     : boolean
  locked      : boolean
  order       : integer  — display order within the page
  presetKey   : string?  — which preset template generated this layer
  objectCount : integer  — derived count (not stored)
```

### Object

```
Object
  id                : string
  pageId            : string   — foreign key → Page.id (REQUIRED)
  layerId           : string   — foreign key → Layer.id within the same Page (REQUIRED)
  objectType        : string   — poly | opening | line | ref | parking
  semanticTag       : string   — primary semantic classification
  measurementProfile: string   — derived from semanticTag
  reportTarget      : string   — derived from semanticTag
  geometry          : points[] | path
  area              : number?  — computed value in m²
  name              : string?
```

---

## 3. Invariants (Must Always Hold)

| # | Rule |
|---|------|
| 1 | `object.layerId` must reference a Layer that exists in the same Page |
| 2 | `layer.pageId === object.pageId` — cross-page references are invalid |
| 3 | Same `layer.name` may appear on multiple pages; `layer.id` is always different |
| 4 | `page.layers` is independent — changing layers on Page A does not affect Page B |
| 5 | Area summaries group by `pageId` (or `floorCode`) + `semanticTag`/`measurementProfile`/`reportTarget` |
| 6 | No area summary may depend on `layer.name` or `layer.slug` |
| 7 | Layer visibility/lock state is per-page |

---

## 4. Layer Presets

A **preset** is a template that defines a default set of layers for a given `pageType`.

Behaviour:
- Applying a preset to Page A creates layers for Page A only (each with a new `id`, `pageId = pageA.id`).
- Applying the same preset to Page B creates a separate, independent set of layers for Page B.
- A preset is **not** shared state — it is a factory, not a shared instance.

Example preset for `pageType = "plan"` (floor plan):

| presetKey      | slug                 | name (TH)        | order |
|----------------|----------------------|------------------|-------|
| plan_default   | base_area            | พื้นที่หลัก        | 1     |
| plan_default   | sub_area             | พื้นที่ย่อย         | 2     |
| plan_default   | deduction            | ช่องว่าง           | 3     |
| plan_default   | reference_geometry   | เส้นอ้างอิง        | 4     |
| plan_default   | labels               | ป้ายชื่อ           | 5     |

Example preset for `pageType = "site"` (site plan):

| presetKey      | slug                 | name (TH)        | order |
|----------------|----------------------|------------------|-------|
| site_default   | site_boundary        | แนวที่ดิน          | 1     |
| site_default   | building_footprint   | แนวอาคาร          | 2     |
| site_default   | reference_geometry   | เส้นอ้างอิง        | 3     |
| site_default   | labels               | ป้ายชื่อ           | 4     |

---

## 5. Calculation and Reporting Rules

Calculation and reporting use **semantic fields only**:

| Field              | Source                         |
|--------------------|--------------------------------|
| semanticTag        | object property                |
| measurementProfile | derived from semanticTag       |
| reportTarget       | derived from semanticTag       |
| objectCategory     | derived from semanticTag       |
| countingRule       | derived from semanticTag       |

Layer is for **workflow/visibility/organization only**.
It plays no role in:
- area calculation
- deduction logic
- floor/project totals
- export grouping
- legal or pass/fail rules (Phase 2 is out of scope)

Area summary grouping key:
```
(pageId | floorCode)  +  semanticTag  +  reportTarget
```
Not:
```
layer.name  ← FORBIDDEN
layer.slug  ← FORBIDDEN
```

---

## 6. Validation Rules (Future Implementation)

When implemented, the system must flag:

| Condition | Severity | Message |
|-----------|----------|---------|
| `object.pageId !== layer.pageId` | Error | Cross-page layer reference |
| `object.layerId` not found in `page.layers` | Error | Orphan layerId |
| `object.pageId` not set | Warning | Missing pageId |
| `object.layerId` not set | Warning | Missing layerId |
| Area summary key uses `layer.name` | Error | Forbidden layer name in calculation |

---

## 7. Hard Forbidden

- Do not use `layer.name` or `layer.slug` for area calculation.
- Do not share a `Layer` object across pages.
- Do not make layer visibility/lock global state.
- Do not infer page membership from layer name.
- Do not introduce legal/FAR/OSR/pass-fail in any layer-related logic.
- Do not add AI/OCR to layer classification.
