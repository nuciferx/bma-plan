# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-09

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase 1 PASS: Raster PDF Measurement Assistant with working left-panel tab switching
(Sheets/Objects/Properties), opening parent reassignment, 5-field semantic metadata
across all exports, Report Target XLSX summary, Page Scales audit columns, and
Layers-first right panel.

## Latest Sprint

- Left Properties Migration: PASS (2026-05-09)
- Opening Parent Reassignment: PASS (2026-05-09)
- Page Scales Audit: PASS (2026-05-09)

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```
Last run: 2026-05-09. Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: `7005903` feat: left properties migration - left panel tab switching PASS
- proto: `e32122e` feat: wire left panel tabs with content switching and auto-Properties on selection

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
