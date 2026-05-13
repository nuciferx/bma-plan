# PATH_GEOMETRY_MODEL.md — Unified Path Geometry for Measurement Shapes

> Date: 2026-05-13
> Status: DESIGN ONLY — no source code, no UI, no tests changed
> Replaces: Phase H.1 split shape system (circle / ellipse / arc-edge)
> Aligns with: AGENTS.md §6 Sprint 5 — Curved Path

---

## 1. Purpose

Define a single geometry model that supports closed shapes made of any mix of straight edges and smooth curves, computed using the existing area math — without changing `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, scale math, snap engine, save format, or `proto/server.py`.

This document is design only. It does not implement code or UI. Implementation will follow in a separate sprint after the design is approved.

---

## 2. Problem Statement

Phase H.1 currently ships four parallel area calculators (`proto/ui.html` lines 952–956):

| Function | Inputs | Used when |
|---|---|---|
| `polyAreaM2(pts)` | straight-edge polygon vertices | default — every existing measurement |
| `circleAreaM2(radiusPt)` | radius only | `obj.shape === "circle"` |
| `ellipseAreaM2(aPt, bPt)` | semi-axes | `obj.shape === "ellipse"` |
| `polygonAreaWithArcsM2(poly)` | polygon + per-edge arc meta | any `edges[i].edgeType === "arc"` |

Dispatched by `objectAreaM2(obj)`.

This split has two real problems:

1. **Mixed shapes are awkward.** A boundary with one curved side and three straight sides — common for site plans (curved frontage along a road) and floor plans (rounded corners) — needs `polygonAreaWithArcsM2`, which only supports per-edge circular arcs and re-uses `polyAreaM2` plus a circular-segment correction. There is no single representation that handles both rectangles and curved shapes uniformly.

2. **No shared rendering / hit-test surface.** Each `shape` value (`"polygon"`, `"circle"`, `"ellipse"`) needs its own render branch and its own hit-test branch in `redraw()` and pointer handlers. Each new shape (rounded rectangle, freeform Bézier) means another branch.

The pivot: represent every closed measurement shape as a path of segments (line + cubic Bézier), and reduce area math to "flatten path to polyline, then call existing `polyAreaM2`."

---

## 3. Decision

Adopt an Illustrator-style closed path model:

```
Path
  segments[]   ordered list of segments
  closed       always true for area objects
```

Each segment is either `line` or `cubic` (cubic Bézier with two control points). Circles, ellipses, arcs, and rectangles become **generator functions** that produce paths — they are no longer first-class shape types on the object.

Area math becomes:
```
pathAreaM2(path, pg) = polyAreaM2( flattenPathToPoints(path, tolerance), pg )
```

`polyAreaM2` is unchanged. This is the entire contract.

---

## 4. Core Rule

Every closed measurement shape is either:

1. **Legacy polygon** — has `pts: [{x,y}, ...]`, no `geometryType`. Area uses `polyAreaM2(pts)`. Unchanged from today.
2. **Path** — has `geometryType: "path"` and `segments: [...]`. Area uses `pathAreaM2(obj, pg)`.

`objectAreaM2(obj, pg)` is the single dispatcher.

The existing `obj.shape === "circle" | "ellipse"` and `obj.edges[i].edgeType === "arc"` fields remain readable for backward compatibility, but **no new code should write them**. Once the new model is implemented, generators write `geometryType: "path"` instead.

---

## 5. Data Model

### 5.1 Segment types

```js
// Straight edge from p0 to p1
{ type: "line", p0: {x, y}, p1: {x, y} }

