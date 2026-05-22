---
name: bma-bug-report
description: |
  Bug report intake → full-auto fix pipeline for BMA-Plan. Captures a bug (free-text from user OR structured finding from /bma-human-test / /bma-sandbox-test), delegates triage to the bma-bug-triager subagent, then orchestrates the correct scope/specialist/regression skills to diagnose, patch, test, finalize, and commit the fix to main. Full-auto by default; halts only on a stop-condition (forbidden surface / regression survives retry / CRASH / design ambiguity / Phase 2 scope). Always files the bug into PHASE_INDEX.md as a tracked sprint, even if it stops early.

  Trigger phrases (Thai): "/bma-bug-report", "แจ้งบั๊ก", "รายงานบั๊ก", "บั๊กนี้", "เจอบั๊ก", "มีบั๊ก", "bug report", "bug นี้", "แก้บั๊กให้หน่อย"
  Trigger phrases (English): "/bma-bug-report", "bug report", "report a bug", "I found a bug", "fix this bug", "there's a bug"

  Do NOT use for: capturing an idea / feature request (use /idea), running tests with no specific bug (use /bma-e2e or /bma-human-test), or finishing a sprint already in progress (use /bma-sprint-finalize).
---

# /bma-bug-report — Bug Intake → Triage → Fix → Ship (one-shot, full-auto)

Goal: turn "มีบั๊ก X" into a tested + committed fix without manual orchestration of the 5+ skills it normally takes. One invocation = one bug = one commit (or one filed-but-stopped sprint with a clear reason).

This skill is an **orchestrator** — it does not write code itself. It:
1. captures the bug,
2. delegates triage to `bma-bug-triager` (sonnet),
3. routes to the right scope skill,
4. spawns the right read-only specialist for a patch plan,
5. lets the main agent apply the minimal patch,
6. runs the right regression skill,
7. finalizes + commits.

## The 9 steps

### 1. INTAKE
Accept input in either form:

- **Free-text from user** — anything from one line ("zoom ขยายไม่ทัน") to a paragraph. If critical info is missing (which page / which tool / what happened vs expected / how to reproduce), ask ONE batched sharpening question (≤3 sub-questions). Never ask more than once.
- **Structured finding** — already-triaged item from `/bma-human-test`, `/bma-sandbox-test`, or `PHASE_INDEX.md` "Discovered backlog". Recognise it by the `severity / step / expected / actual / source` shape and skip the sharpening question.

Optional: if user pasted a screenshot path, include it in the triage input.

### 2. TRIAGE (delegate to `bma-bug-triager`)
Spawn the `bma-bug-triager` subagent with the captured bug. Subagent returns a structured triage block:

- `severity` — CRASH / BROKEN / FRICTION / COSMETIC
- `category` — one of: `ui-menu`, `ui-ribbon`, `ui-panel-left`, `ui-panel-right`, `ui-canvas`, `ui-status`, `ui-summary`, `measure-ux`, `measure-geometry`, `measure-validation`, `server`, `save-load`, `export`, `forbidden`, `out-of-scope`
- `suspected_files` — `proto/ui.html:L1234-L1280`, etc. (delegated to `bma-explorer` internally if needed)
- `scope_skill` — which `/bma-*-scope` (or `/bma-check-forbidden`) to run next
- `specialist` — which read-only specialist subagent to deep-inspect for the patch plan (e.g. `bma-menu-bar-specialist`, `bma-measure-ux-specialist`, `bma-path-geometry-reviewer`)
- `regression_skill` — `/bma-ui-regression` or `/bma-measure-regression`
- `acceptance` — one-sentence pass condition + suggested E2E marker (e.g. `BUG_<id>_OK`)
- `risk` — low / med / high

If triage returns `category: forbidden` (fix genuinely needs polyAreaM2 / pdfToC / cToPdf / RS / snap / .bmaplan rename / server.py core) or `category: out-of-scope` (Phase 2 — legal / OCR / AI / Rule Engine / FAR-OSR verdict) → **jump to step 9 (FILE-ONLY)** with the appropriate `BUG_STOP_*` code.

### 3. FILE the bug into `docs/status/PHASE_INDEX.md`
Before any fix work, write a new sprint row into the **Active sprint queue** of `PHASE_INDEX.md`:

```
| BUG-YYYYMMDD-<slug> | <severity> | <one-line> | scope=<scope_skill> · specialist=<specialist> · regression=<regression_skill> | source=bug-report | queued |
```

CRASH / BROKEN → top of queue. FRICTION → end of queue. COSMETIC → Discovered backlog.

This guarantees: even if the loop halts at step 5/6/7/8, the bug is permanently tracked.

### 4. SCOPE
Run the triage's `scope_skill`:

- `OK` → continue to step 5.
- `SPLIT_REQUIRED` with an obvious split → write sub-sprints into PHASE_INDEX, take the first, continue.
- `SPLIT_REQUIRED` needing a human design decision → **STOP** → `BUG_STOP_DESIGN`.
- `BLOCKED` → **STOP** → `BUG_STOP_BLOCKED`.

