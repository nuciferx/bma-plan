# RUN_TOKEN_REDUCTION_FILE_SPLIT.md

## 0. Sprint Identity

Sprint Name: Token Reduction / Status File Split
Sprint Type: Documentation / Housekeeping
Status: PASS
Date: 2026-05-09

---

## 1. Current Condition

- log.md: 1624 lines (full history from 2026-04-25 to 2026-05-09)
- PATCH_SUMMARY.md: 315 lines (8 sprints of history)
- TEST_RESULT.md: 240 lines (8 sprints of history)
- FINAL_REPORT_FOR_CHATGPT.md: 288 lines (8 sprints of history)
- CURRENT_STATUS.md: 155 lines (mixed current + historical policy)
- index.md: 148 lines (relatively ok)
- Total: ~2807 lines loaded per session

---

## 2. Goal

Reduce agent token load by archiving historical sections to docs/archive/ and
creating small focused status files in docs/status/.

---

## 3. Files Allowed

- CURRENT_STATUS.md, index.md, log.md
- PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md, UI_MANUAL_TEST.md
- docs/status/ (new files)
- docs/archive/ (new files)
- docs/process/ (existing)
- sprints/active/ (this card)

## 4. Files Forbidden

- proto/ui.html, proto/server.py, proto/e2e_ui_test.py, proto/requirements.txt
- Any runtime or source code change

---

## 5. Actions

- [x] Create docs/status/LATEST_STATUS.md
- [x] Create docs/status/NEXT_ACTIONS.md
- [x] Create docs/status/TEST_BASELINE.md
- [x] Create docs/status/COMMIT_HISTORY.md
- [x] Create docs/status/KNOWN_ISSUES.md
- [x] Archive log.md history to docs/archive/log-2026-05-09.md
- [x] Archive PATCH_SUMMARY history to docs/archive/patch-history-2026-05-09.md
- [x] Archive TEST_RESULT history to docs/archive/test-history-2026-05-09.md
- [x] Archive FINAL_REPORT history to docs/archive/reports-2026-05-09.md
- [x] Reduce log.md to short pointer + recent 2 sessions
- [x] Reduce CURRENT_STATUS.md to latest condition only
- [x] Update index.md to read small status files first
- [x] Update FINAL_REPORT_FOR_CHATGPT.md with sprint result

---

## 6. Acceptance Criteria

- [x] docs/status/ has 5 new small focused files (LATEST_STATUS, NEXT_ACTIONS, TEST_BASELINE, COMMIT_HISTORY, KNOWN_ISSUES)
- [x] docs/archive/ has 4 new archive files preserving all history
- [x] log.md reduced to 54 lines (was 1624)
- [x] CURRENT_STATUS.md reduced to 48 lines (was 155)
- [x] No information deleted — all archived
- [x] No source code touched
- [x] git diff --stat shows only docs and status files
- [ ] Committed with message: docs: split status logs for token-efficient agent context
