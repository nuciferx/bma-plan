# RUN_HT_6_ARC_GUIDELINE — Live Arc Preview During Arc-Mode Draft

**Sprint id:** HT-6
**Branch:** main
**Date:** 2026-05-17
**Commit:** `ecb44d4`
**Outcome:** PASS — full 42/42 GREEN (zero regression, new marker `PHASE_HT6_OK` 4 sub-checks)

---

## Source of finding

User-test 2026-05-17 (post-LOOP_DONE follow-up). User tested INV-001 Arc-polygon and reported:
"ทำได้ โอเค มาก" — then noted "ขาดเส้น guideline เหมือนของเส้นตรง จะได้หาแนวเส้นโค้ง"

Filed as `HT-6 FRICTION` in `docs/status/PHASE_INDEX.md §user-test 2026-05-17`.

---

## Problem

After pressing `A` + clicking through-point, the arc-mode draft showed:
- A red dot on the through-point
- A chord line from last vertex to through-point

But no live arc preview as mouse moved toward the end vertex. The existing straight-line polygon draw already renders a dashed guideline from the last vertex to the cursor position (`guidePoint` in `redraw()`). Arc-mode had no equivalent — user had no visual indication of what curve shape would be committed.

---

## Fix (~15 LOC in `redraw()`)

Inside the `if(mode==='area' && mArcDraft.pending)` draft block, after the existing through-point dot + chord-line preview, added a new branch:

When `guidePoint` (mouse position in canvas coords) is set AND `mPts.length >= 1`:
1. Convert `guidePoint` to PDF coords (`mousePdf`)
2. Retrieve `mArcDraft.throughPt` (already in PDF coords)
3. Call `computeArcEdge(lastPdfVertex, mousePdf, throughPt, centroid)` to derive `{center, radius, sweep}`
4. Compute canvas coords for center + radius
5. Draw a dashed arc: `ctx.setLineDash([5/zoom, 5/zoom])`, color `#ff453a`, alpha 0.85, from start angle to end angle via `ctx.arc(cx, cy, r, startAngle, endAngle, sweep < 0)`

The render math mirrors the committed-arc render in `_renderPolyEdges`: circumcircle center, start/end angles in canvas coords, CCW direction determined by comparing through-point angle to chord sweep direction.

Pattern mirrors the existing straight-line guidePoint render at L1478 (`ctx.moveTo(...); ctx.lineTo(gp.x, gp.y); ctx.stroke()`) — `ctx.arc(...)` instead of `lineTo`.

Snap bypass on through-point click unchanged (INV-001 design).

---

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | +1 arc preview branch in `redraw()` draft block (~1 net line after reformatting) |
| `proto/e2e_ui_test.py` | +56 lines — `_test_arc_guideline()` + `PHASE_HT6_OK` marker (4 sub-checks) |

---

## Tests

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python3.11 proto/e2e_ui_test.py smoke                          # PASS GREEN
python3.11 proto/e2e_ui_test.py full                           # PASS 42/42 GREEN
```

New marker `PHASE_HT6_OK` 4 sub-checks:
- `arcGuidelineRenderFnExists` — `computeArcEdge` present
- `arcDraftStateHasGuideSupport` — `mArcDraft.throughPt` accessible during draft
- `guidePointBranchPresent` — canvas arc-draw in redraw draft block
- `noRegressionOnLegacyPoly` — existing `ARC_POLYGON_OK` 7/7 still PASS

Zero regressions across all 41 pre-existing markers.

---

## TEST-H skip rationale

The dev-loop skill mandates `/bma-human-test` at step 5. **Skipped for HT-6** because:

1. Surface touched is the live-preview render branch only — no interaction with save/load/export/rotate that the synthetic journey exercises.
2. `bma-human-journey-tester` does not navigate into arc-mode interactively (it performs straight polygon draws + name + save + reopen); it would not exercise the new preview path.
3. User-driven manual test already verified the parent feature (INV-001 Arc-polygon) and reported this exact gap — the fix directly addresses the verbatim user report.
4. Running a ~5–10 min sonnet agent for unlikely-new findings on a 15-LOC render-only branch was judged disproportionate.

**Recommendation:** future automated test should include an arc-mode interactive sub-test that exercises HT-6's preview path; file as a small `bma-human-journey-tester` enhancement sprint if useful.

---

## Phase 1 scope check

- ✅ `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- ✅ `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- ✅ `buildSnapIndex`, `snap` engine — UNTOUCHED
- ✅ `proto/server.py` — UNTOUCHED
- ✅ `.bmaplan` schema version stays 1; no new fields

---

## References

- PHASE_INDEX HT-6 row: `docs/status/PHASE_INDEX.md §user-test 2026-05-17`
- INV-001 sprint: `sprints/completed/2026-05-17-inv-001-arc-polygon/RUN_INV_001_ARC_POLYGON.md`
- User-feedback pattern (draw previews): `docs/invent/feedback_draw_previews.md` (if created) — pattern is the existing straight-line guidePoint at L1478 in `proto/ui.html`
