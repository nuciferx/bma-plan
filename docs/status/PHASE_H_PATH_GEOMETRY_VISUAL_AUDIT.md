# PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md

Date: 2026-05-14
Auditor: Claude (BMA-Plan)
Trigger: User report — "circle/curve output looks strange even though PATH_GEOMETRY_OK passes"
Mode: **Audit only. No source change.**

---

## 1. Scope of audit

Only the Phase H.1 unified path geometry surface was inspected:

| # | Function | Location | Status |
|---|----------|----------|--------|
| 1 | `_PATH_FLATTEN_TOL` (const = 0.1) | `proto/ui.html:957` | inspected |
| 2 | `_flattenCubicSeg` (De Casteljau) | `proto/ui.html:958` | inspected |
| 3 | `flattenPathToPoints` | `proto/ui.html:959` | inspected |
| 4 | `pathAreaM2` | `proto/ui.html:960` | inspected |
| 5 | `rectangleToPath` | `proto/ui.html:961` | inspected |
| 6 | `circleToPath` | `proto/ui.html:962` | inspected |
| 7 | `ellipseToPath` | `proto/ui.html:963` | inspected |
| 8 | `arcToCubic` | `proto/ui.html:964` | inspected |
| 9 | `renderPath` | `proto/ui.html:965` | inspected |
| 10 | `objectAreaM2` (path branch) | `proto/ui.html:966` | inspected |
| 11 | `applyLoadedProject` (path hydration) | `proto/ui.html:1616` | inspected |
| 12 | `redraw()` (canvas loop) | `proto/ui.html:1209` | inspected |
| 13 | `mode==='circle'` mousedown handler | `proto/ui.html:1327` | inspected |
| 14 | `mode==='ellipse'` mousedown handler | `proto/ui.html:1327` | inspected |
| 15 | `_circlePolygonPts` (legacy 32-gon) | `proto/ui.html:1377` | inspected |
| 16 | `_ellipsePolygonPts` (legacy 32-gon) | `proto/ui.html:1378` | inspected |
| 17 | `_test_path_geometry` (PATH_GEOMETRY_OK) | `proto/e2e_ui_test.py:1930-2025` | inspected |
| 18 | `circle_tool` / `ellipse_tool` E2E | `proto/e2e_ui_test.py:1813,1846` | inspected |

No forbidden surfaces touched (no edits made). `polyAreaM2`, `pdfToC`, `cToPdf`, `RS`, snap core, save/load schema, server.py — read only.

---

## 2. Per-checklist findings

### 2.1 `circleToPath`

- **Cubic segment count:** 4 quadrants. Each quadrant 90° → one cubic Bézier. Correct.
- **Control point constant:** `k = 0.5522847498`. This is the canonical optimal 4-cubic circle approximation (max radial error ≈ 0.027%). Correct.
- **Closed path continuity:** Q1 end `(cx, cy+r)` = Q2 start. Q4 end `(cx+r, cy)` = Q1 start → topologically closed.
- **Direction:** counterclockwise in PDF coordinate system (y-axis points down in PDF, so visually it is clockwise on screen — irrelevant to area magnitude).
- **Radius interpretation:** PDF units (pt). Matches `polyAreaM2`/`pdfToC` convention. Correct.
- **Verdict:** GEOMETRY CORRECT.

### 2.2 `ellipseToPath`

- **Semi-axes:** `a` = x-axis radius, `b` = y-axis radius. Rotation applied via `rot()` closure around center. Correct.
- **Control handles after rotation:** rotation applied per-handle uniformly. Mathematically valid.
- **Closed path continuity:** 4 segments stitched analogously to circle. Correct.
- **Verdict:** GEOMETRY CORRECT.

### 2.3 `arcToCubic`

- **Degenerate handling:** chord < 1e-9 or `sinHalf` < 1e-9 → returns straight `line` segment. Correct.
- **Center reconstruction:** from chord midpoint + perpendicular offset `r·cos(|sweep|/2)`. Correct standard formula.
- **Sweep sign:** `sweepSign = sweepRad >= 0 ? 1 : -1` propagated into tangent direction. Correct.
- **Control handle length:** `(4/3) · tan(|sweep|/4) · r` — canonical formula for cubic Bézier approximation of a circular arc up to 90°. Correct.
- **Large-arc handling:** not split. If `|sweep| > π/2` the standard approximation error grows (formula degrades; >120° is visibly off). However, `arcToCubic` is **not called by any production code path** in the current repo (see §3), so this risk is theoretical for now.
- **Verdict:** GEOMETRY CORRECT for sweeps ≤ 90°; degrades for wide arcs but UNUSED in current code.

