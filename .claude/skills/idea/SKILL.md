---
name: idea
description: |
  Capture a fresh raw idea for BMA-Plan and queue it for the invention pipeline. Appends a verbatim entry to `~/.claude/ideas/IDEAS.md` (user-level, outside the repo) with `Status: invent-queued`, then mirrors a short backlog row into `docs/status/PHASE_INDEX.md` under the `## Discovered backlog` → `### ideas YYYY-MM-DD` sub-block so `/bma-invent` / `/bma-invent-loop` can pick it up later. Does NOT run research, diverge, score, or spike — that is `/bma-invent`'s job. Always halts after capture; the human decides when to invent.

  Trigger phrases (Thai): "/idea", "ไอเดีย", "บันทึกไอเดีย", "เก็บไอเดียไว้", "เพิ่มไอเดีย", "idea this", "queue idea"
  Trigger phrases (English): "/idea", "capture idea", "save this idea", "queue for invent", "new idea"

  Do NOT use for: developing the idea (use `/bma-invent`), filing a known bug (file a sprint card in PHASE_INDEX active queue directly), or routine sprint work (use `/bma-dev-loop`).
---

# /idea — Capture-only skill (raw idea → invent-queued)

Goal: take whatever the user just said and store it as a future-invent candidate without any analysis. The hard rule is **no synthesis** — the body must be the user's verbatim words. Refinement, framing, research, scoring happen in `/bma-invent`.

This skill is intentionally tiny. If you find yourself writing more than ~25 lines of user-visible output, you are overstepping.

## Inputs

- `idea_body` — free text, Thai or English. Whatever the user wrote after `/idea`. If empty, ask one short question: "เก็บไอเดียอะไรครับ?" and wait. Never invent the body.
- (optional) `tags` — comma-separated. If absent, infer 2-4 tags from the body keywords (`measure`, `ui`, `export`, `annotation`, `snap`, `layer`, `geometry`, `perf`, `docs`, etc.) PLUS one priority tag (`p-low` / `p-med` / `p-high`). Default priority is `p-med`. Always include `bma-plan` as the first tag.
- (optional) `short_title` — kebab-case, ≤6 words. If absent, derive from the first sentence of the body. This becomes the artifact stem if `/bma-invent` later picks it up.

## Steps

### 1. Build idea_id

`idea_id = YYYY-MM-DD-HH-MM` from current local time (e.g. `2026-05-18-17-30`).

Use the system date directly — don't ask the user. If the same minute already has an entry (rare), append `-2`, `-3`, etc.

### 2. Append to `~/.claude/ideas/IDEAS.md` (user-level, NOT in repo)

Path: `C:\Users\nucifer\.claude\ideas\IDEAS.md` on this machine (`~/.claude/ideas/IDEAS.md` POSIX).

If the file does not exist, create it with this header:
```markdown
# BMA-Plan raw idea log

Captured by `/idea`. Promoted to the 7-phase pipeline by `/bma-invent`.
One entry per idea. **Body is verbatim — never synthesize.**

Status values: `invent-queued` → `invent-in-progress` → `invent-done-go` | `invent-done-nogo`

---
```

If the dir `C:\Users\nucifer\.claude\ideas\` does not exist, create it.

Append this block at the bottom:
```markdown
## {{idea_id}} — {{short_title}}

- **id**: `{{idea_id}}`
- **Status**: invent-queued
- **Tags**: {{tag1}}, {{tag2}}, ..., {{p-low|p-med|p-high}}
- **Source**: user typed via /idea on {{YYYY-MM-DD}}
- **Body** (verbatim):
  > {{idea_body — preserve newlines, language, punctuation, even typos}}
- **Refinements**: (none yet — `/bma-invent` adds these during Phase 1 PICK)

---
```

### 3. Mirror to `docs/status/PHASE_INDEX.md` Discovered backlog

Find the `## Discovered backlog` section. Look for a sub-heading `### ideas {{YYYY-MM-DD}}` for today's date.

