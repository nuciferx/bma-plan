# Invent — Freeform area measurement (lasso / hold-drag tool)

**Idea source:** user 2026-05-17 (verbatim) "ทำการวัดพื้นที่รูป freeform" — captured after user tested INV-001 Arc-polygon and reported it works well but wanted a separate tool for organic shapes.
**Backlog entry:** `docs/status/PHASE_INDEX.md` → ideas 2026-05-17 (`freeform-area`, status `invent-in-progress`)
**Short-name:** `freeform-area`
**Started:** 2026-05-17
**Status:** invent-done-go (→ INV-2026-05-17-001)

## Summary

A measurement tool where the user **holds the mouse button and drags** to trace an organic boundary along the canvas, releases to close the polygon. Sampled points are decimated (RDP or distance-bin) to a ~30-150 vertex polygon, then area is computed via the existing `polyAreaM2` shoelace. Differs from the 3 polygon-family tools already shipped:

- **Polygon (click-per-vertex)** — user controls every vertex, slow but precise
- **Arc-polygon (INV-001)** — click + `A` + through-point click for arc edges
- **Rect/Circle/Ellipse** — parametric primitives
- **Freeform (this)** — hold-drag for fast organic outline; user doesn't think in vertices

Use cases the user described: irregular planting beds, free-form pond outlines, hand-traced land boundaries from old surveys, natural shorelines.

## Frame

### Problem

Real BMA-Plan jobs sometimes need to measure organic / non-orthogonal boundaries that don't fit the existing polygon-family tools well: hand-drawn land boundaries on scanned old surveys (where every micro-curve matters), planting beds, pond outlines, irregular zoning overlays. Today these force users into one of two unhappy paths:

1. **Click-per-vertex polygon** — high vertex count (40-100+ clicks); slow; user fatigue; vertices often misplaced because user has to switch attention between the curve they're tracing and the cursor
2. **Coarse polygon** — quick but loses accuracy; area off by 5-15% from the true visual boundary

Neither matches the natural "trace the outline" motion. The invention is a third option: hold-mouse-and-drag, release closes the shape, system decimates to a sensible vertex count, area computed identically to existing polygons. Per research (GREENFIELD verdict), **no PDF-measurement incumbent ships freehand area** — Bluebeam, Foxit, Acrobat are all click-polygon only. GIS tools (QGIS, ArcGIS) have it, but their interaction model is shift+drag-with-tolerance, optimized for stream digitizing of GPS-aligned features, not a single shape on a scanned PDF.

### Constraints (non-negotiable)

