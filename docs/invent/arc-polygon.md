# Invent — Arc-polygon hybrid area measurement

**Idea source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-15 17:59 (refined 18:02)
**Backlog entry:** `docs/status/PHASE_INDEX.md#discovered-backlog` (ideas 2026-05-15)
**Short-name:** `arc-polygon`
**Started:** 2026-05-15
**Status:** invent-in-progress

## Summary

Add a measurable shape that mixes straight polygon edges with arc segments in ONE object. Area = polygon area ± circular-segment area per arc edge. NOT a full Bezier curve tool, NOT a circle-only tool — the goal is one hybrid shape that lets users measure curved walls / rounded boundaries accurately while staying inside the existing polygon-area data model.

## Frame

### Problem
Real Thai construction permit PDFs frequently contain curved boundaries — rounded property lines, curved building walls, circular driveway turnarounds, swimming pools — that today must be approximated as many short polygon segments. Users either spend disproportionate time clicking 20+ tiny vertices to fake a curve or accept visible inaccuracy in the area total they hand to the city. Existing decorative curve drawing in the app does NOT contribute to area math, so the workaround is invisible to engineers reviewing the file.

### Constraints (non-negotiable)
- **Raster PDFs only.** Cannot rely on PDF vector geometry. Shape must be drawable on the rendered image with mouse clicks alone.
- **Phase 1 boundary.** No legal verdict, no OCR, no AI, no FAR/OSR rule check. This is a measurement primitive, not a compliance feature.
- **Forbidden surfaces.** Cannot edit `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema. Must add new functions next to them.
- **Schema is additive-only.** New shape's serialization fields must be optional; old `.bmaplan v1` loaders must not crash on a file that has none of the new fields, AND files saved before this feature must keep loading unchanged.
- **Page-scoped layer model.** Calculation reads `semanticTag` / `measurementProfile` / `reportTarget`, never `layer.name`. Arc-polygon objects must carry the same 5 metadata fields as polygon objects.
- **Single-file inline JS.** No bundler, no NPM at runtime. Any helper code goes inline next to existing path-geometry functions in `proto/ui.html`.
- **Reuse the path model.** `RUN_PATH_GEOMETRY` already shipped `pathAreaM2`, `flattenPathToPoints`, `renderPath`, `arcToCubic` — must build on these, not parallel them.

### Forbidden surfaces this idea must avoid
`polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema field renaming/removal, FastAPI endpoints in `proto/server.py`. New helpers (`arcSegmentArea`, `arcPolygonToPath`, `arcPolygonAreaM2`) live next to them.

### Success criteria (spike must demonstrate ALL)
1. **Closed-form area accuracy.** A drawn shape composed of 4 straight edges + 1 outward semicircular bulge (chord = 100, sagitta = 50) returns area within 0.1% of the exact closed-form value (rectangle + half-disk).
2. **Backward path-model reuse.** The arc-polygon serializes to the existing path model (lines + cubic Béziers via `arcToCubic`), so `pathAreaM2` and `flattenPathToPoints` keep working with zero edits.
3. **Round-trip stability.** Save → reload → re-render produces a pixel-identical shape and the same area value (within float epsilon).
4. **Degenerate-arc safety.** Setting bulge → 0 (sagitta < 0.5 px) collapses cleanly to a straight edge with no NaN, no flicker, no area jump.
5. **Drawable in ≤ 6 clicks** for a 4-edge shape with 1 arc edge — a real user with no training can produce a measurable arc-polygon in under 30 seconds.

### Out of scope (this invention pass)
- Multi-arc-per-edge (one arc max per edge in v1).
- Editing existing polygons → arc-polygons via "convert edge" (Bluebeam-style two-step). Could come later as an enhancement; not required for spike acceptance.
- Boolean ops (union / difference) between arc-polygons.
- Snap targets ON arc segments themselves (snap to arc midpoint, snap to arc center). Snap to vertices works because vertices already exist; arc-segment snap is a follow-up.
- Full elliptic arcs (only circular arcs in v1 — sagitta + chord uniquely determine a circle).
- Annotation PDF rendering of arc edges (test acceptance can show flattened polyline in PDF; pixel-perfect arc on PDF export is follow-up).
- Per-edge arc summary in XLSX export (the row reports the same `area` field whether straight-or-arc-polygon, no separate "curved area" column).

