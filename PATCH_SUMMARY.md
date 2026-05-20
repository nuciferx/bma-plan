# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX

Branch: main

Date: 2026-05-20

## Outcome: PASS — Calibration workflow accuracy fixed; area math proven exact (0.08% error); silent wrong-line snap now surfaced as orange warning; Verify Scale promoted to ribbon; tooltip shows exact pts_per_m. Full E2E EXIT 0, 102 _OK markers. NEW HT_ACC_OK GREEN.

## Summary

/bma-human-test on real Downloads PDFs (SCR_Permit_Layout, raster ข.4) returned JOURNEY_OK. The user then reported measuring a 4,000 m² title-deed lot ~1% smaller than deeded. Investigation confirmed the area math is exact (shoelace formula, precise pts_per_m float, 0.08% geometric error). Root cause: snap silently captured a longer nearby vector line instead of the user's intended reference, driving pts_per_m too high and making all derived areas proportionally smaller. HT-ACC-1 surfaces this failure mode with an orange warning the moment it occurs. HT-ACC-2 promotes the Verify Scale button and adds calibration UX nudges. HT-ACC-3 adds an exact pts_per_m tooltip to the scale status fields (no measurement change). HT-NAV-1 required no code fix.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | `calibRaw[]` captures pre-snap click coords; snap-deviation >5% triggers orange warning in calib panel; `#btn-scale-verify` ribbon button added beside Set Scale; longest-baseline tip in calib panel; `finishCalib` nudges to Verify; `activateAreaTool('land')` hints to use arc edges |
| `proto/static/js/status-bar.js` | `updateAnalyseUI` sets tooltip on `#lbl-scale` and `#scale-badge` showing exact `pts_per_m` and precise `1:N.x` (visible label stays rounded; area float unchanged) |
| `proto/e2e_ui_test.py` | `_test_ht_acc_calibration` (5 sub-checks) + `HT_ACC_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED (area math proven exact; this series fixes calibration UX, not the formula)
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` internals — UNCHANGED (`calibRaw` captures raw clicks before snap; snap logic not modified)
- `.bmaplan` schema version stays 1; `calibRaw` is in-memory only, not persisted

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py            → PASS
proto/e2e_ui_test.py full                                   → EXIT 0
  102 _OK markers, 0 E2E_FAIL
  NEW: HT_ACC_OK GREEN (5 sub-checks:
       verifyBtnExists, verifyBtnWired, longestTip,
       calibRawExists, devWarnsWrongLine, devQuietWhenClose)
  CACHE_OK, MAIN_UI_OK (cssLinkPresent/statusBarJsLoaded true) confirm assets serve
  Static-asset safety: NO_BOM on app.css + status-bar.js
  All prior 101 markers retained. Zero regression.
  UI_REGRESSION_PASS. Forbidden-surface diff scan CLEAN.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` internals — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (`calibRaw` in-memory only; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix

Branch: main

Date: 2026-05-20

## Outcome: PASS — Right panel is now always recoverable after Zen Mode. F11 reliably exits Zen, F9/F10 toggle panels, restore tab no longer depends on a dead CSS selector. Full E2E EXIT 0, 101 _OK markers. NEW BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN.

## Summary

Defensive fix for a user-reported bug where the right-panel restore tab (`#rp-restore-tab`) disappeared after Zen Mode exit, making the right panel irrecoverable. Root cause: native-browser F11 fullscreen could collide with the app's F11 `!anyModal && !mPts.length` guard, leaving `body.zen` stuck and the CSS rule `body.zen .panel-restore-tab{display:none}` hiding the tab. The restore-tab visibility CSS also used a dead sibling combinator (`#right-panel.collapsed~#workspace #rp-restore-tab`) that never matched because workspace precedes panel in DOM. Fix is defensive: F11 always calls `preventDefault()`; F9/F10 keyboard recovery added; dead CSS selector replaced with `:has()`.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | F11 handler: unconditional `preventDefault()` + widened exit condition; F9 and F10 keybindings added |
| `proto/static/css/app.css` | Dead sibling selector replaced with `body:has(#right-panel.collapsed) #rp-restore-tab{display:flex}`; attribute fallback + zen/overview overrides kept |
| `proto/e2e_ui_test.py` | `_test_bug_zen_exit_rp_restore` (6 sub-checks) + `BUG_20260520_ZEN_EXIT_RP_RESTORE_OK` marker |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive only (untouched)

## Tests Run

```
py_compile proto/server.py proto/e2e_ui_test.py            → PASS
proto/e2e_ui_test.py full                                   → EXIT 0
  101 _OK markers, 0 E2E_FAIL
  NEW: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks)
  CACHE_OK, MAIN_UI_OK (cssLinkPresent + cssVarLoaded true) confirm CSS serves
  All prior 100 markers retained. Zero regression.
  Static-asset safety: NO_BOM on app.css. UI_REGRESSION_PASS.
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — additive only (untouched; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

<!-- Older entries (INV-2026-05-20-002/003/004 and earlier) archived to docs/archive/patch-history-2026-05-09.md -->
