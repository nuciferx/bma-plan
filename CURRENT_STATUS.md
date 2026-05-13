# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-13

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase H.1 Path Geometry Implementation PASS on branch `main`. Unified path model (line + cubic Bézier) + 9 additive functions in `proto/ui.html`. PATH_GEOMETRY_OK passes all 5 acceptance tests A–E. All 19 E2E markers PASS (smoke + full). `_PATH_FLATTEN_TOL=0.1pt` → circle area error 0.012% vs exact π×r² (threshold 0.1%). Next: Site Plan Measurement (Phase I-A) or Pen tool (UI for path input).

## Latest Sprint

- Phase H.1 Path Geometry Implementation: PASS (2026-05-13) — 9 additive functions, PATH_GEOMETRY_OK, all 19 markers PASS
- Site Plan Measurement Plan (docs-only — Phase I pre-planning): PASS (2026-05-13) — `SITE_PLAN_MEASUREMENT_PLAN.md` produced from 3 law PDFs. No source change.
- Phase H.1 Revision — Path Geometry Design (docs-only): PASS (2026-05-13) — design + decision doc; no source change.
- Phase G: Menu Wiring + Measure/Layer Power-up: PASS (2026-05-11) — 6 menus, 56 items, 11 shortcuts, layer bug fix — proto `52167d8`
- Mockup V3 Alignment — Phase E + F: PASS (2026-05-11) — CSS cleanup + final tests/docs. branch: feature/mockup-v3-alignment
- Mockup V3 Alignment — Phase D: PASS (2026-05-11) — Summary Widget 4 tabs + drag — proto `203ae90`
- Mockup V3 Alignment — Phase B + C: PASS (2026-05-11) — title-bar/menu-bar/ribbon/panel restructure — proto `0ec4cd4`
- Mockup V3 Alignment — Phase A: PASS (2026-05-11) — subtractive removal — proto `72d621c`
- Widget / Menu Placement System: PASS (2026-05-11)
- Docked Toolbar + Panel Layout Options: PASS (2026-05-11)
- UI Layout Options (Mockup V3 modes): PASS (2026-05-10) — proto `087c769`
- Page Floor Setup Panel: PASS (2026-05-10) — proto `9b8c505`
- Right Layers Final Polish: PASS (2026-05-10) — proto `c947a2a`
- Ribbon Toolbar Polish: PASS (2026-05-10) — proto `7461278`
- Canvas Top Info Bar: PASS (2026-05-09) — proto `50d5d68`

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```
Last run: 2026-05-13 (full — 19 markers). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: `d5ec6a8` chore: update proto submodule — e2e smoke tests pass for ribbon UI
- root: `2af21a5` ui: Phase D — Summary Widget 4 tabs + drag (mockup v3 alignment)
- root: `614714e` ui: Phase B+C — title-bar + menu-bar + ribbon + panel restructure
- root: `76977ff` ui: Phase A subtractive removal (mockup v3 alignment)
- proto: `f6a1288` test: fix e2e smoke tests for mockup v3 ribbon (Phase B/C/D)
- proto: `203ae90` ui: Phase D — Summary Widget 4 tabs + drag
- proto: `0ec4cd4` ui: Phase B+C — title-bar + menu-bar + ribbon + panel restructure
- proto: `72d621c` ui: Phase A subtractive removal of excess UI systems

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
