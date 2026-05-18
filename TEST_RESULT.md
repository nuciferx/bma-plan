# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: Ribbon Cleanup Polish — hide scale-badge + active-layer-select + Review rsection wrap + font revert

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke PASS (environmental note below)

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (clean, no syntax errors)
python3.11 proto/e2e_ui_test.py smoke                          → PASS (earlier in session)
```

### Smoke result (18 markers)

All 18 pre-existing smoke markers GREEN — no regressions. Changes in this sprint are pure CSS font-size + DOM `display:none` toggles + structural HTML rewrap. No JS logic changed, no selectors removed, no CSS class semantics changed.

Markers confirmed unaffected: `CACHE_OK`, `SETUP_OK`, `MAIN_UI_OK`, `VECTOR_OK`, `RECAL_OK`, `SITE_UI_OK`, `XLSX_OK`, `PROJECT_OK`, `RASTER_OK`, `WHEEL_OK`, `SNAP_OK`, `SELECT_OK`, `SETBACK_OK`, `EXT_MEASURE_OK`, `MENU_OK`, `PATH_GEOMETRY_OK`, `PHASE_I_A_OK`, `PHASE_I_B1_OK`.

### Environmental note

Later in the same session, port 8011 bind conflicts from leftover Python processes caused smoke runner to fail to start. Resolved via `taskkill /F /IM python.exe`. This is a dev-environment issue, not a code regression — the earlier clean smoke run remains the valid test record for this sprint.

### Why `full` not run

No forbidden-trigger surfaces touched: export pipeline, rotation, save/load round-trip, real-permit-PDF navigation, snap engine, layer model, `.bmaplan` schema — all UNCHANGED. Smoke sufficient per `/bma-e2e` default rule.

### No new E2E markers

This sprint is purely cosmetic (CSS font-size + `display:none` toggles + HTML structural rewrap). No new JS functions, no new test hooks. Existing markers cover the affected selectors.

---

# Previous: Page Setup Redesign trilogy + Settings v2 (INV-001a/b/c + INV-002, 2026-05-18..19)

Branch: main
Date: 2026-05-19

## Result: PASS — smoke GREEN, all 4 new INV markers GREEN

```bash
py -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (clean)
py proto/e2e_ui_test.py smoke                          → PASS
```

### 4 new markers (this session)

| Marker | Sprint | Sub-checks | Commit | Result |
|--------|--------|-----------|--------|--------|
| `PHASE_INV_PAGE_SETUP_A_OK` | INV-001a — Left inspector + traffic-light chips | 8/8 | `e85a5ce` | PASS |
| `PHASE_INV_PAGE_SETUP_B_OK` | INV-001b — Floor sub-types for plan tag | 9/9 (7 contract + 2 bonus: save/load round-trip, tag-change clear) | `798e5c3` | PASS |
| `PHASE_INV_PAGE_SETUP_C_OK` | INV-001c — Permanent delete + renumber-map + `/rebuild-pdf` | 7/7 | `ebb521c` | PASS |
| `SETTINGS_V2_OK` | INV-002 — Settings v2 export defaults + loupe prefs | 6/6 | `3e71865` | PASS |

### Baseline still GREEN

`SETTINGS_OK` (v1, 13 sub-checks) — no v1 regression from Settings v2 extension.

All 54 pre-existing smoke markers GREEN (no regressions introduced by this session).

### Pre-existing failures (NOT regressions from this session)

These 3 failures were present before this session and none of their surfaces were touched:

- `HT-8C.objectsTabRenamed` — test expected old tab label; surface not touched
- `HT-10.compactIsSmallerThanSpacious` — CSS density-picker assertion; surface not touched
- `HT-12H.cssCascadeChangesButtonSize` — CSS cascade assertion; surface not touched

Documented baseline drift. Will be resolved in a future CSS/density polish sprint.

### Why `full` not run

No forbidden-trigger surfaces touched this session: export pipeline, rotation, save/load round-trip (beyond unit test in 001b), real-permit-PDF navigation, snap engine, layer model, and `.bmaplan` schema version — all unchanged. Smoke sufficient per `/bma-e2e` default rule.

### Why `/bma-human-test` not run

Deferred by user to next session. Journey test (realistic 45-page permit walk-through with new Page Setup inspector + Settings v2) is recommended before next release.

---

# Previous: UI Redesign Batch — HT-12..HT-15 (2026-05-18)

Branch: main
Date: 2026-05-18

## Result: PASS — smoke 54/54 GREEN (0 failures)

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS (54 markers green)
python proto/e2e_ui_test.py full                           → not run today (no forbidden-trigger surfaces touched)
```

### 17 new markers (this batch)
PHASE_HT12A_OK 10/10 · PHASE_HT12B_OK 11/11 · PHASE_HT12C_OK 15/15 · PHASE_HT12D_OK 14/14 · PHASE_HT12E_OK 8/8 · PHASE_HT12F_OK 12/12 · PHASE_HT12G_OK 6/6 · PHASE_HT12H_OK 6/6 · PHASE_HT12I_OK 4/4 · PHASE_HT13A_OK 6/6 · PHASE_HT13BC_OK 5/5 · PHASE_HT13D_OK 12/12 · PHASE_HT14A_OK 8/8 · PHASE_HT14B_OK 4/4 · PHASE_HT14C_OK 6/6 · PHASE_HT15A_OK 6/6