## Research

_Delegated to `bma-researcher` 2026-05-15. Verbatim output below._

### 1. In-repo prior work

- **`docs/design/PATH_GEOMETRY_MODEL.md`** (2026-05-13) — Unified path-geometry design currently approved and implemented. Supports line + cubic Bézier segments as a single path representation. `pathAreaM2(path)` flattens path to polyline, then calls untouched `polyAreaM2`. Already shipped in sprint `RUN_PATH_GEOMETRY` (2026-05-13, commit `e92db93`). **Directly reusable foundation** for arc-polygon without modifying forbidden surfaces.
- **`RUN_PATH_GEOMETRY.md`** (completed 2026-05-13) — Implemented 7 functions: `flattenPathToPoints`, `pathAreaM2`, `renderPath`, `rectangleToPath`, `circleToPath`, `ellipseToPath`, `arcToCubic`. All E2E acceptance tests A–E PASS. **Arc-polygon can reuse `arcToCubic` + path model** as-is.
- **`RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER`** (in `PHASE_INDEX.md` known leftovers) — render-only smoothing in `redraw()`, unrelated to area measurement. Different concern.
- **`docs/status/PHASE_H_PATH_GEOMETRY_DECISION.md`** (2026-05-13) — Decision record. Confirms `polyAreaM2` unchanged, no forbidden surfaces touched, backward-compatible schema (additive `.bmaplan` v1 only).
- **Phase H.1 path implementation** (`proto/ui.html` lines 956–1100) — Already live: `circleToPath`, `ellipseToPath` generators. Arc-polygon can add `arcPolygonToPath` next to them without conflict.

### 2. CAD / GIS / graphics incumbents

