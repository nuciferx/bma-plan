---
name: bma-housekeep
description: |
  Audit and propose fixes for BMA-Plan housekeeping debt: root .md files exceeding 15, stale active sprints (>2 weeks old still in active/), date drift between LATEST_STATUS and CURRENT_STATUS, untracked files in unexpected places. Designed from the 2026-05-13 manual Wave 1 housekeeping — captures real patterns. Always PROPOSE moves; never auto-apply destructive changes.

  Trigger phrases (Thai): "housekeeping", "เก็บกวาด", "ตรวจไฟล์", "ทำความสะอาด", "audit ไฟล์"
  Trigger phrases (English): "housekeep", "audit files", "clean up", "check root files"

  Do NOT use when: user wants to commit changes (use direct git commands), wants doc content drift detection (use bma-doc-auditor subagent), or wants to find a symbol (use bma-explorer).
---

# /bma-housekeep — Repo Housekeeping Audit

Goal: catch drift early. Always PROPOSE — never auto-apply moves/deletes.

## Allowed Root Files (canonical list from CLAUDE.md)

```
AGENTS.md, CLAUDE.md, README.md, index.md,
CURRENT_STATUS.md, log.md, FINAL_REPORT_FOR_CHATGPT.md,
TEST_RESULT.md, PATCH_SUMMARY.md, UI_MANUAL_TEST.md,
NEXT_ACTION.md, .gitignore
```

Limit: **≤15** `.md` files at root.

## Steps

1. **Audit in parallel:**
   - `ls *.md | wc -l` — root count
   - `ls *.md` — names → diff against allowlist
   - `ls sprints/active/` + `stat` on each → flag any older than 14 days
   - `head -3 docs/status/LATEST_STATUS.md | grep Date` vs `head -3 CURRENT_STATUS.md | grep Date` → flag if differ
   - `git status --short | grep "^??" | head -10` — untracked
   - Check `docs/status/READ_ORDER.md` references → for each link, verify file exists

2. **Build report** with severity:

   ```
   ## 🧹 BMA-Plan Housekeeping Audit — <date>

   ### 🔴 BLOCK (must fix before next sprint)
   - <e.g., root .md count = 18, exceeds limit of 15>
   - <broken link in READ_ORDER.md to <path>>

   ### 🟡 WARN (recommend fix this week)
   - <e.g., sprint X in active/ has been there 21 days, Status=PASS — should be moved to completed/>
   - <LATEST_STATUS.md date 2026-05-10 vs CURRENT_STATUS.md 2026-05-13 — 3 days drift>

   ### 🟢 OK
   - root count: N/15
   - active sprints: N (all <2 weeks old)
   - status docs in sync

   ### Proposed actions
   For each BLOCK/WARN, give exact `git mv` or `Edit` command. Do NOT execute.
   ```

3. **Patterns to detect** (captured from 2026-05-13 manual Wave 1):

   | Pattern | Severity | Action |
   |---|---|---|
   | Root file not in allowlist | 🟡 WARN | Suggest `docs/design/` (plan/analysis), `archive/old_docs/` (sprint done), `sprints/archive/` (RUN_*.md sprint card) |
   | `RUN_*.md` at root | 🔴 BLOCK | Move to `sprints/archive/` |
   | Active sprint with `Status: PASS` | 🟡 WARN | Move to `sprints/completed/<YYYY-MM-DD>-<slug>/` |
   | Active sprint with `Status: BLOCKED` | 🟡 WARN | Move to `sprints/archive/<YYYY-MM-DD>-<slug>-blocked/` |
   | LATEST_STATUS.md date != CURRENT_STATUS.md date | 🟡 WARN | Update LATEST_STATUS.md |
   | Untracked file matches `archive/**/.claude/` | 🟢 OK | Leftover from old structure, ignore |
   | Broken link in READ_ORDER.md | 🔴 BLOCK | Remove or fix the link |
   | `opus4.7/`, `pic/`, `artifacts/` untracked | 🟢 OK | Should be gitignored (verify) |

4. **Never** apply moves yourself. End with:
   ```
   ⏭ Apply these changes? (y/N)
   ```

   If user says yes, execute one git mv per file with explicit confirmation, not batch.

## Constraints

- Output ≤40 lines.
- Don't read sprint cards beyond first 10 lines (status line is at top).
- Don't read full status docs — only the Date line.
- Defer doc content drift (duplicates, conflicting facts) to `bma-doc-auditor` subagent.
