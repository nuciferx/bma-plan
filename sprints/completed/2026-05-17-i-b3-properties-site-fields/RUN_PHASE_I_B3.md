# RUN_PHASE_I_B3 — Phase I-B3: Properties panel site fields + draw-then-classify

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `c011c4e`

## Goal

Extend the Properties panel so users can edit `buildingHeight_m` for building-coverage polygons,
and classify any drawn polygon's `semanticTag` via the Properties panel after drawing (draw-then-
classify workflow). Also append the 7 site area tags to the Semantic Tag dropdown on site pages.

Source: PHASE_INDEX.md row `I-B3` (depends on I-B1 ✅).

## Scope — IN

- `buildingHeight_m` editable `<input type="number">` in Properties panel, visible only when
  `isBuildingTag(obj.semanticTag)` is true.
- `isBuildingTag(tag)` helper — returns true for `building_coverage`.
- 7 site area `semanticTag` options appended to the Semantic Tag dropdown on site pages (draw-then-
  classify: user draws plain polygon → opens Properties → picks tag).
- Live update: changing the tag or height field in Properties immediately updates the object and
  calls `pushUndo()` + `redrawAll()`.
- New E2E marker `PHASE_I_B3_OK` with 10 sub-checks.

## Scope — OUT

- No changes to area math or measurement flow.
- Opening polygons do not get site semanticTags in v1.
- `buildingHeight_m` write-back does not affect area calculation (height is a separate field).

## Implementation summary

### Functions added (`proto/ui.html`)

- `isBuildingTag(tag)` — returns `tag === 'building_coverage'` (additive helper, not editing
  existing tag-classification logic).
- `buildPropertiesPanel(obj)` — extended: `buildingHeight_m` row rendered when `isBuildingTag`;
  Semantic Tag dropdown extended with site tags when `pageTags[curPage] === 'site'`.
- Height input `onchange` handler — updates `obj.buildingHeight_m`, calls `pushUndo()`, `redraw()`.
- Tag dropdown `onchange` — existing handler already handles general semanticTag update;
  site tags now appear in the list on site pages.

### Key design decisions

- Site tags are appended to the existing dropdown (not a separate control) to keep the UI simple.
- `isBuildingTag` is a thin wrapper intentionally — future building types can extend it without
  touching the calling code.
- Height field stored as `Number(val) || null` (null when empty, not 0).

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `isBuildingTag` helper; Properties panel `buildingHeight_m` row; site-tag dropdown append on site pages |
| `proto/e2e_ui_test.py` | NEW `_test_phase_i_b3(page)` 10 sub-checks + marker `PHASE_I_B3_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS GREEN
```

PHASE_I_B3_OK: 10 sub-checks all PASS.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED
- `.bmaplan` schema — ADDITIVE (`buildingHeight_m` field already defined in I-A; no rename/removal)
- Phase 1 boundary — kept (no legal verdict, no pass/fail, no Rule Engine)

## References

- PHASE_INDEX.md row `I-B3`
- `docs/design/SITE_PLAN_UI_MOCKUP.md` — Properties panel spec
- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md §16` — `buildingHeight_m` decision (Q2=A)