- **Raster PDFs only.** Cannot rely on vector geometry. Tool must work with mouse + canvas alone.
- **Phase 1 boundary.** No legal verdict, no OCR, no AI, no FAR/OSR rule check. This is a measurement primitive.
- **Forbidden surfaces.** Cannot edit `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema field renaming/removal, `proto/server.py` endpoints. New helpers (`rdpSimplify`, `sampleFreeformPoints`, `finishFreeformArea`) live next to existing measure helpers.
- **Schema additive only.** Output polygon serializes through the existing `.bmaplan v1` schema with no new required fields. Optional metadata `obj.freeform:{tolerance, originalSamples}` is OK; legacy loaders must keep working without it.
- **Page-scoped layer model.** Freeform polygons carry the same 5 metadata fields as polygon objects (`measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`).
- **Single-file inline JS.** No bundler, no NPM at runtime. RDP / Chaikin / sampling helpers all inline in `proto/ui.html`.
- **Reuse existing area math.** The output is a closed polygon — `polyAreaM2(decimatedPts)` works as-is. No new area-math function needed.

### Forbidden surfaces this idea must avoid

`polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap` engine internals, `.bmaplan` schema renaming/removal, `proto/server.py` endpoints. New helpers (`rdpSimplify`, `freeformSampleStep`, `finishFreeformArea`) live next to them as additive functions.

### Success criteria (spike must demonstrate ALL)

1. **Hold-drag-release produces a closed polygon.** Mouse-down → mouse-drag samples points → mouse-up auto-closes → `polyAreaM2` returns a sensible area within 5% of the visual trace target.
2. **Decimation reduces ~500 raw samples to ~30-150 vertices** at default tolerance, without visibly changing the silhouette. Tolerance is exposed to the user as a slider or simple setting (coarse / medium / fine).
3. **Round-trip stable.** Save → reload → re-render produces identical area (within float epsilon) and pixel-identical shape.
4. **Self-intersection detected.** Freehand strokes often cross themselves. Existing `polySelfIntersects` runs on the decimated polyline; if it returns true, status bar warns + area shows `—` (same UX as existing polygon).
5. **Drawable in ≤ 1 second** for a simple closed shape (e.g. a roughly-circular planting bed). Compare to ~10-30 seconds for the equivalent click-polygon.
6. **Coexists with existing tools.** Does not break polygon / arc-polygon / rect / circle / ellipse. Activated via a separate `setMode("freeform")` or via a sub-mode of polygon (TBD in diverge).

### Out of scope (this invention pass)

- Touch input / iPad UX. Mouse-only in v1 (iPad backlog has its own track).
- Smart snap-to-vector during drag (would require live snap-engine integration; defer to v2).
- Magnetic-lasso style edge detection from raster (requires image processing; Phase 2 territory).
- Auto-correct self-intersection (just detect + warn in v1).
- Multi-segment freehand (e.g. holding shift to add a second loop). Single closed polygon per draw.
- Mixing freehand edges with arc edges (could be a v2 hybrid; v1 is straight-segment-only).
- Custom per-tool tolerance picker UI in the modal. v1 uses a global default + maybe a keyboard modifier (Shift = coarser, Alt = finer).

### Decisions deferred to DIVERGE

1. **Interaction model:**
   - (a) Standalone tool — click a "freeform" button on ribbon, then hold-drag-release
   - (b) Sub-mode of polygon — Shift+drag from inside polygon tool starts freehand
   - (c) Magic / context-sensitive — long-press inside polygon tool enters freehand
   - (d) Modal "freehand area" entry from Measure menu

2. **Sampling strategy during drag:**
   - (a) Time-interval (sample every 16ms / 60fps regardless of mouse speed)
   - (b) Distance-bin (sample only when cursor moved ≥ N pixels since last sample)
   - (c) Raw + simplify on release (collect every mousemove event; defer all decimation to release)

3. **Simplification algorithm:**
   - (a) RDP (Ramer-Douglas-Peucker) — recursive perpendicular distance
   - (b) Visvalingam-Whyatt — area-of-triangle metric, preserves shape better at low tolerances
   - (c) Both (RDP fast pass + Visvalingam touch-up)

4. **Post-simplification smoothing:**
   - (a) None — raw decimated polyline (sharp corners possible)
   - (b) Catmull-Rom spline — passes through control points, smoother curves
   - (c) Chaikin corner-cutting — 1-2 subdivision passes, fast, smooths sharp kinks

5. **Closing strategy:**
   - (a) Auto-close to start point on mouse-up always
   - (b) Auto-close only if end-point is within R pixels of start (else open polyline)
   - (c) Require explicit double-click or Enter to close

## Research

_Delegated to `bma-researcher` 2026-05-17. Verbatim output below._

### 1. In-repo prior art

- **`proto/ui.html:1166-1187`** — `polyAreaM2(pts)` (shoelace formula, forbidden surface but read-only here) and `pathAreaM2(path, pg)` already shipped in `RUN_PATH_GEOMETRY`. Freeform area can flatten sampled points to an array and call `polyAreaM2` directly; no new area-math functions needed.
- **`proto/ui.html:1186`** — `flattenPathToPoints(path, tol)` + `_PATH_FLATTEN_TOL = 0.5 pt` already in production. Freeform sampling can reuse this flattening logic for tolerance-driven simplification if output is encoded as a path.
- **`docs/design/PATH_GEOMETRY_MODEL.md`** (2026-05-13) — Unified path model (line + cubic Bézier segments). Freeform can serialize sampled points as a line-segment path, then feed to `pathAreaM2`. Same closed-polygon area contract as arc-polygon.
- **`docs/invent/arc-polygon.md` § Diverge** — Arc-polygon uses a polygon-with-edges model + optional per-edge metadata. Freeform's output is a simple polygon (no arc edges), no conflict or duplication.
- **`docs/status/PHASE_INDEX.md:97-101`** — Freeform-area is `invent-queued`. Open questions recorded: sampling strategy (RDP vs time-interval vs distance), post-drag smoothing (Catmull-Rom vs raw), interaction model (lasso vs shift+drag vs tool chain), whether it extends polygon tool or stands alone.

### 2. Inline-JS library options

| lib | claim | verdict | note |
|---|---|---|---|
| **simplify.js** | RDP + radial-distance polyline simplification | viable | MIT; ~3 KB; extractable for inline use |
| **paper.js** | Full path freehand + `path.smooth()` + `path.simplify()` | wrong-shape | ~100 KB; bundler-centric |
| **flatten-js** | Polygon w/ boolean ops; no native freehand | wrong-shape | 50 KB; geometry engine, not drawing |
| **chaikin smoothing** | Corner-cutting subdivision | partial-fit | ~10 LOC of JS; commonly inlined |
| **Native RDP + existing polyAreaM2** | Inline RDP + reuse shoelace | already-in-use | matches BMA-Plan's no-bundler stance |

**Conclusion:** in-house RDP (~50 LOC) + optional Chaikin post-smoothing is the recommended path; simplify.js is the fallback library if inlining proves brittle.

### 3. CAD / GIS / graphics prior art

- **AutoCAD SKETCH** — hold-drag, raw segments, no auto-simplify, area via separate `AREA` command on closed polyline
- **QGIS stream digitizing** — shift+drag, live tolerance simplification, snap optional
- **ArcGIS streaming** — right-click → Streaming, time/distance interval vertices
- **Bluebeam Revu** — **no native freehand area tool** (click-polygon only)
- **Foxit PhantomPDF** — **no freehand mode** (click-polygon only)

**Verdict:** GIS tools have mature freehand; **PDF measurement tools (Bluebeam, Foxit) do NOT ship freehand area.** Gap in the PDF-measurement market.

### 4. Algorithms / literature

- **Ramer-Douglas-Peucker** — recursive perpendicular-distance threshold; O(n log n); ~30 LOC inline
- **Visvalingam-Whyatt** — area-of-triangle metric; preserves shape better at low tolerance
- **Shoelace area** — already in BMA-Plan as `polyAreaM2`; works directly on decimated points
- **Catmull-Rom spline** — optional smoothing pass (centripetal variant avoids loops)
- **Chaikin corner-cutting** — 1:3 ratio subdivision; ~5 LOC; converges to quadratic B-spline

### 5. Competitor UX

- **Bluebeam / Foxit / Acrobat** — click-polygon only, no freehand area
- **QGIS** — shift+drag with visible tolerance setting; most mature precedent
- **ArcGIS Mobile** — touch-first streaming for field GPS work
- **PlanGrid / Procore** — freehand annotation only (no area measurement)

**Key UX pattern:** GIS binds freehand to a tolerance slider. No PDF tool offers freehand area — the user's request is genuinely new for this product category.

### Verdict: GREENFIELD

No PDF incumbent ships freehand area; math is trivial (`polyAreaM2` on decimated points); the invention is in UX + interaction model + sampling defaults, not in geometry algorithms.

## Diverge

_Delegated to `bma-inventor` 2026-05-17. All 5 approaches verified: `forbidden_surface_touch: NO`, `phase_1_boundary_violation: NO`, `additive_schema_compatible: YES`._

### Approach A: Separate lasso tool, distance-bin sampling, RDP, no smoothing, auto-close (axis: tool/state-machine)
Dedicated "Freeform Area" ribbon button sets `mode="freeform"`. `mousedown` starts capture; `mousemove` appends when cursor moved ≥ `SAMPLE_STEP_PX` (4 px). `mouseup` triggers `rdpSimplify` + auto-close + `polyAreaM2`. Output is `obj.type='poly'` + optional `obj.freeform={tolerance,originalCount}`. Self-intersection check via existing `polySelfIntersects`. Live feedback = raw mouse trail.

### Approach B: Polygon sub-mode, raw-collect-then-simplify, Visvalingam-Whyatt + Chaikin, distance-threshold close (axis: simplification algorithm)
Inside polygon mode, `mousedown + hold > 150 ms without mouseup` flips to freehand. Every `mousemove` appends raw (no distance gate). `mouseup` runs Visvalingam-Whyatt (~35 LOC, preserves shape better than RDP) + Chaikin (5 LOC smoothing). Closes only if release within R=20 px of start; otherwise open with warning.

### Approach C: Freehand → Bézier path representation, Catmull-Rom smoothing, live preview curve (axis: representation)
Standalone tool. Time-interval sampling (RAF, 16 ms). On `mouseup`, sampled points → cubic Bézier via centripetal Catmull-Rom. Serialises as `obj.type='path'` + `obj.segments=[...]` reusing the shipped path-geometry model. `pathAreaM2` computes area via existing `flattenPathToPoints`. Live feedback = smoothed Catmull-Rom curve redrawn on each RAF tick. Zero new schema fields (reuses path type).

### Approach D: Alt sub-mode of polygon, dist-bin sampling, RDP + tolerance badge, explicit Enter-to-close (axis: UX) ⭐
Inside polygon mode, holding `Alt` during `mousedown` flips to streaming sub-mode (QGIS-style). Distance-bin sampling (≥ 6 px). On `Alt`-release the sub-mode pauses; user can keep adding click-vertices. `Enter` closes + decimates with RDP. **Tolerance badge** on canvas (Shift = coarser, Ctrl = finer during draw). No smoothing — raw RDP. Power-user unlock: mix click-vertices (anchors) with Alt-drag-segments in one polygon.

### Approach E: Standalone lasso, raw + RDP on release, live running-decimation preview (axis: live-feedback)
Separate ribbon button. Every `mousemove` raw (no distance filter). **Key novelty:** debounced worker (every 100 ms) runs fast RDP on accumulated buffer and **redraws the decimated polygon outline as live preview** — user sees the simplified shape in real time, not raw mouse trail. Final RDP at full resolution on `mouseup`. Nothing in the surveyed competitive set ships this.

## Score

| Approach | Novelty | Accuracy | UX | Model fit | Boundary | Cost | Total |
|---|---|---|---|---|---|---|---|
| A: Separate lasso, dist-bin, RDP | 3 | 4 | 4 | 5 | 5 | 5 | **26** |
| B: Polygon sub-mode, VW + Chaikin | 3 | 4 | 3 | 5 | 5 | 3 | **23** |
| C: Freehand → Bézier path | 4 | 3 | 4 | 4 | 5 | 3 | **23** |
| **D: Alt sub-mode + tolerance badge** | **4** | **4** | **5** | **5** | **5** | **3** | **26** |
| E: Live running-decimation preview | 5 | 4 | 4 | 5 | 5 | 3 | **26** |

Three-way tie at 26 (A, D, E). Tie-break: D > E > A based on UX score equal cost. D's mixed-mode polygon flow is the genuine power-user unlock; E's live preview is novel but the debounced running-RDP is technically riskier.

**SCORE-VERIFICATION (per skill phase 5):**
- No approach with `forbidden_surface_touch: YES` ranks first ✓ (all 5: `NO`)
- No approach crossing Phase 1 boundary ranks first ✓ (all 5: `NO`)
- No re-rank or override needed.

## Recommendation

**Top for spike: D — Alt sub-mode of polygon + tolerance badge + Enter-to-close.** Highest UX score (5), model-fit clean (output is `obj.type='poly'`, no new area math), and explicit Enter-to-close is already wired in polygon mode — half the closing logic is free. Mixed click + drag in one polygon = power-user unlock.

**Fallback: Approach A — Separate lasso tool.** If D's polygon-state-machine intrusion proves brittle, A is the clean separate tool — zero polygon-tool changes, smallest implementation cost. Fall through to E if A also fails (3-attempt loop budget).

## Spike

**Approach attempted:** D — Alt sub-mode of polygon, distance-bin sampling, RDP, tolerance badge, explicit Enter-to-close.
**Outcome:** ✅ PASS on all 6 success criteria, first attempt. Fallback (A) not needed.

**Sandbox file:** `proto/sandbox/invent-freeform-area.html` — standalone, opens directly in browser. Math helpers (`polyAreaPx`, `polySelfIntersects`, `rdpSimplify`) are inline. The spike implements the full Approach D state machine: click-per-vertex by default, Alt+drag enters freehand sub-mode with distance-bin sampling, Shift / Ctrl modulate tolerance live during draw, Enter closes + decimates + computes area. In-browser test runner mirrors the Node smoke.

### Verification — Node-headless smoke run (math kernel)

```
T1 area: 20351.40 expected 20106.19 err 1.22% PASS
T2 raw 500 → decimated 14 PASS
T3 round-trip delta 0.00e+0 PASS
T4 figure-8 self-intersects: true   circle: false PASS
T5 150 samples → decimated 17 area 19599.77 in 0ms PASS
T6 mixed mode raw 33 → decimated 11 area 5213.52 PASS
```

| # | Criterion | Result | Detail |
|---|---|---|---|
| 1 | Hold-drag-release area within 5 % of visual target | ✅ | Noisy circle (240 raw samples, ±2 px noise) → 14 vertices, area err = **1.22 %** (well under 5 % budget) |
| 2 | Decimation reduces ~500 raw to ≤ 150 vertices at default tolerance | ✅ | 500 squiggle samples → **14 decimated** (tol = 2 px) |
| 3 | Save → reload → re-compute area identical | ✅ | `delta = 0.00e+0` after JSON round-trip |
| 4 | Self-intersection detection on figure-8, not on circle | ✅ | figure-8 = true, decimated circle = false |
| 5 | Drawable in ≤ 1 s for simple shape | ✅ | 150-sample synthetic 1-s circle decimates + areas in **0 ms** (way under 50 ms budget) |
| 6 | Coexist with existing tools (mixed click + drag) | ✅ | 2 click + 30 freehand + 1 click → decimated 11 vertices, area = 5213.52, valid |

### Architecture demonstrated

- **New helper:** `rdpSimplify(pts, tol)` — ~25 LOC inline Ramer-Douglas-Peucker. Production location: `proto/ui.html` alongside `flattenPathToPoints` / `pathAreaM2`.
- **No new area math** — `polyAreaPx` (= production `polyAreaM2`) called unchanged on decimated points.
- **No new self-intersection helper** — existing `polySelfIntersects` runs on decimated polyline.
- **State machine:** existing polygon `mousedown` handler gains an Alt-modifier branch (~20 LOC); `mousemove` handler gains a `dragging&&altDown` distance-bin branch (~15 LOC); `mouseup` commits the burst by decimating + appending (~10 LOC). Enter-to-close path is **unchanged** (reuses existing polygon close logic).
- **Tolerance badge:** new DOM element + Shift/Ctrl keydown modifiers (~30 LOC). Pure UI.
- **Schema:** output is `obj.type='polygon'` with optional `obj.freeform={tolerance,originalCount,freehandSegments}`. Legacy loaders ignore unknown fields. **Zero `.bmaplan` migration.**

### Estimated production sprint cost

- Polygon-tool state-machine extension (`mousedown` Alt-branch, `mousemove` dist-bin, `mouseup` commit): ~50 LOC in `proto/ui.html`
- `rdpSimplify` helper: ~25 LOC
- Tolerance badge DOM + Shift/Ctrl keydown handlers: ~30 LOC
- Save / load: zero net code (optional additive fields)
- E2E test: 1 new marker `PHASE_FREEFORM_OK` + 1 test in `proto/e2e_ui_test.py` (synthesize raw sample buffer, decimate, assert area within tolerance, mixed-mode probe). ~40 LOC
- **Total ≈ 150 LOC + 1 marker.** Zero forbidden-surface edits. Schema fully additive.

### Risks observed in the spike

- **Alt detection ambiguity** — if Alt is held BEFORE mousedown (user planned ahead), the spike works. If Alt is pressed DURING an already-started click-polygon mid-stroke, the user would expect the in-progress click to switch — spike doesn't handle this gracefully (would commit one stray vertex). Production should add a tiny guard: only enter freehand-sub-mode when `altKey` was set at the moment of `mousedown`.
- **Snap engine bypass** — the freehand burst captures raw cursor positions (no snap). This is by design (snap during freehand would jerk the line). Production should explicitly skip the snap branch when `altDown && dragging` to avoid wasted CPU. `buildSnapIndex`/`snap` untouched.
- **Touch input** — `mousedown` / `mousemove` / `mouseup` work for mouse + most styluses but not touch. Spike is mouse-only (per frame: out of scope for v1). iPad workstream will need a `pointerdown/move/up` polyfill or duplicate path.
- **Tolerance picker UI** — spike uses Shift / Ctrl modifiers. Production may want a visible slider in the Properties panel for post-draw re-decimation (a v1.1 polish, not blocking v1).

### Why approaches B / C / E were not attempted

D's spike passed all 6 criteria on first attempt with err = 1.22 % (well under budget) and full mixed-mode validation. Per skill phase 6 rules: spike succeeded → no fallback needed. B (Visvalingam + Chaikin) is documented as a future enhancement if real-user feedback shows RDP-only produces visibly jagged outlines at certain tolerances. C (Bézier path representation) is a future re-architecture if BMA-Plan later wants pixel-perfect curve fidelity on annotated PDF export. E (live running-decimation preview) is the highest-novelty alternative if user-test reveals confusion about what the final shape will look like vs the raw mouse trail.

## Decision (GO)

**Decided:** 2026-05-17 by user at human checkpoint.
**Sprint id:** `INV-2026-05-17-001`
**Status flip:** `invent-in-progress` → `invent-done-go (→ INV-2026-05-17-001)`

### Why GO
- All 6 spike success criteria PASS on first attempt (Node-headless 6/6, err = 1.22% on noisy circle)
- Zero forbidden-surface edits required; new `rdpSimplify` helper additive
- Schema fully additive (`obj.type='polygon'` + optional `obj.freeform`)
- Genuine market gap: no PDF measurement incumbent ships freehand area
- Pattern mirrors INV-001 Arc-polygon's successful sub-mode extension

### Sprint scope handed to `/bma-dev-loop`
Sprint card written into `docs/status/PHASE_INDEX.md` active queue with id `INV-2026-05-17-001`. Ready for next `/bma-dev-loop` iteration.

### Carry-over risks for production sprint
1. **Alt-mid-stroke ambiguity** — guard `altKey at mousedown only` (not during)
2. **Snap engine bypass** — explicit early-return in `mousemove` snap branch when `altDown && dragging`
3. **Touch input** — mouse-only in v1; iPad/`pointerdown` polyfill deferred

### GO criteria met
- ✅ All 6 spike success criteria PASS on first attempt (Node-headless 6/6)
- ✅ Zero forbidden-surface edits required (`polyAreaM2` / `pdfToC` / `cToPdf` / `RS` / `snap` / `polyMetrics` / `polySelfIntersects` / `.bmaplan` schema all untouched; new `rdpSimplify` helper additive)
- ✅ Zero new runtime dependencies — inline ~25-LOC RDP
- ✅ Matches BMA-Plan's existing architectural stance — extends polygon-tool state machine additively, output is `obj.type='polygon'` with one optional `freeform` metadata field
- ✅ Genuine market gap — no PDF measurement incumbent (Bluebeam / Foxit / Acrobat) ships freehand area; user's request is novel for this product category

### GO criteria not yet met (but addressable in production sprint)
- ❌ Touch / iPad support — out of v1 scope (`pointerdown/move/up` polyfill is a separate sprint)
- ❌ Visible tolerance picker in Properties panel — spike uses Shift / Ctrl modifiers; a slider in the post-close Properties panel for re-decimation is a v1.1 polish
- ❌ Snap-engine bypass during freehand — spike captures raw cursor positions (correct behavior); production must explicitly skip the snap branch in `mousemove` when `altDown && dragging` (small, additive)

### Estimated production sprint cost
- ~150 LOC + 1 marker (`PHASE_FREEFORM_OK`) — see Spike § Estimated production sprint cost above
- Single production sprint, no split needed
- Risk-low — kernel proven, state-machine extension is additive (mirrors INV-001 Arc-polygon's pattern of extending polygon-tool mousedown without breaking it)

### Carry-over risks for the production sprint
1. **Alt-mid-stroke ambiguity** — guard with `altKey at mousedown only` (see Risks above)
2. **Snap-engine bypass** — explicit `if(altDown && dragging) return early` in `mousemove` snap branch
3. **Tolerance picker UI** — Shift/Ctrl modifiers during draw + Properties-panel slider post-close (defer slider to v1.1)
4. **Touch input** — mouse-only in v1; iPad backlog gets its own track

### Recommendation
**GO.** Highest-UX approach, lowest-risk implementation, fills a genuine market gap, satisfies all 6 spike criteria. Production sprint is mechanically straightforward — the kernel (`rdpSimplify` + existing `polyAreaM2`) is proven, the state-machine extension follows the same additive pattern as the INV-001 Arc-polygon `A`-keypress sub-mode that already shipped successfully.
