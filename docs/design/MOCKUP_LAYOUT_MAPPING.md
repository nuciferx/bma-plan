# MOCKUP_LAYOUT_MAPPING.md

Date: 2026-05-09
Source mockup: docs/design/bma-plan-mockup-v3.html
Current source: proto/ui.html + proto/static/css/app.css
Baseline: proto 797a4a2 — py_compile/smoke/full PASS

---

## A. Existing UI Structure (proto/ui.html)

```
┌─────────────────────────────────────────────────────────┐
│ #topbar (48px)                                          │
│  zone-a: [☰ brand] [📂 PDF] [💾 Proj] [Scale badge]   │
│  zone-b: [Set Scale] [Page Setup] [Review] [workflow]  │
│  zone-c: [📊 Export XLSX] (right-aligned, green)       │
├───────────────────┬─────────────────────┬───────────────┤
│ #left-sidebar     │ #workspace          │ #right-panel  │
│ (236px)           │ (flex 1)            │ (300px)       │
│                   │                     │               │
│ [Sheets|Obj|Prop] │  #empty-state       │ #rp-header    │
│ #sidebar-content  │  (before PDF)       │  "Layers"     │
│ (page list)       │                     │               │
│ #quick-tag-bar    │  #scale-notice      │ #rp-content   │
│ #workflow-card    │  (anchored bottom   │  .rp-layers   │
│ #widget-review-   │   of workspace)     │  .rp-props    │
│  warnings         │                     │  .rp-object-  │
│ #widget-export-   │  #cc / #canvas      │   tree        │
│  ready            │                     │               │
│ #lp-objects-      │                     │               │
│  content          │                     │               │
│ #lp-properties-   │                     │               │
│  content          │                     │               │
├───────────────────┴─────────────────────┴───────────────┤
│ #bottombar (38px)                                       │
│  Tool | Scale | Objects | Warnings | Layer | Snap      │
│  Color | Opacity | Save | Page | Summary                │
├─────────────────────────────────────────────────────────┤
│ #float-toolbar (floating, anchored below #topbar)       │
│  [Pan][Sel] | [Area][Opening][Land] | [Ref][Dist][Calib]│
│  [North] | [Layer select] | [Undo][Redo][Del] | [More▾] │
└─────────────────────────────────────────────────────────┘
```

### Current topbar zone layout

| Element | ID/Class | Purpose |
|---------|----------|---------|
| Brand | `.topbar-brand`, `#sidebar-toggle` | App name + sidebar toggle |
| Open PDF | `#upload-btn` | PDF file upload |
| Open Project | `#top-open-project` | Project .bmaplan load |
| Sample | `#btn-sample-pdf` | Load test PDF |
| Scale badge | `#scale-badge` | Current page scale display |
| Set Scale | topbar zone-b button | Triggers calib mode |
| Page Setup | topbar zone-b button | Opens setup overlay |
| Review | topbar zone-b button | Opens check panel |
| Export | `#btn-export-report` | XLSX export (green, zone-c) |

### Current left sidebar structure

| Element | ID | Content |
|---------|----|---------|
| Tab bar | `.left-panel-tabs` | Sheets / Objects / Properties |
| Sheets content | `#sidebar-content` | Page thumbnail list |
| Quick tag bar | `#quick-tag-bar` | ผังบริเวณ/แปลน/รูปด้าน/รายละเอียด/ซ่อน |
| Workflow card | `#workflow-card` | Steps 1–6 with status dots |
| Review warnings widget | `#widget-review-warnings` | Warning count from currentWarningCount() |
| Export ready widget | `#widget-export-ready` | Page/object/scale state |
| Objects content | `#lp-objects-content` | Flat object list (hidden when not active) |
| Properties content | `#lp-properties-content` | buildLeftProperties() output |
| Footer | `#sidebar-footer` | Auto-name + Expand all buttons |
| Page info strip | `#lp-page-info` | Page name · tag · scale state |

### Current float toolbar structure

| Group | Tools |
|-------|-------|
| Primary | Pan, Select |
| Drawing | Area (room), Opening, Land boundary |
| Reference | Reference line, Distance, Calibrate |
| Orientation | North arrow |
| Layer | Active layer dropdown |
| Edit | Undo, Redo, Delete |
| More | Path, Ref-distance, Perpendicular, Parking, Ortho, Land-edge, Setback |

