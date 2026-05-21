# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: LITE-REPORT (INV-2026-05-21-002) — editable web report page for lite

Branch: main
Date: 2026-05-22

## Result: PASS (no-test rationale for proto full E2E — zero proto/ edits; lite tree isolated)

## No-Test Rationale

Per AGENTS.md §1, sprints that make ZERO changes to proto/ record a no-test rationale instead of running proto E2E. This sprint changed only files under `lite/` and `docs/status/PHASE_INDEX.md`. No source code, UI, test code, or schema under `proto/` changed. Therefore proto `py_compile + smoke + full` were not run as regression tests.

## Tests Run

```bash
py_compile lite/server_lite.py lite/launch_lite.py
  -> PY_COMPILE_OK

lite/tests/test_report.py
  -> LITE_REPORT_OK GREEN (17/17 checks)

lite/tests/test_measure_parity.py
  -> MEASURE_PARITY_OK GREEN (16 fns + 2 consts byte-identical; area math unaffected)

lite/tests/test_menu_clickable.py
  -> BUG_20260521_LITE_MENU_CLIP_OK GREEN (no regression)

lite/tests/test_pan_controls.py
  -> BUG_20260521_LITE_PAN_OK GREEN (no regression)

artifacts/realflow_check.py
  -> REALFLOW_OK
     real permit PDF upload → openReport → popup window caught
     plan image naturalWidth 3576, viewBox "0 0 3576 2526"
     SVG polygon overlay rendered → net area 222.22
```

New E2E marker: LITE_REPORT_OK

## Reference Baseline (from previous sprint HT-ACC series 2026-05-20)

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  -> PASS
python3.11 proto/e2e_ui_test.py smoke                          -> PASS (18 baseline markers)
python3.11 proto/e2e_ui_test.py full                           -> PASS (102 _OK markers)
```

Markers include: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK, ANNOT_OK, PERSIST_OK, REAL_OK, HT_ACC_OK, and 80+ additional sprint markers. Total 102 _OK. All unchanged by this sprint.

---

# Previous: BUG-20260521-lite-pan-controls — Fork proto view/navigation control system into lite

Branch: main
Date: 2026-05-21

## Result: PASS (no-test rationale for proto full E2E — zero proto/ edits; lite tree isolated)

## No-Test Rationale

Per AGENTS.md §1, sprints that make ZERO changes to proto/ record a no-test rationale instead of running proto E2E. This sprint changed only files under `lite/` and `docs/status/PHASE_INDEX.md`. No source code, UI, test code, or schema under `proto/` changed. Therefore proto `py_compile + smoke + full` were not run as regression tests.

## Tests Run

```bash
py -3 -m py_compile lite/server_lite.py lite/tests/test_pan_controls.py lite/tests/test_menu_clickable.py
  -> PYCOMPILE_OK

lite/tests/test_pan_controls.py
  -> BUG_20260521_LITE_PAN_OK GREEN (13/13 checks)
     midPan, spaceArmed, spacePanMidDraw, panToolOn, panToolDrag, panToolOff,
     selectPan, clampMax, clampMin, wheelZoomIn, actualSize, fit, ctrlZoomIn

lite/tests/test_menu_clickable.py
  -> BUG_20260521_LITE_MENU_CLIP_OK GREEN (no regression)

lite/tests/test_measure_parity.py
  -> MEASURE_PARITY_OK GREEN (ptToScreen/screenToPt/RS untouched; coordinate math byte-identical)
```

## Reference Baseline (from previous sprint HT-ACC series 2026-05-20)

```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  -> PASS
python3.11 proto/e2e_ui_test.py smoke                          -> PASS (18 baseline markers)
python3.11 proto/e2e_ui_test.py full                           -> PASS (102 _OK markers)
```

Markers include: CACHE_OK, SETUP_OK, MAIN_UI_OK, VECTOR_OK, RECAL_OK, SITE_UI_OK, XLSX_OK, PROJECT_OK, RASTER_OK, WHEEL_OK, SNAP_OK, SELECT_OK, SETBACK_OK, EXT_MEASURE_OK, MENU_OK, PATH_GEOMETRY_OK, PHASE_I_A_OK, PHASE_I_B1_OK, ANNOT_OK, PERSIST_OK, REAL_OK, HT_ACC_OK, and 80+ additional sprint markers. Total 102 _OK. All unchanged by this sprint.

---

# Previous (older): LITE-0 — scaffold standalone /lite/ tree

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

<!-- HT-ACC series and older test results archived to docs/archive/test-history-2026-05-09.md -->
