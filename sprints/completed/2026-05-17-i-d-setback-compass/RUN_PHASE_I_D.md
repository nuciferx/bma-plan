# RUN_PHASE_I_D — Phase I-D: 4-direction setback + compass overlay

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `dc96f62`

## Goal

Extend setback measurement from front-only (U2) to all 4 directions (front / back / side1 / side2)
by using land-edge roles on site boundary polygons. Add a `#canvas-compass` SVG overlay (top-right
of workspace) that displays a north-pointing arrow rotated to the per-page north angle, giving users
directional context while measuring.

Source: PHASE_INDEX.md row `I-D` (depends on I-C ✅).

## Scope — IN

- **4-direction setback:** `collectSetbackReport(pageObjs, pg)` extended to compute back / side1 /
  side2 min-distances in addition to front, using `landEdgeRole` attribute on site boundary edges.
- `landEdgeRole` additive field on polygon edges (`front` / `back` / `side1` / `side2` / `null`).
  Stored in `pageStore` per-object edge array (additive, legacy files load unchanged).
- `computeEdgeSetback(poly, roleFilter, refObjects, pg)` — returns min distance from edges with
  matching `landEdgeRole` to the nearest building-coverage polygon edge.
- Siteplan tab in Summary Widget updated to show all 4 setback rows.
- **Compass overlay:** `#canvas-compass` SVG element (top-right, workspace-relative, 48×48 px).
  SVG arrow `transform="rotate(northAngle)"` driven by per-page `northAngle` field in `pageTags`.
  `northAngle` editable via Page Setup (0 = north = up; 90 = north = right).
  Visibility: always shown on site pages; hidden on other page types.
- New E2E marker `PHASE_I_D_OK` with 10 sub-checks.

## Scope — OUT

- 45° angle lock (Phase H.0) — still deferred; compass is display-only.
- Auto-detect north from PDF metadata — not in scope (user sets north angle manually).
- Setback comparison against user-defined limits — deferred to a future display-only sprint.

## Implementation summary

### Functions added (`proto/ui.html`)

- `computeEdgeSetback(poly, role, refPolys, pg)` — filters edges by `landEdgeRole`; computes
  min vertex-to-edge distance to nearest building polygon (same algorithm as `collectRefDistanceReport`
  for front, generalized). Pure function, no side effects.
- `collectSetbackReport(pageObjs, pg)` — returns `{front, back, side1, side2}` all in metres.
  Replaces the U2 front-only calculation at the `collectSummaryData` call site.
- `updateCompass(northAngle)` — updates `#canvas-compass` SVG rotate transform.
- `northAngle` field added to `pageTags[pageIdx]` object (additive, default `0`).
- Page Setup form: `northAngle` input (0–359°, step 1).
- `updateSiteRibbon()` — calls `updateCompass()` on site-page activation.

### Key design decisions

- `landEdgeRole` on polygon edges (not on the polygon itself) because a single site boundary
  polygon may have different directional roles on different sides.
- Compass is a pure display overlay; it has no effect on measurement math.
- `northAngle` stored in `pageTags` (already per-page JSON) — schema additive, version stays 1.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `computeEdgeSetback`; `collectSetbackReport` extended; `#canvas-compass` SVG; `updateCompass`; `northAngle` in pageTags; Page Setup input |
| `proto/e2e_ui_test.py` | NEW `_test_phase_i_d(page)` 10 sub-checks + marker `PHASE_I_D_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS GREEN
```

PHASE_I_D_OK: 10 sub-checks all PASS.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED (setback uses same distance formula as U2)
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED
- `.bmaplan` schema — ADDITIVE (`northAngle` in pageTags + `landEdgeRole` on edges; version stays 1)
- Phase 1 boundary — kept (setback displayed as facts; no verdict/pass-fail; no Rule Engine)

## References

- PHASE_INDEX.md row `I-D`
- U2 sprint — `collectRefDistanceReport` front-setback (generalized here to 4 directions)
- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` — setback definitions (กฎกระทรวง 55)