// Cubic Bézier from p0 to p1 with two control points
{ type: "cubic", p0: {x, y}, c1: {x, y}, c2: {x, y}, p1: {x, y} }
```

Coordinates are in **raw PDF points** — the same coordinate system as `mPolys[i].pts[j]`. The raw-geometry contract holds: do not store any value derived from the current scale.

### 5.2 Path object

```js
{
  geometryType: "path",       // discriminator — required
  segments: [ ... ],          // ordered, segment[i].p1 == segment[i+1].p0
  closed: true,               // area objects are always closed
  generator: "rectangle"      // optional — records what produced the path
                              // values: "rectangle" | "circle" | "ellipse" |
                              //         "freeform" | "polygon" | "rounded-rect"
  generatorParams: { ... }    // optional — keep original input for round-tripping
                              //   e.g. rectangle: {p0, p1}
                              //        circle:    {center, radius}
                              //        ellipse:   {center, a, b, rotation}
}
```

`generator` and `generatorParams` are informational only. Area math never reads them — it always goes through `pathAreaM2`. They exist so the UI can re-open a "circle" with the circle tool, not the freeform editor.

### 5.3 Object shape on `mPolys[i]` (after migration)

```js
{
  // Existing fields (unchanged)
  id, name, color, opacity, areaType, semanticTag,
  measurementProfile, objectCategory, reportTarget, lawBasis, countingRule,
  pageIndex, layerSlug, layerId, edgeTags?, parentManual?, ...

  // ONE of:
  pts: [...]                  // legacy polygon — existing behavior
  // OR:
  geometryType: "path",       // new path-based shape
  segments: [...],
  closed: true,
  generator: "...",
  generatorParams: {...}

  // edges[] (legacy arc-edge meta) is read-only for backward compat
}
```

---

## 6. Backward Compatibility (Hard Rule)

| Existing object form | Treated as | Area computed via |
|---|---|---|
| `{ pts: [...], closed: true }`, no `geometryType` | Legacy polygon | `polyAreaM2(pts)` — unchanged |
| `{ pts: [...], shape: "circle", center, radius }` | Legacy circle | `circleAreaM2(radius, pg)` — unchanged |
| `{ pts: [...], shape: "ellipse", center, semiAxisA, semiAxisB }` | Legacy ellipse | `ellipseAreaM2(semiAxisA, semiAxisB, pg)` — unchanged |
| `{ pts: [...], edges: [{edgeType:"arc", arcSweep:...}, ...] }` | Legacy polygon-with-arcs | `polygonAreaWithArcsM2(poly, pg)` — unchanged |
| `{ geometryType: "path", segments: [...], closed: true }` | **New** path object | `pathAreaM2(obj, pg)` |

**No saved `.bmaplan` file becomes invalid.** No existing object loses its area. Old `circleAreaM2` / `ellipseAreaM2` / `polygonAreaWithArcsM2` stay in the source as backward-compat readers; they are not removed in this design.

The single dispatcher updates to a new top branch:

```js
function objectAreaM2(obj, pg = curPage) {
  if (!obj) return null;
  // NEW branch — placed first
  if (obj.geometryType === "path" && Array.isArray(obj.segments))
    return pathAreaM2(obj, pg);
  // Existing branches — unchanged
  if (obj.shape === "circle" && obj.radius != null)
    return circleAreaM2(obj.radius, pg);
  if (obj.shape === "ellipse" && obj.semiAxisA != null && obj.semiAxisB != null)
    return ellipseAreaM2(obj.semiAxisA, obj.semiAxisB, pg);
  if (Array.isArray(obj.edges) && obj.edges.some(e => e?.edgeType === "arc"))
    return polygonAreaWithArcsM2(obj, pg);
  return polyAreaM2(obj.pts || []);
}
```

`polyAreaM2`, `polyMetrics`, `polySelfIntersects` are untouched.

---

## 7. Function Specifications

These are signatures and contracts only. No implementation in this document.

### 7.1 `flattenPathToPoints(path, tolerance)`

```
Inputs:
  path        Path object with segments[]
  tolerance   max allowed perpendicular distance (in pt) between a flattened
              point and the true curve. Default: 0.5 pt at scale 1:1.

Output:
  flatPts: [{x, y}, ...]   ordered polyline approximation of the path

Contract:
  - For each segment[i]:
      type === "line"  → push p0 (only once per shared vertex), p1
      type === "cubic" → adaptive subdivision until the flat-distance
                         between any control point and the chord p0-p1
                         is ≤ tolerance
  - Output is closed implicitly by polygon-area math (last → first).
  - All input coordinates are raw PDF pt. Output too. No scale applied.
  - flatPts.length is bounded — see safety cap below.

Safety cap:
  - Maximum 10 000 points per path. Bezier subdivision halts early if cap
    is reached and a console warning is emitted. Prevents runaway flattening
    on degenerate input.

Tolerance selection:
  - Default 0.5 pt is finer than a single canvas pixel at RS=1.5 and zoom=1.
  - Caller MAY pass a coarser tolerance for hit-testing / quick preview,
    but area computation always uses the default.
