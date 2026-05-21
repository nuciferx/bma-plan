# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: LITE-0 — scaffold standalone /lite/ tree

Branch: main
Date: 2026-05-21

## Result: PASS (no-test rationale for proto full E2E — docs/additive-only sprint in new /lite/ tree)

## No-Test Rationale

Per AGENTS.md §1, sprints that make ZERO changes to proto/ record a no-test rationale instead of running proto E2E. LITE-0 added only new files under `lite/`, `docs/invent/`, `proto/sandbox/`, and `docs/status/PHASE_INDEX.md`. No source code, UI, test code, or schema under `proto/` changed. Therefore proto `py_compile + smoke + full` were not run as regression tests (proto py_compile was run as a sanity guard and passed).

## Tests Run

```bash
python lite/tests/test_measure_parity.py
  -> MEASURE_PARITY_OK
     10 fns + 2 consts byte-identical between proto/ui.html and lite/static/js/measure-engine.js
     5 polys / 2 paths / 4 coords numeric parity via Node.js
     unit square = 25.00 m2 verified

python3.11 -m py_compile lite/server_lite.py lite/launch_lite.py
  -> PASS

python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py
  -> PASS (proto sanity guard — confirmed proto untouched)

Playwright render lite/ui-lite.html
  -> self-test "engine wired", 0 console errors
```

## Reference Baseline (from previous sprint HT-ACC series 2026-05-20)

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  -> PASS
python3.11 proto/e2e_ui_test.py smoke                          -> PASS (18 baseline markers)
python3.11 proto/e2e_ui_test.py full                           -> PASS (102 _OK markers)
```

Markers include: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK, ANNOT_OK, PERSIST_OK, REAL_OK, HT_ACC_OK, and 80+ additional sprint markers. Total 102 _OK. All unchanged by LITE-0.

---

# Previous: HT-ACC series (HT-ACC-1 + HT-ACC-2 + HT-ACC-3 + HT-NAV-1) — Calibration accuracy UX

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

<!-- BUG-20260520-zen-exit-rp-restore and older test results archived to docs/archive/test-history-2026-05-09.md -->
