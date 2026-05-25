---
name: lite-invent
description: |
  Invention pass for a BMA-Plan **lite** idea — a thin lite-framed wrapper over the existing invent pipeline. Reuses the SAME subagents as proto (`bma-researcher` phase 2, `bma-inventor` phase 4) because the measurement domain is shared, but reframes every phase for lite: forbidden surfaces = lite's (`lite/static/js/measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, `.bmaplan` non-additive); spike artifacts land in `lite/sandbox/` (NOT `proto/sandbox/`); the vendoring contract (measure math is copied verbatim from proto, drift-locked) is a hard constraint of every approach. Halts at the human checkpoint (GO / NOGO / RESHAPE) like all invention. Read-only on app code; commits restricted to `docs/invent/`, `lite/sandbox/`, `PHASE_INDEX.md`.

  Trigger phrases (Thai): "invent lite", "คิดวิธีใหม่ให้ lite", "ประดิษฐ์ lite", "วิจัย lite", "ออกแบบฟีเจอร์ lite"
  Trigger phrases (English): "invent for lite", "lite invention", "research a lite feature", "explore lite approaches"

  Do NOT use for: proto invention (use /bma-invent), capturing a raw idea (use /idea), building an already-vetted lite slice (use /bma-lite-dev), or fixing a known lite bug (file a lite sprint).
---

# /lite-invent — Invention pass, lite-framed (I-B wrapper)

Why this exists (chosen 2026-05-22 as I-B over reusing `/bma-invent` raw): the invent *pipeline* and its subagents are domain-coupled to area-measurement (shared with lite) but NOT file-coupled to proto. Running `/bma-invent` raw on a lite idea would carry proto's forbidden-surface list and write spikes into `proto/sandbox/` — which could mislead an invention pass into proposing proto edits. This wrapper keeps the same cheap pipeline but swaps in the lite frame so invention stays inside lite's world.

## What stays identical to `/bma-invent`

The 7 phases and their delegations are unchanged:

1. **PICK** — next `invent-queued` lite idea from `~/.claude/ideas/IDEAS.md` / `PHASE_INDEX.md` (or the one the user names).
2. **RESEARCH** → delegate to **`bma-researcher`** (haiku). Prior-art survey: in-repo lite + proto prior work, inline-JS libs, CAD/GIS/Bluebeam/Foxit incumbents. Returns the 5-section report + verdict (`PRIOR_ART_MATURE` / `PARTIAL` / `GREENFIELD`). **Always delegate — never answer from general knowledge.**
3. **FRAME** — problem / constraints / forbidden surfaces / success criteria / out-of-scope.
4. **DIVERGE** → delegate to **`bma-inventor`** (sonnet). 3–5 genuinely different approaches on different axes.
5. **SCORE** → `bma-inventor` scores on the 6 dimensions; recommend top + fallback.
6. **SPIKE** — build the chosen spike. **In `lite/sandbox/invent-<name>.html`** (create the dir if absent) — NEVER in `lite/ui-lite.html` or `proto/`.
7. **CHECKPOINT** — halt for the human: GO / NOGO / RESHAPE. Invention never auto-promotes.

## What the lite frame overrides (the only differences)

| Aspect | proto `/bma-invent` | this skill |
|---|---|---|
| Forbidden surfaces in FRAME | proto's full table | `lite/static/js/measure-engine.js` (vendored/parity-locked), `RS`, `pdfToC`/`cToPdf`, `.bmaplan` non-additive renames, area math reading a display name |
| Hard constraint baked into every approach | — | **vendoring contract**: measure math is copied verbatim from proto and drift-locked by `lite/tests/test_measure_parity.py`; no approach may fork or relocate it |
| Lean constraint | size discipline (5000-line ui.html trigger) | lite size caps: `ui-lite.html` ≤1200, other runtime files ≤1000 → bulk goes to `static/js/<region>.js` |
| Spike output dir | `proto/sandbox/` | `lite/sandbox/` |
| "Never touch the live app" | `proto/ui.html` / `proto/server.py` | `lite/ui-lite.html` / `lite/server_lite.py` AND `proto/*` |
| On GO | sprint card → `/bma-dev-loop` | sprint card → built via `/bma-lite-dev` (the lite loop) |

## Commit scope (same discipline as `/bma-invent`)

Only `docs/invent/`, `lite/sandbox/`, and `PHASE_INDEX.md`. Invention NEVER edits `lite/ui-lite.html`, `lite/server_lite.py`, `lite/static/*`, or anything in `proto/`.

## On GO

Write the sprint card into `PHASE_INDEX.md` with status `invent-done-go` and a note that it is built via `/bma-lite-dev` (one reviewable slice at a time, human signs off — lite has no full-auto loop). The vetted idea is then eligible for the lite dev orchestrator.

## Rules

- Research-first is non-negotiable: a `PRIOR_ART_MATURE` verdict (e.g. a viable inline-JS lib) skips diverge/spike and goes straight to a standard lite sprint card.
- Always halt at the checkpoint — never promote a lite idea to a sprint without the human's GO.
- If an approach's only viable form needs a measure-math change, mark it `forbidden_surface_touch=YES` and exclude it from rank #1 (same hard rule as proto's Approach B).
