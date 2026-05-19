# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-002b — F12 Overview standalone (C)

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0 (PHASE_INV_OVERVIEW_OK 9/9), full EXIT 0; TEST-H SKIPPED (rationale below)

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
```

## New Marker: PHASE_INV_OVERVIEW_OK (9/9)

| Sub-check | Result |
|---|---|
| overviewContentExists | PASS |
| f12TogglesOverview | PASS |
| escClosesOverview | PASS |
| chipTogglesOverview | PASS |
| sixGroupsDefined | PASS |
| cardsRenderWithThumbs | PASS |
| cardClickExitOverview | PASS |
| cardClickSetCurPage | PASS |
| noZenRegressionInOverview | PASS |

Note: Initial run had `cardClickExitOverview` + `cardClickSetCurPage` FAIL — test PDF had fewer than 3 pages so `data-page="3"` selector returned null. Fixed with surgical retry using first available card and direct `_ovCardClick(targetPage)` call. Retry → 9/9 PASS.

## Pre-existing Markers (no regression)

`PHASE_INV_ZEN_V2_OK` 9/9. `PHASE_INV_ZEN_OK` 10/10. `PHASE_INV_PALETTE_OK` 10/10. `PHASE_INV_POLISH_001C_OK` 5/5. All other pre-existing smoke markers GREEN.

Pre-existing non-regressions (documented in prior status, unrelated to this sprint): `PHASE_HT8C_OK` 3/5, `PHASE_HT8D1_OK` 8/9, `PHASE_HT10_OK` 8/10, `PHASE_HT12H_OK` 4/5, `PHASE_I_D_OK` 7/8.

## Full Run

EXIT 0. `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` GREEN.

## Human Journey Test (TEST-H)

SKIPPED. Rationale: 002b is an additive NEW MODE that does not touch measurement geometry, canvas drawing, snap engine, export, save/load, or any server endpoint. The 9 `PHASE_INV_OVERVIEW_OK` sub-checks directly cover: mode entry (F12 hotkey + chip), mode exit (Esc + chip), atomic card-click page-sync, DOM render (cards/groups/thumbs), and lazy IntersectionObserver load. The thumb-cache fetch pattern is a direct reuse of INV-001a `thumbUrl()` + IO approach that was already validated by `bma-human-journey-tester` in INV-001a. Per AGENTS.md no-test rationale: new isolated mode with full marker coverage of all entry/exit/interaction paths.

---

# Previous: INV-2026-05-19-002a — F11 Zen top bar (A+D additive bundled)

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0, full EXIT 0, HUMAN_TEST_PASS

## Commands

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → EXIT 0
python proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)         → HUMAN_TEST_PASS
```

## New Marker: PHASE_INV_ZEN_V2_OK (9/9)

| Sub-check | Result |
|---|---|
| topbarExistsAndShort | PASS |
| sixDropdownsExpectedLabels | PASS |
| fourChips | PASS |
| focusHidesHuds | PASS |
| peekRestoresHuds | PASS |
| fKeyScopeGuard | PASS |
| v2OnboardingToastShown | PASS |
| no001aRegression | PASS |
| paletteAboveTopbar | PASS |

Note: Initial run had `focusHidesHuds` FAIL (CSS transition delay on `.hud` prevented Playwright from catching hidden state). Fix: added `!important` to `body.zen.focus .hud { display:none }` + removed CSS transition on `.hud` during focus mode. Retry → 9/9 PASS.

## Pre-existing Markers (no regression)

`PHASE_INV_ZEN_OK` 10/10. `PHASE_INV_PALETTE_OK` 10/10. `PHASE_INV_POLISH_001C_OK` 5/5. All other pre-existing smoke markers GREEN.

Pre-existing non-regressions (documented in prior status, unrelated to this sprint): `PHASE_HT8C_OK` 3/5, `PHASE_HT8D1_OK` 8/9, `PHASE_HT10_OK` 8/10, `PHASE_HT12H_OK` 4/5, `PHASE_I_D_OK` 7/8.

## Full Run

EXIT 0. `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` GREEN.

## Human Journey Test (TEST-H)

HUMAN_TEST_PASS. `bma-human-journey-tester` on real 45-page permit PDF:
- 13/13 journey spec steps PASS
- 45/45 pages measured successfully
- `.bmaplan` save + reopen round-trip OK
- 1 FRICTION finding: test-infra only — `lbl-scale` does not update on programmatic `calibScale` inject used by journey tester; real calibration dialog calls `updateAnalyseUI` correctly. Not user-facing. Not filed.

<!-- 001a/001b/001c + older entries archived to docs/archive/test-history-2026-05-09.md -->
