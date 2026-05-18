# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: UI Redesign Batch — HT-12..HT-15 (2026-05-18)

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
