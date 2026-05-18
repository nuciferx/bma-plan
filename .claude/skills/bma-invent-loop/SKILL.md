---
name: bma-invent-loop
description: |
  One iteration of the BMA-Plan Autonomous Invention Loop — picks the next `invent-queued` idea from PHASE_INDEX.md / IDEAS.md, runs the 7-phase invention pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT), and halts at the human checkpoint so the user can decide GO / NOGO / RESHAPE. After the user decides, the loop continues to the next idea. Designed to run via `/loop /bma-invent-loop` until the invent backlog is exhausted. Feeds the regular `/bma-dev-loop` by promoting vetted ideas to sprint cards.

  Trigger phrases (Thai): "invent loop", "วิ่งลูปคิดวิธีใหม่", "loop ประดิษฐ์", "วิจัย-ประดิษฐ์-loop"
  Trigger phrases (English): "invent loop", "run the invent loop", "research-invent-loop"

  Do NOT use for: one-off invention on a single idea (use `/bma-invent`), routine dev work (use `/bma-dev-loop`), or capturing new ideas (use `/idea`).
---

# /bma-invent-loop — Autonomous Invention Loop (one iteration)

Goal: drive BMA-Plan invention idea-by-idea, **with a mandatory human checkpoint per idea**, until the invent backlog is exhausted. **One invocation = one idea taken to checkpoint.** Run `/loop /bma-invent-loop` for continuous operation across many ideas.

Source of truth for the queue: `docs/status/PHASE_INDEX.md` Discovered backlog (entries with status `invent-queued`) + `~/.claude/ideas/IDEAS.md` (entries with `Status: open` AND `tags` containing `experiment` OR `p-high` OR a measurement-math tag).

This loop is the upstream of `/bma-dev-loop`:

```
IDEAS.md ─┐
          ↓
[/bma-invent-loop] ──→ PHASE_INDEX (invent-done-go) ──→ [/bma-dev-loop] ──→ shipped
          ↑                          │
          └───── invent-done-nogo ───┘   (closed, kept for reference)
```

## The 9 steps (one iteration)

1. **PICK** — Read `PHASE_INDEX.md` Discovered backlog + `IDEAS.md`. Pick the topmost `invent-queued` idea (priority: `p-high` > `experiment` tag > oldest first). If none exists → emit `INVENT_LOOP_DONE` and stop. Flip status to `invent-in-progress`.

2. **RESEARCH** — Delegate to `bma-researcher`. Paste output into `docs/invent/<short-name>.md` § Research. If verdict = `PRIOR_ART_MATURE` → SKIP to step 7 with "adopt prior art" recommendation (a WIN exit, not a failure).

3. **FRAME** — Write `## Frame` (problem / constraints / forbidden surfaces / success criteria / out-of-scope). ≤1 page.

4. **DIVERGE** — Delegate to `bma-inventor` with the frame + research. Receive `## Diverge` + `## Score` + `## Recommendation`. If agent returns `INVENT_DESIGN_AMBIGUOUS` → re-sharpen `## Frame` ONCE, re-delegate. Still ambiguous → STOP with `INVENT_DESIGN_AMBIGUOUS`.

5. **SCORE-VERIFY** — Sanity-check the inventor's ranking:
   - Top approach must not require a forbidden-surface edit
   - Top approach must not cross Phase 1 boundary
   - If either is violated, re-rank to the next safe approach and note the override in `## Score`.

6. **SPIKE** — Build `proto/sandbox/invent-<short-name>.html` standalone. Try the top approach. If fail, try the fallback approach. If fail, try the third approach. **3 fails → STOP with `LOOP_STOP_INVENT_DEAD_END`.** Record outcome in `## Spike`.

