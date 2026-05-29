---
name: bma-lite-dev
description: |
  Token-frugal development orchestrator for BMA-Plan **lite** (the slim spinoff in `lite/`). The Opus main agent owns the spec + the review; the actual code-writing is delegated to the `lite-builder` subagent (sonnet) so heavy file-reading + iteration happens in the worker's context, not the main thread. One invocation = one lite sprint: SPEC → DELEGATE → REVIEW → TEST → REPORT. Reuses one `lite-builder` instance across sprints (via SendMessage) so it never re-reads unchanged files.

  Trigger phrases (Thai): "/bma-lite-dev", "พัฒนา lite", "ทำ lite", "lite sprint", "สร้าง layer lite", "แก้ lite", "ให้ sonnet ทำ lite"
  Trigger phrases (English): "/bma-lite-dev", "develop lite", "lite sprint", "build lite feature", "sonnet builds lite"

  Do NOT use for: proto work (use bma-dev-loop / bma-ui-* / bma-measure-*), capturing ideas (use /idea), or finishing a proto sprint (use /bma-sprint-finalize). For lite, this skill IS the loop.
---

# bma-lite-dev — lite development orchestrator (Opus drives, Sonnet builds)

Purpose: develop `lite/` cheaply. **You (Opus) think + review; `lite-builder` (sonnet) writes the code.** Tokens are the constraint — keep the heavy reading inside the worker, keep only spec + diff review in the main thread.

## Division of labor (do not blur)

| Role | Who | Does |
|---|---|---|
| Spec + design decisions | Opus (you) | Decide WHAT, write a tight spec, set acceptance criteria |
| Implementation | `lite-builder` (sonnet) | Read lite files, write code, extract modules, run self-tests |
| Review + gatekeeping | Opus (you) | Read the diff, check forbidden/parity/lean, decide GO / revise / STOP |
| Commit + human sign-off | human + Opus | Only after review PASS |

## Steps

### 1. SPEC (Opus) — spec-driven, the 6 canonical elements

The spec is the single source of truth (2026 spec-driven-development standard — it's what stops the worker from drifting from intent, decaying as context grows, and producing unverifiable output). Write ONE tight spec, one screen, covering all six:

1. **Outcome** — what the user observably gets when this slice lands (one sentence).
2. **Scope boundary** — exact files + function/region names to touch, and what is explicitly OUT this slice.
3. **Constraints** — "behavior preserved unless stated", forbidden/parity surfaces, additive-schema, the lean cap, where to extract if it adds bulk.
4. **Prior decisions** — relevant rows from `LITE_LAYER_ROADMAP` decision log / worker lessons so the builder doesn't relitigate them.
5. **Task breakdown** — the change as 1-5 concrete, ordered steps the builder works through (not one vague blob).
6. **Verification criteria** — the *runnable* acceptance check: which `lite/tests/*` must pass, plus any manual assertion. No prose-only criteria — it must be checkable (carries the eval-first rule from `/lite-invent`).

**Scale effort to complexity** (Anthropic orchestrator lesson): a one-line CSS fix gets a one-line spec, not the full ceremony. If the user gave a multi-part feature, do the **smallest safe slice** first (prefer an invisible refactor before any visible UI). Don't over-spec trivial work or under-spec a schema change.

### 2. DELEGATE (→ lite-builder)
Spawn `lite-builder` (subagent_type: `lite-builder`) with the spec. The worker gets a self-contained task (the spec) + the output format + its own fresh context — it does not need to know what other sprints did (Anthropic subagent isolation).

**Reuse the same instance** for later sprints via SendMessage so it keeps lite's structure in context and avoids re-reading files — **with two guards against context rot** (the failure mode of long-lived reused agents):
- **Stale-memory guard (lite-specific):** `lite/` lives in a Drive-synced folder; files can change between sprints from another session. Before reusing the instance, if `git status` (from `/lite-start` or step 4) shows the target file dirty/changed since the builder last saw it, tell the builder **"re-read <file> fresh, do not trust your cached copy"** in the SendMessage. Never let a reused builder edit from a stale mental copy.
- **Re-baseline trigger:** after ~5 reused sprints, or if the builder's diffs start referencing line numbers/functions that no longer match, start a fresh instance (drop the rotted context) rather than fighting drift.

The worker returns `LITE_BUILD_DONE` / `LITE_BUILD_BLOCKED` + a diff + a self-check table — NOT whole files.

### 3. REVIEW (Opus) — the gate

**Information asymmetry rule (chain-of-verification):** the generator (sonnet) and the verifier (you, Opus) must be independent — that's what breaks self-confirmation bias. So **the worker's self-check table is a claim, not evidence.** For the two things that can corrupt lite — forbidden/parity touches and the test result — do NOT take the self-check at face value: confirm forbidden/parity yourself from the diff, and treat any test the worker says it "couldn't run" as *not passed* until you run it in step 4. (Same principle as eval-first's "read the transcript, don't trust the bare number".)

Read the returned diff (not the files). Check, in order:
- **Forbidden / parity:** did it touch `lite/static/js/measure-engine.js`, `RS`, or `pdfToC`/`cToPdf`? → if yes, STOP, do not apply, surface to user.
- **.bmaplan schema:** any new fields must be **additive**; area math must still read `semanticTag` / role, never a display name. If non-additive → run the logic of `/bma-check-forbidden` mentally (it's a forbidden surface) and STOP.
- **Behavior:** for refactor specs, is user-visible behavior unchanged?
- **Lean (hard cap):** `ui-lite.html` ≤ **1200 lines**; every other runtime file (`server_lite.py`, `lite-report.html`, `static/js/*.js`) ≤ **1000 lines**. If the diff pushes any file over its cap → STOP, send a narrower spec back to extract one cohesive region into a new `static/js/<region>.js` FIRST. No feature lands while a file is over cap. (Tests exempt from the cap; a test file > 1000 lines is a smell — split by feature.)
- **Correctness:** does the diff actually meet the acceptance criteria?

If the worker hit a STOP condition or the review fails, send a corrected/narrower spec back via SendMessage. Do not hand-fix large blobs yourself (that burns Opus tokens) — but DO hand-apply tiny, surgical fixes when cheaper than a round-trip.

### 4. TEST (Opus, cheap)
Run the lite tests the spec named — these are small. **First, the size-cap gate:**
```
cd lite && wc -l ui-lite.html server_lite.py lite-report.html static/js/*.js
# ui-lite.html must be ≤1200; every other runtime file ≤1000. Over cap → back to extract.
cd lite && python -m py_compile server_lite.py
cd lite && python tests/test_measure_parity.py     # if save/load or any geometry-adjacent change
cd lite && python tests/<other named test>
```
For cross-open parity (lite↔proto) on `.bmaplan` changes, verify yourself — never delegate parity judgment.

### 5. REPORT (Opus)
Give the user a 4-line verdict: what changed, files, test result, next slice. Ask GO before committing. Do **not** auto-commit — lite has no full-auto loop; the human signs off.

## Guardrails
- This skill never edits proto. If a lite change reveals a proto bug, note it and stop.
- New `.bmaplan` fields: additive only, and proto must still open lite files (proto ignores unknown fields, reads `semanticTag`). Confirm before shipping schema changes.
- One invocation = one reviewable slice. Resist bundling L1+L2+L3 into one worker call — small diffs review cheaper and fail safer.
