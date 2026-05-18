---
name: bma-invent
description: |
  One-shot invention pass on a single BMA-Plan idea — runs the 7-phase pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT) once and stops at the human checkpoint. Use when you want to deliberately develop a novel method from an idea in IDEAS.md or PHASE_INDEX backlog WITHOUT looping into the next idea. For continuous operation across the whole idea backlog, use `/bma-invent-loop` instead.

  Trigger phrases (Thai): "/bma-invent", "ลองคิดวิธีใหม่", "วิจัย + ออกแบบ", "invent", "ประดิษฐ์"
  Trigger phrases (English): "/bma-invent", "invent on idea", "research and design", "explore approaches"

  Do NOT use for: capturing a fresh idea (use `/idea`), routine sprint work (use `/bma-dev-loop`), or fixing a known bug (just file a sprint card directly).
---

# /bma-invent — One-shot invention pipeline (single idea)

Goal: take one raw idea and walk it from `invent-queued` to either `invent-done-go` (with a real sprint card) or `invent-done-nogo` (with a closed rationale). Output artifact = `docs/invent/<short-name>.md`. Halts at the human checkpoint — only the human decides GO / NOGO / RESHAPE.

This is the manual single-shot version. `/bma-invent-loop` chains it.

## Inputs

- Args: `idea_id` (timestamp from `IDEAS.md` like `2026-05-15-17-59`, OR a `PHASE_INDEX` backlog id like `ideas-2026-05-15-arc-polygon`). If empty: list invent-queued candidates and ask which one.

## The 7 phases

### 1. PICK

- Resolve the idea from `~/.claude/ideas/IDEAS.md` and/or `docs/status/PHASE_INDEX.md` Discovered backlog. Collect: summary, raw idea, refinements, tags, related PHASE_INDEX entries.
- If status is already `invent-in-progress` for someone, ABORT — only one invent pass per idea at a time.
- Decide short-name (kebab case, ≤6 words) — this is the artifact stem `docs/invent/<short-name>.md`.
- Create `docs/invent/<short-name>.md` with sections: Frame, Research, Diverge, Score, Recommendation, Spike, Decision (stubbed).
- Flip the IDEAS.md entry's `Status:` to `invent-in-progress`.
- Flip the PHASE_INDEX backlog entry status to `invent-in-progress`.

### 2. RESEARCH (delegate to `bma-researcher`)

- Hand the agent: `idea_id`, `idea_summary`, `idea_body`, `tags`.
- Receive the 5-section research block + verdict (`PRIOR_ART_MATURE` / `PRIOR_ART_PARTIAL` / `GREENFIELD`).
- Paste verbatim into `docs/invent/<short-name>.md` under `## Research`.
- **If verdict = `PRIOR_ART_MATURE`** → SKIP phases 3-6. Go directly to phase 7 CHECKPOINT with a "use prior art" recommendation: write a normal sprint card that adopts the existing solution. This is a WIN exit, not a failure.

### 3. FRAME

- Write `## Frame` section ≤1 page covering:
  - **Problem** — the concrete user pain in 2 sentences
  - **Constraints** — must work on raster PDFs / Phase 1 boundary / page-scoped layers / additive `.bmaplan` schema
  - **Forbidden surfaces this idea must avoid** — explicit list (`polyAreaM2` / `pdfToC` / `RS` / etc.)
  - **Success criteria** — how we'd know in spike if it works (concrete metric)
  - **Out of scope** — what we're explicitly NOT solving in this invention pass

### 4. DIVERGE (delegate to `bma-inventor`)

- Hand the agent: `idea_id`, `frame` (the section just written), `research_report`, `target_approach_count=5`.
- Receive `## Diverge` block (3-5 approaches, each on a different axis) + `## Score` block + `## Recommendation` line.
- Paste verbatim.
- **If agent returns `INVENT_DESIGN_AMBIGUOUS`** → RESHAPE: edit `## Frame` to be sharper (usually narrower problem statement), then re-delegate. Allow 1 retry. Still ambiguous → emit `INVENT_DESIGN_AMBIGUOUS` and halt for human.

### 5. SCORE (covered inside phase 4 output)

The inventor already produced the 6-dim score table. The skill's job here is just to verify:
- No approach with `forbidden_surface_touch: YES` ranks first
- No approach crossing Phase 1 boundary ranks first
- If the top approach violates either, re-rank and note the override

### 6. SPIKE

