# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-09

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase 1 PASS: Raster PDF Measurement Assistant with 10 UI testability polishes (Sprint B),
server.py export helpers split into proto/export/ package, working left-panel tabs,
opening parent reassignment, 5-field semantic metadata, Report Target XLSX, and Layers-first panel.

## Latest Sprint

- Max Token Reduction / File Split: PASS (2026-05-09)
- Fast UI Testability Polish (Sprint B, 10 micro): PASS (2026-05-09)
- Left Properties Migration: PASS (2026-05-09)

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```
Last run: 2026-05-09. Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: `4bda145` feat: 10 UI testability micro sprints - Sprint B PASS
- proto: `fb89ecd` refactor: split export metadata helpers

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