### 2.4 `flattenPathToPoints` / `_flattenCubicSeg`

- **Tolerance:** `_PATH_FLATTEN_TOL = 0.1` pt. For a circle r=100: max chord deviation ≈ 39 pt → subdivides ~9 levels deep → ~2k points per circle. Within 10000-point cap.
- **Endpoints:** segment 0 pushes `p0` explicitly; subsequent segments push only their `p1`. No accidental duplicate vertex.
- **Closed path tail:** for `circleToPath`, Q4.p1 == Q1.p0 → last flattened point equals first. Polygon shoelace tolerates a duplicate seam vertex (adds zero area). Acceptable.
- **De Casteljau:** depth limit 20, output cap 10000, flatness test via perpendicular distance of both control points to chord. Standard, correct.
- **Verdict:** FLATTEN CORRECT.

### 2.5 `renderPath`

- **Coordinate basis:** converts every `p0/c1/c2/p1` via `pdfToC()` before issuing canvas commands. No double-scaling. No missing `closePath()` (gated on `path.closed`).
- **`moveTo` only on segment 0:** correct for continuous path; subsequent segments use the previous segment's endpoint implicitly.
- **Verdict:** RENDER FUNCTION CORRECT.
- **BUT:** see §3 — **`renderPath` is never called by `redraw()` or any other production code.**

### 2.6 `pathAreaM2`

- **Rectangle path:** identical to polygon area within 1e-9 (E2E Test A passes).
- **Circle approximation:** within 0.1% of πr² (E2E Test B passes — actual error well under threshold thanks to N≈2000 flattened points at tol=0.1).
- **Ellipse path:** not asserted by E2E but by construction analogous to circle (4 cubics, same flatten path).
- **Mixed line + cubic:** deterministic and translation-invariant within 1e-9 (E2E Test C passes).
- **Legacy polygon path:** unchanged — `objectAreaM2` dispatch order preserves `polyAreaM2(obj.pts)` when no `geometryType` (E2E Test D passes within 1e-12).
- **Verdict:** AREA MATH CORRECT.

### 2.7 UI status (THE PROBLEM)

This is where the audit found the actual cause.

**`proto/ui.html:1327` (mousedown handler):**

```js
} else if (mode === "circle") {
  ...
  mPts = _circlePolygonPts(center, radius, 32);   // ← LEGACY 32-gon
  finishCurrentArea();
  ...
  if (newObj) {
    newObj.shape = "circle";          // ← legacy shape flag
    newObj.center = {...};
    newObj.radius = radius;
    // NOTE: NO geometryType='path' assignment.
    // NOTE: NO segments[] from circleToPath().
  }
} else if (mode === "ellipse") {
  ...
  mPts = _ellipsePolygonPts({x:cx,y:cy}, semiA, semiB, 32);   // ← LEGACY 32-gon
  ...
  newObj.shape = "ellipse";
  newObj.semiAxisA = semiA;
  newObj.semiAxisB = semiB;
  // No segments[]. No geometryType='path'.
}
```

**`proto/ui.html:1209` `redraw()`:**

```js
mPolys.forEach((poly, pi) => {
  if (poly.pts.length < 2) return;
  ...
  const cp = poly.pts.map(p => pdfToC(p.x, p.y));   // ← always pts
  ctx.beginPath();
  ctx.moveTo(cp[0].x, cp[0].y);
  cp.slice(1).forEach(p => ctx.lineTo(p.x, p.y));    // ← always lineTo
  if (poly.closed) ctx.closePath();
  ...
});
```

No branch on `poly.geometryType`. No call to `renderPath`. No branch on `poly.shape === 'circle'` or `'ellipse'` to draw a smooth arc.

**Result on screen:** a user-drawn circle / ellipse renders as a **32-vertex polygon**. At moderate zoom it looks reasonable; at high zoom (or for small radii) the polygonal corners are clearly visible — "looks strange".