---

## B. Mockup V3 Intended Structure (bma-plan-mockup-v3.html)

```
┌─────────────────────────────────────────────────────────┐
│ .title-bar (22px) — OS window chrome                   │
│  [●][–][□]   BMA-Plan — filename.pdf                   │
├─────────────────────────────────────────────────────────┤
│ .menu-bar (28px) — application menus                    │
│  BMA | File | Edit | View | Project | Scale | Page     │
│       | Measure | Object | Layer | Review | Export     │
│       | Workspace | Tools | Help    [Phase 1 badge]    │
├─────────────────────────────────────────────────────────┤
│ .ribbon (44px) — grouped icon+label action buttons      │
│  [Open PDF][Save][Recover] | [Set Scale][Scale Mgr]    │
│  [scale badge] | [Page Mgr][Set Floor] |               │
│  [Sel][Pan]|[Area][Opening][Land][Dim][North][Label]   │
│  | [Undo][Redo][Del] | [Review][Export]                │
├───────────────────┬─────────────────────┬───────────────┤
│ .left-panel       │ .canvas-wrap        │ .right-panel  │
│ (220px)           │ (flex 1)            │ (200px)       │
│                   │                     │               │
│ [Sheets|Obj|Prop] │  .canvas-top (28px) │ .right-header │
│ .panel-body       │  [◀ 3/6 ▶] [75%]  │  "Layers" [+] │
│  Sheet list with  │  [Ground Floor·1:100│               │
│  page nums,       │  x:1247 y:834][badge│ Layer items   │
│  types, warn      │  ]                  │ (color + name │
│                   │                     │  + eye + lock │
│ --- (separator) --│  .canvas-bg (grid)  │  + count)     │
│                   │  .pdf-mock          │               │
│ Objects in page   │  .measure-overlay   │ --- separator │
│ (flat list with   │                     │               │
│  color dot, name, │  .summary-widget    │ .props-section│
│  semantic tag)    │  (floating overlay, │ Selected obj  │
│                   │  bottom-right,      │ Name/Category │
│                   │  DRAGGABLE,         │ Tag/Floor/Use │
│                   │  tabs: Area/Floor/  │ /Area         │
│                   │  Site/Warnings,     │               │
│                   │  Export + Review    │               │
│                   │  footer buttons)    │               │
├───────────────────┴─────────────────────┴───────────────┤
│ .status-bar (22px)                                      │
│  [● Scale:1:100] [● 8 objects] [⚠ 2 warnings]         │
│  [Layer: พื้นที่อาคาร] [Tool: Area]                    │
│                              [RAMA4 · 3/6] [✓ Saved]   │
└─────────────────────────────────────────────────────────┘
```

### Mockup zones breakdown

| Zone | Class | Dimensions | Purpose |
|------|-------|-----------|---------|
| Title bar | `.title-bar` | 22px | OS window chrome (web app: N/A) |
| Menu bar | `.menu-bar` | 28px | Full application menus (14 menus) |
| Ribbon | `.ribbon` | 44px | Icon+label grouped action buttons |
| Left panel | `.left-panel` | 220px | Tabs: Sheets / Objects / Properties |
| Canvas | `.canvas-wrap` | flex 1 | PDF + overlays + summary widget |
| Canvas top bar | `.canvas-top` | 28px | Page nav / zoom / scale / coords |
| Summary widget | `.summary-widget` | 270px wide | Floating, collapsible measurement summary |
| Right panel | `.right-panel` | 200px | Layers + mini Properties |
| Status bar | `.status-bar` | 22px | Scale / Objects / Warnings / Layer / Tool / Save |

---

## C. Mapping Table

