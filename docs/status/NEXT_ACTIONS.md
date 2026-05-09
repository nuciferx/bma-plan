# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-09

## Immediate Next

Sprint B (10 UI testability micro sprints) — DONE (2026-05-09).
Max Token Reduction / File Split — DONE (2026-05-09).

Next candidate sprints:
- Left panel Properties refinement (scroll, focus, keyboard navigation)
- Parking-specific rows in สรุปตาม Report Target
- E2E test split into proto/tests/ modules (see docs/design/E2E_SPLIT_PLAN.md)
- Frontend JS module split (see docs/design/RUNTIME_FILE_SPLIT_AUDIT.md — deferred)

## Backlog (Longer Term)

- Left panel Properties refinement (scroll, focus, keyboard navigation)
- Parking-specific rows in สรุปตาม Report Target
- Reference arcs/circles (curved path Sprint 5)
- Manual opening parent reassignment further UX improvements
- iPad touch UX (Sprint 6)
- Full scale record with calibration endpoint storage

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
