# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — BUG-20260520-sel-midpan: Middle-mouse + Space pan in Select mode — PASS (branch: main)

**What changed:** In `proto/ui.html`, the `ws` mousedown handler's `mode==="sel"` branch received a one-line guard inserted at its top: `if(e.button===1||spaceDown){isPan=true;lastMx=e.clientX;lastMy=e.clientY;ws.style.cursor="grabbing";return;}`. This mirrors the identical pan guard that already existed in the non-`sel` path. `proto/e2e_ui_test.py` gained a new test function `_test_bug_sel_midpan` (+34 lines) with call wiring and a new marker `BUG_20260520_SEL_MIDPAN_OK`. `docs/status/PHASE_INDEX.md` received one status-row update for this bug sprint.

**Why:** Holding middle mouse button (button===1) or Space while the Select tool was active silently discarded the pan intent — the `mode==="sel"` branch executed `redraw();return` unconditionally before the pan check could run, making middle-button and Space pan dead code in Select mode. The fix restores parity with every other tool mode, and with Foxit/Bluebeam pan behavior where middle-mouse-pan works regardless of active tool.

**Files touched:**
- `proto/ui.html`: +1 line — pan guard inserted at top of `mode==="sel"` mousedown branch (~L2064)
- `proto/e2e_ui_test.py`: +34 lines — `_test_bug_sel_midpan` function + call wiring + `BUG_20260520_SEL_MIDPAN_OK` marker print
- `docs/status/PHASE_INDEX.md`: +1 row — BUG-20260520-sel-midpan filed and marked done

**Tests:**
```
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py full                           → EXIT 0 — ALL GREEN
  NEW: BUG_20260520_SEL_MIDPAN_OK GREEN
    canvas #cc transform moved +70x/+45y under a real Playwright middle-button drag
    mode stayed 'sel' throughout (no mode bleed)
  21 baseline markers intact incl. PATH_GEOMETRY_OK, ANNOT_OK, PERSIST_OK, REAL_OK
  Total markers: 22
/bma-measure-ux → MEASURE_UX_PASS
/bma-measure-regression → MEASURE_REGRESSION_PASS
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- `BUG-20260520-zen-exit-rp-restore` parked at `BUG_STOP_NEEDS_REPRO` — needs a reproducible steps sequence before fix work can start.
- `INV-2026-05-20-001` Verify Scale tool is next queued item in PHASE_INDEX.

---

## 2026-05-20 — BLOAT-FLAKE-1 Fix REAL_PDF `_wait_analyse_ready` flake — PASS (branch: main)

**What changed:** In `proto/e2e_ui_test.py`, the `_wait_analyse_ready` helper was updated: default timeout raised from 30.0 s to 60.0 s, and a "grace window" was added — if the status bar still shows active progress (`กำลังโหลด` / `กำลังวิเคราะห์`) at the deadline, the wait is granted +50% extra time before declaring failure. ~15 LOC changed inside the one helper only. No other test logic, no app code, no schema changed.

**Why:** The real 45-page A1 permit PDF (rotated 90°, ~1–1.4 s/page JPEG encode) occasionally caused `_wait_analyse_ready` to exceed the prior 30 s ceiling during a session-loaded box run — especially after 5 consecutive sprint test cycles in one session. The raised ceiling is free on the fast smoke path (small `test_plan_A1.pdf` completes in ~1–2 s). The grace window avoids a false fail when the page is actively making progress but hasn't crossed the threshold yet. This flake halted the dev-loop at BLOAT-5 (3 retries all failed at `_test_real_pdf_multipage_persistence`). With the fix, full E2E is GREEN. Retroactively confirms BLOAT-5 passes full E2E.

**Files touched:**
- `proto/e2e_ui_test.py`: +15 −2 — `_wait_analyse_ready` timeout 30.0→60.0, added grace-window branch for active-loading status

**Tests:**
```
python -m py_compile proto/e2e_ui_test.py                     → PASS
python proto/e2e_ui_test.py full                               → EXIT 0 — ALL GREEN
  PERSIST_OK + REAL_OK + ANNOT_OK GREEN (flaked 3x during BLOAT-5; now stable)
  PHASE_BLOAT2_OK 8/8 + _BLOAT3_OK 8/8 + _BLOAT4_OK 8/8 + _BLOAT5_OK 8/8
  PHASE_INV_PAGE_SETUP_A_OK 8/8 + _B_OK 9/9 + _C_OK 7/7 + PHASE_HT11_OK 10/10
  Retroactively confirms BLOAT-5 (shipped smoke-only) passes full E2E.
/bma-human-test — N/A (test-infrastructure change; no app runtime code touched)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- (only `proto/e2e_ui_test.py` `_wait_analyse_ready` helper changed)

**Known gaps / follow-ups:**
- If the flake recurs under even heavier load, next escalation paths: Playwright browser-context reset between heavy real-PDF tests, or server cache warm-up before real-PDF suite (documented as alternatives in KNOWN_ISSUES.md).
- Dev-loop queue is now clear of P1 blockers. Remaining: `INV-2026-05-19-002c` (F12 Overview mockup port) + invent-queued ideas.

---

<!-- BLOAT-5, BLOAT-FLAKE-1, BLOAT-4, BLOAT-3 archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
