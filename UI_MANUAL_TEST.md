# Latest: Mockup V3 Alignment — Phase A (Subtractive Removal)

Branch: feature/mockup-v3-alignment

Date: 2026-05-11

## Result

Automated PASS (py_compile + smoke + full). Visual UI looks similar to before — just less clutter in sidebar.

## Manual Checklist — Removed Elements (must be GONE)

| Check | Expected | Result |
|-------|----------|--------|
| `⚙ Layout` button in topbar | Gone | — |
| Layout Options modal popup | Gone | — |
| Inspection panel in left sidebar | Gone (no "สถานะการตรวจ" card) | — |
| Workflow card in left sidebar | Gone (no "Workflow" with 6 steps) | — |
| Review Warnings widget | Gone | — |
| Export Ready widget | Gone | — |
| Quick Tag bar (🏗 / 📐 / 📏 / 🔍 / 🚫) | Gone | — |

## Manual Checklist — No Regressions

| Check | Expected | Result |
|-------|----------|--------|
| Open PDF | Works, page renders | — |
| Set Scale (Set Scale button in topbar) | Calib mode activates, polygon drawn, area shown | — |
| Page Setup (Page Setup button) | Overlay opens, tag grid renders | — |
| Area drawing (tool-row Area button) | Polygon drawn, name panel opens, area in measure-result | — |
| Opening drawing | Opening drawn, linked to parent | — |
| Right panel layers | Layers list visible per page type | — |
| Save .bmaplan | File saves, reload restores all data | — |
| Export XLSX | File generates, summary matches UI | — |
| Real PDF (45 pages) | Loads, can navigate, rotation works | — |

---

# Previous: Widget / Menu Placement System

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
