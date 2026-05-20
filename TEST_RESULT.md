# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; 102 _OK markers, 0 E2E_FAIL; NEW HT_ACC_OK GREEN (5 sub-checks); all prior 101 markers retained; zero regression.

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python3.11 proto/e2e_ui_test.py full                            # EXIT 0 — 102 _OK markers
```

## New Marker: HT_ACC_OK — 5 sub-checks

| Sub-check | Result | Description |
|---|---|---|
| verifyBtnExists | PASS | `#btn-scale-verify` element present in ribbon DOM |
| verifyBtnWired | PASS | `#btn-scale-verify` onclick wired to `verifyScale()` |
| longestTip | PASS | Calib panel contains "ใช้เส้นที่ยาวที่สุด" tip text |
| calibRawExists | PASS | `calibRaw` array variable exists and resets correctly |
| devWarnsWrongLine | PASS | Snap deviation >5% triggers orange warning text in calib panel |
| devQuietWhenClose | PASS | Snap deviation <=5% produces no warning |

## Static-Asset Safety

| Check | Result |
|---|---|
| NO_BOM on `proto/static/css/app.css` | PASS — no UTF-8 BOM |
| NO_BOM on `proto/static/js/status-bar.js` | PASS — no UTF-8 BOM |
| `CACHE_OK` | PASS |
| `MAIN_UI_OK` (`cssLinkPresent: true`, `statusBarJsLoaded: true`) | PASS |

## Key Baselines GREEN (102 total _OK markers)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| INV_VERIFY_SCALE_OK | PASS (9/9) |
| INV_LAYER_L1_OK / L2_OK / L3_OK | PASS |
| BUG_20260520_ZEN_EXIT_RP_RESTORE_OK | PASS |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing cosmetic all:False markers (HT8C_OK, HT8D1_OK, HT10_OK, HT12H_OK, PHASE_I_D_OK) unchanged. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

---

# Previous: BUG-20260520-zen-exit-rp-restore — Zen Mode right-panel restore fix

Branch: main
Date: 2026-05-20

## Result: PASS — py_compile PASS; full EXIT 0; 101 _OK markers, 0 E2E_FAIL; NEW BUG_20260520_ZEN_EXIT_RP_RESTORE_OK GREEN (6 sub-checks); all prior 100 markers retained; zero regression.

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  # PASS
python3.11 proto/e2e_ui_test.py full                            # EXIT 0 — 101 _OK markers
```

## New Marker: BUG_20260520_ZEN_EXIT_RP_RESTORE_OK — 6 sub-checks

| Sub-check | Result | Description |
|---|---|---|
| inZen | PASS | `body.zen` class applied after F11 press |
| zenExitedMidDraw | PASS | F11 while mid-draw still exits Zen cleanly |
| f10Toggled | PASS | F10 calls `toggleRightPanel`; panel collapses/restores |
| tabVisibleWhenCollapsed | PASS | `#rp-restore-tab` display:flex when right panel collapsed and not in Zen |
| tabHiddenInZen | PASS | `#rp-restore-tab` display:none when `body.zen` active |
| tabVisibleAfterZenExit | PASS | After Zen exit with right panel collapsed, restore tab reappears |

## Static-Asset Safety

| Check | Result |
|---|---|
| NO_BOM on `proto/static/css/app.css` | PASS |
| `CACHE_OK` | PASS |
| `MAIN_UI_OK` (`cssLinkPresent: true`, `cssVarLoaded: true`) | PASS |

## Key Baselines GREEN (101 total _OK markers)

| Marker | Result |
|---|---|
| ANNOT_OK | PASS |
| PERSIST_OK | PASS |
| REAL_OK | PASS |
| PROJECT_OK | PASS |
| XLSX_OK | PASS |
| PATH_GEOMETRY_OK | PASS |
| INV_VERIFY_SCALE_OK | PASS (9/9) |
| INV_LAYER_L1_OK / L2_OK / L3_OK | PASS |
| BUG_20260520_SEL_MIDPAN_OK | PASS |

Pre-existing cosmetic all:False markers (HT8C_OK, HT8D1_OK, HT10_OK, HT12H_OK, PHASE_I_D_OK) unchanged. Forbidden-surface diff scan CLEAN. UI_REGRESSION_PASS.

<!-- Older test results archived to docs/archive/test-history-2026-05-09.md -->