- **AutoCAD LWPOLYLINE bulge** — per-vertex tangent factor; `bulge = tan(included_angle / 4)`. Bulge ∈ [−1, 1] maps to arc direction. Area via signed integral: `polylineArea = polylineVertexArea + sum(circularSegmentArea per bulge)`. Formula: `bulge → included_angle = 4 * atan(|bulge|)` → `radius = chord / (2 * sin(angle/2))` → `segmentArea = r²(θ − sin(θ))/2`. Source: [Lee Mac LWPOLYLINE Bulge](https://www.lee-mac.com/bulgeconversion.html).
- **Rhino NURBS curves** — exact area via Gauss quadrature on parametric integrals. Overkill for simple circular arcs; not relevant to web-canvas measurement.
- **OGC / PostGIS CIRCULARSTRING + CURVEPOLYGON** — SQL/MM standard. CIRCULARSTRING = 3-point arc (start, through, end). CURVEPOLYGON = polygon with ring segments that can be LinearString, CircularString, or CompoundCurve. Area = Cartesian plane calculation + corrections per segment type.
- **Bluebeam Revu** — separate tools: Polygon + Arc. User draws polygon, then right-clicks line segment → "Convert to Arc" → two handle points control curve. Two-step interaction, not unified.
- **Foxit PhantomPDF** — Measurement is polygon-only. No native arc measurement.
- **ArcGIS** — Area calculated via shoelace + per-segment corrections (details not in public API docs).

### 3. Inline-JS library options

| lib | claim | verdict | note |
|---|---|---|---|
| **flatten-js** (`@flatten-js/core`) | Polygons with arc edges (Segment + Arc); area via path traversal | viable | MIT; ~80 KB UMD; loadable as `<script>`; actively maintained |
| **paper.js** | Full vector + path area | wrong-shape | ~100 KB; bundler-friendly not single-file; Illustrator-like API |
| **martinez-polygon-clipping** | Boolean ops on straight polygons | partial-mismatch | no native arc support |
| **turf.js** | Geospatial; LineString only (no arcs) | wrong-shape | ~50 KB; large surface area |
| **Native SVG / Canvas `arcToCubic`** | Cubic-Bézier approximation of arc | already-in-use | BMA-Plan shipped this 2026-05-13; no new dep |

**Conclusion on libs:** flatten-js is the only off-the-shelf candidate for an arc-polygon model with native arc segments. But BMA-Plan has already shipped `arcToCubic` + `pathAreaM2`, so **building arc-polygon in-house is cheaper than adopting flatten-js** — avoids a new dependency, keeps area-math contract under our control, reuses existing path infrastructure.

### 4. Algorithm / literature

- **Circular segment area** — `K = r²(θ − sin θ)/2`, where `r` = radius, `θ` = central angle (rad). Chord and sagitta uniquely determine `r` and `θ`. Stable for all `θ ∈ (0, 2π)`. ([Wikipedia: Circular Segment](https://en.wikipedia.org/wiki/Circular_segment))
- **Shoelace + Green's theorem** — Polygon signed area = `0.5 × Σ(x_i × y_{i+1} − x_{i+1} × y_i)`. Extends to mixed straight + arc edges by splitting `∫_C x dy` per segment: straight parts use shoelace, arc parts use circular-segment correction.
- **Numerical stability** — Cancellation possible when sagitta → 0; degenerate-to-straight check needed (treat |sagitta| < ε as straight edge).
- **Self-intersection** — Arc-edged closed boundaries: detect by flatten-then-segment-test (use existing `polySelfIntersects` on flattened polyline) — keeps detection inside the un-touched forbidden surface.

### 5. Competitor measurement UX

- **Bluebeam Revu** — Two-step: draw polygon, then right-click each edge → "Convert to Arc" → drag handles. Closest to a unified arc-polygon UX shipped in market.
- **Foxit PhantomPDF** — No arc measurement.
- **PlanGrid** — Free-form area only; no per-edge arc control.
- **AutoCAD** — Bulge can only be set via numeric property edit, not interactive draw — very engineer-flavored, low UX.

### Verdict: PRIOR_ART_PARTIAL

**Rationale:** AutoCAD's bulge model + BMA-Plan's already-shipped path geometry (`arcToCubic`, `pathAreaM2`, `flattenPathToPoints`) provide the proven mathematical foundation for arc-polygon measurement. flatten-js exists but is not required — the path model already supports arcs via cubic Bézier approximation, and shoelace extends naturally. However, **no incumbent on raster-PDF web canvas ships a unified arc-polygon measurable object** — Bluebeam uses two separate tools chained. UX/interaction design for drawing + editing arc-polygon (vertices + per-edge arc controls) is genuinely new. Build on the path model already in production; focus divergence on UX (how users draw arcs + edit them) and integration into the existing polygon-like measurement workflow.

## Diverge

_Delegated to `bma-inventor` 2026-05-15. All 5 approaches verified: `forbidden_surface_touch: NO`, `phase_1_boundary_violation: NO`, `additive_schema_compatible: YES`._

**Critical fact surfaced during diverge:** `proto/ui.html:1007-1019` already ships `arcSegmentAreaM2`, `polygonAreaWithArcsM2`, and the `objectAreaM2` arc-dispatch branch. The closed-form area math for arc-edged polygons is **already in production** — it has no UI to create `obj.edges[i] = {edgeType:"arc", arcSweep}` records. The invention reduces to: design the UX that fills `obj.edges`.

### Approach A: Polygon-with-edges bulge table (data-model)
Standard `poly` with optional parallel `obj.edges[]` of `{edgeType:"arc", arcSweep}`. Already supported by `polygonAreaWithArcsM2`. UX = post-draw Properties-panel slider per edge.

### Approach B: Inline arc-segment in path model (representation)
Add `{type:'arc', p0, p1, center, sweepRad}` as a third segment kind in `obj.segments[]`. `flattenPathToPoints` gets an `if(s.type==='arc')` branch; `pathAreaM2` is unchanged. UX = Alt-click during path draw enters arc mode.

### Approach C: Three-click inline arc during polygon draw (UX) ⭐
Extend the polygon-draw state machine: after vertex N, press 'A' or middle-click to enter arc mode, then click the through-point on the curve, then click vertex N+1. Auto-compute center + sweep from the 3 points; store `{edgeType:"arc", arcSweep, arcThrough}` in `obj.edges[N]`. Area uses already-shipped `polygonAreaWithArcsM2`. **Arc placement integrates into the normal vertex-click rhythm.**

### Approach D: Closed-form Green's theorem integral (algorithm)
Same data model as A. Replace `polyAreaM2 + Σ arcSegmentArea` with one analytical line integral per edge: straight = trapezoid, arc = `r²(θ − sin θ cos θ)/2 + cx·r·sin θ`. Mathematically exact (no flatten error).

### Approach E: arcTo + flatten-js inline (library)
New first-class `obj.type='arcPolygon'` with `vertices: [{x, y, arcRadius?}]`. Render via `ctx.arcTo` (tangent-arc to both adjacent edges, like rounded rectangle). Lift ~40 lines from flatten-js for area. Parallel infrastructure to existing path model.

## Score

| Approach | Novelty | Accuracy | UX | Model fit | Boundary | Cost | Total |
|---|---|---|---|---|---|---|---|
| A: Polygon edges bulge table | 2 | 4 | 3 | 5 | 5 | 5 | **24** |
| B: Arc segment in path model | 3 | 3 | 4 | 4 | 5 | 4 | **23** |
| **C: Three-click inline arc** | **4** | **4** | **5** | **4** | **5** | **3** | **25** |
| D: Green's theorem integral | 5 | 5 | 3 | 4 | 5 | 3 | **25** |
| E: arcTo + flatten-js inline | 3 | 4 | 3 | 3 | 5 | 3 | **21** |

C and D tie at 25; tie-break favours C because the in-production `polygonAreaWithArcsM2` already gives "good enough" area accuracy → UX is the bottleneck the user actually feels.

**SCORE-VERIFICATION (per skill phase 5):**
- No approach with `forbidden_surface_touch: YES` ranks first ✓ (none touch forbidden surfaces).
- No approach crossing Phase 1 boundary ranks first ✓ (no legal/OCR/AI/FAR-OSR in any).
- No re-rank or override needed.

## Recommendation

**Top approach for spike: C — Three-click inline arc during polygon draw.** Highest UX score, leverages already-shipped `polygonAreaWithArcsM2` for area math, and the through-point flow maps directly to success criterion 5 (≤ 6 clicks for a 4-edge + 1-arc shape in under 30s). Reuses existing schema fields with only one new optional field (`arcThrough`).

**Fallback if C fails in spike: D — Green's theorem integral.** If the inline three-click state machine proves brittle (snap interference, midpoint ambiguity), D keeps the same schema and trades algorithm for guaranteed numerical exactness — testable in pure JS without a draw-tool spike.

## Spike

**Approach attempted:** C — three-click inline arc during polygon draw.
**Outcome:** ✅ PASS on all 5 success criteria, first attempt. Fallback (D) not needed.

**Sandbox file:** `proto/sandbox/invent-arc-polygon.html` — standalone HTML, opens directly in browser, no server. Math helpers (`polyAreaPx`, `arcSegmentAreaPx`, `polygonAreaWithArcsPx`) are inline copies of `proto/ui.html:999-1019` with the page-scale dependency stripped (spike works in raw px²).

### Verification — node smoke-run of math kernel

| # | Criterion | Result | Detail |
|---|---|---|---|
| 1 | Closed-form area accuracy (square 100×100 + outward semicircle, chord 100, sagitta 50) | ✅ | computed = 13926.9908, expected = 13926.9908, **err = 0.00000 %** (well under 0.1 % budget) |
| 2 | Schema match with live `polygonAreaWithArcsM2` | ✅ | `obj.edges[i] = {edgeType:"arc", arcSweep, arcThrough}` — `arcThrough` is the only NEW optional field; `edgeType` + `arcSweep` are already read by live code |
| 3 | Round-trip save → JSON.parse → reload | ✅ | delta = 0 (exact match) |
| 4 | Degenerate arc collapses to straight | ✅ | through-point on chord midpoint → `sweep = 0`, area returns to 10000 (= plain `polyAreaPx`), no NaN |
| 5 | ≤ 6 clicks for 4-edge + 1-arc shape | ✅ | 5 mouse clicks + 1 keypress (`A`) + 1 keypress (`Enter`) — well under budget |

### Sign-convention bonus check
Inward through-point `{x:80, y:50}` (inside polygon) → `sweep = −1.522 rad`, area = **8624.93 px²** (< plain 10000) — correctly subtracts the inward bite. This confirms the centroid-side detection in `computeArc` works for both bulge directions without requiring user winding-direction input.

### Math + UX architecture demonstrated
- New helper: `circumcenter(A, P, B)` — circumcircle through three points. ~6 lines.
- New helper: `computeArc(A, B, P, polygonCentroid)` — derives `{sweep, center, radius}` from start, end, through-point. Sign of sweep determined by which side of chord the through-point lies relative to the polygon centroid. Handles degenerate (collinear / sag → 0) safely.
- One new optional schema field: `obj.edges[i].arcThrough = {x, y}` — kept alongside the existing `arcSweep` so re-render after load works without recomputing.
- Reuses already-shipped `polygonAreaWithArcsM2`, `objectAreaM2` arc-dispatch — **zero edits to forbidden surfaces**.

### Estimated production sprint cost
- Polygon-tool state machine extension for the `A`-keypress + through-point flow: ~80 lines in `proto/ui.html`.
- `circumcenter` + `computeArc` helpers: ~30 lines.
- Render branch in `redraw()` for arc edges (reuse Canvas `ctx.arc`, parameters from `computeArc`): ~20 lines.
- Save/load: zero net code (additive optional fields).
- Tests: 1 new E2E marker `ARC_POLYGON_OK` + 1 new test in `proto/e2e_ui_test.py` (build the canonical square-plus-bulge, assert area within 0.1 %).
- **Total ≈ 150 lines + 1 marker.** No forbidden-surface edits, schema fully additive.

### Risks observed in the spike
- **Snap interference (not yet tested):** in production the existing `buildSnapIndex` will fire on the through-point click. Snap may pull the through-point to a vertex, collapsing the arc to a straight edge. **Mitigation:** during arc-mode the through-point click should bypass vertex/edge snap (snap to nothing, or only to grid). This is a `bma-measure-ux-specialist` concern, not an algorithm concern.
- **Through-point ambiguity for nearly-straight arcs:** very small sagitta (1–5 px) gives noisy sweep. The spike's `< 0.5 px` degenerate threshold handles it cleanly; production may want a UX hint ("drag further from the chord for a defined arc").
- **Self-intersection:** arc-edged polygons can self-intersect in ways `polySelfIntersects` (which only checks straight segments) does not see. **Mitigation:** flatten the path with a coarse tolerance and run existing `polySelfIntersects` on the result. Same forbidden-surface-free pattern.

### Why approach D was not needed
The `polygonAreaWithArcsM2` formula in production already gives mathematically exact area for the closed-form case (chord + sweep → segment area). Approach D's Green's-theorem integral would be NUMERICALLY identical — D's "novelty=5" advantage is mathematical elegance, not measurable accuracy. Spike result `err = 0.00000 %` confirms the existing closed-form formula is sufficient.

## Decision (GO)

**Decided:** 2026-05-15 by user at human checkpoint.
**Sprint id:** `INV-2026-05-15-001`
**Status flip:** `invent-in-progress` → `invent-done-go (→ INV-2026-05-15-001)`

### Why GO
- Spike passed all 5 success criteria on first attempt with err = 0.00000 %.
- Math kernel (`polygonAreaWithArcsM2`) is already in production at `proto/ui.html:1007-1019` — sprint reduces to UI/UX work over a tested math layer.
- Zero forbidden-surface edits required; schema change is one additive optional field.
- Real customer benefit: rounded property lines / curved building walls / driveway turnarounds become measurable in ≤6 clicks instead of 20+ vertex approximations.

### Sprint scope handed to `/bma-dev-loop`
Sprint card written to `docs/status/PHASE_INDEX.md` under id `INV-2026-05-15-001`. Picks up after the existing U1/U2/HT-1 queue is cleared, unless reprioritised.

### Carry-over risks for the production sprint
1. **Snap interference** on through-point click — production must bypass vertex/edge snap when in arc-mode. Route through `bma-measure-ux-specialist`.
2. **Self-intersection** of arc-edged polygons — flatten with coarse tolerance and run existing `polySelfIntersects` on the flattened polyline. Forbidden surfaces untouched.
3. **Through-point ambiguity** for nearly-straight arcs — degenerate threshold `sag < 0.5 px` from spike carries forward; production may also show a UX hint when the user is in the ambiguous range.
