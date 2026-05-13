---
name: bma-start
description: |
  Use at session start to load BMA-Plan current state efficiently. Reads only the canonical status sources (LATEST_STATUS, NEXT_ACTIONS, KNOWN_ISSUES, active sprints, git status) and returns a 1-page brief instead of forcing the user to wait while you read 5+ docs.

  Trigger phrases (Thai): "เริ่มงาน", "เริ่ม session", "สถานะตอนนี้", "ค้างอะไรอยู่", "ทำอะไรต่อ", "status", "เปิดงาน"
  Trigger phrases (English): "session start", "what's pending", "what's the state", "where did we leave off", "resume"

  Do NOT use when: user asks about a specific symbol/function (use /bma-find or bma-explorer instead), or when running tests (use /bma-e2e instead).
---

# /bma-start — Session-Start Brief

Goal: replace the 5-doc READ_ORDER ritual (~15K tokens) with one consolidated brief (~3K tokens).

## Steps

1. **Read in parallel** — these are the canonical sources, do not read others:
   - `docs/status/LATEST_STATUS.md` — current feature state
   - `docs/status/NEXT_ACTIONS.md` — what's next + blocked sprints
   - `docs/status/KNOWN_ISSUES.md` — open bugs

2. **Run in parallel with the reads:**
   - `git status --short` — uncommitted state
   - `git log --oneline -5` — recent commits
   - `ls sprints/active/` — active sprint cards

3. **Output exactly this structure** (Thai, no extra prose):

   ```
   ## 📊 BMA-Plan Status — <date from system>

   ### 🎯 Current Sprint
   <one-line from LATEST_STATUS top entry: name, date, PASS/BLOCKED/PENDING>

   ### ⏭ Recommended Next
   <one-line from NEXT_ACTIONS "Immediate Next" section>

   ### 🚧 Active Sprint Cards (sprints/active/)
   <list each file with one-line purpose, mark which is PASS / BLOCKED / PENDING per LATEST_STATUS>

   ### 🐛 Known Issues
   <bullet list from KNOWN_ISSUES, MAJOR first then MINOR>

   ### 📝 Working Tree
   <git status short — only flag if dirty>
   Branch: <current>  Recent: <last 3 commits one-line>

   ### ❓ Question
   <one specific question for the user, e.g., "start Phase I-A sprint?" or "commit pending changes first?">
   ```

4. **Do NOT** read `log.md` (50KB) unless the user explicitly asks for session history.
5. **Do NOT** read `CLAUDE.md` or `AGENTS.md` — they're auto-loaded.
6. **Do NOT** read `CURRENT_STATUS.md`, `FINAL_REPORT_FOR_CHATGPT.md`, `PATCH_SUMMARY.md` — these are derivative of LATEST_STATUS.

## Constraints

- Total output ≤ 30 lines.
- End with exactly ONE question — never multiple.
- If git status is clean, write "(clean)" — don't list nothing.
- If NEXT_ACTIONS shows "DECIDED" with no sprint card yet, the question MUST be "create sprint card for X?"
