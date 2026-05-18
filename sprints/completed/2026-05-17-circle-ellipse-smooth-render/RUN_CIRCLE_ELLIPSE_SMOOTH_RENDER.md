# RUN_CIRCLE_ELLIPSE_SMOOTH_RENDER — Analytic circle/ellipse rendering in redraw()

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `1bf61ca`

## Goal

Replace the 32-gon approximation render path for circle and ellipse shapes with native canvas
analytic calls (`ctx.arc` / `ctx.ellipse`). Storage, hit-test, snap, save-load, and area math
all stay on the legacy `poly.pts` 32-gon — this is a render-only change.

This sprint predates the Autonomous Dev Loop and was the last remaining pre-loop backlog item.
The audit document that recommended this fix is:
`docs/status/PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`.

## Background

Phase H.1 (Path Geometry Implementation, 2026-05-13) shipped `circleToPath` / `ellipseToPath`
generators that create `poly.pts` 32-gon approximations. Area math via `polygonAreaWithArcsM2`
is correct. However visual rendering showed a polygonal "faceted" appearance on circles/ellipses
because `redraw()` drew the pts array as line segments, not as arc primitives.

The audit concluded: math PASS, visual presentation = UI wiring gap. Fix = add analytic branches
at the top of `_renderPolyEdges` (already shipped by INV-001) without touching forbidden surfaces.

## What changed

- `_renderPolyEdges(ctx, poly, cp)` in `proto/ui.html` — added two short-circuit branches
  AT THE TOP, before the existing line/arc-edge flow:

  1. `poly.shape === 'circle' && poly.center && poly.radius`
     → `ctx.arc(cx, cy, r, 0, 2*Math.PI)` — one native arc call, no lineTo
  2. `poly.shape === 'ellipse' && poly.center && poly.semiAxisA && poly.semiAxisB`
     → `ctx.ellipse(cx, cy, a, b, poly.rotation||0, 0, 2*Math.PI)` — one native ellipse call

  The else branch falls through to the existing line / arc-edge flow (unchanged for legacy
  polygons and arc-polygon hybrid objects from INV-001).

- `proto/e2e_ui_test.py` — NEW `_test_circle_render(page)` 7 sub-checks + marker
  `CIRCLE_RENDER_OK`.

## Storage unchanged

- `poly.pts` (32-gon) still stored and round-tripped via `.bmaplan`
- `objectAreaM2` already routed circle/ellipse to `circleAreaM2`/`ellipseAreaM2` closed-form
  helpers (shipped in an earlier sprint) — no change
- `polySelfIntersects`, `buildSnapIndex`, `snap`, hit-test — all still operate on `poly.pts`
- Schema version stays 1

## E2E marker: CIRCLE_RENDER_OK (7 sub-checks)

| Sub-check | What is verified |
|-----------|-----------------|
| `arcFnExists` | `_renderPolyEdges` function exists in `proto/ui.html` |
| `circleUsesArc` | circle poly render path emits `ctx.arc` (no `lineTo` on circle) |
| `ellipseUsesEllipse` | ellipse poly render path emits `ctx.ellipse` (no `lineTo` on ellipse) |
| `legacyStillUsesLineTo` | plain polygon with no `shape` field still uses line segments |
| `areaMathIdentical` | `objectAreaM2` result unchanged for circle/ellipse (closed-form still invoked) |
| `pts32gonPreserved` | `poly.pts` array length = 32 for circle/ellipse (storage untouched) |
| `roundTripOK` | save/load via `.bmaplan` round-trip produces identical `poly.pts` |

Result: CIRCLE_RENDER_OK 7/7 PASS

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `_renderPolyEdges` — 2 analytic short-circuit branches added at top (~12 lines) |
| `proto/e2e_ui_test.py` | NEW `_test_circle_render` + marker `CIRCLE_RENDER_OK` |

## Forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` core endpoints — UNTOUCHED
- `.bmaplan` schema version stays 1 — UNTOUCHED (storage unchanged)
- `RS` constant — UNTOUCHED

## Tests run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS 41/41 GREEN
```

Bundled in commit `1bf61ca` together with `dev-website`. Zero regressions.

## Phase 1 scope check

- All forbidden surfaces — UNTOUCHED
- `.bmaplan` schema — UNTOUCHED (version stays 1, storage unchanged)
- `proto/server.py` — UNTOUCHED
- Phase 1 boundary — kept

## Known gaps / follow-ups

- None. This clears the last pre-loop leftover. Phase H visual audit fully resolved.

## Reference

- Audit doc: `docs/status/PHASE_H_PATH_GEOMETRY_VISUAL_AUDIT.md`
- Phase H.1 sprint: `sprints/completed/2026-05-13-path-geometry/RUN_PATH_GEOMETRY.md`
