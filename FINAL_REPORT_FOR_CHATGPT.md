# FINAL_REPORT_FOR_CHATGPT.md — Sprint Outcome Report

> Full report history: [docs/archive/reports-2026-05-09.md](docs/archive/reports-2026-05-09.md)

---

# Latest: LITE-0 — scaffold standalone /lite/ tree (epic INV-2026-05-21-001 sub-sprint 1) — PASS

**Date:** 2026-05-21
**Branch:** main

## Outcome

PASS. LITE-0 scaffolds the `/lite/` sibling tree as the foundation of BMA-Plan Lite (Approach A: vendored-copy + contract-test). The measurement engine is vendored byte-identical from `proto/ui.html` and protected by an anti-drift parity gate that verifies both source byte-identity (10 fns + 2 consts) and numeric parity. The LITE-0 UI shell self-tests on load (unit square = 25.00 m2, 0 console errors). Proto full E2E baseline is unchanged at 102 _OK markers — zero proto/ edits were made.

## What was delivered

- `lite/static/js/measure-engine.js` — vendored engine (RS, pdfToC, cToPdf, polyAreaM2, polyMetrics, polySelfIntersects, pathAreaM2, 6 path helpers) + lite-only `objectAreaM2Lite`
- `lite/tests/test_measure_parity.py` + `lite/tests/fixtures/measure_parity_v1.json` — anti-drift parity gate (MEASURE_PARITY_OK)
- `lite/server_lite.py` — skeleton FastAPI (static mount + /health + /); endpoints deferred to LITE-1
- `lite/launch_lite.py` — free-port (8100+) launcher
- `lite/ui-lite.html` — LITE-0 shell with self-test
- `lite/README.md` — vendoring contract + version-sync policy
- `docs/invent/bma-plan-lite-standalone.md` — invent research + approach decision record
- `proto/sandbox/invent-bma-plan-lite-standalone.html` — invention spike
- `docs/status/PHASE_INDEX.md` — LITE-0 sprint card added + status done

## What's next

- LITE-1: backend endpoints (`/upload`, `/page/{n}`, `/thumb`) reusing PyMuPDF for the raster render path.
- Epic continues LITE-1..7 (chrome, tools, dimension rendering, save/load+count, export, packaging).

## Position in Plan

Phase 1 adjacent — BMA-Plan Lite epic (INV-2026-05-21-001). LITE-0 is the scaffold sprint (sub-sprint 1 of 8). No Phase 2 scope boundary crossed. Proto/ runtime untouched. Parity gate enforces that any future proto engine change is immediately visible.

---

# Previous: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX — PASS

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

<!-- BUG-20260520-zen-exit-rp-restore and older reports archived to docs/archive/reports-2026-05-09.md -->
