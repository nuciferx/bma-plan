---
name: bma-dev-loop
description: |
  One iteration of the BMA-Plan Autonomous Dev Loop — pick the next queued sprint from PHASE_INDEX.md, scope it, build it, test it (markers + human journey), learn from findings, finalize + commit, update the roadmap. Designed to run continuously via `/loop /bma-dev-loop` until the roadmap is exhausted or a stop-condition halts it. Full-auto: commits to main without per-sprint review.

  Trigger phrases (Thai): "dev loop", "รันลูป", "ทำต่อจนจบแผน", "วิ่ง loop", "autonomous", "พัฒนาต่อเอง"
  Trigger phrases (English): "dev loop", "run the loop", "autonomous loop", "keep building until done"

  Do NOT use for: a single targeted change (do it directly), or when the user wants to review each sprint before the next (use the individual skills).
---

# /bma-dev-loop — Autonomous Dev Loop (one iteration)

Goal: drive BMA-Plan development sprint-by-sprint with no per-sprint human review, until the roadmap is done or a stop-condition fires. **One invocation = one sprint.** Run `/loop /bma-dev-loop` for continuous operation.

Roadmap source of truth: `docs/status/PHASE_INDEX.md`. Read it at step 1, write it at step 8 — every iteration.

## The 8 steps (one iteration)

1. **PLAN** — Read `PHASE_INDEX.md`. Pick the topmost `queued` sprint whose `depends-on` is satisfied. If none exists → emit `LOOP_DONE` (roadmap exhausted) and stop.

2. **SCOPE** — Run the sprint's scope skill (`/bma-ui-scope`, `/bma-measure-scope`, or `/bma-check-forbidden`).
   - `BLOCKED` → **STOP** → `LOOP_STOP_BLOCKED`, surface to user.
   - `SPLIT_REQUIRED` with an obvious split → write the sub-sprints into `PHASE_INDEX.md`, take the first, continue.
   - `SPLIT_REQUIRED` / ambiguity needing a human design choice → **STOP** → `LOOP_STOP_DESIGN`.
   - `OK` → continue.

3. **BUILD** — Implement the one sprint. Delegate symbol lookup to `bma-explorer`. Edit only `proto/ui.html` / `proto/static/*` / `proto/e2e_ui_test.py`. Add a `PHASE_<id>_OK` E2E marker for the sprint's acceptance criteria. If the build genuinely needs a forbidden surface → **STOP** → `LOOP_STOP_BLOCKED`.

4. **TEST-M (markers)** — Run `/bma-e2e` (py_compile + smoke + full). If a previously-green marker regresses: make ONE surgical retry. Still failing → **STOP** → `LOOP_STOP_REGRESSION`.

5. **TEST-H (human journey)** — Run `/bma-human-test`. `HUMAN_TEST_CRASH` → **STOP** → `LOOP_STOP_CRASH`. Otherwise its findings are already auto-triaged into `PHASE_INDEX.md`.

6. **LEARN** — Confirm step-5 discovered-backlog items were filed into `PHASE_INDEX.md`. They are now part of the roadmap — the loop will reach them. (This is how "learn → keep developing" works: problems found become future iterations.)

7. **SHIP** — Run `/bma-sprint-finalize` (7 mandatory outputs + sprint card). Full-auto: commit to `main` with a `feat:` / `fix:` message. Do NOT push (no origin remote).

8. **LOOP** — Update `PHASE_INDEX.md`: mark this sprint `✅ done <hash>`, refresh the queue. Emit `LOOP_ITERATION_DONE` with a ≤3-line summary (sprint done, test result, what's next). The `/loop` wrapper re-invokes for the next iteration.

## Stop conditions (halt, report, wait for the user)

| # | Condition | Emit |
|---|---|---|
| 1 | scope = BLOCKED, or the build needs a forbidden surface | `LOOP_STOP_BLOCKED` |
| 2 | marker regression survives one retry | `LOOP_STOP_REGRESSION` |
| 3 | `/bma-human-test` = HUMAN_TEST_CRASH | `LOOP_STOP_CRASH` |
| 4 | SPLIT / ambiguity needing a human design choice | `LOOP_STOP_DESIGN` |
| 5 | the only way forward crosses the Phase 1 scope boundary | `LOOP_STOP_SCOPE` |
| 6 | active queue + discovered backlog both empty | `LOOP_DONE` |

On any stop: write the reason + current state into the iteration report, do NOT continue. The user restarts the loop (`/loop /bma-dev-loop`) after resolving.

## Rules

- One iteration = one sprint = one commit. Never bundle sprints.
- Full-auto commits to `main` — but every commit still passes `py_compile + smoke + full` first (step 4). A failing build never commits.
- Never cross a forbidden surface to "make the sprint work" — STOP instead (`polyAreaM2` / `pdfToC` / `cToPdf` / `RS` / `snap` / `.bmaplan` rename / `server.py` core).
- Never auto-add Phase 2 scope (legal / OCR / AI / Rule Engine / FAR-OSR verdict UI) — STOP instead.
- `PHASE_INDEX.md` is the single source of truth — every iteration reads it (step 1) and writes it (step 8).
- Keep each iteration report ≤25 lines — the loop runs many times; tight reports keep the trail readable.
