# LAYER_MODEL_ALIGNMENT_AUDIT.md — Current vs. Target Layer Model

> Sprint: RUN_PAGE_SCOPED_LAYER_MODEL_LOCK
> Date: 2026-05-10
> Source files read: proto/ui.html, proto/server.py, proto/static/js/semantic-meta.js, proto/export/semantic_metadata.py

---

## 1. Current Page Model

**How pages are stored in the frontend:**

```js
// ui.html
let pageStore = {};        // pageStore[n] = {lines, polys, openings, refs, parking, calibScale}
let pageTags  = {};        // pageTags[n]  = "site" | "plan" | "elev" | ...
let pageNames = {};        // pageNames[n] = display string
let curPage   = 1;         // current integer page number
```

Pages are **not objects** — they are integer keys into dictionaries.
There is no `Page.id` (UUID), no `Page.pageType` field, no `Page.floorName` or `Page.floorCode`.
Page identity = integer page number from the PDF.

**How pages are stored in the backend:**

```python
# server.py — CASES[case_id]
{
  "page_tags":   {},   # {str(n): tag}
  "project_info": {},
  "page_cache":  {}
}
```

The backend has no persistent page model. Page data (objects) lives entirely in the frontend `pageStore`.

---

## 2. Current Layer Model

**Layer state in the frontend:**

```js
// ui.html line 311
let layerVis  = {base_area: true, sub_area: true, deduction: true, reference_geometry: true, labels: true};
let layerLock = {base_area: false, sub_area: false, deduction: false, reference_geometry: false};
```

These are **global** JS objects — shared across all pages in the session.
Toggling `layerVis.base_area` affects the visibility of base_area objects on ALL pages simultaneously.

The layer list is **hardcoded** — there is no `Layer` data model, no `Layer.id`, no `Layer.pageId`.
Layers are plain slug strings: `base_area`, `sub_area`, `deduction`, `reference_geometry`, `labels`.

**Layer selection in the ribbon:**

```html
<!-- ui.html -->
<select id="active-layer-select" onchange="setActiveLayer(this.value)">
```

`setActiveLayer(layer)` maps the slug to a drawing mode — it does not set a `layerId` on objects.

**Layer-to-object mapping:**

```js
// ui.html
function areaTypeLayer(t) {
  return (t === "land" || t === "gfa" || t === "building") ? "base_area" : "sub_area";
}
```

Objects have no `layerId` field. Layer membership is derived at render time from `areaType`.

---

## 3. Layer Scope — Global vs. Page-Scoped

| Aspect | Current | Target |
|--------|---------|--------|
| Layer visibility state | Global (`layerVis` object) | Per-page (`pageStore[n].layerVis`) |
| Layer lock state | Global (`layerLock` object) | Per-page (`pageStore[n].layerLock`) |
| Layer data model | None — slugs only | `Layer { id, pageId, name, slug, visible, locked, order }` |
| Layer list storage | Hardcoded in JS | `pageStore[n].layers[]` |
| Layer count per page | N/A | `layer.objectCount` (derived) |
| Layer presets | Not implemented | Template → instantiate per page |

---

## 4. Object `pageId` and `layerId` Fields

| Field | Current State | Target |
|-------|---------------|--------|
| `object.pageId` | **Missing** — implicit from `pageStore[n]` | Required string |
| `object.layerId` | **Missing** — derived via `areaTypeLayer(areaType)` | Required string → Layer.id |
| `object.semanticTag` | Present (recent sprints) | Present — correct |
| `object.measurementProfile` | Present | Present — correct |
| `object.reportTarget` | Present | Present — correct |
| `object.areaType` | Present | Kept — used to derive layer and semanticTag |

---

## 5. semanticTag / measurementProfile / reportTarget

These fields are correctly implemented and must **not** change:

```js
// proto/static/js/semantic-meta.js
function deriveMeasurementMeta(tag) {
  return {
    measurementProfile: SEMANTIC_PROFILE_MAP[tag] || "review_note",
    objectCategory:     SEMANTIC_CATEGORY_MAP[tag] || "annotation",
    reportTarget:       SEMANTIC_REPORT_TARGET_MAP[tag] || "Audit Log",
    lawBasis:           SEMANTIC_LAW_BASIS_MAP[tag] || null,
    countingRule:       SEMANTIC_COUNTING_RULE_MAP[tag] || "reference",
  };
}
```

```python
# proto/export/semantic_metadata.py
def _derive_measurement_meta(tag: str) -> dict:
    return {
        "measurementProfile": SEMANTIC_PROFILE_MAP.get(tag, "review_note"),
        "objectCategory":     SEMANTIC_CATEGORY_MAP.get(tag, "annotation"),
        "reportTarget":       SEMANTIC_REPORT_TARGET_MAP.get(tag, "Audit Log"),
        ...
    }
```

Both JS and Python versions are consistent. This is the correct foundation.

---

## 6. Does Any Calculation or Export Use Layer Name?

