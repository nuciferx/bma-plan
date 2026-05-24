# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-24 — SIM-2 — /bma-simulate regression-probe hardening — PASS (branch: main)

**What changed:** Added a permanent regression-probe mechanism to `/bma-simulate` (Pack J). Two memory channels now coexist: the existing soft channel (`artifacts/sim/lite/history.jsonl`, rolling ~30 entries, gitignored, used for few-shot context in Phase A) and a new hard channel (`.claude/skills/bma-simulate/regression_probes.json`, tracked, permanent until retired, curated per sprint). Each probe in the hard channel is a mandatory step prepended to every SCENARIO_PLAN right after `open_pdf` — a false assertion returns a new REGRESSION severity tier, which ranks above CRASH and triggers the new `SIM_REGRESSION` stop condition. Two initial probes registered and verified PASS against the current build: LITE-BUG-MODAL-NEST (evaluate-type, 860 ms — verifies `#setupModal` renders with non-zero rect, `parent === #stage`, `select.offsetParent` exists when `openSetup()` runs) and LITE-BUG-DBLCLICK-OVER-POP (mouse_sequence-type, 2919 ms — verifies a 4-vertex polygon survives dblclick at the last click position, asserting `PS[1].objects[0].pts.length === 4`). `SKILL.md` and `bma-sim-driver.md` updated to document the new probe step type, severity list, and stop conditions. Zero changes to `lite/` or `proto/` runtime code.

**Why:** SIM-1.1 found 2 real lite bugs (LITE-BUG-MODAL-NEST and LITE-BUG-DBLCLICK-OVER-POP) that LITE-BUG-2-OPUS47-FINDINGS fixed. Without a regression-probe mechanism those bugs could silently reopen in a future sprint — the simulator would re-find them and they would appear as new findings rather than regressions. The hard probe channel closes this loop: each closed bug becomes a mandatory assertion that every future `/bma-simulate` run must pass before the scenario plan even starts, making regressions immediately visible at the highest severity tier (REGRESSION > CRASH > BROKEN > FRICTION > COSMETIC).

**Files touched:**
- `.claude/skills/bma-simulate/regression_probes.json`: NEW — 2 active probes + `_schema` documentation block (~50 lines)
- `.claude/skills/bma-simulate/SKILL.md`: Phase A gains steps to read probes file and prepend probe steps to SCENARIO_PLAN; Phase C severity list gains REGRESSION (highest); stop conditions extended with SIM_REGRESSION + SIM_PROBES_MALFORMED; "Few-shot learning loop" section rewritten with soft/hard memory table (~+30 lines)
- `.claude/agents/bma-sim-driver.md`: Step types table gains `regression_probe`; new "How to execute regression_probe" sub-section documenting setup_js → trigger → assertion_js → cleanup_js recipe (~+45 lines)
- `sprints/active/SIM-2-REGRESSION-PROBES-2026-05-24.md`: NEW sprint card (to be moved to `sprints/completed/2026-05-24-sim-2-regression-probes/`)

**Tests:**
```
python -c "import json; json.load(open('.claude/skills/bma-simulate/regression_probes.json', encoding='utf-8'))"
  → PASS (2 probes registered, both schema-valid)

artifacts/sim/lite/regression-probes-verify-20260524T200000/probe_executor.py
  (loads regression_probes.json, runs both probes against current lite build
   using the exact bma-sim-driver recipe: setup_js → trigger → assertion_js → cleanup_js)
  === LITE-BUG-MODAL-NEST ===
    result: PASS  (860ms)
  === LITE-BUG-DBLCLICK-OVER-POP ===
    result: PASS  (2919ms)
  2 PASS · 0 FAIL

No proto/lite source changes → proto py_compile + E2E not re-run (baseline unchanged).
```

**Phase 1 scope check:**
- ✅ polyAreaM2 / polyMetrics / polySelfIntersects unchanged
- ✅ pdfToC / cToPdf / RS / scale math unchanged
- ✅ proto/server.py core endpoints unchanged (zero proto edits)
- ✅ .bmaplan schema additive only (probes read PS in-memory, ephemeral — schema untouched)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ buildSnapIndex / snap engine unchanged
- ✅ lite/static/js/measure-engine.js (drift-locked vendored copy) unchanged
- ✅ Size cap honored (no lite/ runtime files touched)

**Known gaps / follow-ups:**
- Option 2: snap-to-walls polygon strategy — replace synthetic 80%-quad placeholder with real wall-snap geometry (read PDF vector edges, snap to walls), new `lite/static/js/snap-walls.js`, run via `/bma-lite-dev`
- Option 3: Lite PDF page classifier — auto-tag floor/site/cover from title block OCR or layout hints; invention-level, run `/bma-invent` first