- **If today's sub-heading exists** — append the bullet under it (right before the next `###` or `##` boundary).
- **If today's sub-heading does NOT exist** — insert a new `### ideas {{YYYY-MM-DD}}` sub-block AFTER any existing `### ideas <older-date>` block, before `## Known leftovers` (or whichever section follows Discovered backlog).

The bullet uses the same format as existing entries (see `### ideas 2026-05-17` in PHASE_INDEX):

```markdown
- [ ] **{{Title sentence-case from short_title}}** — `invent-queued` — from /idea {{YYYY-MM-DD}} ({{1-line context, e.g. "user typed after testing X"}})
    - Source: user {{YYYY-MM-DD}}, "{{verbatim quote ≤120 chars; full body lives in IDEAS.md}}"
    - Tags: {{same tag list as IDEAS.md}}
    - Direction: (unframed — pending /bma-invent FRAME phase)
    - Open questions: (pending /bma-invent)
    - Scope skill: pending (`/bma-invent` decides after research)
    - Forbidden-surface profile: unknown — `/bma-invent` checks during RESEARCH
```

Do NOT pretend to know the direction, scope skill, or forbidden-surface profile at capture time. Those fields are placeholders that `/bma-invent` fills.

### 4. Print confirmation (≤8 lines, Thai)

```
💡 เก็บไอเดียแล้ว: {{short_title}}
id: {{idea_id}}
status: invent-queued
tags: {{tags}}

→ IDEAS.md (user-level): {{idea_id}}
→ PHASE_INDEX.md: ## Discovered backlog → ### ideas {{YYYY-MM-DD}}

รัน `/bma-invent {{idea_id}}` เมื่ออยากเริ่ม 7-phase pipeline
```

Stop. **Do not start `/bma-invent`.** Capture is the entire contract.

## Hard rules

- **Verbatim body, no synthesis.** If the body is unclear, capture it unclear. The whole point is to record what the user actually said before invention re-frames it. Re-framing happens in `/bma-invent` FRAME phase.
- **Two stores, both updated.** User-level `IDEAS.md` holds the raw body; repo `PHASE_INDEX.md` holds the short backlog row for visibility in the dev loop. Skipping the PHASE_INDEX mirror means the idea is invisible to `/bma-invent-loop` (which reads from PHASE_INDEX).
- **No commit from this skill.** Only `docs/status/PHASE_INDEX.md` would change in-repo — let the user commit it with the next sprint or via their own habit. `~/.claude/ideas/IDEAS.md` is outside the repo entirely.
- **No git operations.** Do not stage, commit, or push.
- **No status changes to existing entries.** This skill only ever appends. If the user wants to flip status (`invent-done-nogo` etc.), they edit by hand or use the relevant invent skill.
- **One idea per `/idea` invocation.** If the user dumps three ideas in one message, ask which to capture first — do not batch-create silently.

## Files touched

| Path | Action |
|---|---|
| `C:\Users\nucifer\.claude\ideas\IDEAS.md` | append (create if missing) — user-level, NOT in repo |
| `docs/status/PHASE_INDEX.md` | append one bullet under `### ideas YYYY-MM-DD` (create sub-heading if missing) |

## What this skill does NOT do

- Does not run `bma-researcher` (that is `/bma-invent` Phase 2)
- Does not write `docs/invent/<short-name>.md` (that is `/bma-invent` Phase 1)
- Does not create `proto/sandbox/invent-*.html` (that is `/bma-invent` Phase 6)
- Does not score or rank ideas (that is `/bma-inventor` inside `/bma-invent`)
- Does not flip any status — capture only

## Stop conditions

| # | Condition | Emit |
|---|---|---|
| 1 | Capture complete | `IDEA_CAPTURED` |
| 2 | Body is empty after asking once | `IDEA_BODY_MISSING` (halt, don't fabricate) |
| 3 | Same minute already has 9+ entries with `-2`..`-9` suffix | `IDEA_ID_EXHAUSTED` (wait a minute, ask user to retry) |
