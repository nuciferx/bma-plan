# NEXT_ACTIONS.md — BMA-Plan Next Recommended Actions

Date: 2026-05-09

## Immediate Next (Sprint B)

Execute 10 UI testability micro sprints in order:
0. Confirm Commit / Clean State
1. Test Mode Landing / Start Screen
2. Top Action Bar Simplify
3. Set Scale CTA / Scale Status
4. Page Setup Mini Panel
5. Measurement Toolbar Clean Mode
6. Properties Panel Usability
7. Right Panel Layers Visual Cleanup
8. Review Warning Summary
9. Export Ready Screen
10. Quick Test Guide (docs/process/QUICK_TEST_GUIDE.md)

Source files allowed: proto/ui.html, proto/e2e_ui_test.py only.

## Backlog (After Sprint B)

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