| Mockup Area | Current Element / File | Current Status | Gap | Recommended Sprint |
|-------------|------------------------|----------------|-----|--------------------|
| Title bar (.title-bar, 22px) | None | MISSING | OS chrome not needed for web app | LATER |
| Menu bar (.menu-bar, 28px) | #topbar zone-b (partial) | PARTIAL | No real menu bar; actions spread across topbar | MEDIUM IMPLEMENTATION |
| Ribbon (.ribbon, 44px) | #float-toolbar (floating) | PARTIAL | Float toolbar has same tools; visual style differs (no icon+label, not anchored as ribbon) | SMALL POLISH |
| Left panel tabs (Sheets/Obj/Prop) | .left-panel-tabs in #left-sidebar | DONE | Tab structure matches | — |
| Left panel — Sheets tab | #sidebar-content | DONE | Page list present | — |
| Left panel — Objects tab | #lp-objects-content | DONE | Flat object list present | — |
| Left panel — Properties tab | #lp-properties-content | DONE | Full editor present | — |
| Left panel — page warn indicators | #quick-tag-bar (tags only) | PARTIAL | No per-page warning icon in sheet list | SMALL POLISH |
| Canvas area | #workspace + #cc + #canvas | DONE | Canvas renders correctly | — |
| Canvas top info bar (.canvas-top) | None (scale-badge in topbar) | MISSING | Page nav/zoom/coords/scale-badge not on canvas | SMALL POLISH |
| PDF rendering | #cc/canvas (fabric.js-like render) | DONE | PDF renders via server API | — |
| Summary widget — static version | #widget-review-warnings + #widget-export-ready (sidebar) | PARTIAL | Basic widgets in sidebar; not a full tabbed summary widget; no big area number | MEDIUM IMPLEMENTATION |
| Summary widget — draggable | .summary-widget dragging in mockup | FORBIDDEN | Draggable workspace out of scope | FORBIDDEN |
| Summary widget — collapsible | .summary-widget.collapsed in mockup | LATER | After static version is done | LATER |
| Right panel — Layers | #rp-content .rp-layers-section | DONE | 5 layers with counts, eye/lock controls | — |
| Right panel — mini Properties | #rp-content .rp-properties-section | DONE | Compat section present | — |
| Right panel — width | 300px (#right-panel) | PARTIAL | Mockup is 200px; current is 300px | SMALL POLISH |
| Status bar | #bottombar | PARTIAL | Has all data; 38px vs 22px; no dot indicators; no autosave (FORBIDDEN) | SMALL POLISH |
| Status bar — autosave badge | .autosave-badge in mockup | FORBIDDEN | Full autosave engine out of scope | FORBIDDEN |
| Canvas color scheme (--bg) | app.css :root --bg:#090b10 | PARTIAL | Mockup uses #1a1d21 (lighter); current is #090b10 (darker) | SMALL POLISH |

---

## D. Widget Mapping

| Widget | Mockup Location | Current Element | Current Status | Gap | Sprint |
|--------|----------------|-----------------|----------------|-----|--------|
| Workflow Widget | Not in mockup | `#workflow-card` in sidebar | DONE | Present in current UI only; mockup replaced by ribbon workflow | — |
| Scale Status Widget | Ribbon scale-badge + canvas-top badge | `#scale-badge` in topbar + `#scale-notice` in canvas | DONE | Exists; location differs from mockup | SMALL POLISH |
| Page Info Widget | Canvas top bar (.canvas-top text) | `#lp-page-info` in sidebar | PARTIAL | Sidebar vs. canvas top bar | SMALL POLISH |
| Review Warning Widget | Summary widget tab "แจ้งเตือน" + menu Review | `#widget-review-warnings` in sidebar | PARTIAL | Basic card; mockup has rich tab with categorized warnings | MEDIUM IMPLEMENTATION |
| Export Ready Widget | Summary widget footer + Export menu | `#widget-export-ready` in sidebar | PARTIAL | Basic card; mockup has full footer with export button | SMALL POLISH |
| Layers Widget | Right panel (full) | `#rp-content .rp-layers-section` | DONE | Structurally matches | — |
| Properties Widget | Left panel Properties tab + Right panel mini | `#lp-properties-content` + `.rp-properties-section` | DONE | Both present | — |
| Page Setup Widget | Page menu + Ribbon Page group | Setup overlay `#setup-overlay` | PARTIAL | Overlay-based; mockup has ribbon Page group + Page Manager | SMALL POLISH |
| Scale Manager Widget | Scale menu + Ribbon Scale group | Single-page calibration only | MISSING | No multi-page scale overview table | MEDIUM IMPLEMENTATION |
| Export Summary Widget | Summary widget footer + Export menu | `#export-readiness` in export panel + sidebar widget | PARTIAL | Rich export preview not yet present | SMALL POLISH |

---

## E. Gap Classification Summary

| Classification | Count | Items |
|----------------|-------|-------|
| DONE | 10 | Left panel tabs, Sheets/Objects/Properties content, Canvas render, Layers, Properties, Workflow, Scale notice |
| SMALL POLISH | 9 | Ribbon visual, Canvas top bar, Page warn icons, Right panel width, Status bar dots, Color scheme, Scale/Page badges on canvas, Export summary, Export ready widget |
| MEDIUM IMPLEMENTATION | 4 | Menu bar, Full summary widget (static), Scale Manager, Review Warning widget (tabbed) |
| LATER | 2 | Title bar, Summary widget collapsible |
| FORBIDDEN | 3 | Summary widget drag, Custom workspace save, Autosave engine |

---

## F. Forbidden Mockup Areas

These items appear in the mockup but are **permanently forbidden** in Phase 1:

| Item | Mockup Reference | Reason Forbidden |
|------|-----------------|------------------|
| Draggable summary widget | `.sw-header { cursor: grab }`, drag logic in JS | Draggable workspace — Phase 1 scope |
| Custom workspace save | Workspace menu › Save Current Workspace | Custom workspace save layout — Phase 1 scope |
| Full autosave engine | Status bar `.autosave-badge "✓ Saved 2 min ago"`, File menu › Autosave Settings | Full autosave engine — Phase 1 scope |
| Legal checker | Not in mockup | Phase 1 scope lock |
| OCR | Not in mockup | Phase 1 scope lock |
| AI checker | Not in mockup | Phase 1 scope lock |
| Rule Engine / FAR/OSR pass-fail | Not in mockup | Phase 1 scope lock |
| K.1 generator | Not in mockup | Phase 1 scope lock |
| Auto boundary detection | Not in mockup | Phase 1 scope lock |

Items marked DISABLED in mockup dropdowns (badge-hidden):
- Copy Scale to Selected/Similar Pages
- Group/Ungroup Objects
- Large File Mode
- Split PDF Suggestion
- Performance Monitor
- Export History
- Scale History
- Developer Debug
- Move/Collapse Panels
- Save Current Workspace

These are intentionally hidden in the mockup and remain LATER in Phase 1.

---

## G. What Is Already Implemented

The following mockup areas already work correctly in proto/ui.html:

1. Left panel with 3 tabs (Sheets / Objects / Properties) — full switching logic
2. Page list in Sheets tab with page names, quick-tag bar, auto-naming
3. Object list in Objects tab (flat list, click → auto-switch to Properties)
4. Properties editor in Properties tab (grouped: Basic / Measurement / Metadata)
5. Right panel Layers section (5 layers, counts, eye/lock, active indicator)
6. Right panel mini Properties section (compat)
7. Canvas with PDF rendering, zoom/pan, snap
8. Scale calibration and badge in topbar
9. Scale notice in canvas (anchored bottom, shows when scale not set)
10. Workflow card (#workflow-card) with 6-step status
11. Review Warning Widget (#widget-review-warnings) — sidebar card
12. Export Ready Widget (#widget-export-ready) — sidebar card
13. Page Info Widget (#lp-page-info) — sidebar strip
14. Status bar (Tool/Scale/Objects/Warnings/Layer/Save/Page)
15. Export panel (XLSX, JSON, CSV, annotated PDF)
16. Opening parent reassignment (right panel select)
17. Semantic tag + measurement metadata (5 fields)

## H. What Is Missing / Partially Implemented

1. **Menu bar** — 14-menu application menu bar (MEDIUM IMPLEMENTATION)
2. **Ribbon-style toolbar** — current float-toolbar has tools but not ribbon icon+label style (SMALL POLISH)
3. **Canvas top info bar** — page nav / zoom / coords overlay above canvas (SMALL POLISH)
4. **Scale Manager** — multi-page scale overview and copy-to-page (MEDIUM IMPLEMENTATION)
5. **Full tabbed summary widget** — Area/Floor/Site/Warnings tabs with big numbers (MEDIUM IMPLEMENTATION, no drag)
6. **Per-page warning icons in sheet list** — visual warn indicator per page item (SMALL POLISH)
7. **Right panel width** — 300px vs. mockup 200px (SMALL POLISH)
8. **Status bar cleanup** — 38px vs. 22px; no dot indicators (SMALL POLISH)
