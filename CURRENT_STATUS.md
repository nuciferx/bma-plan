# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-09

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase 1 PASS: Left Inspection Status Panel added to left sidebar — collapsible panel
showing current context, workflow steps, per-page stats, measurement summary, and warnings.

## Latest Sprint

- Left Inspection Status Panel: PASS (2026-05-09) — proto `24b41c5`, 6 new E2E assertions
- Static 404 Fix: PASS (2026-05-09) — unconditional mount, aiofiles installed, BOM removed
- Mockup Layout Mapping: PASS (2026-05-09, docs only) — gap table + 6-sprint plan

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```
Last run: 2026-05-09 (proto 24b41c5). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: (this commit)
- proto: `24b41c5` ui: add left inspection status panel

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
