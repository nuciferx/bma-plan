# RUN_INV_001_ARC_POLYGON — INV-2026-05-15-001: Arc-polygon hybrid measurement

Date: 2026-05-17 (card created)
Branch: main
Status: PASS — completed 2026-05-17 · moved to sprints/completed/2026-05-17-inv-001-arc-polygon/
Commit hash: `<COMMIT_HASH_PENDING>` (user will commit; hash will be backfilled in a separate "docs: backfill INV-001 commit hash" sprint — same pattern as HT-1/-2/-3/-4/-5)

## Goal

Port the arc-polygon hybrid measurement spike (`docs/invent/arc-polygon.md` + `proto/sandbox/invent-arc-polygon.html`) to the live production `proto/ui.html`. Users can draw polygons with inline arc edges using a three-click pattern: draw vertices normally → press `A` → click a through-point → continue drawing next vertex. The arc is measured correctly using the already-shipped `polygonAreaWithArcsM2` function. Zero forbidden-surface edits. Schema fully additive.

Source of truth: `docs/invent/arc-polygon.md` (spike design + algorithm rationale) + `proto/sandbox/invent-arc-polygon.html` (spike implementation).

## Why this sprint exists

INV-2026-05-15-001 was filed as `queued — invent-done-go` in `PHASE_INDEX.md` after the 7-phase invention pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT). Status was `invent-done-go` = the invention loop passed checkpoint; user approved GO. This sprint is the production implementation pass. Inserted ad-hoc per user request 2026-05-17 (between HT-5 and SB-002 in the queue).

## Scope — IN

### New helpers (additive — right after `objectAreaM2` at L1043 in area-math block)

- `_arcCircumcenter(A, P, B)` — circumcircle through 3 points (~5 lines). Returns `{cx, cy, r}` or null if degenerate.
- `_arcPolygonCentroid(pts)` — simple centroid of polygon pts array (~3 lines). Used to determine arc sweep sign.
- `computeArcEdge(A, B, P, polygonCentroid)` — derives `{sweep, center, radius}` from start/end/through-point. Sign of sweep set by which side of chord the through-point lies relative to polygon centroid. Handles degenerate (sag < 0.5 px → sweep=0). (~10 lines).
- `polyMetricsAnyShape(poly, pg)` — wrapper around `polyMetrics` that routes arc-edged polys to `polygonAreaWithArcsM2` + `polySelfIntersects` check. Legacy polys (no `edges` or `edges` not an Array) call `polyMetrics` directly. `polyMetrics` itself unchanged (forbidden surface). (~3 lines).
- `_renderPolyEdges(ctx, poly, cp)` — draws polygon edges into ctx with per-edge branch (line vs arc). Used by both committed polys in `redraw()` AND draft polys during draw. (~15 lines).

### New state

`let mArcDraft = {pending:false, throughPt:null, edges:[]};` at L459. Mirrors `mPts` indexing. Reset on commit/cancel/mode-change.

### Edit sites in `proto/ui.html`

