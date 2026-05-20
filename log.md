# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — INV-2026-05-20-001 Verify Scale tool — PASS (branch: main)

**What changed:** Implemented the GO'd Verify Scale feature (approach A from `docs/invent/verify-scale.md`) into `proto/ui.html`. Replaced the `verifyScale()` stub (previously just opened Scale Manager) with a full second-reference cross-check flow: Scale-menu "Verify Scale" → reuses the existing 2-point calibration draw → `verifyFinish()` computes `%dev = 100·|d_meas − d_enter| / d_enter` → a verify modal renders a green (<0.5%) / yellow (<2%) / red (≥2%) confidence band plus measured distance, entered distance, area-impact estimate (≈2×%dev), and three action buttons: Accept / Re-calibrate / Average. A new `calibPanelOk()` router was added so the calib panel OK button calls `verifyFinish()` when in verify mode and `finishCalib()` otherwise — `finishCalib()` itself is unchanged. New `#verify-modal` HTML is inline-styled (no `app.css` edit). Schema is additive: `calibScale.verifyResult{pct, action, verifyPts_per_m, ts}` round-trips automatically through `_makeProjBlob()` / `applyLoadedProject()` because it rides on `pageStore.calibScale`. The `anyModal` guard was extended to include `#verify-modal`. `proto/e2e_ui_test.py` gained `_test_verify_scale` (9 sub-checks) and the new `INV_VERIFY_SCALE_OK` marker wired into `main()`.

**Why:** Calibration-by-single-reference gives no quality signal — a mis-click or misread dimension passes silently. Verify Scale closes this gap by letting the user immediately draw a second known dimension and get instant numeric feedback. The %dev band (green/yellow/red) is the core UX value: it quantifies systematic scale error and gives three actionable recovery paths (accept the current scale, discard and re-calibrate, or average the two references). This was the GO'd outcome of the invent pipeline (spike 10/10 in `proto/sandbox/invent-verify-scale.html`). The feature is purely additive — no existing calibration path was changed.

**Files touched:**
- `proto/ui.html`: +82/−5 — calib panel h3 id + OK button re-pointed to `calibPanelOk`; `#verify-modal` HTML block; new fns `verifyScale` / `verifyFinish` / `openVerifyModal` / `_verifyBand` / `_verifyWriteResult` / `_afterVerifyScaleChange` / `verifyAccept` / `verifyRecalibrate` / `verifyAverage` / `closeVerifyModal`; `cancelCalib` reset of `calibVerifyMode` + panel title; `anyModal` guard extended.
- `proto/e2e_ui_test.py`: +124 lines — `_test_verify_scale` (9 sub-checks) + `INV_VERIFY_SCALE_OK` marker wired into `main()`.

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py           → PASS
proto/e2e_ui_test.py full                                  → EXIT 0
  NEW: INV_VERIFY_SCALE_OK = 9/9 all:True
    sub-checks: domAndHelpers, guardWhenNoScale, greenBandZeroDev,
                acceptWritesResult, redBandHighDev, recalibrateSetsPpm,
                averageSetsPpm, finishCalibIntact, roundTripSaveLoad
  ANNOT_OK / PERSIST_OK / REAL_OK / PROJECT_OK / XLSX_OK / PATH_GEOMETRY_OK — GREEN
  Pre-existing 5 markers (PHASE_HT8C_OK, PHASE_HT8D1_OK, PHASE_HT10_OK,
    PHASE_HT12H_OK, PHASE_I_D_OK) remain at same pre-sprint state —
    confirmed pre-existing env artifacts (Python 3.14 + newer Chromium in
    this sandbox; canonical 3.11 env has them green). Zero regression.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibScale.verifyResult` optional field; version stays 1)
- ✅ `finishCalib()` — UNCHANGED (`calibPanelOk` wrapper routes to it; original fn body intact)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Follow-on D (live canvas badge showing %dev after verify) — deferred.
- Follow-on E (fold verifyResult into phase1Warnings + export note) — deferred, recommended next.
- Follow-on C (dual-axis H/V stretch detector) — deferred.
- Manual Chrome verification of `#verify-modal` visual rendering recommended (add to `UI_MANUAL_TEST.md`).
- 5 pre-existing env-artifact markers worth a separate housekeeping note (not this sprint).
- `BUG-20260520-zen-exit-rp-restore` still parked at `BUG_STOP_NEEDS_REPRO` — awaiting user repro steps.
- Invent artefacts: `docs/invent/verify-scale.md` + `proto/sandbox/invent-verify-scale.html`. `PHASE_INDEX` row `INV-2026-05-20-001` → mark done.

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

<!-- INV-2026-05-20-001, BUG-20260520-sel-midpan are the 2 sessions kept in this file -->
<!-- BLOAT-FLAKE-1, BLOAT-5, BLOAT-4, BLOAT-3 archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