| Location | Uses layer name in calculation? | Notes |
|----------|--------------------------------|-------|
| `server.py` — area sheet | **No** | Groups by `pg_name` (page name); area from `poly.pts + pts_per_m` |
| `server.py` — report target sheet | **No** | Groups by `meta["reportTarget"]` from `semanticTag` |
| `server.py` — _semantic_tag() | **No** | Maps `areaType` → semanticTag, not layer name |
| `ui.html` — `updatePageSummary()` | **No** | Sums `poly.area` from pageStore |
| `ui.html` — layer visibility | Layer slug controls visibility only | Correct — not calculation |
| `ui.html` — `setActiveLayer()` | Layer slug controls drawing mode | Correct — not calculation |

**Finding: No calculation or export currently uses layer name as input. This is correct and must be preserved.**

---

## 7. How Area Summary by Floor/Page Currently Works

**Frontend (`ui.html`):**
```js
function updatePageSummary(n) {
  // iterates mPolys, mOpenings for current page
  // sums .area field
  // displays in sidebar
}
```

**Backend export (`server.py` line 898):**
```python
for pg_str in sorted(page_store.keys(), key=lambda x: int(x)):
    pg = int(pg_str)
    pg_data = page_store[pg_str]
    polys = pg_data.get("polys", [])
    # area from poly.pts + pts_per_m — no layer name
```

Summary is grouped by integer page number, then by `semanticTag`/`reportTarget`.
No layer name in the grouping key. **Correct.**

Cross-page total (`grand_total`) sums all pages. This is a raw sum — does not distinguish floor type.
Future improvement: group by `floorCode` from `pageTags` (e.g., only `plan`-tagged pages for GFA total).

---

## 8. Gap List — What Must Change for Page-Scoped Layers

| # | Gap | Risk if Not Fixed | Sprint |
|---|-----|-------------------|--------|
| G1 | `layerVis` and `layerLock` are global | Toggling layer on Page 1 affects all pages | RUN_LAYER_SCOPE_AUDIT |
| G2 | No `Layer` data model (no `id`, no `pageId`) | Cannot enforce cross-page isolation | RUN_PAGE_LAYER_INSTANCE_MODEL |
| G3 | `pageStore[n]` has no `layers[]` array | No per-page layer list or metadata | RUN_PAGE_LAYER_INSTANCE_MODEL |
| G4 | Objects have no `layerId` field | Cannot validate layer ownership | RUN_OBJECT_LAYER_VALIDATION |
| G5 | Objects have no `pageId` field | Cannot validate cross-page references | RUN_OBJECT_LAYER_VALIDATION |
| G6 | Layer presets are not defined | No consistent layer set per page type | RUN_PAGE_TYPE_LAYER_PRESETS |
| G7 | Active layer control sets mode, not `layerId` | Objects never record which layer they're on | RUN_LAYER_TOOL_AWARENESS |
| G8 | Cross-page total sums all pages regardless of type | GFA total may include site/elevation pages | RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR |

---

## 9. Risks if Layers Remain Global

| Risk | Impact |
|------|--------|
| User hides "Deduction" layer → all pages affected | Measurement error on multi-page project |
| Layer lock on Page 1 prevents editing on all pages | UX confusion, user cannot unlock per-page |
| Same-named layer on different pages is treated as the same entity | Data model ambiguity in future features |
| Export cannot distinguish "ชั้น 1 deduction" from "ชั้น 2 deduction" | Report quality degrades on multi-floor projects |
| Layer preset applied globally pollutes page-specific setups | Wrong layers appear on non-applicable pages |

---

## 10. Implementation Sequence

Execute in this order (one sprint per item):

| # | Sprint | Goal |
|---|--------|------|
| 1 | RUN_LAYER_SCOPE_AUDIT | Read all global layer state usages; confirm blast radius; document which functions must change |
| 2 | RUN_PAGE_LAYER_INSTANCE_MODEL | Add `pageStore[n].layers[]`; add `Layer` data class; migrate `layerVis`/`layerLock` to per-page |
| 3 | RUN_PAGE_TYPE_LAYER_PRESETS | Define preset templates by `pageType`; apply preset on new page creation |
| 4 | RUN_OBJECT_LAYER_VALIDATION | Add `layerId` and `pageId` to all objects; add validation guard in save/load |
| 5 | RUN_LAYER_TOOL_AWARENESS | Make active layer control write `layerId` onto new objects |
| 6 | RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR | Refine cross-page totals to group by `semanticTag`/`reportTarget` + `floorCode` |

**Do not skip steps or merge sprints** — each step must PASS (py_compile + smoke + full) before the next begins.

---

## 11. What Must Not Change (Contracts)

- `semanticTag`, `measurementProfile`, `reportTarget` as the source of truth for calculation.
- `areaType` field on objects — layer derives from it, not the reverse.
- Export area calculation: `_poly_area_pt2(poly.pts) / pts_per_m²`.
- No layer name in any calculation or export grouping key.
- `pageStore[n]` structure (lines, polys, openings, refs, parking, calibScale).
- Save/load format backward compatibility (new fields must be optional).
