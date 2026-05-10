# Latest: Page-Scoped Layer Implementation Batch

Date: 2026-05-10

## Result

Automated PASS (py_compile + smoke + full). Manual verification checklist below — run after next browser session.

## Manual Checklist — Layer Behavior Per Page

| Check | Expected | Result |
|-------|----------|--------|
| Open test PDF; go to Page 1 (site). Right panel Layers section shows site-preset labels (ที่ดิน/แนวเขต, กรอบอาคาร, ที่ว่าง, เส้นอ้างอิง, ป้าย/หมายเหตุ) | 5 layer rows, site labels | — |
| Switch to a plan-type page. Layers section shows plan-preset labels (พื้นที่หลัก, พื้นที่ย่อย, ช่องว่าง, เส้นอ้างอิง, ป้าย) | 5 layer rows, plan labels | — |
| Toggle Layer Lock on "ช่องว่าง" (deduction). `layerVis.deduction===true && layerLock.deduction===true` | Lock icon shows; deduction layer still visible | — |
| Draw a poly on plan page. Object appears in "พื้นที่หลัก" row count | Count increments by 1 | — |
| Draw an opening on plan page. Opening appears in "ช่องว่าง" row count | Count increments by 1 | — |
| Switch back to site page. Site-preset layers still show (not plan labels) | Layers revert to site preset | — |
| Active layer selector updates when switching tool (ref → deduction → base_area) | Selector value matches tool mode | — |
| Add a new poly. Object has `pageIndex`, `layerSlug`, `layerId` fields in browser console | All three fields non-null | — |
| Hide "เส้นอ้างอิง" layer via toggle. Reference lines disappear from canvas | Canvas clear of ref lines | — |
| Export XLSX. Exported data groups by `reportTarget`, not layer name | Report Target Summary sheet correct | — |

## Viewport Check

| Viewport | Result | Notes |
|----------|--------|-------|
| 1440 x 900 | — | Right panel layer rows readable with counts |
| 1366 x 768 | — | No overflow; layer section still first in right panel |

---

# Latest: Widget Placement Polish

Date: 2026-05-09

## Result

PASS by automated viewport-sensitive smoke/full coverage. Final manual viewport pass remains scheduled after Sprint 10.

## Checked

- Left widget visibility remained covered by E2E.
- Compact layout at 1440x900 remained PASS in `MAIN_UI_OK`.
- Final required manual viewport checks will be run after the visual consistency sprint.

---

# UI_MANUAL_TEST.md - Right Panel Organization After Mockup V3

Date: 2026-05-09

## Result

PASS

## Viewports Checked

| Viewport | Result | Notes |
|---|---|---|
| 1440 x 900 | PASS | Header and toolbar fit; Layers is the first right-panel section. |
| 1512 x 982 | PASS | Left labels, Layers panel, status bar, and canvas remain readable. |
| 1366 x 768 | PASS | No horizontal overflow; Layers remains first with counts visible. |

## Checklist

| Item | Result |
|---|---|
| Header/menu does not overflow | PASS |
| Ribbon/toolbar does not overflow badly | PASS |
| Set Scale is visible | PASS |
| Page Setup is after Set Scale | PASS |
| Left panel labels are readable | PASS |
| Right Layers panel is readable and first | PASS |
| Right layer rows show counts | PASS |
| Existing Properties/Object Tree remain accessible below Layers | PASS |
| Status bar is readable | PASS |
| Canvas remains usable | PASS |
| No fake active copy-scale/autosave/debug buttons visible | PASS |

## Notes

- No screenshots or manual artifacts were created in this sprint.
- The check used `proto/test_plan_A1.pdf` through the existing upload/start workflow.
- Right panel Properties/Object Tree remain below Layers as labeled compatibility sections.
