---
name: bma-sprint-finalize
description: |
  Use when finishing a BMA-Plan sprint to generate ALL mandatory sprint outputs per AGENTS.md §1 in one shot. Updates 7 files with consistent cross-links: log.md, PATCH_SUMMARY.md, TEST_RESULT.md, FINAL_REPORT_FOR_CHATGPT.md, CURRENT_STATUS.md, docs/status/LATEST_STATUS.md, docs/status/NEXT_ACTIONS.md. Delegates writing to the bma-sprint-writer subagent (sonnet) to save tokens in the main thread.

  Trigger phrases (Thai): "จบ sprint", "sprint เสร็จ", "update docs", "เขียน log", "ทำ patch summary", "เตรียม commit", "อัพเดทสถานะ", "finalize", "sprint done"
  Trigger phrases (English): "sprint done", "finalize sprint", "update sprint outputs", "write log", "prepare commit", "wrap up sprint"

  Do NOT use when: starting a new sprint (use /bma-start instead), running tests (use /bma-e2e), or for non-sprint commits (just commit directly).
---

# /bma-sprint-finalize — Mandatory Sprint Outputs Generator

Goal: replace ~10K tokens of per-file generation with delegated batch write.

## Steps

1. **Gather sprint context** — run these in parallel:
   - `git status --short` and `git diff --stat HEAD` — what changed
   - `git log --oneline origin/main..HEAD` — commits since main
   - Read top entry of current `log.md` (last 50 lines only) — most recent session note
   - Read top entry of current `PATCH_SUMMARY.md` — to know what's now "Previous"

2. **Ask user for inputs** (one batched question, not many turns):
   ```
   📋 Sprint Finalize — ตอบเป็นบล็อก
   - Sprint name: <e.g., Phase I-A Schema + Project Setup>
   - Branch: <current branch>
   - Outcome: PASS / BLOCKED / DOCS-ONLY
   - One-line summary (≤120 chars):
   - Files touched (auto-detected from git, confirm/edit):
   - Tests run: smoke / full / none (with no-test rationale if docs-only)
   - Phase 1 scope check items: <list any forbidden-surface concerns or "✅ all unchanged">
   - Next sprint suggestion:
   ```

   If user already provided this in the conversation, skip the question and confirm parsed values briefly.

3. **Delegate writing** to the `bma-sprint-writer` subagent with the gathered context. Subagent receives:
   - Sprint context block (from step 1+2)
   - Explicit file list to update (the 7 mandatory)
   - Template structure rules (see subagent definition)

4. **After subagent returns**, verify with parallel reads:
   - First 30 lines of each of the 7 files contains the new sprint title or date
   - `log.md` has new session entry appended (not replacing old)
   - `PATCH_SUMMARY.md` "Latest" demoted previous to "Previous"
   - `CURRENT_STATUS.md` one-liner updated
   - `docs/status/LATEST_STATUS.md` Date stamp refreshed + new row in Latest Sprint Results table

5. **Report back** to user:
   ```
   ✅ Sprint outputs updated:
   - log.md (+N lines)
   - PATCH_SUMMARY.md (Latest = <new>, Previous = <demoted>)
   - TEST_RESULT.md (test result block + reference baseline)
   - FINAL_REPORT_FOR_CHATGPT.md (sprint outcome)
   - CURRENT_STATUS.md (one-liner)
   - docs/status/LATEST_STATUS.md (date + table row + Active Feature State if runtime changed)
   - docs/status/NEXT_ACTIONS.md (immediate-next refresh)

   ⏭ Next: commit + push? (y/N)
   ```

## Rules

- **NEVER** auto-commit. Always ask user explicitly.
- **NEVER** delete previous "Latest" entries — demote to "Previous" so 1-2 sprints of history stays in each file.
- If outcome = BLOCKED, additionally append to `docs/status/KNOWN_ISSUES.md` with rationale.
- If forbidden surfaces touched (polyAreaM2 / pdfToC / cToPdf / RS / server.py core / .bmaplan schema rename), STOP and warn user — finalize blocked until they confirm.
- If tests not run on code-touching sprint, STOP and require test run first.

## Phase 1 Scope Check (auto-include in PATCH_SUMMARY)

The subagent MUST include this block:
```
- ✅/❌ polyAreaM2 / polyMetrics / polySelfIntersects unchanged
- ✅/❌ pdfToC / cToPdf / RS / scale math unchanged
- ✅/❌ proto/server.py core endpoints unchanged
- ✅/❌ .bmaplan schema additive only (no field renames/removals)
- ✅/❌ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
```
Mark `❌` only if actually changed; default `✅`.
