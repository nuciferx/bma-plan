# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-11

## Immediate Next

PyMuPDF render audit complete (2026-05-11) — `RUN_PYMUPDF_RENDER_REGRESSION_COMPARE` PASS.

**Finding: NO code regression.** Old and current `/page/{n}` render path are identical.
Measured bottleneck: **JPEG encode (`tobytes`) takes 93% of render time** at scale=1.5.
- Test PDF at 1.5×: `get_pixmap=110ms  encode=1366ms  total=1476ms`
- Real 45-page permit PDF at 1.5×: ~15 000ms — legitimate cost of large complex page, not a bug.

**Instrumentation added:** `[BMA_PAGE_RENDER_PERF]` server log line on every `/page/{n}` request.
Check server terminal for: `session=Xms cache=Xms get_pixmap=Xms encode=Xms bytes=N total=Xms MISS/HIT`

**Next recommended sprint: `RUN_RENDER_SCALE_REDUCE.md`** — reduce default render scale
from 1.5 to 1.2. Cuts pixel count by 36% → encode ~36% faster. No architecture change,
no schema change, no quality issue for architectural review use.

Pre-first-page JS fixed (2026-05-10) — `RUN_PRE_FIRST_PAGE_LOAD_REGRESSION_AUDIT` PASS.

**Open Bug:** TC-12-B1 (MINOR) — `lbl-save-state` stays "Manual save required" instead of "Unsaved changes" after `pushUndo()` when no prior save has occurred. Cosmetic only.

Performance sprints queue:
1. RUN_RENDER_SCALE_REDUCE.md — reduce default render scale 1.5→1.2 (fastest safe win)
2. RUN_SAVE_STATE_LABEL_FIX.md — fix TC-12-B1 save state label (MINOR)

Remaining UI polish sprints:
1. RUN_RIBBON_TOOLBAR_POLISH.md — mockup-style ribbon polish without fake actions
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
