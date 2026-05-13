---
name: bma-log-add
description: |
  Append a single new entry to log.md without reading or rewriting the whole 50KB file. Use for mid-sprint decision notes, "we decided X today", quick observations — anything that's not a full sprint outcome. For sprint outcomes use /bma-sprint-finalize instead.

  Trigger phrases (Thai): "log ไว้", "บันทึก", "จด log", "log this", "เพิ่ม log"
  Trigger phrases (English): "log this", "add to log", "note this", "record this"

  Do NOT use when: finishing a sprint (use /bma-sprint-finalize — it does log.md plus 6 others).
---

# /bma-log-add — Append Single Log Entry

Goal: avoid reading + rewriting log.md (50KB) when all that's needed is a 5-line entry.

## Steps

1. **Ask user for entry** (one batched question, only if not provided):
   ```
   📝 Log entry — ตอบเป็นบรรทัด
   - Title (≤80 chars):
   - Type: decision / observation / blocker / note
   - Why / context (1-2 sentences):
   - Files touched (if any):
   ```

2. **Read only the first 30 lines** of `log.md` to find where to insert (above the most recent entry, below the header).

3. **Use Edit** (not Write) with the smallest possible `old_string` — typically the first heading or first `---` divider — to insert the new entry above.

4. **Entry format:**
   ```markdown
   ## <YYYY-MM-DD> — <Title> — [<type>]

   <why/context paragraph>

   **Files touched:** <list, or "none">

   ---
   ```

5. **Report back** to user (≤3 lines):
   ```
   ✅ log.md +<N> lines
   Top: ## <date> — <title>
   ```

## Constraints

- **Never** read more than 30 lines of `log.md` (it's 50KB+).
- **Never** Write the whole file. Always Edit with minimal `old_string`.
- **Never** commit — log.md entries are not standalone commits, they batch with sprint work.
- If log.md has >5 entries at top before the archive divider, suggest archiving the oldest 2-3 to `docs/archive/log-<YYYY-MM>.md` — but ask the user first.
