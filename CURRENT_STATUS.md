# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-11

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase 1 PASS: Widget / Menu Placement System — per-widget control over left/right panel widgets (visibility, region, order, size) via `WIDGET_MENU_REGISTRY` + `bmaPlan.widgetPlacement.v1` localStorage. No backend or schema changes.

## Latest Sprint

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
Last run: 2026-05-11 (current working tree). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: (this commit)
- proto: `4a09693` ui: visual consistency pass

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