---

## 2026-05-24 — LITE-BUG-2-OPUS47-FINDINGS — 2 lite bugs fixed (modal nesting + dblclick vertex pop) — PASS (branch: main)

**What changed:** Fixed two `lite/ui-lite.html` bugs surfaced by the Opus-4.7-self-drive multi-model simulator on 2026-05-24. LITE-BUG-MODAL-NEST (BROKEN): `<div id="modal">` at line 191 was missing its closing `</div>`, causing `#setupModal` (line 195) to be nested inside `#modal` (calibration modal). Because `#modal` defaults to `display:none`, `#setupModal` was invisible regardless of `openSetup()` setting `style.display='flex'` — `getBoundingClientRect()=0×0`, `offsetParent=null`. Fix: added the missing `</div>` at end of line 194 to properly close `#modal` before `#setupModal`. LITE-BUG-DBLCLICK-OVER-POP (FRICTION): `cv.addEventListener("dblclick", ...)` had an unbounded `while` loop popping trailing pts within 6 screen-px of the dblclick spot. Intended to remove 2 stray points from dblclick's two mousedowns, but without an upper bound it also ate any intentional vertex placed within 6 px, causing saved polygons to be triangles (confirmed: 4 pts → 3 pts, area 713 m² → 356 m²). Fix: replaced with bounded `for(_np<2)`. Zero net lines across both patches. `lite/ui-lite.html` stays at 1197 lines (cap 1200).

**Why:** The Opus-4.7 multi-model simulator (Pack J, `/bma-simulate`) ran a full lite workflow on `lite/test.pdf` and identified both regressions as BROKEN/FRICTION severity. LITE-BUG-MODAL-NEST blocked the Page Setup flow entirely — users clicking Page → Page Setup saw nothing. LITE-BUG-DBLCLICK-OVER-POP silently corrupted polygon vertex counts, causing wrong areas in saved projects. Both were silent bugs (no console error) that standard py_compile/smoke did not surface — proving the value of the multi-model simulator as a finding mechanism.

**Files touched:**
- `lite/ui-lite.html`: Added missing `</div>` at line 194 end (closes `#modal`); replaced unbounded `while` with bounded `for(_np<2)` at lines 502-503 (0 net lines)
- `sprints/completed/2026-05-24-lite-bug-2-opus47-findings/LITE-BUG-2-OPUS47-FINDINGS-2026-05-24.md`: NEW sprint card (moved from active/)

**Tests:**
```
python -c "open('lite/ui-lite.html', encoding='utf-8').read()"  → parseable PASS
wc -l lite/ui-lite.html                                          → 1197 (≤1200 cap) PASS
<div> vs </div> regex balance: opens=92 closes=92 delta=0        PASS (was delta=1)
cd lite && python -m py_compile server_lite.py                   → PASS
cd lite && python tests/test_pan_controls.py                     → BUG_20260521_LITE_PAN_OK PASS

Live Playwright verify (artifacts/sim/lite/test-pdf-opus47-direct-20260524T194000/verify_bug_fixes.py):
  BUG_A_modal_rect_nonzero:     PASS — #setupModal now renders 1600×958, parent=#stage
  BUG_A_calib_modal_still_works: PASS — no regression, 1600×958
  BUG_B_dblclick_preserves_vertex: PASS — 4 pts saved, area=714.07 m² (drift 0.13% from screen-to-pt rounding — acceptable)

No proto/ E2E run (lite-only sprint, zero proto/ edits).
```

**Phase 1 scope check:**
- ✅ polyAreaM2 / polyMetrics / polySelfIntersects unchanged
- ✅ pdfToC / cToPdf / RS / scale math unchanged
- ✅ proto/server.py core endpoints unchanged (zero proto edits — lite-only sprint)
- ✅ .bmaplan schema additive only (untouched)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- ✅ lite/static/js/measure-engine.js (drift-locked vendored copy) unchanged
- ✅ Size cap honored — lite/ui-lite.html still 1197 ≤ 1200

**Known gaps / follow-ups:**
- Simulator reflection-loop hardening: read last 1-3 history.jsonl entries in Phase A and add closed bugs as regression checks so they are not re-found.
- Snap-to-walls polygon strategy: replace synthetic 80%-quad placeholder with real measurement (read PDF vector edges, snap to walls).
- Lite PDF page classifier: auto-tag floor/site/cover from title block OCR or layout hints, eliminating the manual tagging step.

---

<!-- SIM-2 (2026-05-24) and LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) are the 2 sessions kept in this file -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
