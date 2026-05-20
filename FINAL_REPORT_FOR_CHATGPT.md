# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX — PASS

**Date:** 2026-05-20
**Branch:** main
**Commit:** `c0834f0`

## Outcome

PASS. Full E2E EXIT 0, 102 _OK markers, 0 E2E_FAIL. The area math in BMA-Plan is exact — shoelace formula with a precise pts_per_m float shows 0.08% geometric error, well within any practical tolerance. A /bma-human-test session on real Downloads PDFs revealed the user's ~1% measurement loss was a calibration UX failure: snap silently captured a longer nearby vector line as the reference, driving pts_per_m too high and making all derived areas proportionally smaller. This series surfaces that failure mode at the moment it occurs (HT-ACC-1 orange warning), promotes the Verify Scale workflow to the ribbon (HT-ACC-2), and adds an exact pts_per_m tooltip to the scale status fields (HT-ACC-3). HT-NAV-1 required no code change. New E2E marker `HT_ACC_OK` GREEN (5 sub-checks). Static-asset safety confirmed: NO_BOM on app.css and status-bar.js, CACHE_OK, MAIN_UI_OK. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

## What was delivered

- `proto/ui.html` — `calibRaw[]` captures the raw pre-snap click coordinates alongside `calibPts`; after the 2nd calibration click, if snap moved the captured line more than 5% from the user's click, the calib panel shows an orange warning ("snap จับเส้นต่างจากที่คลิก") with raw and snapped coordinates and a reminder to zoom in before re-clicking. This is the single highest-impact fix. `calibRaw` resets in `cancelCalib`/`finishCalib`/`loadPage`. Verify Scale promoted to a ribbon button (`#btn-scale-verify`) beside Set Scale. Longest-baseline tip added to calib panel. `finishCalib` nudges user to Verify. `activateAreaTool('land')` hints to use arc edges on curved boundaries.
- `proto/static/js/status-bar.js` — `updateAnalyseUI` sets a tooltip on `#lbl-scale` and `#scale-badge` with exact `pts_per_m` and precise `1:N.x`. The visible rounded label is unchanged; area computation uses the full float; no measurement change.
- `proto/e2e_ui_test.py` — `_test_ht_acc_calibration` (5 sub-checks: verifyBtnExists, verifyBtnWired, longestTip, calibRawExists, devWarnsWrongLine/devQuietWhenClose) + `HT_ACC_OK` marker.
- `UI_MANUAL_TEST.md` — 6-check HT-ACC calibration accuracy manual checklist added (static JS touched → required per AGENTS.md §8).

## What's next

- Run `/bma-sandbox-test` on large Downloads PDFs (589 MB BKM, 59 MB RM1) for pre-release stress testing.
- Pick from Discovered backlog items in PHASE_INDEX.
- Verify Scale follow-on E: fold `calibScale.verifyResult` into `phase1Warnings` (amber when verify not run or %dev >= 2%) + export note in XLSX/CSV.

## Position in Plan

Phase 1 — Measurement workflow accuracy. This series (HT-ACC-1/2/3 + HT-NAV-1) closes the calibration-UX accuracy gap surfaced by /bma-human-test on real Downloads PDFs. Area math correctness confirmed. No Phase 2 scope boundary crossed.

---

# Previous: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix — PASS

**Date:** 2026-05-20
**Branch:** main

## Outcome

PASS. Full E2E EXIT 0, 101 _OK markers, 0 E2E_FAIL. A user-reported bug where the right-panel restore tab vanished after Zen Mode exit has been fixed defensively. F11 now always calls `preventDefault()` preventing native-fullscreen desync; F9/F10 provide keyboard recovery for both panels; the dead sibling CSS selector was replaced with `:has()`. New E2E marker `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` GREEN (6 sub-checks). Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

## What was delivered

- `proto/ui.html` — F11 unconditional `preventDefault()`; exit condition widened to `body.zen || (!anyModal && !mPts.length)`; F9→`toggleLeftPanel` + F10→`toggleRightPanel` keybindings.
- `proto/static/css/app.css` — dead `#right-panel.collapsed~#workspace #rp-restore-tab` rule replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`.
- `proto/e2e_ui_test.py` — `_test_bug_zen_exit_rp_restore` (6 sub-checks) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker.
- `UI_MANUAL_TEST.md` — 5-check Zen exit / F9/F10 / restore-tab manual checklist.
- Commit: `9453777`.

## What's next

(superseded by HT-ACC series — see Latest above)

## Position in Plan

Phase 1 — UI reliability. Closes `BUG-20260520-zen-exit-rp-restore` in PHASE_INDEX. No Phase 2 scope boundary crossed.

---

<!-- Older reports archived to docs/archive/reports-2026-05-09.md -->
