# RUN_PHASE_I_E — Phase I-E: Building-to-building distance + wallEdges schema

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `504b993`

## Goal

Measure building-to-building distance (มร.55 ข้อ 48: ระยะห่างระหว่างอาคาร ≥ 2h pre-check) using a
vertex-to-edge metric between all building-coverage polygon pairs on a page. Introduces `wallEdges`
additive schema (`WALL_EDGE_TYPES` catalog) so users can classify wall edges before or after drawing.
Results displayed in the "ผังบริเวณ" siteplan tab under "ระยะระหว่างอาคาร (2h pre-check)". Save/load
round-trip safe.

Source: PHASE_INDEX.md row `I-E` (depends on I-D ✅). Decision Q4 (2h rule) = deferred from I-A;
this sprint implements the measurement fact collection only (no pass/fail verdict).

## Scope — IN

- `WALL_EDGE_TYPES` catalog: 4 types — `exterior_wall`, `party_wall`, `fire_wall`, `glass_wall`.
  Each type has a Thai label. Stored as `wallEdgeType` on polygon edge objects (additive).
- `computeBuildingPairsForPage(pageObjs, pg)` — returns array of `{idA, idB, distM}` for all
  unique pairs of `building_coverage` polygons on the page. Distance = min vertex-to-edge over
  all cross-pairs (additive computation, no in-place mutation of polygon data).
- `computeAllBuildingPairs(allPageObjs, pg)` — aggregates across all pages for the summary view.
- Siteplan tab: new "ระยะระหว่างอาคาร (2h pre-check)" section listing pair distances. Each row:
  `อาคาร A — อาคาร B: X.XX ม.` (plain fact; no "PASS/FAIL" column — Phase 1 boundary).
- `wallEdgeType` additive field on polygon edges; carried through existing `pageStore` save/load path.
  Legacy files without `wallEdgeType` load unchanged (field defaults to `null`).
- New E2E marker `PHASE_I_E_OK` with 9 sub-checks.

## Scope — OUT

- Automatic 2h threshold comparison UI — deferred (Phase 1: facts only).
- Wall-edge-type editing UI in Properties panel — deferred to a future sprint.
- Cross-page building distance — `computeAllBuildingPairs` computes it but the tab v1 shows
  per-page only.

## Implementation summary

### Functions added (`proto/ui.html`)

- `WALL_EDGE_TYPES` const object (4 entries with Thai labels).
- `computeBuildingPairsForPage(pageObjs, pg)` — pure function; iterates all
  `building_coverage` poly pairs; calls existing vertex-to-edge distance helper (same geometry
  used for setback in I-D); returns `[{nameA, nameB, distM}]` sorted ascending by `distM`.
- `computeAllBuildingPairs(allPageObjs, pg)` — wraps per-page function across `pageStore`.
- `updateSiteplanTab()` (I-C) — extended: renders building-distance section when pairs exist.
- `wallEdgeType` written to edge objects on creation (default `null`); round-trip via `pageStore`.

### Key design decisions

- Vertex-to-edge metric (minimum over all vertex-to-opposite-edge distances) is the same geometry
  used for I-D setback — code reuse, no new distance algorithm introduced.
- "2h pre-check" label in the tab is informational, not a verdict UI. The `h` value is not computed
  (building height exists in `buildingHeight_m` but comparison is deferred).
- `wallEdgeType` is per-edge (not per-polygon) to support mixed-wall buildings (e.g. party wall on
  one side, exterior on another). Same model as `landEdgeRole` from I-D.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `WALL_EDGE_TYPES` catalog; `computeBuildingPairsForPage`; `computeAllBuildingPairs`; siteplan tab extended; `wallEdgeType` on edge objects |
| `proto/e2e_ui_test.py` | NEW `_test_phase_i_e(page)` 9 sub-checks + marker `PHASE_I_E_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS GREEN
```

PHASE_I_E_OK: 9 sub-checks all PASS.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED (distance uses same formula as I-D setback)
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED
- `.bmaplan` schema — ADDITIVE (`wallEdgeType` on edges; `WALL_EDGE_TYPES` catalog client-only;
  version stays 1; backward compat via `null` default)
- Phase 1 boundary — kept (no 2h verdict, no pass/fail column, facts only)

## References

- PHASE_INDEX.md row `I-E`
- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` — มร.55 ข้อ 48 building distance requirement
- I-D sprint — vertex-to-edge distance geometry reused
