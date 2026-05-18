---
name: bma-sprint-status
description: |
  Show which BMA-Plan sprints are active, recently completed, or recently blocked — with their current status. Drill-down to sprint state without reading 5 status docs. Use when planning what to work on next or before starting a new sprint.

  Trigger phrases (Thai): "sprints ค้าง", "active sprints", "sprint ไหนเหลือ", "sprint status", "งานไหนค้าง"
  Trigger phrases (English): "what sprints are active", "sprint status", "what's left to do in sprints"

  Do NOT use when: user wants overall project state (use /bma-start instead — it includes sprint summary).
---

# /bma-sprint-status — Sprint State Drill-Down

Goal: focused view on sprint queue. Lighter than `/bma-start` (no full project state).

## Steps

1. **Run in parallel:**
   - `ls sprints/active/` — current cards
   - `ls -t sprints/completed/ | head -5` — 5 most recent done
   - `ls -t sprints/archive/ | head -3` — 3 most recent blocked/superseded
   - For each active card: `grep -E "^(Sprint Name|Status|Outcome|Result):" <card>` — extract sprint identity

2. **Output format:**

   ```
   ## 🚧 Active Sprints (sprints/active/)
   <list each card with: name, status from grep, file path>
   <or "(empty — ready for new sprint)" if folder empty>

   ## ✅ Recently Completed (last 5)
   <date — folder name — one-line if available from RUN_*.md>

   ## ⛔ Recently Archived/Blocked (last 3)
   <date — folder name — reason if BLOCKED>

   ## 🎯 Suggested Next
   <if active empty AND NEXT_ACTIONS has DECIDED-but-no-card → suggest that sprint>
   <else → "use /bma-start to see overall state">
   ```

3. **Constraints:**
   - Output ≤25 lines.
   - Don't read entire sprint cards — just the identity lines (first 15 lines).
   - Don't read `NEXT_ACTIONS.md` unless suggesting next sprint and no active cards exist.
