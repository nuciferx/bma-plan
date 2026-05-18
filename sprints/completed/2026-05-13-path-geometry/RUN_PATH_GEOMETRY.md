# RUN_PATH_GEOMETRY — Phase H.1 Path Geometry Implementation

Date: 2026-05-13
Branch: main
Status: PASS

## Goal

Replace Phase H.1's split shape system with a unified Illustrator-style path model (line + cubic Bézier segments). Generators (rectangleToPath, circleToPath, ellipseToPath, arcToCubic) produce paths; area math reduces to `pathAreaM2 = polyAreaM2(flattenPathToPoints(path))`. Additive only — no existing objects changed.

## Implementation

All changes in `proto/ui.html` (additive, near line 956):

| Symbol | Type | Contract |
|--------|------|---------|
| `_PATH_FLATTEN_TOL` | const | 0.1pt — forces level 5 subdivision for r≥10pt |
| `_flattenCubicSeg(p0,c1,c2,p1,tol,out,depth)` | fn | De Casteljau adaptive; d1+d2≤tol, depth≤20, 10000-pt cap |
| `flattenPathToPoints(path,tol)` | fn | Returns `[{x,y},...]` in PDF coords |
| `pathAreaM2(path,pg)` | fn | `polyAreaM2(flattenPathToPoints(path))` |
| `rectangleToPath(p0,p1)` | fn | 4 line segments |
| `circleToPath(center,radius)` | fn | 4 cubics, k=0.5522847498 |
| `ellipseToPath(center,a,b,rotation)` | fn | 4 cubics with rotation matrix |
| `arcToCubic(p0,p1,sweepRad)` | fn | Chord→center→(4/3)tan(|sweep|/4)×r |
| `renderPath(ctx,path)` | fn | beginPath/moveTo/lineTo/bezierCurveTo via pdfToC |

Modified:
- `objectAreaM2`: `geometryType==='path'` first branch
- `applyLoadedProject`: regenerate cached `pts` for path objects

Also fixed missing `proto/export/` package (lost in submodule absorption) and regenerated `proto/test_plan_A1.pdf`.

## Tolerance Tuning

`_PATH_FLATTEN_TOL` history: 0.5 → 0.25 → 0.1

Root cause why 0.5 and 0.25 both failed test B:
- r=100pt circle: d_0≈39, d_1≈10.1, d_2≈2.5, d_3≈0.63, d_4≈0.158
- 0.63 > 0.5 > 0.25 > 0.158 → both stop at level 4 → identical results
- 0.158 > 0.1 → 0.1 forces level 5 (d_5≈0.039 < 0.1) → error 0.012% < 0.1% threshold ✓

## E2E Acceptance Tests

| Test | Description | Result |
|------|-------------|--------|
| A | rectangleToPath area == polyAreaM2(corners) ±1e-9 | PASS |
| B | circleToPath area error < 0.1% vs exact π×r² | PASS (0.012%) |
| C | Mixed path (3 line + 1 cubic): deterministic + translation-invariant ±1e-9 | PASS |
| D | Legacy polygon (no geometryType) routes through polyAreaM2 unchanged | PASS |
| E | JSON round-trip preserves segments + generator identically | PASS |
| fnsExist | All 7 functions present on window | PASS |

## Test Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → PASS (16 markers)
python3.11 proto/e2e_ui_test.py full                           → PASS (19 markers)
```

## Hard Forbidden Surfaces — All Preserved

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — unchanged
- `pdfToC`, `cToPdf`, `RS`, scale math, snap engine — unchanged
- `proto/server.py` — unchanged
- `.bmaplan` schema version stays 1

## Out of Scope (Deferred)

- Pen tool / freeform drawing UI
- Vertex handle drag
- Convert-to-path command
- Curve rendering style (dash, stroke width per segment)
- Hit-test for curved edges
