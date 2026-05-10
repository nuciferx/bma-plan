# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-10

## Immediate Next

Page-Scoped Layer Model Lock — DONE (2026-05-10, docs-only).
Design docs: docs/design/PAGE_SCOPED_LAYER_MODEL.md
Audit: docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md

Layer implementation sprints (in order — must complete before area summary work):
1. RUN_LAYER_SCOPE_AUDIT.md — audit all global layer state usages; confirm blast radius
2. RUN_PAGE_LAYER_INSTANCE_MODEL.md — add `pageStore[n].layers[]`; migrate layerVis/layerLock per-page
3. RUN_PAGE_TYPE_LAYER_PRESETS.md — define preset templates by pageType; apply on page creation
4. RUN_OBJECT_LAYER_VALIDATION.md — add `layerId` + `pageId` to objects; save/load guard
5. RUN_LAYER_TOOL_AWARENESS.md — active layer control writes `layerId` onto new objects
6. RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR.md — group cross-page totals by semanticTag + floorCode

UI polish sprints (can interleave with layer sprints that are docs-only):
7. RUN_CANVAS_TOP_INFO_BAR.md — overlay above canvas with page/zoom/scale/coords (LOW-MEDIUM risk)
8. RUN_RIBBON_TOOLBAR_POLISH.md — mockup-style ribbon polish without fake actions
9. RUN_RIGHT_LAYERS_FINAL_POLISH.md — final Layers-first right panel polish
10. RUN_PAGE_FLOOR_SETUP_PANEL.md — page/floor setup usability polish
11. RUN_SCALE_MANAGER_FOUNDATION.md — audit-only scale overview
12. RUN_REVIEW_WARNING_PANEL_POLISH.md — grouped warning panel
13. RUN_EXPORT_READY_PANEL_POLISH.md — export readiness UI summary
14. RUN_UI_VISUAL_CONSISTENCY_PASS.md — final visual consistency pass

## Backlog (Longer Term)

- Left panel Properties refinement (scroll, focus, keyboard navigation)
- Parking-specific rows in สรุปตาม Report Target
- Reference arcs/circles (curved path Sprint 5)
- Manual opening parent reassignment further UX improvements
- iPad touch UX (Sprint 6)
- Full scale record with calibration endpoint storage
- Summary widget (tabbed: Area/Floor/Site/Warnings) — requires per-page backend summary

## Hard Forbidden (All Sprints)

- Legal checker, OCR, AI checker, Rule Engine
- FAR/OSR/setback pass-fail
- K.1 generator, auto boundary detection
- Draggable workspace, full autosave engine
- Large file mode engine
- Save/load breaking migration
- Export rewrite
- Calculating from layer names

## Policy

- One sprint = one problem
- PASS (py_compile + smoke + full) before commit
- PASS before starting next sprint
- Update status docs after every sprint