7. **CHECKPOINT** — **HALT here.** Print the ≤15-line summary (artifact path, sandbox path, verdict so far) and ask the user: `GO` / `NOGO` / `RESHAPE`. The loop does not proceed until the user answers.

   - **GO** → write a full sprint card into `PHASE_INDEX.md` with status `queued` (ready for `/bma-dev-loop`). Sprint id = `INV-YYYY-MM-DD-NNN`. Update backlog entry to `invent-done-go (→ INV-...)`. Update `IDEAS.md` entry's `Status:` to `invent-done-go`.
   - **NOGO** → append `## Decision (NOGO)` with rationale. Update backlog + IDEAS.md to `invent-done-nogo`.
   - **RESHAPE** → restart at step 3 with new framing from the user. Mark the prior frame in the artifact as `(v1, reshaped)`.

8. **COMMIT** — One commit, message: `invent(<short-name>): <GO|NOGO|PRIOR_ART> — <takeaway>`. Paths allowed in this commit:
   - `docs/invent/<short-name>.md`
   - `proto/sandbox/invent-<short-name>.html` and any sibling assets
   - `docs/status/PHASE_INDEX.md`

   Paths forbidden in this commit (will fail the safety check): `proto/ui.html`, `proto/server.py`, `proto/static/js/*`, `proto/static/css/app.css`, `proto/e2e_ui_test.py`, `.bmaplan` schema files. Invention never touches the live app — that's `/bma-dev-loop`'s job.

9. **LOOP** — Emit `INVENT_LOOP_ITERATION_DONE` with a ≤3-line summary (idea done, decision, what's next from the queue). The `/loop` wrapper re-invokes for the next idea.

## Stop conditions (halt, report, wait for the user)

| # | Condition | Emit |
|---|---|---|
| 1 | Invent backlog + IDEAS.md candidates both empty | `INVENT_LOOP_DONE` |
| 2 | Inventor cannot produce ≥3 distinct approaches after 1 RESHAPE retry | `INVENT_DESIGN_AMBIGUOUS` |
| 3 | Every approach requires editing a forbidden surface | `INVENT_FORBIDDEN_REQUIRED` |
| 4 | Idea crosses Phase 1 boundary (legal / OCR / AI / FAR-OSR verdict) — auto-flip to NOGO and continue loop | (no halt; loop continues) |
| 5 | 3 spike attempts all fail | `LOOP_STOP_INVENT_DEAD_END` |
| 6 | Budget: one idea > 3 reshape rounds | `LOOP_STOP_INVENT_BUDGET` |
| 7 | Reached human checkpoint successfully | `INVENT_AT_CHECKPOINT` (always — by design) |

Stop conditions 1, 2, 3, 5, 6 require the user to investigate before restarting `/loop /bma-invent-loop`. Stop condition 7 is the normal end-of-iteration: the user answers GO/NOGO/RESHAPE then the loop continues automatically on next firing.

## Rules

- **One iteration = one idea = one commit at checkpoint resolution.** Never bundle ideas.
- **Human always decides GO/NOGO/RESHAPE.** This is the explicit difference from `/bma-dev-loop` (which is full-auto). Invention requires human risk-taking — the loop never auto-promotes a spike to a sprint card.
- **Never touch the live app during invention.** Spike lives in `proto/sandbox/`, full stop. The pre-commit path check enforces this.
- **Never auto-add Phase 2 scope.** If an idea inherently requires AI/OCR/legal verdict, auto-NOGO it (stop condition 4) — the loop logs the rejection and moves on.
- **Schema is additive only.** Any data-model change proposed in an approach must be backward-compatible with v1 `.bmaplan`.
- **Research-first is non-negotiable.** Even if the user marked the idea "experiment / novel", step 2 still runs — it's haiku-cheap and often saves a whole sprint by finding a viable library.
- **The dev loop reads only `invent-done-go` items.** Raw `invent-queued` items are NOT eligible for `/bma-dev-loop` — they must pass through this loop first.

## Output budget per iteration

≤30 lines user-facing per iteration. The detail lives in `docs/invent/<short-name>.md`. The user should be able to read every iteration's report in under 30 seconds and decide GO/NOGO/RESHAPE without re-deriving context.