- mousedown handler in `mode==="area"`: 2 new branches — arc-flush (pending + throughPt set) and arc through-point capture (pending + no throughPt). Through-point click uses raw `cToPdf(cx,cy)` — snap bypassed deliberately.
- `finishCurrentArea`: poly literal gets optional `edges:[...]` ONLY when arc edges exist. `mPolys.push(poly)` unchanged. `measure-result` shows "(arc-polygon)" suffix if applicable. Reset `mArcDraft` in both poly and opening branches.
- `redraw()` mPolys.forEach: replaced inline `ctx.beginPath()+lineTo` chain with `_renderPolyEdges(ctx, poly, cp)`. Label calls `polyMetricsAnyShape` (was `polyMetrics`).
- `redraw()` draft block: replaced inline with `_renderPolyEdges` over `{pts:mPts, edges:mArcDraft.edges, closed:false}`. Added through-point red dot + dashed line preview + pending circle around last vertex.
- `setMode`, `clearMeasures`, `drawBarCancel`: reset `mArcDraft` alongside `mPts=[]`.
- `drawBarUndoPt` + Ctrl+Z undo-point: trim `mArcDraft.edges.length` to match `mPts.length-1` and reset pending.
- Esc keydown: special-case `mode==="area" && mArcDraft.pending` → cancel arc-mode only (do not drop vertices); otherwise reset `mArcDraft` alongside `mPts=[]`.
- `A` keydown: when `mode==="area" && mPts.length>=1 && !mArcDraft.pending`, enter arc-mode pending; otherwise behavior unchanged (activates area tool).
- 9 `polyMetrics(poly,pg)` display call sites → `polyMetricsAnyShape(poly,pg)`: L808, L1286 redraw label, L1292 objMetricText, L1320 rp-metric Gross, L1340 buildLeftProperties Gross, L1517 showObjPicker, L1606 buildRows, L1665 collectSummaryData, L1903 updatePageSummary. Opening calls at L1614 and L1738 NOT touched (openings don't get arc edges in v1).

### Schema additive

New optional field `obj.edges[i] = {edgeType:"arc", arcSweep, arcThrough}` in `pageStore` per-page objects. Carried via existing `saveCurrentPage`/`applyLoadedProject` path (`[...mPolys]` + read as-is). Legacy `.bmaplan v1` files without `edges` load unchanged via `Array.isArray(obj.edges)` guard in `polyMetricsAnyShape` / `objectAreaM2` / `_renderPolyEdges`.

### `proto/e2e_ui_test.py`

NEW `_test_arc_polygon(page)` after `_test_path_geometry` (~L1958–2053 region). 7 sub-checks:
- A. `fnsExist` — 7 functions present: `_arcCircumcenter`, `_arcPolygonCentroid`, `computeArcEdge`, `polyMetricsAnyShape`, `_renderPolyEdges`, `arcSegmentAreaM2`, `polygonAreaWithArcsM2`
- B. `closedFormPasses` — canonical square 100×100 + outward semicircle bulge (chord 100, sagitta 50): err = **0.000000%** (< 0.1% budget). computed = expected = 13926.9908 px².
- C. `dispatchOK` — `objectAreaM2(arcPoly) === polygonAreaWithArcsM2(arcPoly)`
- D. `degenerateOK` — through-point on chord midpoint → sweep=0, area = plain polyAreaPx, no NaN
- E. `roundTripOK` — JSON.parse + recompute identical
- F. `legacyUnchanged` — `polyMetrics(legacy) === polyMetricsAnyShape(legacy)` for non-arc poly
- G. `polyMetricsAnyShapeOK` — arc poly routes through arc-aware path

Wired into `main()` between `path_geometry` and `phase_i_a`. Marker `print("ARC_POLYGON_OK", arc_polygon)` between `PATH_GEOMETRY_OK` and `PHASE_I_A_OK`.

## Scope — OUT (not done here)

- Arc through-point snap (perpendicular to chord, nearest-on-arc) — deferred; v1 uses raw coordinate bypass
- Arc edges for opening polygons — deliberately excluded in v1 (scope limit)
- Bezier / cubic curves — separate concern (path geometry model from Phase H.1)
- Circle-only or ellipse measurement — render-only smoothing sprint `RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER`

## Hard Forbidden — untouched

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, scale math, snap engine
- `proto/server.py`
- `.bmaplan` version stays `1` (additive optional fields ONLY — no rename, no removal)
- No FAR/OSR auto-judgment, no pass/fail, no verdict UI

## Mid-sprint correction — infinite recursion trap

**Bug found:** Initial `replace_all polyMetrics(poly,pg) → polyMetricsAnyShape(poly,pg)` was applied broadly. It caught the internal call inside `polyMetricsAnyShape`'s own legacy branch:

```javascript
function polyMetricsAnyShape(poly, pg) {
  if (Array.isArray(poly.edges) && ...) return polygonAreaWithArcsM2(...);
  return polyMetricsAnyShape(poly, pg);  // <-- accidentally replaced from polyMetrics
}
```

This caused: infinite recursion → stack overflow → `updatePageSummary` always crashed → smoke `VECTOR_OK` failed with `'page summary not updated: ยังไม่มีรายการพื้นที่'`.

**Fix:** One targeted Edit restoring the legacy branch to call `polyMetrics(poly, pg)` directly (not `polyMetricsAnyShape`).

**Lesson for future devs:** When doing `replace_all` on a forbidden-surface function name (e.g. `polyMetrics`, `polyAreaM2`, `pdfToC`), always check whether the replacement string appears INSIDE the body of the new wrapper/shim you just wrote. If it does, the `replace_all` will hit the shim body too and create infinite recursion. Prefer a narrowly-scoped multi-Edit over `replace_all` for forbidden-surface names.

Smoke + full passed on second attempt after the fix. Total: 2 test runs, 1 retry.

## E2E Results

| # | Sub-check | Result |
|---|-----------|--------|
| A | fnsExist (7 functions) | PASS |
| B | closedFormPasses (err=0.000000%) | PASS |
| C | dispatchOK | PASS |
| D | degenerateOK (sweep=0, no NaN) | PASS |
| E | roundTripOK | PASS |
| F | legacyUnchanged | PASS |
| G | polyMetricsAnyShapeOK | PASS |

Debug tokens: `{computedPx:'13926.9908', expectedPx:'13926.9908', errPct:'0.000000', sweep:'3.141593', arcAwareM2:17.332388003402624, dispatchedM2:17.332388003402624, degSweep:0}`.

## Test Run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS 29/29 GREEN
python proto/e2e_ui_test.py full                           → PASS 32/32 GREEN
```

All 31 pre-existing markers still GREEN. New marker: `ARC_POLYGON_OK`. Marker count: smoke 28→29, full 31→32.

## Files changed (git diff --stat)

```
NEXT_ACTION.md       |   4 +-
proto/e2e_ui_test.py | 123 ++++++++++++++++++++++++++++++++++++++++
proto/ui.html        |  56 +++++++++++++++--------
3 files changed, 163 insertions(+), 20 deletions(-)
```

## Phase 1 scope check

- ✅ `polyAreaM2` — UNTOUCHED
- ✅ `polyMetrics` — UNTOUCHED; `polyMetricsAnyShape` shim dispatches on `obj.edges` presence
- ✅ `polySelfIntersects` — UNTOUCHED; called by `polyMetricsAnyShape` for arc polys
- ✅ `pdfToC`, `cToPdf`, `RS` — UNTOUCHED
- ✅ `buildSnapIndex` / `snap` — UNTOUCHED; through-point bypass is a call-site choice, engine unmodified
- ✅ `.bmaplan` schema — ADDITIVE; version stays 1
- ✅ `proto/server.py` — UNTOUCHED (pure client feature)
- ✅ Phase 1 boundary — kept (no legal verdict, no OCR, no AI, no FAR/OSR rule)

## References

- `docs/invent/arc-polygon.md` — invention doc (research + 3 approaches + scoring + spike rationale)
- `proto/sandbox/invent-arc-polygon.html` — spike implementation (SPIKE_PASS 8/8, self-contained)
- `docs/status/PHASE_INDEX.md` — INV-2026-05-15-001 row (status `queued — invent-done-go` → `✅ done`)
