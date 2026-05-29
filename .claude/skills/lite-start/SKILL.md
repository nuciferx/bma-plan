---
name: lite-start
description: |
  Session-start brief for BMA-Plan **lite** (`lite/`). Loads only the canonical lite sources (lite/README.md, docs/design/LITE_LAYER_ROADMAP.md, git status) and returns a 1-page brief (~4K tokens) instead of reading the bloated project-wide status docs (PHASE_INDEX ~29K, LATEST_STATUS ~24K). Also reports the size-cap headroom for every lite runtime file so the next slice knows whether it must extract to a module first.

  Trigger phrases (Thai): "เริ่มงาน lite", "lite ค้างอะไร", "สถานะ lite", "ทำ lite ต่อ", "lite resume"
  Trigger phrases (English): "lite session start", "lite status", "where did lite leave off", "resume lite", "what's next in lite"

  Do NOT use for: the proto app (use /bma-start), running lite tests (run lite/tests/* or use /bma-lite-dev), or finding a specific symbol (use bma-explorer scoped to lite/).
---

# /lite-start — Lite Session-Start Brief

Goal: replace reading the giant project-wide status docs with one cheap lite-scoped brief. Lite is a slim, separate tree — its state lives in 2 small docs + git, not in PHASE_INDEX.

## Steps

1. **Read in parallel** — these are the canonical lite sources, do not read others:
   - `lite/README.md` (~855 tok) — what lite is, vendoring contract, layout, run, roadmap LITE-0..7, **size discipline**
   - `docs/design/LITE_LAYER_ROADMAP.md` (~3.4K tok) — layer roadmap L1→L2c, current status table, **next slice**, decision log + worker lessons

2. **Run in parallel with the reads:**
   - `git status --short` — uncommitted state (lite is in a Drive-synced folder; concurrent edits happen — always check before touching `ui-lite.html`)
   - `git log --oneline -5` — recent commits
   - `cd lite && wc -l ui-lite.html server_lite.py lite-report.html static/js/*.js` — the size-cap gate (ui-lite.html ≤1200, others ≤1000)

3. **Output exactly this structure** (Thai, no extra prose):

   ```
   ## 📐 BMA-Plan Lite — <date from system>

   ### 🎯 Last slice
   <one-line from LITE_LAYER_ROADMAP decision log / git log top lite commit: name + PASS/done>

   ### ⏭ Next slice
   <one-line from the roadmap "ถัดไป" / status table 🟡 row>

   ### 📏 Size headroom (cap: ui-lite 1200, others 1000)
   <one line per runtime file: name N/cap (X left) — flag any <100 left as ⚠️>

   ### 📝 Working tree
   <git status short — flag if ui-lite.html dirty (possible concurrent edit)>
   Branch: <current>  Recent: <last 3 commits one-line>

   ### ❓ Question
   <one specific question, e.g. "start L2c-3 (custom-layer UI panel) — land it in layer-panel.js per size cap?">
   ```

## Constraints

- Total output ≤ 30 lines. End with exactly ONE question.
- Do NOT read `PHASE_INDEX.md`, `LATEST_STATUS.md`, `NEXT_ACTIONS.md`, `log.md` (token-bloated; lite state is in the 2 docs above). If the user needs a specific lite sprint row, Grep `lite` in PHASE_INDEX instead of reading it whole.
- Do NOT read `CLAUDE.md` / `AGENTS.md` — auto-loaded.
- If any runtime file is over its cap, the question MUST be "extract <file> to static/js/ before the next feature?" (size discipline is the only counter-force to lite bloat).
- Clean git → write "(clean)". Dirty `ui-lite.html` with no active lite sprint → flag possible concurrent edit from another session and ask to confirm before proceeding. **When a runtime file is dirty, also note it must be passed to `/bma-lite-dev` as "re-read fresh" — a reused `lite-builder` instance may hold a stale cached copy (the stale-memory guard).**
