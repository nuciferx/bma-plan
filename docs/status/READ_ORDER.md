# READ_ORDER.md — Agent Reading Guide

Date: 2026-05-09

## Required Reading (every session, in order)

1. `AGENTS.md` — GTM Infinite Loop operating method, Phase 1 scope lock, stop conditions
2. `CURRENT_STATUS.md` — one-line status, latest sprint, latest commits
3. `docs/status/LATEST_STATUS.md` — active feature state table
4. `docs/status/NEXT_ACTIONS.md` — next sprint candidates, backlog, hard forbidden list
5. `docs/status/TEST_BASELINE.md` — full assertion list for smoke and full suites

## Conditional Reading

- `docs/status/COMMIT_HISTORY.md` — if you need to reference specific commit hashes
- `docs/status/KNOWN_ISSUES.md` — if a stop condition is hit or a known issue is relevant
- Active sprint card in `sprints/active/` — if a sprint is in progress
- `docs/design/RUNTIME_FILE_SPLIT_AUDIT.md` — if planning further server.py or frontend splits
- `docs/design/E2E_SPLIT_PLAN.md` — if planning e2e test reorganization

## Skip (too large / stale)

- `log.md` — only if debugging a specific prior decision; use archive link inside
- `PATCH_SUMMARY.md` — summary is in FINAL_REPORT_FOR_CHATGPT.md
- `docs/archive/` — historical only; do not read unless specifically needed

## Before Any Code Edit

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py   # must PASS
python proto/e2e_ui_test.py smoke                             # must PASS
```

Restore from git if either fails before your edit.

## Before Commit

```bash
python proto/e2e_ui_test.py full                             # must PASS
```

Rollback with `git checkout proto/server.py` etc. if FAIL.
