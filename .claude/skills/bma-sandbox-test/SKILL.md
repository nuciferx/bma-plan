---
name: bma-sandbox-test
description: |
  Pre-release gate. Run every PDF in `sandbox/` through BMA-Plan to surface issues that ONLY real customer files expose (huge size, weird page count, unusual rotation, vendor quirks). Delegates per-file journey to `bma-sandbox-journey-tester` (sonnet) and category-triage to `bma-issue-triager` (sonnet). Triaged findings — including proposals for NEW specialist skills/subagents — are filed into `docs/status/PHASE_INDEX.md` so the dev loop picks them up. Returns SANDBOX_TEST_PASS / SANDBOX_TEST_ISSUES / SANDBOX_TEST_CRASH.

  Trigger phrases (Thai): "sandbox test", "ทดสอบ sandbox", "เทสไฟล์จริง", "ไฟล์ลูกค้าจริง", "ก่อนปล่อยรุ่น", "pre-release"
  Trigger phrases (English): "sandbox test", "real-pdf test", "pre-release check", "customer-pdf test"

  Do NOT use for: synthetic marker test (use /bma-e2e), fixing the issues it finds (those become their own sprints), or testing one specific PDF outside `sandbox/` (point the journey-tester at it directly).
---

# /bma-sandbox-test — Real-PDF Pre-Release Gate + Triage

Goal: catch problems that *only* real customer PDFs expose, BEFORE a release goes out. Each unique failure category becomes a queued sprint in `PHASE_INDEX.md` — possibly with a proposed new specialist skill/subagent if no existing one covers it. `/bma-e2e` proves functions work on test fixtures; this proves the app survives real-world inputs.

## Sandbox location

`F:/My Drive/01 project/ai/bma-plan/sandbox/` — drop real customer / problematic PDFs here. Files persist; this skill is read-only on `sandbox/`.

## Steps

1. **Enumerate** — list every `*.pdf` in `sandbox/`. If empty → emit `SANDBOX_EMPTY` and stop.

2. **Per-file journey (delegate to `bma-sandbox-journey-tester`)** — for each PDF, the subagent runs:
   - **Tier 1 (always):** start uvicorn, upload PDF, render every page, watch for HTTP error / timeout / `malloc failed` / blank-page / wrong-rotation. Records failures and continues to the next PDF.
   - **Tier 2 (only if Tier 1 PASS for that PDF):** set scale (manual stub) → draw one test polygon on page 1 → export XLSX → save `.bmaplan` → reopen → verify object count round-trips.
   - Output per PDF: severity-tagged findings (CRASH / BROKEN / FRICTION / COSMETIC) + per-file log in `artifacts/sandbox-tests/<pdf-stem>/journey.md`.
   - **Read-only on `proto/`.** Subagent never edits app code.

3. **Triage (delegate to `bma-issue-triager`)** — pass the union of findings. Triager:
   - Buckets findings into unique categories (e.g. "large-PDF render OOM", "rotation=90 + multi-page", "embedded XFA form").
   - For each category, checks existing `.claude/skills/` + `.claude/agents/` for coverage.
   - If covered → recommends "extend X" with the specific case.
   - If not covered → drafts a **new-skill / new-subagent spec** (name, model, trigger phrases, input/output contract, scope boundary).
   - Returns a structured proposal block ready to paste into `PHASE_INDEX.md`.

4. **File sprints into `PHASE_INDEX.md`** — under the existing **"Discovered backlog"** section, append a new dated sub-block `### sandbox YYYY-MM-DD`. One row per unique category:
   - **CRASH / BROKEN** → also insert near the TOP of the active queue (high priority) with id `SB-YYYY-MM-DD-NNN`
   - **FRICTION** → end of active queue
   - **COSMETIC** → stays in the Discovered backlog only
   - Each entry: id, one-line description, source PDF(s), severity, suggested scope skill, AND — if applicable — a "new-specialist proposal:" line linking to the triager's spec block at the bottom of the discovered-backlog section.
   - **De-dup:** if a category already exists in `PHASE_INDEX.md` (active queue or backlog), do not file again — append the new source PDF to the existing entry's "found in:" list.

5. **Return the verdict:**
   - `SANDBOX_TEST_PASS` — every PDF cleared Tier 1+2. No new sprints needed.
   - `SANDBOX_TEST_ISSUES` — BROKEN/FRICTION/COSMETIC filed; no CRASH.
   - `SANDBOX_TEST_CRASH` — at least one PDF caused a CRASH → loop stop-condition; surface to the user immediately.

## Output (≤30 lines)

```
### Sandbox Test — <date>

Verdict: 🟢 SANDBOX_TEST_PASS / 🟡 SANDBOX_TEST_ISSUES / 🔴 SANDBOX_TEST_CRASH

Files tested: N (<list ≤3 filenames>)
Tier 1 (open+render): M/N pass   ·   Tier 2 (journey): K/M pass

#### Categories filed
| id | severity | category | source PDF(s) | proposed specialist? |
|---|---|---|---|---|
| SB-2026-05-15-001 | BROKEN | large-PDF render OOM | 251121_CHH_... | new: bma-large-pdf-debugger (sonnet) |
| ... |

#### De-dup (already filed earlier)
- <existing id> — added source: <pdf>

#### CRASH details (if any)
<one-line per CRASH, the rest in artifacts/>

<if SANDBOX_TEST_CRASH>⛔ STOP — the dev loop must halt and a human must decide.
```

## Rules

- **Propose-first, never auto-create.** This skill writes specs for new skills/subagents into `PHASE_INDEX.md`, it does NOT create `.claude/skills/<new>/SKILL.md` or `.claude/agents/<new>.md` files. Creating those is a separate sprint that `/bma-dev-loop` picks up, so each new specialist gets normal sprint discipline (scope + tests + commit).
- **Read-only on `proto/` and `sandbox/`.** Findings → docs only.
- Temp artifacts go in `artifacts/sandbox-tests/` (gitignored). Never commit per-file logs.
- Every filed sprint must include the source PDF filename so the fix can be reproduced.
- Output ≤30 lines. Detailed per-file logs live in `artifacts/`, not in chat.
- **Pre-release gate:** before any user-visible release (PyInstaller build, demo to stakeholder, customer hand-off) `/bma-sandbox-test` should return `SANDBOX_TEST_PASS` or `SANDBOX_TEST_ISSUES` with all CRASH-level items resolved.
- If `sandbox/` is missing (e.g. fresh clone) → emit `SANDBOX_MISSING`, do not error.
