---
name: bma-measure-geometry
description: |
  Audit or implement the BMA-Plan path-geometry core, shape generators, and curve/Bezier drawing UI — they all share one path model. Covers flattenPathToPoints, pathAreaM2, renderPath, objectAreaM2 path branch, line/cubic segment model, rectangleToPath, circleToPath, ellipseToPath, arcToCubic, and the pen/curve tool. Never edits polyAreaM2, polyMetrics, pdfToC, cToPdf, RS. Returns MEASURE_GEOMETRY_PASS / MEASURE_GEOMETRY_RISK / MEASURE_GEOMETRY_FAIL.

  Trigger phrases (Thai): "path geometry", "flatten path", "pathArea", "renderPath", "shape generator", "rectangleToPath", "circleToPath", "ellipseToPath", "arcToCubic", "pen tool", "วาดเส้นโค้ง", "Bezier"
  Trigger phrases (English): "path geometry", "shape generator", "curve tool", "Bezier drawing", "flatten path", "cubic segment"

  Do NOT use when: working on measure interaction only — loupe / undo-point / angle-lock (use /bma-measure-ux), or pure area-math contract changes (use /bma-check-forbidden).
---

# /bma-measure-geometry — Path Geometry / Shape / Curve Inspector

Goal: one skill for the whole path model — because `circleToPath` IS a shape generator that IS path geometry, and the curve tool just produces the same line/cubic segments. Splitting them creates artificial sprint boundaries. This skill carries a **sub-area** field so a sprint stays narrow without needing 3 separate skills.

## Sub-areas (declare which in the verdict)

| Sub-area | Surface | Notes |
|---|---|---|
| `core` | `flattenPathToPoints`, `pathAreaM2`, `renderPath`, `objectAreaM2` path branch, line/cubic segment model | The path data contract. Other sub-areas depend on it being PASS. |
| `generator` | `rectangleToPath`, `circleToPath`, `ellipseToPath`, `arcToCubic` | Pure functions: shape params → path segments. Must verify theoretical area. |
| `curve-ui` | pen/curve tool — click=corner, click-drag=Bezier handles, Alt break handle, Shift lock 0/45/90, Enter close, Esc cancel, Ctrl+Z remove last point | **Must not start until `core` is PASS.** Input handling here; the key-event ergonomics overlap `/bma-measure-ux`. |

## Hard boundary — NEVER edit

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — the area-math contract. Path area lives in a SEPARATE function (`pathAreaM2`); add new helpers next to it, never edit the `poly*` family.
- `pdfToC`, `cToPdf`, scale math, `RS` — coordinate conversion. Path geometry stores raw PDF-coordinate segments and re-derives metric values through the *existing* pipeline.
- `buildSnapIndex`, `snap` core.
- `.bmaplan` schema field rename/remove — new path fields must be **additive only**.

If a fix needs any of the above → STOP, emit `FORBIDDEN_ROUTE`, route to `/bma-check-forbidden`.

## Checklist (run in order)

1. **Sub-area declaration** — state `core` / `generator` / `curve-ui`. If a sprint spans 2+, recommend `SPLIT_REQUIRED` unless it is a strict `core → curve-ui` sequencing within one sprint.
2. **Function inventory** — list each touched function, its signature, and its callers. Flag any new function with **zero production callers** (Phase H.1 left several — note them, don't treat as done).
3. **Backward compatibility** — legacy polygon objects (`poly.pts`) must render and measure identically. A path object and its flattened polygon must agree within tolerance.
4. **Theoretical area verification** (`generator` sub-area — mandatory):
   - rectangle area == `width * height`
   - circle area ≈ `π r²` (within flatten tolerance)
   - ellipse area ≈ `π a b` (within flatten tolerance)
   - `arcToCubic` zero-sweep arc → degenerate, no NaN
5. **Closed-path continuity** — first and last anchor coincide for closed paths; no duplicate-point area inflation.
6. **Flatten tolerance** — `flattenPathToPoints` tolerance is bounded; document the value; verify area stable across reasonable tolerance changes.
7. **Render parity** — `renderPath` draws what the math measures (no visual 32-gon while area uses analytic, or vice versa — that mismatch was the Phase H visual-audit finding).
8. **Save round-trip** — path objects serialize and restore with identical geometry.

## Output

```
### Measure Geometry Check: <target>

Verdict: 🟢 MEASURE_GEOMETRY_PASS / 🟡 MEASURE_GEOMETRY_RISK / 🔴 MEASURE_GEOMETRY_FAIL

Sub-area: core / generator / curve-ui

#### Function inventory
| Function | Signature | Production callers | Status |
|---|---|---|---|

#### Backward compatibility
- Legacy poly.pts renders + measures unchanged: ✅/❌
- Path ↔ flattened polygon agree within tolerance: ✅/❌

#### Theoretical area (generator sub-area)
- rectangle = w*h: ✅/❌   circle ≈ πr²: ✅/❌   ellipse ≈ πab: ✅/❌   arc zero-sweep safe: ✅/❌

#### Continuity & tolerance
- Closed-path first==last: ✅/❌   flatten tolerance bounded (value: <n>): ✅/❌
- renderPath ↔ math parity: ✅/❌

#### Forbidden surface
- <none / FORBIDDEN_ROUTE — which>

#### Recommended minimal patches (if RISK/FAIL)
- proto/ui.html L<n>–<m> — <one-line, add-next-to never edit-poly*>
- Test required: py_compile + smoke + full (PATH_GEOMETRY_OK must stay GREEN)

#### Defer to subagent
- bma-path-geometry-reviewer for deep Bezier correctness + area-approximation review
```

## Constraints

- Output ≤35 lines.
- `generator` verdict cannot be PASS without the theoretical-area block all ✅.
- `curve-ui` verdict cannot be PASS unless `core` is already PASS (state it as a precondition, not a silent assumption).
- Never edit the `poly*` family or coordinate conversion — add new functions, route forbidden cases out.
- Never auto-apply — propose only.
