# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-25 — Centerline Snap arc (invent → 2 sprints → 2 bugfixes) — PASS (branch: main)

**What changed:** ผู้ใช้รายงาน "วัดที่ดินเส้นปะได้ 3 ค่าต่างกัน" จาก `SCR_ผังต่อโฉนด.pdf` (cadastral deed plan เส้นปะหนา) → รัน `/bma-invent` 7-phase pipeline (invent-id `2026-05-24-22-14`, spike commit `0208314`) → ผลลัพธ์เป็น 2 sprints: INV-2026-05-24-002a สำหรับ proto (commit `6db0461`) — NEW `proto/static/js/centerline-snap.js` 208 LOC (Otsu threshold + Zhang-Suen thinning + ROI snap `CL_snapCanvasToCenterline` + post-draw PCA corner refinement `CL_refineCornersOnSkeleton`; no CDN dependency); `proto/ui.html` +15 lines net (script include, "⊙ CL" Helpers ribbon button, `toggleCenterlineSnap()`, `centerlineSnapOn` state, area mousedown click-hook, `finishCurrentArea` refine call, `PREFS.measure.centerlineSnap` default false, `_applyCenterlineSnapPref()` at boot + Settings save); `proto/e2e_ui_test.py` +162 lines (`_test_centerline_snap` 10 sub-checks, `PHASE_CENTERLINE_SNAP_OK`). Accuracy: maxDelta=0.140% ≤ 0.5% target. Additive schema: `obj.traceMode = "centerline-roi"` on corrected polygons; legacy .bmaplan loads fine. INV-2026-05-24-002b สำหรับ lite (commit `ad920c6`) — NEW `lite/static/js/centerline-snap.js` 306 LOC (Section A = proto algorithm vendored verbatim byte-identical per drift-locked contract; Section B = lite glue: `CL_litePolyClick` + `CL_litePolyFinish` + self-installing toggle button + localStorage persistence); `lite/ui-lite.html` +2 net lines (1197→1199, within 1200 cap); NEW `lite/tests/test_centerline_snap.py` 235 LOC, LITE_CENTERLINE_SNAP_OK 8/8 (expanded from 6 after bugfixes; accuracy maxDelta=0.1778%). Commit `916d379` backfilled PHASE_INDEX.md. Post-ship user-reported 2 bugs in lite same day: BUG-20260525-lite-cl-dpr (commit `ff3f9fe`) — DPR coord mismatch: `cv.width = clientWidth * dpr` makes canvas bitmap dpr× larger than CSS; `getImageData` reads bitmap pixels but `e.offsetX/Y` are CSS pixels → on DPR>1 (Windows 125/150%, Retina 200%) ROI read wrong region → no dark pixels → `found:false` → zero effect; fix: multiply CSS coords by dpr before passing to algorithm, divide back after; also added inline `.active` CSS (green bg + glow) that was missing, making toggle visually indistinguishable; +2 test sub-checks (dprBridge + activeCssRule). BUG-20260525-lite-cl-position (commit `5783df4`) — CL button at `position:fixed; bottom:8px; right:8px` overlapped `#hud-br` zoom controls; fix: insert via `insertBefore(firstChild)` into `#hud-br` as flex-column with 4px gap; fallback to top-right float if `#hud-br` missing. All tests GREEN after both fixes.

**Why:** เส้นปะหนาบน cadastral deed plan ไทยกว้าง 1-3 mm — trace outer/inner/center ให้พื้นที่ต่างกัน แต่ถูกต้องทางกฎหมายคือ centerline. Research phase (bma-researcher haiku) ยืนยัน `PRIOR_ART_PARTIAL` — Zhang-Suen thinning (1984) มีอยู่แล้ว แต่ไม่มี incumbent (Bluebeam/Foxit/QGIS/AutoCAD/ArcGIS) expose stroke-centerline เป็น user choice → BMA-specific gap ที่มีคุณค่า. Diverge phase (bma-inventor sonnet) ให้ 5 approaches; Approach A (click-time local-ROI Zhang-Suen) score 27/30, Spike pass 3 + PCA = maxDelta 0.185% PASS 4/4. ผู้ใช้ approve GO + ขอลง lite ด้วย. DPR bug ไม่ถูกจับโดย initial tests เพราะ headless Chromium + offscreen canvas test รายงาน DPR=1 เสมอ — Windows text scaling 125/150% คือ surface จริงที่ trigger.

