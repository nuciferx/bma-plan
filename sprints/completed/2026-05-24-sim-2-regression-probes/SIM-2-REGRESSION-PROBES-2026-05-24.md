# Sprint: SIM-2 — `/bma-simulate` reflection-loop hardening (regression probes)
**Date:** 2026-05-24
**Status:** DONE
**Files touched:** 3 `.claude/` config files; 0 lite/proto code changes

---

## What this is

Upgrade `/bma-simulate` so that every previously-fixed bug becomes a permanent regression probe — re-verified on every simulator run. Closed bugs cannot silently reopen.

## Why

After SIM-1.1 found 2 lite bugs (LITE-BUG-MODAL-NEST, LITE-BUG-DBLCLICK-OVER-POP, fixed in LITE-BUG-2-OPUS47-FINDINGS commit 2dae5c0), the user pushed back: "เก่งขึ้นจริงๆ" requires the simulator to *remember* what was fixed and refuse to let it regress, not just re-discover the same bug each run.

The existing `history.jsonl` is **soft memory** (rolling few-shot context, gitignored). It biases the orchestrator but doesn't guard anything. SIM-2 adds **hard memory**: `.claude/skills/bma-simulate/regression_probes.json` (tracked, curated, permanent until retired).

## Design

Two memory channels with distinct cadence:

| Channel | File | Lifetime | Mutability | Purpose |
|---|---|---|---|---|
| Soft (few-shot) | `artifacts/sim/lite/history.jsonl` (gitignored) | rolling ~30 | append-only | Bias scenario_id; spot patterns |
| Hard (regression) | `.claude/skills/bma-simulate/regression_probes.json` (tracked) | permanent until retired | curated per sprint | Mandatory step; fail = REGRESSION (highest severity) |

Each probe in `regression_probes.json`:
```json
{
  "id": "<BUG-ID>",
  "fixed_in_sprint": "...",
  "fixed_in_commit": "<short-sha>",
  "preconditions": "<human-readable>",
  "trigger": {
    "type": "evaluate" | "mouse_sequence",
    "setup_js": "() => { ... }",
    "evaluate_js": "() => { ... }",     // when type=evaluate
    "mouse_sequence": [...]             // when type=mouse_sequence
  },
  "assertion_js": "() => boolean",
  "cleanup_js": "() => { ... }"
}
```

Phase A reads this file and prepends one `regression_probe` step per entry to the SCENARIO_PLAN. The driver (`bma-sim-driver`) supports a new step type `regression_probe` that runs setup → trigger → assertion → cleanup. A false assertion produces a **REGRESSION** finding — a new severity tier above CRASH.

## Files changed

| File | Change |
|---|---|
| `.claude/skills/bma-simulate/regression_probes.json` | NEW — 2 active probes (LITE-BUG-MODAL-NEST, LITE-BUG-DBLCLICK-OVER-POP) with schema docs in `_schema` block |
| `.claude/skills/bma-simulate/SKILL.md` | Phase A step 4 (NEW) reads regression_probes.json; step 5 prepends regression_probe steps. Phase C severity list gains REGRESSION (highest). New stop conditions: SIM_REGRESSION, SIM_PROBES_MALFORMED. "Few-shot learning loop" section rewritten with the soft/hard memory table. |
| `.claude/agents/bma-sim-driver.md` | `regression_probe` added to the supported step-types table. New "How to execute regression_probe" sub-section with exec recipe: setup_js → trigger (evaluate or mouse_sequence) → assertion_js → cleanup_js. |

Zero changes to `lite/` or `proto/` code.

## Verification

A focused verifier — `artifacts/sim/lite/regression-probes-verify-20260524T200000/probe_executor.py` — loads `regression_probes.json` and runs both probes through the same recipe the bma-sim-driver agent will use, against the current lite build.

Result:
```
=== LITE-BUG-MODAL-NEST ===
  result: PASS  (860ms)
=== LITE-BUG-DBLCLICK-OVER-POP ===
  result: PASS  (2919ms)
2 PASS · 0 FAIL
```

Both fixes hold; the reflection loop's mechanism is proven end-to-end (schema parses, evaluate-type probe works, mouse_sequence-type probe works, assertions return bool, cleanup restores neutral state).

## Self-check table

| Check | Result |
|---|---|
| `regression_probes.json` parses as valid JSON | PASS |
| 2 probes registered, schema fields populated | PASS |
| SKILL.md Phase A reads probes file (documented step 4) | PASS |
| SKILL.md Phase C lists REGRESSION as highest severity | PASS |
| SKILL.md stop conditions include SIM_REGRESSION + SIM_PROBES_MALFORMED | PASS |
| bma-sim-driver supports `regression_probe` step type | PASS |
| Evaluate-type probe (LITE-BUG-MODAL-NEST) executes + asserts PASS | PASS (860ms) |
| Mouse-sequence-type probe (LITE-BUG-DBLCLICK-OVER-POP) executes + asserts PASS | PASS (2919ms) |
| No `lite/` or `proto/` source changes | PASS |
| No forbidden surfaces touched | PASS |

## Next slice

User has option 2 queued: snap-to-walls polygon strategy (replace synthetic 80%-quad placeholder with real wall snap). That's a `/bma-lite-dev` sprint targeting `lite/static/js/` (likely a new file `snap-walls.js`).
