# PHASE_H_PATH_GEOMETRY_DECISION.md — Phase H.1 Revision Decision

> Date: 2026-05-13
> Sprint: Phase H.1 Revision — Unified Path Geometry (design only)
> Status: **DESIGN APPROVED PENDING USER REVIEW.** No source code, no UI, no tests changed.
> Output: `docs/design/PATH_GEOMETRY_MODEL.md` (this doc's companion)
> Aligns with: AGENTS.md §6 Sprint 5 — Curved Path

---

## 1. Context

Phase H.1 (Curves & Circle/Ellipse/Arc/Rect) was merged in commit `10588ef` (root) /
`2962fba` (proto, pre-absorption). It shipped four parallel area helpers in
`proto/ui.html` lines 952–956:

| Function | Used when |
|---|---|
| `circleAreaM2(radiusPt, pg)` | `obj.shape === "circle"` |
| `ellipseAreaM2(aPt, bPt, pg)` | `obj.shape === "ellipse"` |
| `arcSegmentAreaM2(chordPt, sweepRad, pg)` | per arc-edge correction |
| `polygonAreaWithArcsM2(poly, pg)` | any `edges[i].edgeType === "arc"` |

Dispatched by `objectAreaM2(obj, pg)`.

This implementation is functional. All existing E2E markers (`VECTOR_OK`,
`XLSX_OK`, `PERSIST_OK`, `REAL_OK`, plus the H.1-era new markers) PASS.

---

## 2. Problem Identified

User requirement (2026-05-13):
> "We need to support area measurement for arbitrary curved boundaries,
> including shapes where one side is a curve and other sides are normal
> polygon lines."

The current split prevents this cleanly:

1. **Mixed shapes are awkward.** A boundary with one curved side and three
   straight sides — common for site plans (curved frontage along a road)
   and floor plans (rounded corners) — needs `polygonAreaWithArcsM2`, which
   only supports per-edge **circular** arcs and re-uses `polyAreaM2` plus a
   circular-segment correction. There is no single representation that
   handles both rectangles and curved shapes uniformly.

2. **No shared render / hit-test surface.** Each `shape` value (`"polygon"`,
   `"circle"`, `"ellipse"`) needs its own render branch and its own
   hit-test branch. Adding rounded rectangle, freeform Bézier, or non-
   circular arcs means another branch each time.

3. **Off-backlog alignment.** AGENTS.md §6 lists **Sprint 5 — Curved Path**:
   > [ ] Path data model (line + arc_3pt)
   > [ ] Flatten arc → polyline → คำนวณพื้นที่
   > [ ] Export ระบุ area_method = flattened_arc
   
   The split shape system does not match this backlog item. The pivot
   brings Phase H.1 in line with the original Sprint 5 plan.

---

## 3. Decision

Adopt an Illustrator-style closed path model:

```
Path = ordered list of segments, each "line" or "cubic" Bézier
```

- Circles, ellipses, arcs, rectangles become **generator functions** that
  produce paths (`rectangleToPath`, `circleToPath`, `ellipseToPath`,
  `arcToCubic`).
- All area math reduces to: `pathAreaM2(path, pg) = polyAreaM2(flattenPathToPoints(path, tol), pg)`.
- `polyAreaM2` is unchanged.

Full specification: `docs/design/PATH_GEOMETRY_MODEL.md`.

---

## 4. Hard Constraints (must hold throughout implementation)

From AGENTS.md §3, CLAUDE.md "Forbidden surfaces", and user instruction:

- ❌ Do **not** modify `polyAreaM2`, `polyMetrics`, `polySelfIntersects`.
- ❌ Do **not** modify `pdfToC`, `cToPdf`, `RS`, scale math, snap engine.
- ❌ Do **not** modify `proto/server.py`.
- ❌ Do **not** change `.bmaplan` save format version (stays at 1; additive only).
- ❌ Do **not** break existing polygon / circle / ellipse / arc-edge objects.
- ❌ Do **not** break save / load / export.
- ❌ Do **not** implement UI in this sprint (Pen tool, vertex-handle edit,
  "convert to path" command are all out of scope).
- ❌ Do **not** add legal / OCR / AI / FAR / OSR / rule-engine logic.
- ❌ Do **not** calculate from `layer.name` / `layer.slug`.

Existing helpers (`circleAreaM2`, `ellipseAreaM2`, `arcSegmentAreaM2`,
`polygonAreaWithArcsM2`) **stay** as backward-compat readers. They are
not removed.

---

## 5. Position in Project Plan

```
Phase G        ✅ DONE — Menu Wiring + Layer Power-up (merged main d3e6f14)
Phase H.0      ⏸ PLANNED — 45° Angle Lock
Phase H.1      ✅ DONE — Curves & Circle/Ellipse/Arc/Rect (split system)
                       ↓
               🔄 REVISION = THIS SPRINT (design only)
                       ↓
Sprint 5       ⏭ NEXT — Implementation of unified path geometry
                       (Curved Path per AGENTS.md §6)
Phase H.2      ✅ DONE — Annotate Menu
Phase H.3      ⏸ DEFERRED — File/Edit/View/... menu dropdowns
Phase I        📝 ANALYSIS — Measurement by Section
```

The path model unblocks:
- Curved site boundaries (e.g. road frontage)
- Rounded corner floor plans
- Future Pen tool (freeform Bézier)
- Phase I roof-terrace curved boundaries
- Sprint 5 backlog completion (`area_method = flattened_arc`)

---

## 6. Out of Scope (this sprint)

- Implementation code in `proto/ui.html`
- UI tools (Pen, vertex-handle edit, "convert to path")
- Hit-testing on cubic segments (load step caches `pts` for legacy hit-test)
- Migration of existing legacy objects to path form
- `area_method` XLSX/CSV column (separate sprint)
- Phase H.0 (45° lock) — independent, not affected

---

## 7. Verification (docs-only sprint)

| Item | Result |
|---|---|
| Source code change | None |
| `proto/server.py` touched | No |
| `proto/ui.html` touched | No |
| `proto/e2e_ui_test.py` touched | No |
| `.bmaplan` schema | Unchanged (additive plan only) |
| `py_compile` | Not required (no Python change) |
| `smoke` test | Not required (no source change) |
| `full` test | Not required (no source change) |
| Phase 1 scope check | ✅ No legal / AI / OCR / Rule Engine introduced |
| Backward compat plan | ✅ Documented in PATH_GEOMETRY_MODEL.md §6 |
| Hard forbidden plan | ✅ Documented in PATH_GEOMETRY_MODEL.md §12 |

No-test rationale: This is a documentation-only sprint. The two new files
under `docs/` introduce no runtime change. The existing test baseline
(2026-05-11 — `MENU_OK` + all H.1/H.2 markers) is the reference for the
**next** sprint (implementation).

---

## 8. Files Created

| File | Purpose |
|---|---|
| `docs/design/PATH_GEOMETRY_MODEL.md` | Full design specification |
| `docs/status/PHASE_H_PATH_GEOMETRY_DECISION.md` | This decision record |

## Files Modified

| File | Reason |
|---|---|
| `log.md` | Session entry per AGENTS.md §3.2 |
| `PATCH_SUMMARY.md` | Docs-only sprint entry |
| `TEST_RESULT.md` | No-test rationale entry |
| `FINAL_REPORT_FOR_CHATGPT.md` | Sprint outcome |

---

## 9. Next Step

Wait for user approval of `PATH_GEOMETRY_MODEL.md`. After approval, schedule
the implementation sprint following AGENTS.md GTM Infinite Loop. Implementation
sprint will:

1. Add `flattenPathToPoints`, `pathAreaM2`, `renderPath`, and the four
   generators next to existing `polyAreaM2`.
2. Add `geometryType === "path"` branch as the first case in `objectAreaM2`.
3. Add path-aware branch to `applyLoadedProject` per-object normalization.
4. Add E2E acceptance tests A–E from `PATH_GEOMETRY_MODEL.md §10`.
5. Run `py_compile + smoke + full`. All existing markers must remain PASS;
   add new marker `PATH_GEOMETRY_OK` for the new assertions.
6. UI tooling for creating paths remains a **separate** later sprint.

---

## 10. Stop Conditions (if implementation sprint hits any of these → halt)

- Any existing E2E marker regresses (VECTOR_OK, XLSX_OK, PERSIST_OK, REAL_OK, etc.)
- `polyAreaM2` returns different value for any legacy polygon after the change
- Loading a pre-existing `.bmaplan` produces different summary totals
- `proto/server.py` requires modification
- Test runtime exceeds previous baseline by > 50% (performance regression)
- Any forbidden surface (CLAUDE.md table) needs to be changed to make the
  design work — in that case, redesign instead of breaking the contract
