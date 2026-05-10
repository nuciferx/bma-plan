# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-10

## Immediate Next

8-phase batch complete (2026-05-10). Manual acceptance test complete (2026-05-10) — 20 TCs, all PASS, one MINOR bug.

**Open Bug:** TC-12-B1 (MINOR) — `lbl-save-state` stays "Manual save required" instead of "Unsaved changes" after `pushUndo()` when no prior save has occurred. Guard in `_setDirty()` prevents update from initial label. Cosmetic only — save/load functionality unaffected. Fix: reset label to `""` on `loadPage()` success, or remove the guard condition.

Recommended next sprint: `RUN_SAVE_STATE_LABEL_FIX.md` (low-risk one-liner) or defer to next UI polish sprint.

Remaining UI polish sprints:
1. RUN_SAVE_STATE_LABEL_FIX.md — fix TC-12-B1 save state label initial-state guard (MINOR)
2. RUN_RIBBON_TOOLBAR_POLISH.md — mockup-style ribbon polish without fake actions
2. RUN_RIGHT_LAYERS_FINAL_POLISH.md — final Layers-first right panel polish
3. RUN_PAGE_FLOOR_SETUP_PANEL.md — page/floor setup usability polish
4. RUN_SCALE_MANAGER_FOUNDATION.md — audit-only scale overview
5. RUN_REVIEW_WARNING_PANEL_POLISH.md — grouped warning panel
6. RUN_EXPORT_READY_PANEL_POLISH.md — export readiness UI summary
7. RUN_UI_VISUAL_CONSISTENCY_PASS.md — final visual consistency pass

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
