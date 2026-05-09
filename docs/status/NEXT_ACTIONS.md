# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-09

## Immediate Next

Mockup Layout Mapping — DONE (2026-05-09). See docs/design/MOCKUP_LAYOUT_MAPPING.md.
Implementation plan ready: docs/design/MOCKUP_IMPLEMENTATION_PLAN.md

Next sprints (in order):
1. RUN_WIDGET_PLACEMENT_POLISH.md — polish sidebar widgets to match mockup style (LOW risk)
2. Canvas Top Info Bar — overlay above canvas with page/zoom/scale/coords (LOW-MEDIUM risk)
3. Scale Manager Foundation — per-page scale overview overlay (MEDIUM risk)
4. Page Setup Table — per-page warn icons in Sheets tab (LOW risk)
5. Export Review Preview — richer export-ready widget (LOW risk)
6. Mockup Visual Phase 1 — menu-bar + ribbon implementation (HIGH risk, do last)

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