```

### 7.2 `pathAreaM2(path, pg)`

```
Inputs:
  path  Path object
  pg    page index (default curPage)

Output:
  area in m² (number) or null if no scale on page pg.

Contract:
  return polyAreaM2( flattenPathToPoints(path, DEFAULT_TOLERANCE), pg )

Note: pg parameter is passed for symmetry with polyMetrics(poly, pg).
polyAreaM2 today reads curPage internally — this contract relies on that
being correct for the caller's context.
```

### 7.3 `renderPath(ctx, path)`

```
Inputs:
  ctx   2D canvas context (already transformed for zoom/pan/rotation)
  path  Path object

Side effect:
  Draws the path outline. Does not fill, stroke, or close — caller manages
  paint state. Equivalent to building a CanvasPath that the caller can
  ctx.stroke() / ctx.fill() afterward.

Contract:
  ctx.beginPath();
  for (let i = 0; i < path.segments.length; i++) {
    const s = path.segments[i];
    const p0c = pdfToC(s.p0.x, s.p0.y);
    const p1c = pdfToC(s.p1.x, s.p1.y);
    if (i === 0) ctx.moveTo(p0c.x, p0c.y);
    if (s.type === "line") {
      ctx.lineTo(p1c.x, p1c.y);
    } else if (s.type === "cubic") {
      const c1c = pdfToC(s.c1.x, s.c1.y);
      const c2c = pdfToC(s.c2.x, s.c2.y);
      ctx.bezierCurveTo(c1c.x, c1c.y, c2c.x, c2c.y, p1c.x, p1c.y);
    }
  }
  if (path.closed) ctx.closePath();

Existing render paths (mPolys.forEach polygon render, shape==="circle"
ctx.arc render, etc.) are unchanged and remain active for legacy objects.
```

---

## 8. Generators

Each generator is a pure function: input shape parameters → output Path. No state, no canvas, no scale. Coordinates are PDF pt.

### 8.1 `rectangleToPath(p0, p1)`

```
Two opposite corners → 4-segment closed line path.

segments = [
  { type:"line", p0:{x:x0,y:y0}, p1:{x:x1,y:y0} },
  { type:"line", p0:{x:x1,y:y0}, p1:{x:x1,y:y1} },
  { type:"line", p0:{x:x1,y:y1}, p1:{x:x0,y:y1} },
  { type:"line", p0:{x:x0,y:y1}, p1:{x:x0,y:y0} },
]
generator        = "rectangle"
generatorParams  = { p0, p1 }

Acceptance: pathAreaM2(rectangleToPath(p0, p1), pg) equals
            polyAreaM2(corners-as-polygon, pg) within 1e-9 m².
```

### 8.2 `circleToPath(center, radius)`

```
Closed circle as 4 cubic Bézier segments.

Use the standard k = 4*(sqrt(2)-1)/3 ≈ 0.5522847498 control-point offset
that approximates a unit-circle quadrant with maximum radial error
≈ 0.000273. For radius r, control offset = k*r.

The 4 quadrant arcs go counter-clockwise from (cx+r, cy).
segments[i].p1 == segments[i+1].p0 == quadrant endpoint.

generator        = "circle"
generatorParams  = { center, radius }

Acceptance: |pathAreaM2(circleToPath(c, r), pg) - π·r²_m| / (π·r²_m) < 0.001
            where r_m = radius / scale.pts_per_m.
```

### 8.3 `ellipseToPath(center, a, b, rotation = 0)`

```
Closed ellipse as 4 cubic Bézier segments, axis-aligned, then rotated.

Same k = 0.5522847498... as circle, applied to semi-axes:
  horizontal control offset = k*a
  vertical   control offset = k*b

Build segments in unrotated coordinates; if rotation !== 0, transform all
8 points (4 endpoints + 4×2 control points) by the rotation matrix around
center.

generator        = "ellipse"
generatorParams  = { center, a, b, rotation }

Acceptance: |pathAreaM2(...) - π·a_m·b_m| / (π·a_m·b_m) < 0.001
```

### 8.4 `arcToCubic(p0, p1, sweepRad)`

```
Construct ONE cubic Bézier approximating a circular arc with chord p0-p1
and signed sweep angle. For arcs spanning more than 90°, the caller is
expected to split into multiple cubics; this primitive handles |sweep| ≤ π/2
accurately.

