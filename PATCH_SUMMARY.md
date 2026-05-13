# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: Phase H.1 Path Geometry Implementation

Branch: main

Date: 2026-05-13

## Outcome: PASS — all 19 E2E markers PASS including new PATH_GEOMETRY_OK

## Summary

Unified path geometry model (line + cubic Bézier segments) added to `proto/ui.html`. Replaces need for separate shape-type dispatch in future objects. Existing legacy objects (polygon, circle, ellipse, arc-edge) continue through their unchanged branches — additive only. Also fixed missing `proto/export/` Python package (was lost in submodule absorption) and regenerated `proto/test_plan_A1.pdf` fixture.

Key tuning: `_PATH_FLATTEN_TOL=0.1pt` forces de Casteljau level 5 for r=100pt circles (d_4≈0.158>0.1, d_5≈0.039<0.1) → area error vs exact π×r² drops to 0.012% (threshold: 0.1%).

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | Added 9 new functions (additive, after line 955): `_flattenCubicSeg`, `flattenPathToPoints`, `pathAreaM2`, `rectangleToPath`, `circleToPath`, `ellipseToPath`, `arcToCubic`, `renderPath`. Added `geometryType==='path'` first branch in `objectAreaM2`. Added path normalization in `applyLoadedProject`. |
| `proto/e2e_ui_test.py` | Added `_test_path_geometry(page)` with tests A–E. Added `PATH_GEOMETRY_OK` to `main()`. |
| `proto/export/__init__.py` | **New** — recreated missing package init. |
| `proto/export/semantic_metadata.py` | **New** — recreated from submodule backup: SEMANTIC_PROFILE_MAP, SEMANTIC_CATEGORY_MAP, etc. |
| `proto/export/xlsx_helpers.py` | **New** — recreated from submodule backup: _hex_to_rgb, _poly_area_pt2, _line_points, etc. |
| `proto/test_plan_A1.pdf` | **New** — regenerated fixture PDF via make_test_pdf.py. |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — unchanged
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` in `proto/ui.html` — unchanged
- `pdfToC`, `cToPdf`, `RS`, scale math, snap engine — unchanged
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → PASS (16 markers)
python3.11 proto/e2e_ui_test.py full                           → PASS (19 markers)
```

PATH_GEOMETRY_OK: `{pathRectMatchesPolygon: True, pathCircleWithinTolerance: True, pathMixedStable: True, pathLegacyUnchanged: True, pathSaveRoundTrip: True, fnsExist: True, all: True}`

## Phase 1 Scope Check

- ✅ `polyAreaM2`/`polyMetrics`/`polySelfIntersects` unchanged
- ✅ `pdfToC`/`cToPdf`/`RS` unchanged
- ✅ `proto/server.py` unchanged
- ✅ Schema version 1, additive only
- ✅ No UI (Pen tool / vertex drag = later sprint)
- ✅ No legal / OCR / AI / FAR / OSR

---

# Previous: Site Plan Measurement Plan (docs-only — Phase I pre-planning)

Branch: feature/menu-power-up

Date: 2026-05-13

## Outcome: PASS (docs-only)

Plan ของ "ต้องวัดอะไรบ้างบนผังบริเวณ" — extract requirements จากกฎกระทรวง 2 ฉบับ + เคสจริง 1 ฉบับ; output เป็น measurement specification ที่ระบบต้องรองรับใน Phase I. **Phase 1 hard rule:** capture facts, never auto-judge pass/fail.

Files: `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` (~520 lines). No source change.

---

# Previous: Phase G — Menu Wiring + Measure/Layer Power-up

Branch: feature/mockup-v3-alignment · Date: 2026-05-11 · Proto HEAD: `52167d8`

6 dropdown menus (56 items), 11 keyboard shortcuts, per-page layer bug fix. MENU_OK added to smoke.
