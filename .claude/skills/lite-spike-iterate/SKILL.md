---
name: lite-spike-iterate
description: >
  Iterate a BMA-Plan lite SPIKE (or a RESHAPE of one) in lite/sandbox/ until the
  claimed user-facing UX actually works — not until the eval merely prints OK.
  Drives the SPIKE→EVAL→root-cause-fix loop with a strict halt criterion: every
  eval case PASS (N/N), zero page errors, AND the claimed interaction is exercised
  through real DOM events (not API string injection). Honest re-eval of any prior
  PASS claim first; separates orthogonal lib-level failures from the claim under
  test; ends by updating the invent doc with an honest RESHAPE block. Read-only on
  live app code — commits restricted to lite/sandbox/, docs/invent/, PHASE_INDEX.md.

  Trigger phrases (Thai): "spike จนใช้ได้", "iterate spike", "ทำ spike ให้ใช้ได้จริง",
    "RESHAPE", "วน spike", "eval ขับ DOM"
  Trigger phrases (English): "iterate the spike", "make the spike actually work",
    "spike until it works", "RESHAPE the spike", "drive the eval through DOM"

  Do NOT use for: building the vetted slice into live lite/ (use /bma-lite-dev),
  first-time invention research/diverge (use /lite-invent), capturing a raw idea
  (use /idea), or proto spikes (this is lite-scoped — proto spikes live in
  proto/sandbox/ and use /bma-invent).
---

# /lite-spike-iterate — drive a lite spike until the real UX works

Codified 2026-06-04 from the editable-report D2 run (memory:
`feedback_spike_iterate_until_real`). The escalation rule said: codify on the 3rd
RESHAPE of a single idea that reuses this loop. This is that skill.

## What this is for

A SPIKE proves an approach is buildable BEFORE it becomes a `/bma-lite-dev` slice.
The failure mode this skill exists to kill: **an eval that prints PASS while the
user-facing interaction was never actually exercised** (D's `-d-eval.py` injected
`setCell('B5','=B1+B2')` and reported 4/4 — the Excel cell-click UX it claimed was
never driven, and the user caught it by hand: "Excel cell-click ยังใช้ไม่ได้").

Input: a spike file under `lite/sandbox/invent-*.html` (+ its `*-eval.py`), and the
**UX claim** the spike must prove (e.g. "click a cell while editing a formula and
the cell ref is inserted").

Output: the spike reaches **N/N + zero page errors + DOM-driven**, and the invent
doc gets an honest RESHAPE block. Halts at the human checkpoint (GO / NOGO /
RESHAPE-again) — never auto-promotes to a build.

## The 5 rules (apply every iteration)

1. **Honest re-eval before trusting the prior claim.** Re-run the existing eval
   yourself. Treat any logged PASS count as suspect until reproduced. If the prior
   eval bypassed the UX claim, the real starting score is whatever an honest,
   DOM-driven eval reports — say so out loud and correct the invent doc.
2. **Close the eval-gate hole.** If the claim is a user interaction (click / drag /
   key / hover), the eval MUST drive it via real DOM events
   (`el.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,...}))`, real
   `KeyboardEvent`, real `.click()` on the actual control) — NEVER via an API that
   sets the end-state directly. If the eval can't reach the binding, the binding
   isn't proven.
3. **Root-cause iterate, not retry blind.** On failure, grep the vendor/library
   source or the app code to find the real API before re-trying. (D2 it1
   `opened=False` was solved by grepping `obj.openEditor=function` in jss-CE and
   learning it takes a TD element — not by nudging dblclick coordinates.)
4. **Separate orthogonal concerns.** When a failure is lib-level and unrelated to
   the claim, split the assertion. (D2 case 4: `=B1+B3`→NaN when an input is 'abc'
   is jss-CE evaluator behaviour — orthogonal to whether the picker BUILT the right
   formula string. Assert the picker output; capture the lib NaN as informational,
   to be guarded at app-layer in the build.)
5. **Halt only at: N/N PASS AND zero page errors AND the claim is DOM-driven.**
   "Mostly passing" is not the halt point. Capture (but do not gate on) risks that
   are out of this spike's scope, and list them as build-spec items.

## Steps

1. **Locate & frame.** Read the spike file + its eval + the invent doc's latest
   RESHAPE block. State the UX claim in one line. `wc -l` the spike (sandbox files
   are exempt from the 1000-line cap, but keep them lean).

2. **Honest re-eval (rule 1).** Run `python3.11 lite/sandbox/<spike>-eval.py`.
   Record the true N/M. If the eval injects end-state instead of driving DOM for
   the claim, REWRITE the eval first (rule 2) and re-run to get the honest baseline.

3. **Iterate SPIKE↔EVAL (rules 2-4).** Loop:
   - Read the failing case. Grep vendor/app source for the real API (rule 3).
   - Edit the spike (or the eval if it's the eval that's wrong).
   - Re-run the eval. Show the case table each iteration.
   - Split any orthogonal lib-level failure (rule 4).
   Continue until rule 5's halt criterion holds.

4. **Halt check (rule 5).** Confirm: every case PASS, `pg.on("pageerror")` captured
   nothing, and each UX-claim case used real DOM events. If not all three, keep
   iterating — do not stop.

5. **Update the invent doc (honest RESHAPE block).** Append
   `## RESHAPE #N (date) — <one-line>` to `docs/invent/<idea>.md`:
   - what changed and why (the user feedback or risk that drove it)
   - the new spike + eval filenames + the marker (e.g. `D3_SPIKE_OK N/N`)
   - eval actuals per case (DOM-driven)
   - **honest caveats** — correct any stale PASS claim from a prior block; list
     risks captured but NOT gated (these become `/bma-lite-dev` build-spec items)
   - build params if GO

6. **Checkpoint.** Present GO / NOGO / RESHAPE-again to the human. Do not start a
   `/bma-lite-dev` build — that is a separate, human-authorized step.

## Constraints (ทำตามกฎ)

- **Sandbox-only.** Edit ONLY `lite/sandbox/invent-*`, `docs/invent/*`,
  `PHASE_INDEX.md`. NEVER touch `lite/ui-lite.html`, `lite/static/js/*`,
  `lite/server_lite.py`, or any `proto/*`. If the spike proves the approach, the
  real code lands later via `/bma-lite-dev`.
- **Forbidden surfaces stay forbidden** even in spike framing: a spike must not
  depend on editing `measure-engine.js` / `RS` / `pdfToC` / `cToPdf` / area math /
  non-additive `.bmaplan`. Vendored math is byte-identical to proto.
- **Eval must be deterministic & runnable** — Playwright, headless, fixed tolerance,
  ≥3 cases, captures `pageerror`. No `Date.now()`/random in assertions.
- **Halts at the human checkpoint.** Like all invention, never auto-promote.
- **One idea, one invent doc.** RESHAPE blocks accumulate in the same doc so the
  decision history is one file.

## Marker convention

Each spike's eval prints `<TAG>_SPIKE_OK N/N` on full pass, or
`<TAG>_SPIKE_PARTIAL k/N` otherwise. The TAG is the approach letter + reshape index
(e.g. `D2`, `D3`). The skill is NOT done until the OK form prints with no page
errors.