Inputs:
  p0        arc start
  p1        arc end
  sweepRad  signed sweep angle (positive = left of chord direction)

Output:
  { type:"cubic", p0, c1, c2, p1 }

Control point derivation:
  - Find arc center given chord midpoint, chord length, and sweep angle.
  - Radius r = chord_length / (2 * sin(|sweep|/2))
  - Tangent at p0 is perpendicular to (center → p0), rotated by sweep direction.
  - Control distance along tangent = (4/3) * tan(|sweep|/4) * r.
  - c1 = p0 + tangent0 * control_distance
    c2 = p1 - tangent1 * control_distance (i.e. backward tangent at p1)

This is the standard cubic approximation used by SVG arc-to-cubic and
most vector tools. Max chord-to-arc error at sweep=π/2 is ≈ 0.000273*r.

Used internally by circleToPath / ellipseToPath if simpler than the
4-quadrant approach proves convenient; also exposed for the existing
"arc-edge" legacy migration path.
```

### 8.5 Other generators (deferred, listed for completeness)

```
roundedRectangleToPath(p0, p1, cornerRadius)
  → 4 lines + 4 quarter-circle cubics. Not in initial scope.

freeformPolygonToPath(pts)
  → trivial conversion of legacy polygon to all-line path.
    Used only when an existing polygon is upgraded to path during edit.
```

---

## 9. Save / Load Compatibility

### 9.1 `.bmaplan` schema additions

The save format is `version: 1` (and stays at 1). Schema is additive only.

For each measurement object stored in `pageStore[n].polys[i]`:

```jsonc
{
  // Existing fields stay exactly as today

  // New optional fields (when geometryType === "path")
  "geometryType": "path",
  "segments": [
    { "type": "line",  "p0": {"x":0,"y":0}, "p1": {"x":100,"y":0} },
    { "type": "cubic", "p0": {"x":100,"y":0}, "c1":{"x":...}, "c2":{"x":...}, "p1": {"x":100,"y":100} }
  ],
  "closed": true,
  "generator": "rectangle",
  "generatorParams": { "p0": {...}, "p1": {...} }
}
```

### 9.2 Load behavior

`applyLoadedProject` and its per-object normalization (`restorePage` /
`validateObjectLayerScope` and friends) gain one branch:

```
if (obj.geometryType === "path" && Array.isArray(obj.segments)) {
  // Trust segments as-is. Compute pts as a flattened cache for legacy code
  // paths that still read obj.pts (label centroid, vertex drag hit-test, etc.):
  obj.pts = flattenPathToPoints(obj, LEGACY_PTS_TOLERANCE);
  obj.closed = true;
}
```

`LEGACY_PTS_TOLERANCE` is chosen so the cached `pts` is dense enough for
hit-testing but not so dense that JSON bloats. Likely value: 1.0 pt.

The cached `pts` is **regenerated on load** — it is not stored on disk.
Source of truth = `segments`.

### 9.3 Old files (no `geometryType`)

Load unchanged. Behave exactly as today. Nothing to migrate. No
forced upgrade. If the user edits a legacy polygon with a future "convert
to path" tool, the resulting object is a path; the original object is
replaced, not mutated in place.

### 9.4 Export

XLSX and PDF export read `objectAreaM2(obj)` only. With the dispatcher
update, both new path objects and all legacy forms produce the same
`area_m2` value. No export sheet/column change.

CSV/JSON export carries `geometryType` and `segments` as-is when present;
old keys (`pts`, `shape`, `radius`, `edges`) are written only when set.

---

## 10. Acceptance Tests (specification only — no implementation here)

The implementation sprint must add these E2E assertions. Each must be
satisfied before the sprint can be marked PASS.

### A. Straight-edge regression

```
1. Build a legacy polygon with 4 corners forming a 5m × 4m rectangle.
2. Build a path with rectangleToPath() on the same 4 corners.
3. Assert: |polyAreaM2(legacy.pts) - pathAreaM2(path)| < 1e-9 m².
```

### B. Circle approximation tolerance

```
For r ∈ {0.1, 1, 5, 50} m at the active page scale:
  area_path     = pathAreaM2(circleToPath(center, r_pt))
  area_analytic = circleAreaM2(r_pt)   // = π r²
  assert |area_path - area_analytic| / area_analytic < 0.001
