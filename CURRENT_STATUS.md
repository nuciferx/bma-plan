# CURRENT_STATUS.md — BMA-Plan Current Status

Date: 2026-05-09

> Full status details: [docs/status/LATEST_STATUS.md](docs/status/LATEST_STATUS.md)
> Next actions: [docs/status/NEXT_ACTIONS.md](docs/status/NEXT_ACTIONS.md)
> Known issues: [docs/status/KNOWN_ISSUES.md](docs/status/KNOWN_ISSUES.md)

## One-Line Status

Phase 1 PASS: Static serving regression fixed — /static/* now returns 200 OK.
Root causes: missing aiofiles + guarded mount masked the failure. UI renders styled.

## Latest Sprint

- Static 404 Fix: PASS (2026-05-09) — unconditional mount, aiofiles installed, BOM removed
- Mockup Layout Mapping: PASS (2026-05-09, docs only) — gap table + 6-sprint plan
- Static Asset Healthcheck: PASS (2026-05-09) — server.py path fix + 4 E2E assertions

## Test Baseline

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python proto/e2e_ui_test.py smoke                          # PASS
python proto/e2e_ui_test.py full                           # PASS
```
Last run: 2026-05-09 (proto a2099ec). Full test detail: [docs/status/TEST_BASELINE.md](docs/status/TEST_BASELINE.md)

## Latest Commits

- root: (this commit)
- proto: `a2099ec` fix: serve static assets unconditionally from absolute proto path

Full commit history: [docs/status/COMMIT_HISTORY.md](docs/status/COMMIT_HISTORY.md)

## Phase 1 Scope (Locked)

Phase 1 = Raster PDF Measurement Assistant only.
Forbidden: legal checker, OCR, AI, Rule Engine, FAR/OSR/setback pass-fail, K.1 generator,
auto boundary detection, draggable workspace, full autosave engine, save/load migration.

## Agent Operating Method

All agents must follow AGENTS.md (GTM Infinite Loop).
Read AGENTS.md + this file + docs/status/LATEST_STATUS.md before starting any sprint.
Run py_compile + smoke before any edit. Run full before commit.