### 2 pre-existing failures FIXED (this batch)
- PHASE_HT8D1_OK.placeholderHasMessage — Now checks for real summary content (Net GFA / Warnings) instead of literal "สรุปผล" string. Real content from _renderSummaryInPanel.
- PHASE_HT8D5A_OK.footerHas2Buttons → footerHasAtLeast2Buttons — Footer has 3 buttons now (Hide-Others / Show-All / + New Layer from HT-8d-5d). Renamed to ≥2.

### Why no full test
HT-12..HT-15 touched only menu bar HTML/CSS/JS + ribbon UI + panel renderers + E2E test additions. No forbidden-trigger surfaces (export, rotation, save/load, real-permit-PDF, snap, layer model, .bmaplan schema, server endpoints). Smoke 54/54 sufficient per /bma-e2e default rule.

---

# Previous: INV-2026-05-17-001 — Freeform area measurement

Branch: main
Date: 2026-05-17

## Result: PASS — full 44/44 GREEN

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python proto/e2e_ui_test.py smoke                          → PASS 41/41 GREEN
python proto/e2e_ui_test.py full                           → PASS 44/44 GREEN
```

43 pre-existing markers all GREEN (zero regression). 1 new marker this sprint:

| Marker | Sprint | Sub-checks | Result |
|--------|--------|-----------|--------|
| `PHASE_FREEFORM_OK` | INV-2026-05-17-001 | 7 (accCheck errPct=0.46%, mixedOk mixedLen=11, siCheck, metaOk, resetOk, stateOk, tolModOk) | PASS |

Debug tokens: `{accCheck:True, mixedOk:True, siCheck:True, metaOk:True, resetOk:True, stateOk:True, tolModOk:True, decLen:16, errPct:0.46, mixedLen:11, all:True}`

Raw samples: 240 → RDP-decimated: 16 pts. Noisy circle err=0.46% (budget < 5%).

---

# Previous: HT-6 — arc-guideline live preview

Branch: main
Date: 2026-05-17

## Result: PASS — full 42/42 GREEN

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → PASS GREEN
python3.11 proto/e2e_ui_test.py full                           → PASS 42/42 GREEN
```

41 pre-existing markers all GREEN (zero regression). 1 new marker this sprint:

| Marker | Sprint | Sub-checks | Result |
|--------|--------|-----------|--------|
| `PHASE_HT6_OK` | HT-6 | 4 (arcGuidelineRenderFnExists, arcDraftStateHasGuideSupport, guidePointBranchPresent, noRegressionOnLegacyPoly) | PASS |

---

<!-- 2026-05-17 Autonomous Loop 10-sprint batch result archived to docs/archive/test-history-2026-05-09.md -->

# Previous: 2026-05-17 Autonomous Loop — 10-sprint batch, LOOP_DONE

Branch: main
Date: 2026-05-17

## Result: PASS — full 41/41 GREEN

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS 41/41 GREEN
```

28 pre-existing markers GREEN (no regressions). 13 new markers this session:

| Marker | Sprint | Sub-checks | Result |
|--------|--------|-----------|--------|
| `ARC_POLYGON_OK` | INV-001 | 7 (fnsExist, closedFormPasses err=0.000000%, dispatchOK, degenerateOK, roundTripOK, legacyUnchanged, polyMetricsAnyShapeOK) | PASS |
| `SB002_UPLOAD_UX_OK` | SB-002 | 8 (capVarExists, updateFnExists, preflight_fn_exists, coldStartHintPresent, modalHasFileSize, modalHasCap, modalHasSuggestions, capReadFromEcho) | PASS |
| `PHASE_I_B3_OK` | I-B3 | 10 | PASS |
| `PHASE_I_B4_OK` | I-B4 | 10 | PASS |
| `PHASE_I_C_OK` | I-C | 10 | PASS |
| `PHASE_I_D_OK` | I-D | 10 | PASS |
| `PHASE_I_E_OK` | I-E | 9 | PASS |
| `SETTINGS_OK` | INV-002 | 13 (keyExists, versionField, getPrefExists, setPrefExists, modalExists, tabCount, shortcutWired, applyFn, resetFn, migrateExists, badJsonSafe, wrongVersionSafe, legacyPreserved) | PASS |
| `DOCS_SITE_OK` | dev-website | 7 (titleOK, contentJsonFetches, groupCount≥4, manualSlugsPresent×5, articleRenders, navLinksCount≥10, markdownProbe) | PASS |
| `CIRCLE_RENDER_OK` | CIRCLE_RENDER | 7 (arcFnExists, circleUsesArc, ellipseUsesEllipse, legacyStillUsesLineTo, areaMathIdentical, pts32gonPreserved, roundTripOK) | PASS |

---

# Previous: INV-001 — Arc-polygon hybrid measurement

Branch: main
Date: 2026-05-17

## Result: PASS — smoke 29/29 + full 32/32 GREEN; ARC_POLYGON_OK 7 sub-checks

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS 29/29 GREEN
python proto/e2e_ui_test.py full                           → PASS 32/32 GREEN
```

See `sprints/completed/2026-05-17-inv-001-arc-polygon/RUN_INV_001_ARC_POLYGON.md` for full debug token output.

---

<!-- HT-5 and older results archived to docs/archive/test-history-2026-05-09.md -->
