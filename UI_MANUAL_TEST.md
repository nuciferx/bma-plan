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
