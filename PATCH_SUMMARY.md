# PATCH_SUMMARY.md — Latest Sprint

> Full patch history: [docs/archive/patch-history-2026-05-09.md](docs/archive/patch-history-2026-05-09.md)

---

# Latest: BUG-20260520-sel-midpan — Middle-mouse + Space pan in Select mode

Branch: main

Date: 2026-05-20

## Outcome: PASS — Select-mode middle-mouse-button and Space pan now work. Full E2E GREEN. New marker BUG_20260520_SEL_MIDPAN_OK. Total markers: 22.

## Summary

The `ws` mousedown handler's `mode==="sel"` branch had an unconditional `redraw();return` that fired before the pan-intent check, silently discarding middle-mouse (button===1) and Space pan while the Select tool was active. Fixed by inserting a one-line guard at the top of the `sel` branch that mirrors the identical pan guard already in the non-`sel` path. A new E2E test `_test_bug_sel_midpan` verifies that a Playwright middle-button drag moves the canvas transform by the expected delta while keeping `mode==='sel'` throughout. All 21 prior baseline markers remain GREEN.

## Files Changed

| File | Change |
|---|---|
| `proto/ui.html` | +1 line — pan guard at top of `mode==="sel"` mousedown branch (~L2064): `if(e.button===1\|\|spaceDown){isPan=true;...return;}` |
| `proto/e2e_ui_test.py` | +34 lines — `_test_bug_sel_midpan` + call wiring + `BUG_20260520_SEL_MIDPAN_OK` marker |
| `docs/status/PHASE_INDEX.md` | +1 row — BUG-20260520-sel-midpan filed and marked done |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py full                           → EXIT 0 — ALL GREEN
  NEW: BUG_20260520_SEL_MIDPAN_OK GREEN (canvas #cc transform +70x/+45y; mode stayed 'sel')
  21 baseline markers intact incl. PATH_GEOMETRY_OK, ANNOT_OK, PERSIST_OK, REAL_OK
  Total markers: 22
/bma-measure-ux → MEASURE_UX_PASS
/bma-measure-regression → MEASURE_REGRESSION_PASS
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

# Previous: BLOAT-FLAKE-1 — Fix REAL_PDF `_wait_analyse_ready` flake

Branch: main
Date: 2026-05-20

## Outcome: PASS — Full E2E GREEN. Resolves the LOOP_STOP_REGRESSION halt from BLOAT-5. Retroactively confirms BLOAT-5 passes full E2E.

## Summary

Raised `_wait_analyse_ready` default timeout from 30.0 s to 60.0 s and added a grace window: if the status bar still shows active progress (`กำลังโหลด` / `กำลังวิเคราะห์`) at the original deadline, the wait is granted +50% extra time before declaring failure. ~15 LOC changed inside that one helper. No app code, no schema, no other test logic touched. Full E2E now GREEN — `PERSIST_OK` / `REAL_OK` / `ANNOT_OK` no longer flake. Dev-loop unblocked.

## Files Changed

| File | Change |
|---|---|
| `proto/e2e_ui_test.py` | +15 −2 — `_wait_analyse_ready` timeout 30.0→60.0; added grace-window branch for active-loading status |

## Source Files NOT Touched (Forbidden Surfaces)

- `proto/server.py` — NOT TOUCHED
- `proto/ui.html` — NOT TOUCHED
- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNCHANGED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNCHANGED
- `buildSnapIndex`, `snap` engine — UNCHANGED
- `.bmaplan` schema version stays 1; additive fields only

## Tests Run

```
python -m py_compile proto/e2e_ui_test.py                  → PASS
python proto/e2e_ui_test.py full                           → EXIT 0 — ALL GREEN
  PERSIST_OK + REAL_OK + ANNOT_OK GREEN (these flaked 3x during BLOAT-5)
  PHASE_BLOAT2_OK 8/8 + _BLOAT3_OK 8/8 + _BLOAT4_OK 8/8 + _BLOAT5_OK 8/8
  PHASE_INV_PAGE_SETUP_A_OK 8/8 + _B_OK 9/9 + _C_OK 7/7 + PHASE_HT11_OK 10/10
  Retroactively confirms BLOAT-5 (shipped smoke-only) passes full E2E.
/bma-human-test — N/A (test-infrastructure only; no runtime code touched)
```

## Phase 1 Scope Check

- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` — NOT TOUCHED
- ✅ `proto/ui.html` — NOT TOUCHED
- ✅ `.bmaplan` schema — UNCHANGED (version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail
- (only `proto/e2e_ui_test.py` `_wait_analyse_ready` helper changed)

---

<!-- Older entries archived to docs/archive/patch-history-2026-05-09.md -->