### 5. DIAGNOSE (delegate to specialist subagent)
Spawn the triage's `specialist` (read-only) with: bug description, suspected files, acceptance criteria. Specialist returns a **minimal patch plan** (selector / function / line range + proposed change). The main agent does NOT skip this — even a "obvious" fix gets a 1-paragraph patch plan to anchor the edit.

If specialist says "the patch needs a forbidden surface" → **STOP** → `BUG_STOP_BLOCKED`.

### 6. FIX
Main agent applies the minimal patch from step 5. Constraints:

- Edit only the files the patch plan named.
- Add an E2E marker for the acceptance criteria — `BUG_<id>_OK` printed by `proto/e2e_ui_test.py` when the bug case passes. (If the bug is COSMETIC and infeasible to assert in headless, document the manual repro in `UI_MANUAL_TEST.md` instead — and say so.)
- Never cross a forbidden surface to "make the fix work" — STOP instead.

### 7. TEST (markers)
Run `/bma-e2e` (py_compile + smoke + full).

- New `BUG_<id>_OK` marker GREEN + no regressions → continue.
- A previously-green marker regresses → make ONE surgical retry. Still failing → **STOP** → `BUG_STOP_REGRESSION`.

If the bug was reported via a user-flow problem (FRICTION / BROKEN that affects journey), also run `/bma-human-test`. `HUMAN_TEST_CRASH` → **STOP** → `BUG_STOP_CRASH`.

### 8. REGRESS
Run the triage's `regression_skill` (`/bma-ui-regression` or `/bma-measure-regression`).

- `*_REGRESSION_PASS` → continue.
- `*_REGRESSION_FAIL` → **STOP** → `BUG_STOP_REGRESSION`.

### 9. SHIP (or FILE-ONLY on stop)

**On success:**
- Run `/bma-sprint-finalize` (writes the 7 mandatory outputs with sprint id `BUG-YYYYMMDD-<slug>`).
- Commit to `main` with message `fix(BUG-<slug>): <one-line>`.
- Update PHASE_INDEX row: `queued → ✅ done <hash>`.
- Emit `BUG_REPORT_DONE` with ≤5-line summary.

**On stop (any `BUG_STOP_*`):**
- Append the stop reason + current state to the PHASE_INDEX row (keep `queued` if fix not started, or `🟠 in-progress-blocked` if mid-fix with uncommitted changes).
- If uncommitted changes exist, list them in the summary but do NOT auto-commit a partial fix — let the user decide revert vs continue.
- Emit the `BUG_STOP_*` code + reason + suggested next action for the user.

## Stop conditions

| # | Code | When |
|---|---|---|
| 1 | `BUG_STOP_BLOCKED` | triage says forbidden, or scope/specialist says the only fix needs a forbidden surface |
| 2 | `BUG_STOP_REGRESSION` | marker regression or regression-guardian FAIL survives one retry |
| 3 | `BUG_STOP_CRASH` | `/bma-human-test` returns HUMAN_TEST_CRASH during step 7 |
| 4 | `BUG_STOP_DESIGN` | SPLIT_REQUIRED needs a human design choice, or triage cannot classify confidently |
| 5 | `BUG_STOP_SCOPE` | bug requires Phase 2 capability (legal / OCR / AI / Rule Engine / FAR-OSR verdict) |
| 6 | `BUG_STOP_NEEDS_REPRO` | after one sharpening question the bug is still not reproducible |

On any stop the bug stays filed in `PHASE_INDEX.md` (step 3 already wrote it) — nothing is lost.

## Output format

```
### Bug Report — BUG-YYYYMMDD-<slug>

Verdict: 🟢 BUG_REPORT_DONE  /  🟠 BUG_STOP_<code>

Severity · Category · Scope verdict · Test result · Regression verdict

Patch: <file:line> — <one-line change description>
Marker: BUG_<id>_OK <GREEN / RED / N-A>

<if DONE>Commit: <hash> on main · 7 sprint outputs updated.
<if STOP>Reason: <one-line>. Filed as <id> in PHASE_INDEX.md (status: <queued / in-progress-blocked>). Next: <one-line suggestion>.
```

Keep ≤25 lines. The loop runs often — tight reports keep the trail readable.

## Rules

- **Always file first (step 3).** Even on `BUG_STOP_*`, the bug must already be tracked.
- **Triage owns routing.** Don't second-guess the `category` / `scope_skill` / `specialist` mapping unless triage was clearly wrong (then re-run triage with corrected input, don't ad-hoc).
- **Never cross a forbidden surface to fix a bug.** STOP and file as BLOCKED — the user can decide if it warrants the larger refactor.
- **Never auto-fix a Phase 2 request.** A "bug" that's really "add legal verdict / OCR / AI" is `BUG_STOP_SCOPE`, not a fix.
- **One bug = one sprint = one commit.** Never bundle multiple bug fixes into one invocation — re-invoke per bug.
- Specialists are read-only — the main agent applies the patch. Never delegate code edits to a specialist subagent.
- Iteration report ≤25 lines.
