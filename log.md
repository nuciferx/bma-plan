# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-20 — HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — PASS (branch: main)

**What changed:** Fixed the calibration UX gap that caused the user to measure title-deed land (โฉนด 2 ไร่ 2 งาน = 4,000 m²) ~1% smaller than the deeded area. The investigation confirmed the area math is exact (shoelace with precise pts_per_m float, 0.08% error on reference geometry); the loss came from snap silently capturing a different — longer — reference line than the one the user intended to click. Four coordinated changes: (1) HT-ACC-1: `calibRaw[]` captures the raw pre-snap click points alongside `calibPts`; after the 2nd click, if snap moved the captured line >5% from the user's click the calib panel shows an orange warning with raw→snapped coordinates and a reminder to zoom in before re-clicking — this was the root cause of the systematic measurement loss. (2) HT-ACC-2: Verify Scale promoted to a ribbon button beside Set Scale; longest-baseline tip added to calib panel; `finishCalib` status nudges to Verify; `activateAreaTool('land')` hints to use arc edges on curved boundaries. (3) HT-ACC-3: `status-bar.js` `updateAnalyseUI` sets a tooltip on `#lbl-scale` and `#scale-badge` showing exact `pts_per_m` and precise `1:N.x` — the visible label stays rounded, area computation uses the full float, so there is no measurement change. (4) HT-NAV-1: navigation root-cause investigation concluded — no code fix required; `getNextPage`/`loadPage` logic is sound; exception observed by journey-tester was a Playwright timing artifact. New E2E marker `HT_ACC_OK` (5 sub-checks). Total full E2E: EXIT 0, 102 _OK markers.

**Why:** `/bma-human-test` 2026-05-20 on real Downloads PDFs (SCR_Permit_Layout, raster ข.4) returned JOURNEY_OK with no CRASH/BROKEN. However, the user subsequently reported measuring title-deed land at ~1% less than the deeded 4,000 m². Journey-tester analysis isolated the discrepancy: area math is EXACT (verified analytically); the only plausible source is the calibration step itself — snap grabbing a longer nearby vector line drives pts_per_m too high, making all derived areas proportionally smaller. The orange snap-deviation warning (HT-ACC-1) directly surfaces this failure mode to the user at the moment of calibration.

**Files touched:**
- `proto/ui.html`: `calibRaw[]` state + snap-deviation warning in calib panel; Verify ribbon button (`#btn-scale-verify`); longest-baseline tip; `finishCalib` Verify nudge; `activateAreaTool('land')` arc hint
- `proto/static/js/status-bar.js`: `updateAnalyseUI` adds tooltip to `#lbl-scale` and `#scale-badge` (pts_per_m + precise 1:N.x)
- `proto/e2e_ui_test.py`: `_test_ht_acc_calibration` (5 sub-checks) + `HT_ACC_OK` marker

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py                   → PASS
proto/e2e_ui_test.py full                                          → EXIT 0 (102 _OK markers, 0 E2E_FAIL)
  NEW: HT_ACC_OK GREEN (5 sub-checks:
       verifyBtnExists, verifyBtnWired, longestTip,
       calibRawExists, devWarnsWrongLine, devQuietWhenClose)
  Static-asset safety: NO_BOM on app.css + status-bar.js
  CACHE_OK + MAIN_UI_OK (cssLinkPresent/statusBarJsLoaded true) — assets serve
  All prior 101 markers retained. Zero regression.
UI_REGRESSION_PASS. Forbidden-surface diff scan CLEAN.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED (area math proven exact; this series fixes calibration UX, not the formula)
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED (calibRaw captures pre-snap raw clicks; snap logic itself not modified)
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibRaw` is in-memory only, not persisted; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Static JS touched (`status-bar.js`) → `UI_MANUAL_TEST.md` updated with 6-check HT-ACC calibration accuracy manual checklist.
- `calibRaw` reset is confirmed in `cancelCalib` / `finishCalib` / `loadPage` — no stale state across pages.
- HT-NAV-1 closed as no-fix: `getNextPage`/`loadPage` nav logic is sound; `REAL_OK` already exercises real multi-page navigation.
- Next: `/bma-sandbox-test` on large Downloads PDFs (589 MB BKM, 59 MB RM1) for pre-release stress, or Discovered backlog items.
- Commit: `c0834f0` on main.

---

## 2026-05-20 — BUG-20260520-zen-exit-rp-restore — PASS (branch: main)

**What changed:** Defensive fix making the right panel always recoverable after Zen Mode exits. Three coordinated changes: (1) F11 keydown handler now calls `preventDefault()` unconditionally so the browser can never enter native fullscreen and leave `body.zen` stuck — Zen exit (`if(body.zen || ...)`) always works; entering Zen is still blocked mid-draw or when a modal is open. (2) F9/F10 keybindings added — F9 calls `toggleLeftPanel`, F10 calls `toggleRightPanel`; the restore tabs already advertised [F9]/[F10] labels but had no handler wired. (3) `proto/static/css/app.css`: dead sibling selector `#right-panel.collapsed~#workspace #rp-restore-tab` (workspace precedes panel in DOM so `~` never matched) replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`; the existing attribute-based fallback `.canvas-wrap[data-right-collapsed="1"]` kept. New E2E test `_test_bug_zen_exit_rp_restore` + marker `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` (6 sub-checks).

**Why:** User-reported: after hiding L+R panels → F11 Zen → exit to normal, the restore tab (`#rp-restore-tab`) was gone and the right panel could not be re-shown. Headless repro (3 variants in `artifacts/repro_zen_exit_rp.py`) could not reproduce — tab returned to flex in Playwright. Lead hypothesis: real-browser native F11 fullscreen collides with the app F11 `!anyModal && !mPts.length` guard; when a modal is open or mid-draw, `preventDefault` was skipped, the browser entered native fullscreen, and `body.zen` desynced/stayed stuck causing `body.zen .panel-restore-tab{display:none}` to hide the tab permanently. Fix is defensive — recoverable regardless of exact trigger.

**Files touched:**
- `proto/ui.html`: F11 handler — unconditional `preventDefault()` + widened exit condition; F9→`toggleLeftPanel` + F10→`toggleRightPanel` added
- `proto/static/css/app.css`: `#right-panel.collapsed~#workspace #rp-restore-tab` dead rule replaced with `:has()` selector; zen/overview `display:none !important` overrides unchanged
- `proto/e2e_ui_test.py`: `_test_bug_zen_exit_rp_restore` (+6 sub-checks) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker wired into `main()`

**Tests:**
```
py_compile proto/server.py proto/e2e_ui_test.py                → PASS
proto/e2e_ui_test.py full                                       → EXIT 0 (101 _OK markers, 0 E2E_FAIL)
  NEW: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks:
       inZen, zenExitedMidDraw, f10Toggled, tabVisibleWhenCollapsed,
       tabHiddenInZen, tabVisibleAfterZenExit)
  CACHE_OK / MAIN_UI_OK (cssLinkPresent + cssVarLoaded true) — CSS still serves
  All prior 100 markers retained. Zero regression.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Static CSS touched → `UI_MANUAL_TEST.md` updated with 5-check Zen exit / F9/F10 / restore-tab checklist.
- Headless repro could not reproduce the original trigger — fix is defensive. Real-browser manual test (checklist item 3: open modal then F11) is the only way to confirm the native-fullscreen desync path is closed.
- Commit: `9453777` on main.

---

<!-- HT-ACC series (2026-05-20) and BUG-20260520-zen-exit-rp-restore are the 2 sessions kept in this file -->
<!-- INV-2026-05-20-002/003/004 Layer L1+L2+L3 and earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