**Files touched:**
- `docs/invent/centerline-snap-dashed-boundary.md`: NEW — full 7-phase invent record
- `proto/sandbox/invent-centerline-snap-dashed-boundary.html`: NEW — interactive spike (?auto=1 runs self-test), commit `0208314`
- `proto/static/js/centerline-snap.js`: NEW 208 LOC — Otsu threshold, Zhang-Suen thin, CL_snapCanvasToCenterline, CL_refineCornersOnSkeleton (IIFE, no CDN)
- `proto/ui.html`: +15 lines net — script include, ribbon button, toggleCenterlineSnap state+fn, click hook, finishCurrentArea hook, PREFS default, boot init
- `proto/e2e_ui_test.py`: +162 lines — _test_centerline_snap 10 sub-checks + PHASE_CENTERLINE_SNAP_OK
- `lite/static/js/centerline-snap.js`: NEW 306 LOC — Section A proto algo byte-identical, Section B lite glue + toggle button
- `lite/ui-lite.html`: +2 lines net (1197→1199) — script include + poly click hook + finishDraft refinement hook; bugfixes: dpr multiply/divide, inline .active CSS
- `lite/tests/test_centerline_snap.py`: NEW 235 LOC; grew 6→8 sub-checks (dprBridge + activeCssRule added post-bugfix)
- `docs/status/PHASE_INDEX.md`: 002a + 002b sprint rows added, backlog flipped, commit hashes backfilled (commit `916d379`)

**Tests:**
```
proto:
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → 18/18 PASS
python proto/e2e_ui_test.py full                           → 21/21 PASS + PHASE_CENTERLINE_SNAP_OK 10/10
  accuracy maxDelta=0.140% (target ≤0.5%)
  PROJECT_OK + PERSIST_OK confirm obj.traceMode round-trips through save/load

lite:
python lite/tests/test_centerline_snap.py  → LITE_CENTERLINE_SNAP_OK 8/8 PASS
  accuracy maxDelta=0.1778% ≤0.5%; dprBridge + activeCssRule regression locks added post-bugfix
python lite/tests/test_measure_parity.py   → MEASURE_PARITY_OK GREEN (no regression)
wc -l lite/ui-lite.html                    → 1199 (≤1200 cap) PASS

Commits: 0208314 (invent spike GO) → 6db0461 (INV-002a proto)
       → ad920c6 (INV-002b lite) → 916d379 (roadmap chore)
       → ff3f9fe (DPR bugfix) → 5783df4 (button position bugfix)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (centerline snap injects corrected pts before area math reads them; uses canvas getImageData public API only)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (zero server changes across entire arc)
- ✅ `.bmaplan` schema — additive only (NEW optional `obj.traceMode`; absence = legacy; proto↔lite cross-open parity preserved)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail (centerline-of-stroke is geometry/snap, in-scope Phase 1)
- ✅ Lite-vendoring contract — `lite/static/js/measure-engine.js` UNCHANGED; `centerline-snap.js` Section A byte-identical to proto
- ✅ Lite size cap — `ui-lite.html` 1199/1200 (1-line headroom); all `lite/static/js/*.js` ≤1000

**Known gaps / follow-ups:**
- Vector PDF route (Approach E from diverge) — extract stroke-width from `extract_snaps_typed()` server response, offset by w/2 when snap.t==='nl'. Separate sprint, does not depend on 002a/b.
- Real-raster threshold robustness — current Otsu works on synthetic + first user PDF. If contrast-faded scans misfire, swap to adaptive Sauvola/Niblack. Wait for user reports.
- Sharp corner < 60° fallback — PCA fit from 5 samples can be unstable on very short edges. Add step-1-only fallback when refine confidence is low.
- Real-user verification — ask user to re-measure SCR_ผังต่อโฉนด.pdf with CL toggle ON on both proto + lite, confirm 3 traces converge.

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

<!-- Centerline Snap arc (2026-05-25) and SIM-2 (2026-05-24) are the 2 sessions kept in this file -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
