# BMA-Plan — Evolutionary AI Test & Develop Loop

- **Created:** 2026-05-30
- **Author:** Opus 4.8 (orchestrated build)
- **Status:** DESIGN — approved direction; implemented incrementally (see PHASE_INDEX `EVOLT-*` sprints)
- **Trigger:** user research request 2026-05-30 "ใช้ AI ทำการเทสและพัฒนาระบบ ให้มีการวิวัฒนาการ", grounded by a full-program bug hunt the same day that found 10 bugs (B1–B10) in the freshly-shipped page-manager (INV-2026-05-29-LPM) which the 49-marker unit suite did NOT catch.

## Why this doc exists

The unit suite was **42 PASS** while the feature had **5 release-blockers** (silent data loss + wrong-page measurement). That gap is the whole problem: example-based unit markers verify *what we thought to check*, not *what the program promises*. This doc defines a self-improving (evolutionary) test+develop loop so the system gets better at catching its own purpose-violations over time — without Claude weight fine-tuning (not available), so all "learning" lives in the **prompt/scaffolding + an archive of past failures**.

## Research basis (2025–2026 prior art)

| Source | What we take |
|---|---|
| [Anthropic — Property-Based Testing with Claude](https://red.anthropic.com/2026/property-based-testing/) | The 5-step agent loop (understand → propose property → write Hypothesis test → **reflect to kill false-positives** → report). 984 bug reports across 100+ pkgs, top-ranked 86% valid. PBT fits LLMs because models reason about *invariants* from context better than they enumerate cases. |
| [Darwin-Gödel Machine (arXiv 2505.22954)](https://arxiv.org/pdf/2505.22954) | **Archive of all attempts** (keep "losers" as stepping stones) + **novelty bonus > greedy** + **empirical fitness** (real benchmarks, not proxies). Watch **Goodhart/objective-hacking** (an agent once improved a metric by deleting logging). |
| [Agentic PBT (arXiv 2510.09907)](https://arxiv.org/pdf/2510.09907) | Property selection heuristics: type-inference, docstring claims, **differential testing**, common math invariants (commutativity, idempotence). Auto-minimize counterexamples. |
| [Metamorphic Testing in the Age of LLMs (arXiv 2603.24774)](https://arxiv.org/pdf/2603.24774) | Solves the **oracle problem**: instead of "what's the right answer", assert "how must output change/stay when input changes systematically". One relation = millions of cases. |
| [Tricentis 2026 QA trends](https://www.tricentis.com/blog/qa-trends-ai-agentic-testing) | QA = **orchestration + accountability layer**; human-in-the-loop mandatory (95% of AI pilots fail on missing guardrails); **risk coverage > test coverage**. |

## The loop (one diagram)

```
            ┌──────────────────────── ARCHIVE ─────────────────────────┐
            │ bug-archive.jsonl  (every confirmed bug ever = regression │
            │                     seed; "we missed this before")        │
            │ sim history.jsonl  (past run outcomes = few-shot context)  │
            └───────────────┬──────────────────────────────────────────┘
                            │ seeds + few-shot
                            ▼
 (1) GENERATE TESTS   AI reads measure-engine/page-manager/server →
     (PBT + Metamorphic) proposes invariants → writes runnable tests
                            ▼
 (2) HUNT             agent runs tests + journey on REAL customer PDFs →
                      captures minimized counterexamples
                            ▼
 (3) REFLECT (gate)   "real bug or flawed test?" — self-review, dedup vs
                      archive, severity score; NEVER trust the bare result
                            ▼
 (4) FIX              /bma-lite-dev: spec → sonnet build → Opus review →
                      the failing PBT/metamorphic test must turn GREEN
                            ▼
 (5) ARCHIVE + EVOLVE confirmed bug → bug-archive.jsonl (now a permanent
                      regression); winning approach kept; loop restarts
                      from a strictly stronger baseline
                            ▲
                    HUMAN ORCHESTRATOR gates (3)→(4)→(5): risk-coverage
                    priorities, Goodhart watch, release sign-off
```

## Four pillars → concrete BMA-Plan work

### Pillar 1 — AI-generated tests (replace hand-written examples)
- **EVOLT-1 (PBT):** Claude reads `lite/static/js/measure-engine.js` + path-geometry, proposes invariants, emits Node-run property tests. Seed invariants (un-gameable, outcome-based):
  - area ≥ 0 for any closed polygon
  - vertex-order independence: reverse/rotate the point list → identical m²
  - scale linearity: `pts_per_m × k` → area `÷ k²`
  - translation invariance: shift all points by (dx,dy) → identical m²
  - degenerate input (<3 pts / collinear) → 0, never NaN/throw
- **EVOLT-2 (Metamorphic, page-manager):** the relations that auto-catch today's blockers:
  - **MR-reorder:** reorder pages → every page's m²/tag/floor must stay attached by identity (catches **B1/B3**)
  - **MR-rotate:** rotate a page 90° → its measured area unchanged
  - **MR-save-roundtrip:** mutate → save → reload → deep-equal page identities + areas (catches **B1/B2**)
  - **MR-dirty:** any page mutation must flip the dirty fingerprint (catches **B5**)
  - **MR-render-source:** display page n must fetch its origin server page (catches **B3**)

### Pillar 2 — Agentic hunting (already partly in repo)
- Reuse `bma-human-journey-tester` / `lite-sandbox-journey-tester` as the "hunt" stage; add the **reflect gate** explicitly (the subagent already returns severity-tagged findings; the orchestrator dedups vs `bug-archive.jsonl` and scores). Real customer PDFs (`sandbox/`, the 90 MB / 95-page CHH file) are the **acceptance/beta analog**.

### Pillar 3 — Self-healing tests (kill maintenance tax)
- **EVOLT-3:** the CFSS suite hard-codes `ui-lite.html == 1200 lines`; our LPM work made it 1119 → 6 false-RED tests. Replace brittle line-count guards with **content-anchored** assertions (the *measure-engine hash* check already in those tests is the right pattern; the line-count check is the wrong one). General rule: assert on **invariants/anchors, not magic numbers**.

### Pillar 4 — Evolution (the archive that makes it self-improving)
- **EVOLT-4 (bug-archive):** `artifacts/bug-archive/bug-archive.jsonl` — one line per confirmed bug: `{id, date, severity, file, surface, repro, metamorphic_relation_that_now_guards_it, fixed_commit}`. Every new test run **seeds from this first** ("you have missed these before — verify them again"). This is the prompt-side analog of DGM's archive: the loop never re-ships a bug class it already learned.
- **EVOLT-5 (loop wiring):** `/bma-human-test` → triage (reflect+dedup) → `/bma-lite-dev` fix → regression → append archive → repeat. Human gate every cycle.

## Guardrails (non-negotiable, from the research)
1. **Human-in-the-loop at the fix + release gate** — AI proposes, human signs off (95%-pilot-failure lesson).
2. **Risk coverage > test coverage** — prioritize the measurement-correctness + data-loss surfaces, not line %.
3. **Goodhart watch** — a green metric is necessary, not sufficient; read the actual behavior on edge+adversarial before believing a PASS (we already caught a heuristic runner false-FAIL on `report_vars_report` this way).
4. **Reflect before report** — generator (sonnet) and verifier (Opus) stay independent; the verifier re-runs, never trusts the self-check.
5. **Sandbox + archive every change** — commits per slice; nothing auto-merges to a release without the gate.
6. **Forbidden surfaces still forbidden** — `measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, `.bmaplan` non-additive are never edited by the loop; tests assert their integrity (hash), they don't mutate them.

## Success metric for the loop itself (meta-fitness)
The loop is "evolving" if, over successive cycles: (a) new metamorphic relations convert each newly-found bug into a permanent guard, (b) escaped-bug count per release trends down, (c) the archive grows and replays cost ~0. Tracked in the EVOLT sprint logs.

## Relationship to existing assets
Already-present pieces this formalizes: `eval.js` taxonomy (happy/edge/adversarial) = PBT mindset; `/bma-simulate` `history.jsonl` = archive+few-shot; subagent verify-don't-trust = reflect gate; 49 markers = empirical fitness. The gap this closes = **PBT/metamorphic layer + a feedback archive that makes next cycle start stronger.**
