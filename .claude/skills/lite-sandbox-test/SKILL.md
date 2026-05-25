---
name: lite-sandbox-test
description: |
  Pre-release gate for BMA-Plan **lite** (`lite/`). Runs every PDF in `sandbox/` through the lite app (`lite/ui-lite.html` + `lite/server_lite.py`) to surface issues only real customer files expose (huge size, weird page count, unusual rotation, vendor quirks). Delegates the per-file journey to the `lite-sandbox-journey-tester` subagent (sonnet, Tier 1 open+render → Tier 2 set-scale+draw+export+save+reopen). Findings come back to YOU (Opus) for review — there is NO auto-triage and NO auto-file (matches lite's "Opus reviews, human signs off" ethos). Returns LITE_SANDBOX_TEST_PASS / LITE_SANDBOX_TEST_ISSUES / LITE_SANDBOX_TEST_CRASH.

  Trigger phrases (Thai): "lite sandbox test", "เทสไฟล์จริง lite", "ก่อนปล่อย lite", "pre-release lite", "lite ก่อนปล่อยรุ่น"
  Trigger phrases (English): "lite sandbox test", "lite pre-release check", "test lite on real PDFs", "lite customer-pdf test"

  Do NOT use for: the proto app (use /bma-sandbox-test — it drives proto/ui.html), lite unit markers (run lite/tests/* directly via /bma-lite-dev), or fixing the issues it finds (those become lite sprints via /bma-lite-dev).
---

# /lite-sandbox-test — Lite Real-PDF Pre-Release Gate (SB-D)

Goal: catch problems that *only* real customer PDFs expose in the **lite** tree, BEFORE a lite build ships. The lite app has its own server, port, selectors and shortcuts, so the proto sandbox gate cannot cover it — this is the lite-side equivalent.

This is **SB-D** (chosen 2026-05-22 over SB-A/B/C/E): full Tier-1+2 journey coverage via a dedicated subagent, but findings return to Opus for judgment — **no auto-triage subagent, no auto-write to PHASE_INDEX**. That keeps lite's `.claude/` surface lean and honours the "human signs off" rule shared with `/bma-lite-dev`.

## Sandbox location

`F:/drives/My Drive/01 project/ai/bma-plan/sandbox/` — the SAME gitignored folder proto uses. Drop real customer / problematic PDFs here. Read-only on `sandbox/`.

## Steps

1. **Enumerate** — list every `*.pdf` in `sandbox/`. Empty → emit `LITE_SANDBOX_EMPTY` and stop. Missing folder → `LITE_SANDBOX_MISSING`, do not error.

2. **Per-file journey (delegate to `lite-sandbox-journey-tester`)** — pass all PDF paths. The subagent boots `lite/server_lite.py` (free port from 8240, mirroring `lite/tests/test_pan_controls.py`), drives `lite/ui-lite.html` with Playwright, and for each PDF runs:
   - **Tier 1 (always):** upload → render every page → watch for 5xx / timeout / `malloc failed` / blank / rotation drift.
   - **Tier 2 (only if Tier 1 PASS):** set scale (`S`, stub) → draw a 4-point polygon (`A`) → export → save `.bmaplan` (Ctrl+S) → reopen → verify object count + area round-trip.
   - Returns severity-tagged findings (CRASH / BROKEN / FRICTION / COSMETIC) + per-file log in `artifacts/sandbox-tests/lite/<pdf-stem>/`. Read-only on `lite/`.

3. **REVIEW the findings yourself (Opus) — the gate.** Do NOT delegate this to a triager. For each finding:
   - Confirm it is reproducible (cite the endpoint + log excerpt the subagent gave).
   - Decide severity and whether it is a genuine lite bug vs a known proto-shared limitation vs a sandbox-file quirk.
   - Group obvious duplicates.

4. **Hand the user a decision, do NOT auto-file.** Present the reviewed findings and, for CRASH/BROKEN, recommend filing a lite sprint via `/bma-lite-dev` (one bug = one slice). Filing into `PHASE_INDEX.md` happens only after the user says GO — this skill never writes to PHASE_INDEX and never creates `.claude/` files.

5. **Return the verdict:**
   - `LITE_SANDBOX_TEST_PASS` — every PDF cleared Tier 1+2.
   - `LITE_SANDBOX_TEST_ISSUES` — BROKEN/FRICTION/COSMETIC found; no CRASH.
   - `LITE_SANDBOX_TEST_CRASH` — at least one PDF crashed lite → surface immediately; recommend halting any lite release.

## Output (≤30 lines)

```
### Lite Sandbox Test — <date>

Verdict: 🟢 LITE_SANDBOX_TEST_PASS / 🟡 LITE_SANDBOX_TEST_ISSUES / 🔴 LITE_SANDBOX_TEST_CRASH

Files tested: N (<list ≤3 filenames>)
Tier 1 (open+render): M/N pass   ·   Tier 2 (journey): K/M pass

#### Findings (reviewed by Opus — not yet filed)
| # | severity | category | source PDF(s) | recommended next |
|---|---|---|---|---|
| 1 | BROKEN | polygon lost on reopen | foo.pdf | file lite sprint via /bma-lite-dev |
| ... |

#### Decision needed
<for each CRASH/BROKEN: "file as lite sprint? (GO/skip)"> — nothing written to PHASE_INDEX until you say GO.

<if CRASH>⛔ Lite release should halt until the CRASH is resolved.
```

## Rules

- **No auto-triage, no auto-file.** Opus reviews; the human decides what becomes a sprint. This is the deliberate SB-D difference from proto's `/bma-sandbox-test` (which auto-files via `bma-issue-triager`).
- **Read-only on `lite/`, `proto/`, and `sandbox/`.** Findings → chat + `artifacts/` only.
- Temp artifacts go in `artifacts/sandbox-tests/lite/` (gitignored). Never commit per-file logs.
- Every recommended sprint must name the source PDF so the fix is reproducible.
- Output ≤30 lines; detailed per-file logs live in `artifacts/`, not chat.
- **Pre-release gate:** before any lite hand-off (PyInstaller lite build, demo, customer hand-off) this should return PASS or ISSUES with all CRASH-level items resolved.
- If a finding implicates the vendored `measure-engine.js` math, do NOT propose editing it — that is parity-locked; surface it as a proto-side question instead.