```

### C. Mixed path stability

```
1. Build a closed path with 3 line segments and 1 cubic segment forming
   a rounded triangle.
2. Compute pathAreaM2 twice (no edit between calls).
3. Assert the two values are bitwise identical.
4. Apply a translation +(dx, dy) to every point (endpoints AND controls).
5. Assert pathAreaM2 is unchanged within 1e-9 m² (translation-invariant).
```

### D. Legacy unchanged

```
1. Load a known-good .bmaplan from before this change.
2. For every poly: confirm objectAreaM2(poly) returns the same value as
   the baseline recorded in the project.
3. Confirm no object has geometryType set after load (legacy must stay legacy).
```

### E. Save round-trip

```
1. Create a path object via rectangleToPath().
2. Save .bmaplan to disk.
3. Load it back into a fresh session.
4. Assert: loaded path has identical segments, generator, generatorParams.
5. Assert: pathAreaM2 on the loaded path equals the saved area.
```

---

## 11. Out of Scope (this sprint)

None of the following are part of this design and must not be implemented
in the design-only stage:

- UI tools to create paths (Pen, Bezier handle drag, "convert to path")
- Hit-testing on cubic segments (current polygon hit-test reads `pts`,
  which the load step now caches — good enough for the design stage)
- Vertex-level edit of cubic control handles
- Migration of existing circle / ellipse / arc-edge objects to path form
- Export `area_method` metadata change (Sprint 5 backlog mentions
  `area_method = flattened_arc`; that is a separate sprint)
- Server.py changes (forbidden)
- Replacement / removal of `circleAreaM2`, `ellipseAreaM2`,
  `arcSegmentAreaM2`, `polygonAreaWithArcsM2` (they stay as legacy readers)

---

## 12. Hard Forbidden (during implementation)

From AGENTS.md §3 and CLAUDE.md "Forbidden surfaces":

- Do not modify `polyAreaM2`, `polyMetrics`, `polySelfIntersects`.
- Do not modify `pdfToC`, `cToPdf`, `RS`, scale math, snap engine.
- Do not modify `proto/server.py`.
- Do not modify `.bmaplan` save format version (stays at 1; additive fields only).
- Do not introduce legal / OCR / AI / FAR / OSR / rule-engine logic.
- Do not calculate from `layer.name` / `layer.slug` (use `semanticTag` /
  `measurementProfile` / `reportTarget` as always).
- Do not add UI in this sprint.

---

## 13. Implementation Order (for the next sprint)

Recorded here so the implementer can pick up without re-deriving:

1. Add `flattenPathToPoints` and `pathAreaM2` near the existing
   `polyAreaM2` (line ~946 in `proto/ui.html`).
2. Add `renderPath` near the existing polygon render block.
3. Add generators: `rectangleToPath`, `circleToPath`, `ellipseToPath`,
   `arcToCubic`.
4. Add the `geometryType === "path"` branch at the top of `objectAreaM2`.
5. Add the path branch to `applyLoadedProject` per-object normalization,
   regenerating `obj.pts` cache from `segments`.
6. Add E2E assertions A–E from §10.
7. Run `py_compile + smoke + full`. All existing markers must remain PASS;
   add a new marker (e.g. `PATH_GEOMETRY_OK`) for the new assertions.
8. Update `PATCH_SUMMARY.md`, `TEST_RESULT.md`, `FINAL_REPORT_FOR_CHATGPT.md`,
   `log.md`, `CURRENT_STATUS.md`, `docs/status/NEXT_ACTIONS.md`.

UI tooling (Pen tool, conversion commands, vertex handle editor) is a
later sprint and is explicitly out of scope.

---

## 14. References

- `proto/ui.html` lines 946–956 — current `polyAreaM2`, `polyMetrics`, and
  the four Phase H.1 area helpers.
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` — layer / object schema this
  design extends additively.
- `docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md` — semantic tag pyramid that
  drives calculation independent of layer/geometry choice.
- `AGENTS.md` §6 Sprint 5 — "Curved Path" backlog item this design implements.
- `docs/status/PHASE_H_PATH_GEOMETRY_DECISION.md` — decision record for
  pivoting from Phase H.1 split shapes to this unified model.