**Area shown is still correct** because `objectAreaM2` dispatches on `shape==='circle'` to the analytic `circleAreaM2(radius)` (and analogously for ellipse). So the user sees:
- A polygonal outline (visibly 32-gon at zoom),
- An accurate area label (πr² analytic),
- An apparent mismatch between what they see drawn and what the number says — hence "looks strange even though math is fine".

---

## 3. Production wiring map of Phase H.1 surfaces

| Phase H.1 function | Called from production code? | Called from E2E only? |
|--------------------|------------------------------|-----------------------|
| `_flattenCubicSeg` | yes (via `flattenPathToPoints`) | — |
| `flattenPathToPoints` | `pathAreaM2` (l.960), `applyLoadedProject` (l.1616, tol=1.0) | yes |
| `pathAreaM2` | `objectAreaM2` (l.966) | yes |
| `rectangleToPath` | **no production caller** | yes (`_test_path_geometry`) |
| `circleToPath` | **no production caller** | yes (`_test_path_geometry`) |
| `ellipseToPath` | **no production caller** | yes (`_test_path_geometry`) |
| `arcToCubic` | **no production caller** | yes (`_test_path_geometry` via `fnsExist`) |
| `renderPath` | **no production caller** | yes (`fnsExist` check only) |

**Conclusion:** Phase H.1 added a complete and correct *data + math + render API* for the new unified path geometry, but **none of the user-facing measurement tools have been migrated to it.** The circle/ellipse tools still build legacy 32-gon polygons with `shape="circle"/"ellipse"` and the canvas loop still draws them as straight-edged polygons.

`applyLoadedProject` at line 1616 *does* hydrate `pts` from `segments` for any saved object with `geometryType==='path'` — but since no tool currently produces such objects, this branch is dormant.

---

## 4. Why PATH_GEOMETRY_OK passes

`_test_path_geometry` (`proto/e2e_ui_test.py:1930-2025`) calls every Phase H.1 function **directly via `page.evaluate()`** with hard-coded JS literals:

```js
const pathRect = rectangleToPath({x:100,y:100}, {x:200,y:180});
const pathA    = pathAreaM2(pathRect);
const pathCirc = circleToPath({x:200,y:200}, 100);
const numeric  = pathAreaM2(pathCirc);
```

It validates that the math returns correct numbers and that the seven function names exist on `window`. **It never invokes a UI tool**, never opens the Circle/Ellipse tool from the toolbar, never inspects the rendered canvas pixels.

The companion `circle_tool` test (`e2e_ui_test.py:1846`) does activate `activateCircleTool('room')` — but immediately overrides:

```js
mPts = _circlePolygonPts(center, radius, 32);   // exactly mirrors the legacy mousedown
```

…confirming that the test, like the production code, **exercises the legacy 32-gon path** and never calls `circleToPath` through the user tool. So both tests pass simultaneously while the visual problem persists.

---

## 5. Suspected cause — classification

| Category | Verdict |
|----------|---------|
| Geometry math (generators, area, flatten) | **CORRECT** — no defect |
| Render function (`renderPath` itself) | **CORRECT** — no defect, but unused |
| Flatten tolerance / De Casteljau | **CORRECT** — no defect |
| User-tool / render integration | **GAP** — circle and ellipse tools still produce legacy 32-gon polygons; `redraw()` draws them as polygons |

**Root cause:** UI / integration gap. Phase H.1 delivered foundation only. The actual user-visible "strange-looking circle/curve" is the long-standing 32-vertex polygon rendering that Phase H.1 has not yet replaced.

This is **not a regression introduced by Phase H.1**. Phase H.1's sprint card explicitly scoped itself to the unified data model + math + render-function API. Wiring the legacy circle/ellipse tools to the new model was deferred.

---

## 6. Minimal safe fix recommendation

**Option A — Render-only smoothing (RECOMMENDED, lowest risk):**

In `redraw()` at `proto/ui.html:1209`, inside `mPolys.forEach`, before the existing polygon line-loop, branch on `poly.shape`:

- `poly.shape === 'circle'` (with `poly.center` + `poly.radius`): draw an analytic arc via `ctx.arc()` in canvas space (using `pdfToC` on the center and the appropriate canvas-radius derivation via the existing zoom transform).
- `poly.shape === 'ellipse'` (with `poly.center` + `poly.semiAxisA` + `poly.semiAxisB` + `poly.rotation`): draw via `ctx.ellipse()`.
- Otherwise: fall through to the existing polygon line loop.

Hit-testing, snap, drag-vertex, save/load all continue to use `poly.pts` (the legacy 32-gon) — **no data-model change, no schema change, no forbidden-surface change.**

The visible outline becomes smooth; the stored geometry stays compatible with existing saves. Area is unaffected (still analytic via `objectAreaM2`).

Risk: small. Touches only the `mPolys` rendering block in `redraw()`. Does not touch `polyAreaM2`, `polyMetrics`, `pdfToC`, `cToPdf`, `RS`, snap, save/load schema, or server.py.

**Option B — Wire UI tools to Phase H.1 (correct long-term direction, larger sprint):**

Modify `mode==='circle'` and `mode==='ellipse'` mousedown branches to emit `geometryType:'path'` objects via `circleToPath` / `ellipseToPath`. Modify `redraw()` to dispatch `renderPath(ctx, poly)` when `poly.geometryType==='path'`. Bridge `pts` from `flattenPathToPoints(poly, tol)` for hit-test compatibility.

This is the eventual destination but expands blast radius into: hit-test (`hitTestAll`, `hitVertex`), drag-vertex (origData paths), snap index (vertex coords), save/load (already partly handled at l.1616), opening-parent logic, and any code that reads `obj.pts`. Out of scope for a minimal visual fix.

**Option C — Do nothing:**

The visual ugliness is not new; it predates Phase H.1. Phase H.1 is correctly DONE on its own scoped terms. If polishing circle/ellipse rendering is not a priority, the audit can be filed without a follow-up sprint.

---

## 7. Sprint split recommendation

**YES — split into a separate sprint.** Recommended sprint card name:

`sprints/active/RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER.md`

One problem (visible polygonal corners on circle/ellipse), one fix (Option A render-only branch in `redraw()`), one file touched (`proto/ui.html`), no forbidden surface touched, full E2E required because rendering tests + `circle_tool` / `ellipse_tool` markers must continue to pass.

Phase H.1 itself should **remain marked PASS** — its scope (model + math + render API) is correctly delivered. The audit confirms PATH_GEOMETRY_OK is a valid pass; it just does not cover the legacy circle/ellipse user tools because those tools were not yet migrated.

---

## 8. Tests run for this audit

This audit is **docs-only**. No source files were modified.

- `py_compile proto/server.py proto/e2e_ui_test.py` — run as sanity (see `TEST_RESULT.md`).
- `smoke` / `full` E2E — **not re-run**. Rationale: no source changed; the most recent `full` PASS is from commit `e92db93` (Phase H.1) per `LATEST_STATUS.md`. AGENTS.md §1 explicitly allows no-test rationale for docs-only sprints.

If Option A or Option B is later implemented as a separate sprint, that sprint must:
- Run `py_compile + smoke + full` (rendering changes are a forbidden-trigger surface for `full`)
- Add a marker (e.g. `CIRCLE_RENDER_OK`) that actually inspects the drawn pixels or the draw-call sequence, so a future regression is caught
- Use `/bma-sprint-finalize` at the end

---

## 9. Summary (one paragraph)

Phase H.1 unified path geometry math is **fully correct** — `circleToPath`, `ellipseToPath`, `arcToCubic`, `_flattenCubicSeg`, `flattenPathToPoints`, `pathAreaM2`, and `renderPath` all check out and PATH_GEOMETRY_OK validly tests their math via direct JS evaluation. However the circle and ellipse user tools (`mode==='circle'` / `mode==='ellipse'`) still build legacy 32-vertex polygons via `_circlePolygonPts` / `_ellipsePolygonPts`, the canvas `redraw()` loop still draws polygons line-by-line, and `renderPath` is never called from production. The "strange-looking circle/curve" is therefore not a geometry bug — it is a **UI/render integration gap**: the new path API exists but is not wired into the legacy circle/ellipse tools. Recommended minimal fix is a render-only smoothing branch in `redraw()` keyed on `poly.shape`, deferred to a separate sprint `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER`.
