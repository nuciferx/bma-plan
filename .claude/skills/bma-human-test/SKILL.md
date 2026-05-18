---
name: bma-human-test
description: |
  Run a realistic full-workflow "human journey" test of BMA-Plan and triage the findings into the roadmap. Delegates the actual Playwright journey to the bma-human-journey-tester subagent (sonnet), then files each issue into docs/status/PHASE_INDEX.md "Discovered backlog" by severity. Returns HUMAN_TEST_PASS / HUMAN_TEST_ISSUES / HUMAN_TEST_CRASH.

  Trigger phrases (Thai): "เทสเหมือนคน", "human test", "ทดสอบแบบผู้ใช้", "เดิน journey", "ลองใช้จริง"
  Trigger phrases (English): "human test", "real user test", "journey test", "what would a user hit"

  Do NOT use for: marker pass/fail only (use /bma-e2e), or fixing the issues it finds (those become their own sprints).
---

# /bma-human-test — Realistic User Journey Test + Triage

Goal: see the problems a real person hits — then turn them into roadmap items so the dev loop fixes them. This is the loop's "see problems" mechanism; `/bma-e2e` proves functions work, this proves a human can finish the job.

## Steps

1. **Delegate to the `bma-human-journey-tester` subagent.** It opens the real 45-page permit PDF and runs the full workflow — open → set scale → page setup → **measure EVERY page** → openings/markers → review → export XLSX → save → reopen → verify the round-trip — and returns a Human Journey Report with issues categorized CRASH / BROKEN / FRICTION / COSMETIC.

2. **Triage findings into `docs/status/PHASE_INDEX.md` → "Discovered backlog":**
   - **CRASH / BROKEN** → add as a sprint near the TOP of the Active sprint queue (high priority — blocks confidence in the app)
   - **FRICTION** → add as a normal sprint at the END of the active queue
   - **COSMETIC** → add to the Discovered backlog section, low priority
   - Each entry: short id, one-line description, suggested scope skill, severity, source = `human-test <date>`
   - **De-dup:** if an issue is already in the backlog, do not add it twice — note the recurrence instead.

3. **Return the verdict:**
   - `HUMAN_TEST_PASS` — no CRASH/BROKEN; any FRICTION/COSMETIC was triaged, not blocking
   - `HUMAN_TEST_ISSUES` — BROKEN issues found and triaged into the queue
   - `HUMAN_TEST_CRASH` — a CRASH-level blocker → this is a loop stop-condition; surface to the user immediately

## Output

```
### Human Test — <date>

Verdict: 🟢 HUMAN_TEST_PASS / 🟡 HUMAN_TEST_ISSUES / 🔴 HUMAN_TEST_CRASH

Journey: <N/N steps OK>   ·   Marker baseline: full <N/N>

#### Issues triaged into PHASE_INDEX.md
| severity | issue | filed as |
|---|---|---|
| BROKEN | ... | sprint <id> (top of queue) |
| FRICTION | ... | sprint <id> (queue end) |

#### Already known (not re-filed)
- ...

<if HUMAN_TEST_CRASH>⛔ STOP — <the crash> — the loop must halt; needs a human decision.
```

## Rules

- Never edit `proto/` — this skill observes + triages only. Fixes happen in their own sprints.
- Always write triaged issues to `PHASE_INDEX.md` — an issue not filed is an issue lost.
- Output ≤30 lines.
- If the `bma-human-journey-tester` subagent is not yet available (e.g. before a session restart picks it up), say so and fall back to `/bma-e2e full` as a partial proxy — but note that the every-page coverage and friction observation are then missing.
