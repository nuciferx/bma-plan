# Latest: Widget / Menu Placement System

Date: 2026-05-11

## Result

Automated PASS (py_compile + smoke + full). Manual viewport check below.

## Manual Checklist — Widget / Menu Placement Section

| Check | Expected | Result |
|-------|----------|--------|
| Open Layout Options panel | Panel appears, "G. Widget / Menu Placement" section visible | — |
| Search box filters list | Typing e.g. `review` filters list to Review Warnings | — |
| Category filter | Changing category to "Layer" leaves only Layer-category rows | — |
| Visibility toggle for Review Warnings | Widget hides/shows in left panel | — |
| Region select moves Review Warnings to right | Widget appears in right panel under Layers | — |
| Region select returns Review Warnings to left | Widget returns to left panel above Sheets | — |
| Order input changes display order in left zone | Higher order moves widget visually lower | — |
| Size = `collapsed` for Review Warnings | Body collapses to title only; state preserved | — |
| Size = `full` for Review Warnings | Widget body shows again | — |
| Reset button | All widgets restored to defaults; locked widgets re-snap to original parents | — |
| Reload page after changes | Custom placement persists from localStorage | — |
| Locked widget region select is disabled | Sheets / Objects / Properties / Layer Context / Current Page Layers / Page Info / Inspection Status / Scale Status cannot be moved by region select | — |

## Workflow Regression Checklist

| Check | Expected | Result |
|-------|----------|--------|
| Left panel scroll (Sheets / Objects / Properties) | Scrolls smoothly | — |
| Right panel scroll (Layers) | Scrolls smoothly | — |
| Current Page Layers still visible | All page-tag layers listed | — |
| Active Layer dropdown still works | Switching layer applies | — |
| Sidebar tabs (Sheets / Objects / Properties) | Toggling tabs works as before | — |
| Set Scale → Calibrate → Confirm | Still works, no regression | — |
| Draw Area | Polygon drawn, area shown, summary updated | — |
| Draw Opening | Opening drawn and linked, summary updated | — |
| Export Excel | XLSX file downloads | — |
| Export Current Page + Annotations | PDF file downloads | — |
| Save Project / Load Project | Round-trip works | — |
| Layout Options → Reset to Current Stable | Removes v3 body classes; widget placement unaffected | — |
| Layout Options → Reset Panel Layout | Restores 236/300 widths and docked modes | — |

## Notes

- Hidden widgets via placement use `.widget-hidden { display:none !important; }`; state is preserved.
- Collapsed size hides body details (`.widget-body`, `.widget-link`, `.widget-links-row`, `.wf-row`) but keeps DOM and titles.
- Movable widgets default to left (their original region). They are re-parented to `#wp-right-zone` only when explicitly placed in right.