- Create `proto/sandbox/invent-<short-name>.html` — a standalone HTML page (or `.js` module loaded by one) that prototypes the top-ranked approach.
- **Strict isolation:**
  - Never edit `proto/ui.html`, `proto/server.py`, `proto/static/js/*`, `proto/static/css/app.css`.
  - The sandbox file must run by opening it directly in a browser — no server, no build step.
  - May copy small helper functions from `proto/ui.html` but must not import the live file.
- Spike acceptance = the `success_criteria` from `## Frame` are demonstrably met when the sandbox HTML is opened.
- Record results under `## Spike`:
  - Approach attempted (A / B / C)
  - Outcome (pass / fail) + ≤5 line rationale
  - Screenshots optional in `artifacts/invent/<short-name>/`
- **If the first approach fails** → spike approach #2 (the fallback from the inventor's recommendation). If that fails → spike approach #3. **3 failed spikes → STOP** with `LOOP_STOP_INVENT_DEAD_END`.

### 7. CHECKPOINT (human decides)

Print a ≤15-line summary to the user:
```
🧪 Invent pass complete: <short-name>
Research verdict: <MATURE / PARTIAL / GREENFIELD>
Approaches generated: <count>
Top approach: <name>
Spike outcome: <pass / fail-then-recovered-with-X / dead-end>

Doc: docs/invent/<short-name>.md
Sandbox: proto/sandbox/invent-<short-name>.html

Decide:
  GO     — promote to a real sprint card (I will write it into PHASE_INDEX)
  NOGO   — close this idea with rationale (I will record why)
  RESHAPE — frame is wrong; go back to phase 3 with new framing
```

Ask the user. **Do not pick automatically.**

### 8. Apply decision

- **GO** → write a full sprint card into `docs/status/PHASE_INDEX.md` (status `queued`, ready for `/bma-dev-loop`). Card must include: title, sprint id (`INV-YYYY-MM-DD-NNN`), depends-on, scope skill to use (`/bma-measure-scope` etc.), success markers needed, links back to `docs/invent/<short-name>.md`. Update the backlog entry status to `invent-done-go (→ INV-YYYY-MM-DD-NNN)`. Update IDEAS.md entry's `Status:` to `invent-done-go`.
- **NOGO** → append `## Decision` to `docs/invent/<short-name>.md` with the reason. Update both backlog statuses to `invent-done-nogo`. The artifact stays for future reference.
- **RESHAPE** → reset phases 3-6 in the artifact (mark as "v2 attempt"), keep phases 1-2 (research is still valid). User specifies the new framing; restart at phase 3.

### 9. Commit

Commit only these paths (never `proto/ui.html` / `proto/server.py` / static assets):
- `docs/invent/<short-name>.md`
- `proto/sandbox/invent-<short-name>.html` (and any related `.js`/`.css`)
- `docs/status/PHASE_INDEX.md`
- `~/.claude/ideas/IDEAS.md` (status flip) — this is outside the repo; skip in git
- `artifacts/invent/<short-name>/` (gitignored — do not commit)

Commit message: `invent(<short-name>): <verdict> — <one-line takeaway>` e.g. `invent(arc-polygon): GO — AutoCAD bulge per edge, spike passed`.

## Stop conditions (this skill, single-shot)

| # | Condition | Emit |
|---|---|---|
| 1 | Research verdict = MATURE → recommend adopt prior art (this is a WIN exit) | `INVENT_DONE_PRIOR_ART` |
| 2 | Inventor cannot reach 3 distinct approaches after 1 RESHAPE retry | `INVENT_DESIGN_AMBIGUOUS` |
| 3 | Every approach requires a forbidden-surface edit | `INVENT_FORBIDDEN_REQUIRED` |
| 4 | Idea crosses Phase 1 boundary (legal / OCR / AI / FAR-OSR verdict) | `INVENT_PHASE1_BOUNDARY` (auto-NOGO) |
| 5 | 3 spike attempts fail | `LOOP_STOP_INVENT_DEAD_END` |
| 6 | Successful spike → human checkpoint reached | `INVENT_AT_CHECKPOINT` |

## Hard rules

- **No code in `proto/ui.html` / `proto/server.py` during invention.** Spike lives in `proto/sandbox/` only. The whole point is to test ideas without destabilizing the app.
- **Schema-additive only** — any data-model change proposed must be backward-compatible with v1 `.bmaplan` files.
- **Human decides GO/NOGO/RESHAPE — never the skill.** This is the explicit boundary from `/bma-dev-loop` (which IS full-auto): invention requires human risk-taking.
- **Research-first is non-negotiable.** Even if the user is sure the idea is novel, run phase 2 — it's cheap (haiku) and often reveals a library that saves a sprint.
- **Output budget:** ≤25 lines to the user per phase update; the artifact `docs/invent/<short-name>.md` holds the detail.
